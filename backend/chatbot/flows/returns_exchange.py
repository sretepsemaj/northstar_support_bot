from typing import Any

from backend.chatbot.constants import ACTIVE_FLOW, RETURNS_EXCHANGE_FLOW
from backend.chatbot.responses.returns_exchange import format_returns_exchange_response
from backend.services.intent_service import Intent
from backend.services.returns_service import get_exchange_policy, get_returns_policy


def build_returns_exchange_result(message: str) -> tuple[str, Intent, dict[str, Any], bool]:
    normalized_message = message.lower()

    if "exchange" in normalized_message:
        policy = get_exchange_policy()
    else:
        policy = get_returns_policy()

    return (
        format_returns_exchange_response(policy),
        Intent.RETURNS_EXCHANGE,
        {ACTIVE_FLOW: RETURNS_EXCHANGE_FLOW},
        False,
    )
