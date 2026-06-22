import pytest

from backend.services.intent_service import Intent, detect_intent, normalize_message


@pytest.mark.parametrize(
    ("message", "expected_intent"),
    [
        ("Where is my order?", Intent.ORDER_TRACKING),
        ("Track my package", Intent.ORDER_TRACKING),
        ("My order is 111", Intent.ORDER_TRACKING),
        ("#222", Intent.ORDER_TRACKING),
        ("I want to return this jacket", Intent.RETURNS_EXCHANGE),
        ("Can I exchange this?", Intent.RETURNS_EXCHANGE),
        ("What tent should I buy?", Intent.PRODUCT_RECOMMENDATION),
        ("I need waterproof gear", Intent.PRODUCT_RECOMMENDATION),
        ("I want to talk to a person", Intent.HUMAN_HANDOFF),
        ("Can I speak to customer service?", Intent.HUMAN_HANDOFF),
        ("Hi", Intent.MAIN_MENU),
        ("What can you help with?", Intent.MAIN_MENU),
        ("Show me options", Intent.MAIN_MENU),
        ("thank you", Intent.GRATITUDE),
        ("thanks", Intent.GRATITUDE),
        ("thx", Intent.GRATITUDE),
        ("appreciate it", Intent.GRATITUDE),
        ("appreciate your help", Intent.GRATITUDE),
        ("you were a great help", Intent.GRATITUDE),
        ("that helped", Intent.GRATITUDE),
        ("this helped", Intent.GRATITUDE),
        ("perfect thanks", Intent.GRATITUDE),
    ],
)
def test_detect_intent_handles_required_exact_variations(message, expected_intent):
    result = detect_intent(message)

    assert result.intent == expected_intent
    assert result.matched_terms


@pytest.mark.parametrize(
    ("message", "expected_intent"),
    [
        ("wher is my oder", Intent.ORDER_TRACKING),
        ("track my pakage", Intent.ORDER_TRACKING),
        ("i want to retrun this", Intent.RETURNS_EXCHANGE),
        ("can i exchagne this", Intent.RETURNS_EXCHANGE),
        ("talk to an agnet", Intent.HUMAN_HANDOFF),
        ("reccomend a tent", Intent.PRODUCT_RECOMMENDATION),
        ("thnak", Intent.GRATITUDE),
        ("thanx", Intent.GRATITUDE),
    ],
)
def test_detect_intent_handles_common_typos(message, expected_intent):
    result = detect_intent(message)

    assert result.intent == expected_intent
    assert result.matched_terms


def test_human_handoff_takes_priority_when_message_mentions_another_intent():
    result = detect_intent("I need a person to help me return this")

    assert result.intent == Intent.HUMAN_HANDOFF


def test_specific_help_request_does_not_route_to_main_menu():
    result = detect_intent("I need help choosing waterproof gear")

    assert result.intent == Intent.PRODUCT_RECOMMENDATION


def test_plain_help_does_not_route_to_gratitude():
    result = detect_intent("help")

    assert result.intent == Intent.MAIN_MENU


def test_handoff_takes_priority_over_gratitude():
    result = detect_intent("thanks, can I talk to an agent?")

    assert result.intent == Intent.HUMAN_HANDOFF


def test_business_intent_takes_priority_over_gratitude():
    result = detect_intent("thanks, I need to return this")

    assert result.intent == Intent.RETURNS_EXCHANGE


@pytest.mark.parametrize("message", ["asdf banana moon", "", "   "])
def test_detect_intent_returns_fallback_for_unknown_or_empty_messages(message):
    result = detect_intent(message)

    assert result.intent == Intent.FALLBACK
    assert result.matched_terms == ()


def test_normalize_message_keeps_order_numbers_and_removes_extra_punctuation():
    assert normalize_message("  Track order #111!! ") == "track order #111"
