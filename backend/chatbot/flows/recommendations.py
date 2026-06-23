from typing import Any

from backend.chatbot.constants import (
    ACTIVE_FLOW,
    PRODUCT_RECOMMENDATION_FLOW,
    RECOMMENDATION_CONTEXT,
    WAITING_FOR,
)
from backend.chatbot.responses.recommendations import format_recommendation_response
from backend.services.intent_service import Intent
from backend.services.recommendation_service import recommend_category


def build_recommendation_result(message: str) -> tuple[str, Intent, dict[str, Any], bool]:
    recommendation = recommend_category(message)
    state: dict[str, Any] = {ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW}

    if recommendation.needs_clarification:
        state[WAITING_FOR] = RECOMMENDATION_CONTEXT

    return (
        format_recommendation_response(recommendation),
        Intent.PRODUCT_RECOMMENDATION,
        state,
        False,
    )
