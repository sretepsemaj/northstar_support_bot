import pytest

from backend.services.recommendation_service import (
    recommend_category,
    recommend_category_detail,
)


@pytest.mark.parametrize(
    ("message", "expected_category"),
    [
        ("I need a tent for camping", "Camping Gear"),
        ("What jacket should I buy for layering?", "Outdoor Apparel"),
        ("I need boots for a hiking trip", "Hiking Footwear"),
        ("What should I get for rock climbing?", "Climbing Essentials"),
        ("I need something waterproof for rain", "Weather Protection"),
        ("I need a raincoat", "Weather Protection"),
        ("weather protection for cold weather", "Weather Protection"),
        ("I need cold weather gear", "Outdoor Apparel"),
    ],
)
def test_recommend_category_matches_outdoor_shopping_contexts(message, expected_category):
    result = recommend_category(message)

    assert result.category == expected_category
    assert result.needs_clarification is True
    assert result.waiting_for_detail is True
    assert expected_category in result.message


def test_recommend_category_asks_clarifying_questions_for_vague_requests():
    result = recommend_category("I need help choosing gear")

    assert result.category is None
    assert result.needs_clarification is True
    assert len(result.questions) == 5
    assert result.questions[0] == "1. Camping Gear"
    assert result.questions[4] == "5. Weather Protection"


def test_recommend_category_selection_asks_category_specific_follow_up():
    result = recommend_category("5")

    assert result.category == "Weather Protection"
    assert result.needs_clarification is True
    assert result.waiting_for_detail is True
    assert "What kind of gear" in result.message
    assert "Rain shells" in result.questions[0]
    assert "Snow or storm protection" in result.questions[3]


def test_recommend_category_detail_returns_final_recommendation():
    result = recommend_category_detail("Weather Protection", "1")

    assert result.category == "Weather Protection"
    assert result.needs_clarification is False
    assert "Weather Protection" in result.message
    assert "rain shells" in result.message.lower()


def test_recommend_category_detail_can_switch_categories():
    result = recommend_category_detail("Hiking Footwear", "no better get a tent")

    assert result.category == "Camping Gear"
    assert result.needs_clarification is True
    assert result.waiting_for_detail is True
    assert "Camping Gear is a good fit" in result.message
    assert "Tents and shelters" in result.questions[0]


def test_recommend_category_detail_ignores_weak_words_when_matching_options():
    result = recommend_category_detail("Hiking Footwear", "what else do you have")

    assert result.category == "Hiking Footwear"
    assert result.needs_clarification is False
    assert "Great choice" not in result.message
    assert "It covers" in result.message
    assert "Hiking boots" in result.message


def test_recommend_category_does_not_invent_specific_products():
    result = recommend_category_detail("Camping Gear", "1")

    assert "sku" not in result.message.lower()
    assert "model" not in result.message.lower()
    assert "buy the" not in result.message.lower()
