from dataclasses import dataclass, field
from typing import Any

from backend.chatbot.constants import (
    ACTIVE_FLOW,
    MAIN_MENU_FLOW,
    ORDER_NUMBER,
    RECOMMENDATION_CATEGORY,
    RECOMMENDATION_CONTEXT,
    RECOMMENDATION_DETAIL,
    WAITING_FOR,
)
from backend.chatbot.flows.fallback import build_fallback_result
from backend.chatbot.flows.gratitude import build_gratitude_result
from backend.chatbot.flows.handoff import build_handoff_result
from backend.chatbot.flows.main_menu import build_main_menu_result
from backend.chatbot.flows.order_tracking import (
    build_order_lookup_result,
    build_order_tracking_result,
)
from backend.chatbot.flows.recommendations import (
    build_recommendation_detail_result,
    build_recommendation_result,
)
from backend.chatbot.flows.returns_exchange import build_returns_exchange_result
from backend.chatbot.flows.shipping import build_shipping_result
from backend.services.intent_service import Intent, IntentResult, detect_intent
from backend.services.llm_service import (
    LLMAssistResult,
    is_llm_configured,
    review_ambiguous_message,
)
from backend.services.order_service import normalize_order_number


@dataclass(frozen=True)
class ChatServiceResult:
    reply: str
    intent: Intent
    state: dict[str, Any] = field(default_factory=dict)
    handoff: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


def _build_metadata(
    intent_result: IntentResult,
    llm_attempted: bool = False,
    intent_reviewed: bool = False,
    llm_category: str | None = None,
) -> dict[str, Any]:
    metadata = {
        "matched_terms": intent_result.matched_terms,
        "match_strategy": intent_result.match_strategy,
        "needs_review": intent_result.needs_review,
        "llm_attempted": llm_attempted,
        "intent_reviewed": intent_reviewed,
    }
    if llm_category:
        metadata["llm_category"] = llm_category
    return metadata


def _build_result(
    flow_result: tuple[str, Intent, dict[str, Any], bool],
    intent_result: IntentResult,
    llm_attempted: bool = False,
    intent_reviewed: bool = False,
    llm_category: str | None = None,
) -> ChatServiceResult:
    reply, intent, state, handoff = flow_result
    return ChatServiceResult(
        reply=reply,
        intent=intent,
        state=state,
        handoff=handoff,
        metadata=_build_metadata(
            intent_result,
            llm_attempted=llm_attempted,
            intent_reviewed=intent_reviewed,
            llm_category=llm_category,
        ),
    )


def _is_waiting_for_order_number(state: dict[str, Any] | None) -> bool:
    return bool(state and state.get(WAITING_FOR) == ORDER_NUMBER)


def _is_waiting_for_recommendation_context(state: dict[str, Any] | None) -> bool:
    return bool(state and state.get(WAITING_FOR) == RECOMMENDATION_CONTEXT)


def _is_waiting_for_recommendation_detail(state: dict[str, Any] | None) -> bool:
    return bool(
        state
        and state.get(WAITING_FOR) == RECOMMENDATION_DETAIL
        and state.get(RECOMMENDATION_CATEGORY)
    )


def _should_handle_order_number_reply(message: str, intent_result: IntentResult) -> bool:
    if normalize_order_number(message) is not None:
        return True
    return intent_result.intent in {Intent.ORDER_TRACKING, Intent.FALLBACK}


def _is_main_menu_selection(state: dict[str, Any] | None) -> bool:
    return bool(state and state.get(ACTIVE_FLOW) == MAIN_MENU_FLOW)


def _build_menu_selection_result(message: str) -> tuple[str, Intent, dict[str, Any], bool] | None:
    normalized = message.strip().lower()
    if normalized == "1":
        return build_order_tracking_result("order tracking")
    if normalized == "2":
        return build_returns_exchange_result("return policy")
    if normalized == "3":
        return build_recommendation_result("recommend")
    return None


