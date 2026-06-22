import pytest

from backend.services.order_service import lookup_order, normalize_order_number


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("111", "111"),
        ("#222", "222"),
        ("my order is 333", "333"),
    ],
)
def test_normalize_order_number_accepts_common_order_formats(raw_value, expected):
    assert normalize_order_number(raw_value) == expected


@pytest.mark.parametrize(
    ("order_number", "expected_status", "expected_message"),
    [
        ("111", "shipped", "arriving tomorrow"),
        ("222", "processing", "ship in 24 hours"),
        ("333", "delivered", "delivered"),
    ],
)
def test_lookup_order_returns_required_mock_order_statuses(
    order_number,
    expected_status,
    expected_message,
):
    result = lookup_order(order_number)

    assert result.found is True
    assert result.order_number == order_number
    assert result.status == expected_status
    assert expected_message in result.message


def test_delivered_order_includes_follow_up_help():
    result = lookup_order("333")

    assert result.follow_up is not None
    assert "did everything arrive" in result.follow_up.lower()
    assert "live agent" in result.follow_up.lower()


@pytest.mark.parametrize("order_number", ["444", "999", "abc", ""])
def test_lookup_order_returns_invalid_for_unknown_or_malformed_orders(order_number):
    result = lookup_order(order_number)

    assert result.found is False
    assert result.status == "invalid"
    assert "order" in result.message.lower()
