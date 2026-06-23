from typing import Any

from backend.chatbot.constants import (
    ACTIVE_FLOW,
    RECOMMENDATION_CATEGORY,
    PRODUCT_RECOMMENDATION_FLOW,
    RECOMMENDATION_CONTEXT,
    RECOMMENDATION_DETAIL,
    WAITING_FOR,
)
from backend.chatbot.responses.recommendations import format_recommendation_response
from backend.services.intent_service import Intent
from backend.services.recommendation_service import (
    recommend_category,
    recommend_category_detail,
)


def build_recommendation_result(message: str) -> tuple[str, Intent, dict[str, Any], bool]:
    recommendation = recommend_category(message)
    state: dict[str, Any] = {ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW}

    if recommendation.needs_clarification:
        state[WAITING_FOR] = (
            RECOMMENDATION_DETAIL
            if recommendation.waiting_for_detail
            else RECOMMENDATION_CONTEXT
        )
        if recommendation.category is not None:
            state[RECOMMENDATION_CATEGORY] = recommendation.category

    return (
        format_recommendation_response(recommendation),
        Intent.PRODUCT_RECOMMENDATION,
        state,
        False,
    )


def build_recommendation_detail_result(
    category: str,
    message: str,
) -> tuple[str, Intent, dict[str, Any], bool]:
    recommendation = recommend_category_detail(category, message)
    state: dict[str, Any] = {ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW}

    if recommendation.needs_clarification:
        state[WAITING_FOR] = (
            RECOMMENDATION_DETAIL
            if recommendation.waiting_for_detail
            else RECOMMENDATION_CONTEXT
        )
        if recommendation.category is not None:
            state[RECOMMENDATION_CATEGORY] = recommendation.category

    return (
        format_recommendation_response(recommendation),
        Intent.PRODUCT_RECOMMENDATION,
        state,
        False,
    )
