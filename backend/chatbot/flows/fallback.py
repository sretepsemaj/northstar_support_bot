from typing import Any

from backend.chatbot.constants import ACTIVE_FLOW, MAIN_MENU_FLOW
from backend.chatbot.responses.fallback import FALLBACK_RESPONSE
from backend.services.intent_service import Intent


def build_fallback_result() -> tuple[str, Intent, dict[str, Any], bool]:
    return FALLBACK_RESPONSE, Intent.FALLBACK, {ACTIVE_FLOW: MAIN_MENU_FLOW}, False
