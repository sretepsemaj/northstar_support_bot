from backend.chatbot.constants import (
    ACTIVE_FLOW,
    HUMAN_HANDOFF_FLOW,
    MAIN_MENU_FLOW,
    ORDER_NUMBER,
    ORDER_TRACKING_FLOW,
    PRODUCT_RECOMMENDATION_FLOW,
    RECOMMENDATION_CATEGORY,
    RECOMMENDATION_CONTEXT,
    RECOMMENDATION_DETAIL,
    RETURNS_EXCHANGE_FLOW,
    WAITING_FOR,
)
from backend.chatbot.responses.main_menu import MAIN_MENU_RESPONSE
from backend.services.chatbot_service import handle_chat
from backend.services.intent_service import Intent, MatchStrategy
from backend.services.llm_service import (
    LLMAssistResult,
    build_recommendation_assist_result,
)


def test_handle_chat_routes_greeting_to_main_menu():
    result = handle_chat("hello", state={})

    assert result.reply == MAIN_MENU_RESPONSE
    assert result.intent == Intent.MAIN_MENU
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.handoff is False
    assert result.metadata["match_strategy"] == MatchStrategy.EXACT_KEYWORD
    assert result.metadata["needs_review"] is False
    assert result.metadata["llm_attempted"] is False
    assert result.metadata["intent_reviewed"] is False


def test_handle_chat_routes_specific_recommendation_to_category_response():
    result = handle_chat("What tent should I buy?", state={})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "Camping Gear" in result.reply
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_DETAIL,
        RECOMMENDATION_CATEGORY: "Camping Gear",
    }
    assert result.handoff is False


def test_handle_chat_asks_clarifying_questions_for_vague_recommendation():
    result = handle_chat("I need help choosing gear", state={})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "What are you shopping for today" in result.reply
    assert "1. Camping Gear" in result.reply
    assert "5. Weather Protection" in result.reply
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
    result = handle_chat("oaky thatnkyou", state={})

    assert result.intent == Intent.GRATITUDE
    assert "You're welcome" in result.reply
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.metadata["needs_review"] is True
    assert result.metadata["llm_attempted"] is False
    assert result.metadata["intent_reviewed"] is False
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


def test_handle_chat_routes_unknown_message_to_fallback_menu(monkeypatch):
    monkeypatch.setattr("backend.services.chatbot_service.is_llm_configured", lambda: False)

    result = handle_chat("what is the weather today?", state={})

    assert result.intent == Intent.FALLBACK
    assert "didn't quite catch" in result.reply
    assert "1. Order Tracking" in result.reply
    assert "2. Returns & Exchanges" in result.reply
    assert "3. Product Recommendations" in result.reply
    assert "live agent" in result.reply.lower()
    assert result.state == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert result.metadata["needs_review"] is True
    assert result.metadata["llm_attempted"] is False
    assert result.metadata["intent_reviewed"] is False
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
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_DETAIL,
        RECOMMENDATION_CATEGORY: "Hiking Footwear",
    }


def test_main_menu_option_three_routes_to_product_recommendations():
    result = handle_chat("3", state={ACTIVE_FLOW: MAIN_MENU_FLOW})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "What are you shopping for today" in result.reply
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_CONTEXT,
    }


def test_shopping_question_routes_to_product_recommendations():
    result = handle_chat("what stuff can I get here", state={})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "What are you shopping for today" in result.reply


def test_purchase_question_with_typo_routes_to_product_recommendations():
    result = handle_chat("what can I purchase ehre", state={})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "What are you shopping for today" in result.reply


def test_recommendation_menu_selection_routes_to_category_specific_follow_up():
    result = handle_chat(
        "5",
        state={
            ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
            WAITING_FOR: RECOMMENDATION_CONTEXT,
        },
    )

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "Weather Protection is a good fit" in result.reply
    assert "Rain shells" in result.reply
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_DETAIL,
        RECOMMENDATION_CATEGORY: "Weather Protection",
    }


def test_recommendation_detail_selection_returns_final_recommendation():
    result = handle_chat(
        "1",
        state={
            ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
            WAITING_FOR: RECOMMENDATION_DETAIL,
            RECOMMENDATION_CATEGORY: "Weather Protection",
        },
    )

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "Weather Protection" in result.reply
    assert "rain shells" in result.reply.lower()
    assert result.state == {ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW}


