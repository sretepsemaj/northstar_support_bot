import pytest

from backend.services.recommendation_service import recommend_category


@pytest.mark.parametrize(
    ("message", "expected_category"),
    [
        ("I need a tent for camping", "Camping Gear"),
        ("What jacket should I buy for layering?", "Outdoor Apparel"),
        ("I need boots for a hiking trip", "Hiking Footwear"),
        ("What should I get for rock climbing?", "Climbing Essentials"),
        ("I need something waterproof for rain", "Weather Protection"),
    ],
)
def test_recommend_category_matches_outdoor_shopping_contexts(message, expected_category):
    result = recommend_category(message)

    assert result.needs_clarification is False
    assert result.category == expected_category
    assert expected_category in result.message


def test_recommend_category_asks_clarifying_questions_for_vague_requests():
    result = recommend_category("I need help choosing gear")

    assert result.category is None
    assert result.needs_clarification is True
    assert len(result.questions) == 2
    assert "activity" in result.questions[0].lower()
    assert "conditions" in result.questions[1].lower()


def test_recommend_category_does_not_invent_specific_products():
    result = recommend_category("I need a tent for camping")

    assert "sku" not in result.message.lower()
    assert "model" not in result.message.lower()
    assert "buy the" not in result.message.lower()