def _build_llm_assist_result(
    assist: LLMAssistResult | None,
    message: str,
) -> tuple[str, Intent, dict[str, Any], bool] | None:
    if assist is None:
        return None

    if assist.intent == Intent.MAIN_MENU:
        return build_main_menu_result()

    if assist.needs_handoff or assist.intent == Intent.HUMAN_HANDOFF:
        return build_handoff_result()

    if assist.intent == Intent.PRODUCT_RECOMMENDATION and assist.category:
        return build_recommendation_result(assist.category)

    if assist.intent == Intent.PRODUCT_RECOMMENDATION:
        return build_recommendation_result(message)

    if assist.intent == Intent.ORDER_TRACKING:
        return build_order_tracking_result(message)

    if assist.intent == Intent.SHIPPING_INFO:
        return build_shipping_result()

    if assist.intent == Intent.RETURNS_EXCHANGE:
        return build_returns_exchange_result(message)

    if assist.intent == Intent.GRATITUDE:
        return build_gratitude_result()

    return None


def handle_chat(message: str, state: dict[str, Any] | None = None) -> ChatServiceResult:
    intent_result = detect_intent(message)

    if _is_main_menu_selection(state):
        menu_selection_result = _build_menu_selection_result(message)
        if menu_selection_result is not None:
            return _build_result(menu_selection_result, intent_result)

    if _is_waiting_for_order_number(state) and _should_handle_order_number_reply(message, intent_result):
        return _build_result(build_order_lookup_result(message), intent_result)

    if _is_waiting_for_recommendation_context(state) and intent_result.intent in {
        Intent.PRODUCT_RECOMMENDATION,
        Intent.FALLBACK,
    }:
        return _build_result(build_recommendation_result(message), intent_result)

    if _is_waiting_for_recommendation_detail(state) and intent_result.intent in {
        Intent.PRODUCT_RECOMMENDATION,
        Intent.FALLBACK,
    }:
        detail_result = build_recommendation_detail_result(
            state[RECOMMENDATION_CATEGORY],
            message,
        )
        detail_state = detail_result[2]
        llm_attempted = is_llm_configured()
        if detail_state.get(WAITING_FOR) == RECOMMENDATION_CONTEXT and llm_attempted:
            assist = review_ambiguous_message(message)
            assist_result = _build_llm_assist_result(assist, message)
            if assist_result is not None:
                return _build_result(
                    assist_result,
                    intent_result,
                    llm_attempted=llm_attempted,
                    intent_reviewed=bool(assist and assist.used_llm),
                    llm_category=assist.category if assist else None,
                )

        return _build_result(
            detail_result,
            intent_result,
            llm_attempted=(
                llm_attempted
                if detail_state.get(WAITING_FOR) == RECOMMENDATION_CONTEXT
                else False
            ),
        )

    if intent_result.intent == Intent.PRODUCT_RECOMMENDATION:
        return _build_result(build_recommendation_result(message), intent_result)

    if intent_result.intent == Intent.ORDER_TRACKING:
        return _build_result(build_order_tracking_result(message), intent_result)

    if intent_result.intent == Intent.SHIPPING_INFO:
        return _build_result(build_shipping_result(), intent_result)

    if intent_result.intent == Intent.RETURNS_EXCHANGE:
        return _build_result(build_returns_exchange_result(message), intent_result)

    if intent_result.intent == Intent.GRATITUDE:
        return _build_result(build_gratitude_result(), intent_result)

    if intent_result.intent == Intent.HUMAN_HANDOFF:
        return _build_result(build_handoff_result(), intent_result)

    if intent_result.intent == Intent.FALLBACK:
        llm_attempted = is_llm_configured()
        assist = review_ambiguous_message(message)
        assist_result = _build_llm_assist_result(assist, message)
        if assist_result is not None:
            return _build_result(
                assist_result,
                intent_result,
                llm_attempted=llm_attempted,
                intent_reviewed=bool(assist and assist.used_llm),
                llm_category=assist.category if assist else None,
            )
        return _build_result(
            build_fallback_result(),
            intent_result,
            llm_attempted=llm_attempted,
        )

    return _build_result(build_main_menu_result(), intent_result)
