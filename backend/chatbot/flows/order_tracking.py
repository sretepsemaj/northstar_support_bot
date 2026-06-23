from typing import Any

from backend.chatbot.constants import (
    ACTIVE_FLOW,
    MAIN_MENU_FLOW,
    ORDER_NUMBER,
    ORDER_TRACKING_FLOW,
    WAITING_FOR,
)
from backend.chatbot.responses.order_tracking import (
    ORDER_NUMBER_PROMPT,
    format_order_lookup_response,
)
from backend.services.intent_service import Intent
from backend.services.order_service import lookup_order, normalize_order_number


def build_order_tracking_result(message: str) -> tuple[str, Intent, dict[str, Any], bool]:
    order_number = normalize_order_number(message)

    if order_number is None:
        return (
            ORDER_NUMBER_PROMPT,
            Intent.ORDER_TRACKING,
            {ACTIVE_FLOW: ORDER_TRACKING_FLOW, WAITING_FOR: ORDER_NUMBER},
            False,
        )

    return build_order_lookup_result(message)


def build_order_lookup_result(message: str) -> tuple[str, Intent, dict[str, Any], bool]:
    result = lookup_order(message)
    next_state = {ACTIVE_FLOW: MAIN_MENU_FLOW}

    if not result.found:
        next_state = {ACTIVE_FLOW: ORDER_TRACKING_FLOW, WAITING_FOR: ORDER_NUMBER}

    return (
        format_order_lookup_response(result),
        Intent.ORDER_TRACKING,
        next_state,
        False,
    )
