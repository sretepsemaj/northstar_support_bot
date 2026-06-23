from dataclasses import replace

import httpx
import pytest

from backend.core.config import Settings
from backend.services.intent_service import Intent
from backend.services.llm_service import (
    LLMAssistResult,
    build_recommendation_assist_result,
    is_llm_configured,
    review_ambiguous_message,
)

BASE_SETTINGS = Settings(
    app_name="North Star Support Bot",
    app_env="test",
    app_host="0.0.0.0",
    app_port=8000,
    use_llm=False,
    llm_provider=None,
    llm_model=None,
    llm_api_key=None,
)


def test_review_ambiguous_message_returns_none_when_llm_is_disabled():
    result = review_ambiguous_message("I need raincoats", settings=BASE_SETTINGS)

    assert result is None
    assert is_llm_configured(BASE_SETTINGS) is False


def test_review_ambiguous_message_returns_none_when_llm_config_is_incomplete():
    settings = replace(BASE_SETTINGS, use_llm=True, llm_provider="openai-compatible")

    result = review_ambiguous_message("I need raincoats", settings=settings)

    assert result is None


def test_review_ambiguous_message_uses_openai_adapter_when_configured(monkeypatch):
    settings = replace(
        BASE_SETTINGS,
        use_llm=True,
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        llm_api_key="test-key",
    )

    assert is_llm_configured(settings) is True

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": (
                                '{"intent":"product_recommendation", '
                                '"category":"Weather Protection", '
                                '"reply_hint":null, '
                                '"needs_handoff":false}'
                            )
                        }
                    }
                ]
            }

    def fake_post(url, headers, json, timeout):
        assert url == "https://api.openai.com/v1/chat/completions"
        assert headers["Authorization"] == "Bearer test-key"
        assert json["model"] == "gpt-4o-mini"
        assert json["temperature"] == 0
        assert json["max_tokens"] == 80
        assert timeout == 10
        return FakeResponse()

    monkeypatch.setattr("backend.services.llm_service.httpx.post", fake_post)

    result = review_ambiguous_message("I need raincoats", settings=settings)

    assert result == LLMAssistResult(
        intent=Intent.PRODUCT_RECOMMENDATION,
        category="Weather Protection",
        used_llm=True,
    )


def test_review_ambiguous_message_returns_none_when_openai_call_fails(monkeypatch):
    settings = replace(
        BASE_SETTINGS,
        use_llm=True,
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        llm_api_key="test-key",
    )

    def fake_post(url, headers, json, timeout):
        raise httpx.ConnectError("network unavailable")

    monkeypatch.setattr("backend.services.llm_service.httpx.post", fake_post)

    result = review_ambiguous_message("I need raincoats", settings=settings)

    assert result is None


def test_build_recommendation_assist_result_limits_categories():
    result = build_recommendation_assist_result("Weather Protection")

    assert result == LLMAssistResult(
        intent=Intent.PRODUCT_RECOMMENDATION,
        category="Weather Protection",
        used_llm=True,
    )


def test_build_recommendation_assist_result_rejects_unknown_categories():
    with pytest.raises(ValueError):
        build_recommendation_assist_result("Made Up Gear")
