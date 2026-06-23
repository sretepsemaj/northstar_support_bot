from typing import Any

from backend.chatbot.constants import ACTIVE_FLOW, SHIPPING_INFO_FLOW
from backend.chatbot.responses.shipping import format_shipping_response
from backend.services.intent_service import Intent
from backend.services.shipping_service import get_shipping_policy


def build_shipping_result() -> tuple[str, Intent, dict[str, Any], bool]:
    policy = get_shipping_policy()
    return (
        format_shipping_response(policy),
        Intent.SHIPPING_INFO,
        {ACTIVE_FLOW: SHIPPING_INFO_FLOW},
        False,
    )
