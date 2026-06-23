from typing import Any

from backend.chatbot.constants import ACTIVE_FLOW, MAIN_MENU_FLOW
from backend.chatbot.responses.gratitude import GRATITUDE_RESPONSE
from backend.services.intent_service import Intent


def build_gratitude_result() -> tuple[str, Intent, dict[str, Any], bool]:
    return GRATITUDE_RESPONSE, Intent.GRATITUDE, {ACTIVE_FLOW: MAIN_MENU_FLOW}, False
