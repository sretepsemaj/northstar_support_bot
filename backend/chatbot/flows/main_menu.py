from typing import Any

from backend.chatbot.constants import ACTIVE_FLOW, MAIN_MENU_FLOW
from backend.chatbot.responses.main_menu import MAIN_MENU_RESPONSE
from backend.services.intent_service import Intent


def build_main_menu_result() -> tuple[str, Intent, dict[str, Any], bool]:
    return MAIN_MENU_RESPONSE, Intent.MAIN_MENU, {ACTIVE_FLOW: MAIN_MENU_FLOW}, False
