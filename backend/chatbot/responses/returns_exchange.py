from backend.services.returns_service import ReturnsPolicyResult


def format_returns_exchange_response(result: ReturnsPolicyResult) -> str:
    return result.message
