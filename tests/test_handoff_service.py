from backend.services.handoff_service import create_handoff


def test_create_handoff_returns_live_agent_state_payload():
    result = create_handoff()

    assert result.should_handoff is True
    assert result.queue == "customer_support"
    assert result.reason == "user_requested_human_support"
    assert "live agent" in result.message.lower()
    assert "human support" in result.message.lower()
