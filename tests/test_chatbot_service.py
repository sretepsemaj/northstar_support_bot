from backend.chatbot.constants import (
    ACTIVE_FLOW,
    HUMAN_HANDOFF_FLOW,
    MAIN_MENU_FLOW,
    ORDER_NUMBER,
    ORDER_TRACKING_FLOW,
    PRODUCT_RECOMMENDATION_FLOW,
    RECOMMENDATION_CONTEXT,
    RETURNS_EXCHANGE_FLOW,
    WAITING_FOR,
)
from backend.chatbot.responses.main_menu import MAIN_MENU_RESPONSE
from backend.services.chatbot_service import handle_chat
from backend.services.intent_service import Intent, MatchStrategy


def test_handle_chat_routes_greeting_to_main_menu():
    result = handle_chat("hello", state={})

    assert result.reply == MAIN_MENU_RESPONSE
    assert result.intent == Intent.MAIN_MENU
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.handoff is False
    assert result.metadata["match_strategy"] == MatchStrategy.EXACT_KEYWORD
    assert result.metadata["needs_review"] is False
    assert result.metadata["intent_reviewed"] is False


def test_handle_chat_routes_specific_recommendation_to_category_response():
    result = handle_chat("What tent should I buy?", state={})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "Camping Gear" in result.reply
    assert result.state == {ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW}
    assert result.handoff is False


def test_handle_chat_asks_clarifying_questions_for_vague_recommendation():
    result = handle_chat("I need help choosing gear", state={})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "couple quick questions" in result.reply
    assert "activity" in result.reply.lower()
    assert "conditions" in result.reply.lower()
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_CONTEXT,
    }
    assert result.handoff is False


def test_handle_chat_prompts_for_order_number_when_tracking_request_has_no_number():
    result = handle_chat("Where is my order?", state={})

    assert result.intent == Intent.ORDER_TRACKING
    assert "What is your order number" in result.reply
    assert result.state == {
        ACTIVE_FLOW: ORDER_TRACKING_FLOW,
        WAITING_FOR: ORDER_NUMBER,
    }
    assert result.handoff is False


def test_handle_chat_returns_order_status_when_order_number_is_in_message():
    result = handle_chat("My order is 222", state={})

    assert result.intent == Intent.ORDER_TRACKING
    assert "Order #222" in result.reply
    assert "ship in 24 hours" in result.reply
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.handoff is False


def test_handle_chat_uses_waiting_state_to_lookup_order_number():
    result = handle_chat(
        "111",
        state={ACTIVE_FLOW: ORDER_TRACKING_FLOW, WAITING_FOR: ORDER_NUMBER},
    )

    assert result.intent == Intent.ORDER_TRACKING
    assert "Order #111" in result.reply
    assert "arriving tomorrow" in result.reply
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.handoff is False


def test_handle_chat_keeps_order_flow_active_for_invalid_order_number():
    result = handle_chat(
        "999",
        state={ACTIVE_FLOW: ORDER_TRACKING_FLOW, WAITING_FOR: ORDER_NUMBER},
    )

    assert result.intent == Intent.ORDER_TRACKING
    assert "could not find order #999" in result.reply.lower()
    assert result.state == {
        ACTIVE_FLOW: ORDER_TRACKING_FLOW,
        WAITING_FOR: ORDER_NUMBER,
    }
    assert result.handoff is False


def test_handle_chat_routes_return_question_to_returns_policy():
    result = handle_chat("I want to return this jacket", state={})

    assert result.intent == Intent.RETURNS_EXCHANGE
    assert "30 days" in result.reply
    assert "unused" in result.reply.lower()
    assert "original packaging" in result.reply.lower()
    assert "https://northstar.example.com/returns" in result.reply
    assert result.state == {ACTIVE_FLOW: RETURNS_EXCHANGE_FLOW}
    assert result.handoff is False


def test_handle_chat_routes_exchange_question_to_exchange_policy():
    result = handle_chat("Can I exchange this?", state={})

    assert result.intent == Intent.RETURNS_EXCHANGE
    assert "Exchanges follow the same policy" in result.reply
    assert "30 days" in result.reply
    assert result.state == {ACTIVE_FLOW: RETURNS_EXCHANGE_FLOW}
    assert result.handoff is False


