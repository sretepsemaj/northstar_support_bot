import json
from dataclasses import dataclass

import httpx

from backend.core.config import Settings, get_settings
from backend.services.intent_service import Intent

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"

ALLOWED_RECOMMENDATION_CATEGORIES = {
    "Camping Gear",
    "Outdoor Apparel",
    "Hiking Footwear",
    "Climbing Essentials",
    "Weather Protection",
}

ALLOWED_LLM_INTENTS = {
    Intent.MAIN_MENU,
    Intent.PRODUCT_RECOMMENDATION,
    Intent.ORDER_TRACKING,
    Intent.RETURNS_EXCHANGE,
    Intent.GRATITUDE,
    Intent.HUMAN_HANDOFF,
    Intent.FALLBACK,
}


@dataclass(frozen=True)
class LLMAssistResult:
    intent: Intent
    category: str | None = None
    reply_hint: str | None = None
    needs_handoff: bool = False
    used_llm: bool = False


def _is_configured(settings: Settings) -> bool:
    return bool(
        settings.use_llm
        and settings.llm_provider
        and settings.llm_model
        and settings.llm_api_key
    )


def _build_openai_messages(message: str) -> list[dict[str, str]]:
    allowed_categories = ", ".join(sorted(ALLOWED_RECOMMENDATION_CATEGORIES))
    allowed_intents = ", ".join(intent.value for intent in ALLOWED_LLM_INTENTS)
    return [
        {
            "role": "developer",
            "content": (
                "You are a lightweight classifier for North Star Support Bot, "
                "a fictional outdoor apparel and camping gear e-commerce support chatbot. "
                "Do not answer the customer directly. Return compact JSON only. "
                f"Allowed intents: {allowed_intents}. "
                f"Allowed recommendation categories: {allowed_categories}. "
                "Use product_recommendation for shopping, gear, apparel, boots, jackets, "
                "rainwear, camping, hiking, climbing, tents, sleeping bags, or outdoor products. "
                "Use order_tracking for shipping, arrival, package, delivery, or order status. "
                "Use returns_exchange for returns, exchanges, refunds, or return policy. "
                "Use human_handoff only for explicit human/live agent requests or clear frustration. "
                "Use fallback for unrelated messages. "
                "JSON shape: "
                '{"intent":"...", "category":null, "reply_hint":null, "needs_handoff":false}'
            ),
        },
        {
            "role": "user",
            "content": message,
        },
    ]


def _parse_assist_payload(content: str) -> LLMAssistResult | None:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return None

    try:
        intent = Intent(payload.get("intent"))
    except ValueError:
        return None

    if intent not in ALLOWED_LLM_INTENTS:
        return None

    category = payload.get("category")
    if category is not None and category not in ALLOWED_RECOMMENDATION_CATEGORIES:
        category = None

    return LLMAssistResult(
        intent=intent,
        category=category,
        reply_hint=payload.get("reply_hint") or None,
        needs_handoff=bool(payload.get("needs_handoff")),
        used_llm=True,
    )


def _review_with_openai(message: str, settings: Settings) -> LLMAssistResult | None:
    response = httpx.post(
        OPENAI_CHAT_COMPLETIONS_URL,
        headers={
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.llm_model,
            "messages": _build_openai_messages(message),
            "temperature": 0,
            "max_tokens": 80,
        },
        timeout=10,
    )
    response.raise_for_status()

    content = (
        response.json()
        .get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    if not isinstance(content, str):
        return None
    return _parse_assist_payload(content)


def review_ambiguous_message(
    message: str,
    settings: Settings | None = None,
) -> LLMAssistResult | None:
    """Optional last automated pass before fallback or handoff.

    The deterministic bot owns business facts. This seam exists so a provider
    adapter can later map ambiguous user language to one of our allowed intents
    or recommendation categories without changing the conversation flow.
    """
    active_settings = settings or get_settings()
    if not _is_configured(active_settings):
        return None

    if active_settings.llm_provider == "openai":
        try:
            return _review_with_openai(message, active_settings)
        except httpx.HTTPError:
            return None

    return None


def build_recommendation_assist_result(category: str) -> LLMAssistResult:
    if category not in ALLOWED_RECOMMENDATION_CATEGORIES:
        raise ValueError(f"Unsupported recommendation category: {category}")

    return LLMAssistResult(
        intent=Intent.PRODUCT_RECOMMENDATION,
        category=category,
        used_llm=True,
    )