def test_recommendation_detail_can_switch_to_new_category():
    result = handle_chat(
        "no better get a tent",
        state={
            ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
            WAITING_FOR: RECOMMENDATION_DETAIL,
            RECOMMENDATION_CATEGORY: "Hiking Footwear",
        },
    )

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "Camping Gear is a good fit" in result.reply
    assert "Tents and shelters" in result.reply
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_DETAIL,
        RECOMMENDATION_CATEGORY: "Camping Gear",
    }


def test_recommendation_detail_unknown_reply_returns_to_category_menu_when_llm_is_off(monkeypatch):
    monkeypatch.setattr("backend.services.chatbot_service.is_llm_configured", lambda: False)

    result = handle_chat(
        "walking stick",
        state={
            ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
            WAITING_FOR: RECOMMENDATION_DETAIL,
            RECOMMENDATION_CATEGORY: "Hiking Footwear",
        },
    )

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "What are you shopping for today" in result.reply
    assert "1. Camping Gear" in result.reply
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_CONTEXT,
    }
    assert result.metadata["llm_attempted"] is False


def test_recommendation_detail_unknown_reply_can_use_llm_category(monkeypatch):
    monkeypatch.setattr("backend.services.chatbot_service.is_llm_configured", lambda: True)
    monkeypatch.setattr(
        "backend.services.chatbot_service.review_ambiguous_message",
        lambda message: build_recommendation_assist_result("Climbing Essentials"),
    )

    result = handle_chat(
        "helmet",
        state={
            ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
            WAITING_FOR: RECOMMENDATION_DETAIL,
            RECOMMENDATION_CATEGORY: "Hiking Footwear",
        },
    )

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "Climbing Essentials is a good fit" in result.reply
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_DETAIL,
        RECOMMENDATION_CATEGORY: "Climbing Essentials",
    }
    assert result.metadata["llm_attempted"] is True
    assert result.metadata["intent_reviewed"] is True
    assert result.metadata["llm_category"] == "Climbing Essentials"


def test_general_help_question_routes_to_main_menu():
    result = handle_chat("what can I do here", state={})

    assert result.intent == Intent.MAIN_MENU
    assert "1. Order Tracking" in result.reply


def test_fallback_response_includes_closed_live_agent_quote():
    result = handle_chat("random moon banana", state={})

    assert 'say "live agent."' in result.reply


def test_fallback_can_use_llm_assist_for_recommendation_category(monkeypatch):
    def fake_review_ambiguous_message(message):
        assert message == "I need raincoats"
        return build_recommendation_assist_result("Weather Protection")

    monkeypatch.setattr(
        "backend.services.chatbot_service.review_ambiguous_message",
        fake_review_ambiguous_message,
    )
    monkeypatch.setattr("backend.services.chatbot_service.is_llm_configured", lambda: True)

    result = handle_chat("I need raincoats", state={})

    assert result.intent == Intent.PRODUCT_RECOMMENDATION
    assert "Weather Protection is a good fit" in result.reply
    assert result.state == {
        ACTIVE_FLOW: PRODUCT_RECOMMENDATION_FLOW,
        WAITING_FOR: RECOMMENDATION_DETAIL,
        RECOMMENDATION_CATEGORY: "Weather Protection",
    }
    assert result.metadata["llm_attempted"] is True
    assert result.metadata["intent_reviewed"] is True
    assert result.metadata["llm_category"] == "Weather Protection"
    assert result.handoff is False


def test_fallback_can_use_llm_assist_for_handoff(monkeypatch):
    monkeypatch.setattr(
        "backend.services.chatbot_service.review_ambiguous_message",
        lambda message: LLMAssistResult(
            intent=Intent.HUMAN_HANDOFF,
            needs_handoff=True,
            used_llm=True,
        ),
    )
    monkeypatch.setattr("backend.services.chatbot_service.is_llm_configured", lambda: True)

    result = handle_chat("this is not helping", state={})

    assert result.intent == Intent.HUMAN_HANDOFF
    assert result.state == {ACTIVE_FLOW: HUMAN_HANDOFF_FLOW}
    assert result.metadata["llm_attempted"] is True
    assert result.metadata["intent_reviewed"] is True
    assert result.handoff is True
