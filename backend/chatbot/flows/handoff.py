from typing import Any

from backend.chatbot.constants import ACTIVE_FLOW, HUMAN_HANDOFF_FLOW
from backend.chatbot.responses.handoff import HANDOFF_RESPONSE
from backend.services.intent_service import Intent


def build_handoff_result() -> tuple[str, Intent, dict[str, Any], bool]:
    return HANDOFF_RESPONSE, Intent.HUMAN_HANDOFF, {ACTIVE_FLOW: HUMAN_HANDOFF_FLOW}, True
