from backend.services.returns_service import get_exchange_policy, get_returns_policy


def test_returns_policy_includes_required_scope_details():
    result = get_returns_policy()
    message = result.message.lower()

    assert "30 days" in message
    assert "unused" in message
    assert "original packaging" in message


def test_returns_policy_provides_returns_link():
    result = get_returns_policy()

    assert result.returns_link == "https://northstar.example.com/returns"
    assert result.returns_link in result.message


def test_exchange_policy_uses_same_policy_and_link():
    result = get_exchange_policy()
    message = result.message.lower()

    assert "exchanges" in message
    assert "same policy" in message
    assert "30 days" in message
    assert result.returns_link in result.message
