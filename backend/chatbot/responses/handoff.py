from backend.services.handoff_service import HandoffResult


def format_handoff_response(result: HandoffResult) -> str:
    return result.message