def test_handle_chat_routes_gratitude_to_polite_response():
    result = handle_chat("thank you", state={})

    assert result.intent == Intent.GRATITUDE
    assert "You're welcome" in result.reply
    assert "order tracking" in result.reply
    assert "returns" in result.reply
    assert "product recommendations" in result.reply
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.handoff is False


def test_handle_chat_routes_gratitude_typo_to_polite_response_with_review_flag():
    result = handle_chat("thnak", state={})

    assert result.intent == Intent.GRATITUDE
    assert "You're welcome" in result.reply
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.metadata["needs_review"] is True
    assert result.handoff is False


def test_handle_chat_routes_explicit_handoff_request_to_live_agent_state():
    result = handle_chat("I want to talk to a person", state={})

    assert result.intent == Intent.HUMAN_HANDOFF
    assert "live agent" in result.reply.lower()
    assert "human support" in result.reply.lower()
    assert result.state == {ACTIVE_FLOW: HUMAN_HANDOFF_FLOW}
    assert result.handoff is True


def test_handle_chat_prioritizes_handoff_over_other_business_intents():
    result = handle_chat("I need a person to help me return this", state={})

    assert result.intent == Intent.HUMAN_HANDOFF
    assert result.state == {ACTIVE_FLOW: HUMAN_HANDOFF_FLOW}
    assert result.handoff is True


def test_handle_chat_routes_unknown_message_to_fallback_menu():
    result = handle_chat("what is the weather today?", state={})

    assert result.intent == Intent.FALLBACK
    assert "didn't quite catch" in result.reply
    assert "1. Order Tracking" in result.reply
    assert "2. Returns & Exchanges" in result.reply
    assert "3. Product Recommendations" in result.reply
    assert "live agent" in result.reply.lower()
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.metadata["needs_review"] is True
    assert result.handoff is False


def test_waiting_for_order_number_allows_handoff_escape():
    result = handle_chat(
        "live agent",
        state={ACTIVE_FLOW: ORDER_TRACKING_FLOW, WAITING_FOR: ORDER_NUMBER},
    )

    assert result.intent == Intent.HUMAN_HANDOFF
    assert result.state == {ACTIVE_FLOW: HUMAN_HANDOFF_FLOW}
    assert result.handoff is True


def test_waiting_for_order_number_allows_help_escape_to_main_menu():
    result = handle_chat(
        "help",
        state={ACTIVE_FLOW: ORDER_TRACKING_FLOW, WAITING_FOR: ORDER_NUMBER},
    )

    assert result.intent == Intent.MAIN_MENU
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.handoff is False


def test_waiting_for_order_number_allows_return_question_escape():
    result = handle_chat(
        "can I return my item",
        state={ACTIVE_FLOW: ORDER_TRACKING_FLOW, WAITING_FOR: ORDER_NUMBER},
    )

    assert result.intent == Intent.RETURNS_EXCHANGE
    assert "30 days" in result.reply
    assert result.state == {ACTIVE_FLOW: RETURNS_EXCHANGE_FLOW}


def test_waiting_for_order_number_allows_recommendation_escape():
    result = handle_chat(
        "I need boots",
        state={ACTIVE_FLOW: ORDER_TRACKING_FLOW, WAITING_FOR: ORDER_NUMBER},
    )

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "Hiking Footwear" in result.reply
    assert result.state == {ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW}


def test_main_menu_option_three_routes_to_product_recommendations():
    result = handle_chat("3", state={ACTIVE_FLOW: MAIN_MENU_FLOW})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "couple quick questions" in result.reply
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_CONTEXT,
    }


def test_shopping_question_routes_to_product_recommendations():
    result = handle_chat("what stuff can I get here", state={})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "couple quick questions" in result.reply


def test_purchase_question_with_typo_routes_to_product_recommendations():
    result = handle_chat("what can I purchase ehre", state={})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "couple quick questions" in result.reply


def test_general_help_question_routes_to_main_menu():
    result = handle_chat("what can I do here", state={})

    assert result.intent == Intent.MAIN_MENU
    assert "1. Order Tracking" in result.reply


def test_fallback_response_includes_closed_live_agent_quote():
    result = handle_chat("random moon banana", state={})

    assert 'say "live agent."' in result.reply
