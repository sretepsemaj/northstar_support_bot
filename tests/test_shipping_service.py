from backend.services.shipping_service import get_shipping_policy


def test_get_shipping_policy_uses_provided_mock_data():
    result = get_shipping_policy()

    assert result.standard == "3-5 days"
    assert result.expedited == "1-2 days"
    assert "Standard (3-5 days)" in result.message
    assert "Expedited (1-2 days)" in result.message
