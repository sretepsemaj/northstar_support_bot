from typing import Any

from backend.chatbot.constants import ACTIVE_FLOW, HUMAN_HANDOFF_FLOW
from backend.chatbot.responses.handoff import format_handoff_response
from backend.services.handoff_service import create_handoff
from backend.services.intent_service import Intent


def build_handoff_result() -> tuple[str, Intent, dict[str, Any], bool]:
    result = create_handoff()
    return (
        format_handoff_response(result),
        Intent.HUMAN_HANDOFF,
        {ACTIVE_FLOW: HUMAN_HANDOFF_FLOW},
        result.should_handoff,
    )
