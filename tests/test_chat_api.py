from fastapi.testclient import TestClient

from backend.chatbot.constants import (
    ACTIVE_FLOW,
    MAIN_MENU_FLOW,
    ORDER_NUMBER,
    ORDER_TRACKING_FLOW,
    WAITING_FOR,
)
from backend.main import app
from backend.services.intent_service import Intent

client = TestClient(app)


def test_chat_endpoint_routes_greeting_to_main_menu():
    response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == Intent.MAIN_MENU.value
    assert "North Star customer support" in payload["reply"]
    assert payload["state"] == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert payload["handoff"] is False
    assert payload["metadata"]["needs_review"] is False


def test_chat_endpoint_preserves_state_for_order_number_follow_up():
    response = client.post(
        "/chat",
        json={
            "message": "111",
            "state": {ACTIVE_FLOW: ORDER_TRACKING_FLOW, WAITING_FOR: ORDER_NUMBER},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == Intent.ORDER_TRACKING.value
    assert "Order #111" in payload["reply"]
    assert "arriving tomorrow" in payload["reply"]
    assert payload["state"] == {ACTIVE_FLOW: MAIN_MENU_FLOW}
    assert payload["handoff"] is False


def test_chat_endpoint_returns_validation_error_for_empty_message():
    response = client.post("/chat", json={"message": ""})

    assert response.status_code == 422


def test_root_serves_frontend_chat_ui():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "North Star Gear" in response.text
    assert "/static/js/support-widget.js" in response.text
    assert "/static/css/storefront.css" in response.text
