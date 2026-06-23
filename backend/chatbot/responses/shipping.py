from backend.services.shipping_service import ShippingPolicyResult


def format_shipping_response(result: ShippingPolicyResult) -> str:
    return result.message
