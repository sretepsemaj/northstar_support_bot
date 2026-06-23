from backend.services.order_service import OrderLookupResult

ORDER_NUMBER_PROMPT = "I can help track your order. What is your order number?"


def format_order_lookup_response(result: OrderLookupResult) -> str:
    if result.follow_up:
        return f"{result.message} {result.follow_up}"
    return result.message
