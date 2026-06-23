from dataclasses import dataclass, field
from typing import Any

from backend.chatbot.constants import ORDER_NUMBER, WAITING_FOR
from backend.chatbot.flows.fallback import build_fallback_result
from backend.chatbot.flows.gratitude import build_gratitude_result
from backend.chatbot.flows.handoff import build_handoff_result
from backend.chatbot.flows.main_menu import build_main_menu_result
from backend.chatbot.flows.order_tracking import (
    build_order_lookup_result,
    build_order_tracking_result,
)
from backend.chatbot.flows.recommendations import build_recommendation_result
from backend.chatbot.flows.returns_exchange import build_returns_exchange_result
from backend.services.intent_service import Intent, IntentResult, detect_intent


@dataclass(frozen=True)
class ChatServiceResult:
    reply: str
    intent: Intent
    state: dict[str, Any] = field(default_factory=dict)
    handoff: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


def _build_metadata(intent_result: IntentResult) -> dict[str, Any]:
    return {
        "matched_terms": intent_result.matched_terms,
        "match_strategy": intent_result.match_strategy,
        "needs_review": intent_result.needs_review,
        "intent_reviewed": False,
    }


def _build_result(
    flow_result: tuple[str, Intent, dict[str, Any], bool],
    intent_result: IntentResult,
) -> ChatServiceResult:
    reply, intent, state, handoff = flow_result
    return ChatServiceResult(
        reply=reply,
        intent=intent,
        state=state,
        handoff=handoff,
        metadata=_build_metadata(intent_result),
    )


def _is_waiting_for_order_number(state: dict[str, Any] | None) -> bool:
    return bool(state and state.get(WAITING_FOR) == ORDER_NUMBER)


def handle_chat(message: str, state: dict[str, Any] | None = None) -> ChatServiceResult:
    intent_result = detect_intent(message)

    if _is_waiting_for_order_number(state):
        return _build_result(build_order_lookup_result(message), intent_result)

    if intent_result.intent == Intent.PRODUCT_RECOMMENDATION:
        return _build_result(build_recommendation_result(message), intent_result)

    if intent_result.intent == Intent.ORDER_TRACKING:
        return _build_result(build_order_tracking_result(message), intent_result)

    if intent_result.intent == Intent.RETURNS_EXCHANGE:
        return _build_result(build_returns_exchange_result(message), intent_result)

    if intent_result.intent == Intent.GRATITUDE:
        return _build_result(build_gratitude_result(), intent_result)

    if intent_result.intent == Intent.HUMAN_HANDOFF:
        return _build_result(build_handoff_result(), intent_result)

    if intent_result.intent == Intent.FALLBACK:
        return _build_result(build_fallback_result(), intent_result)

    return _build_result(build_main_menu_result(), intent_result)
