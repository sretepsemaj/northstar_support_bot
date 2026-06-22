from dataclasses import dataclass
import re

from backend.data.orders import ORDERS, Order


@dataclass(frozen=True)
class OrderLookupResult:
    order_number: str | None
    found: bool
    status: str
    message: str
    follow_up: str | None = None


def normalize_order_number(value: str) -> str | None:
    match = re.search(r"#?\b(\d{3})\b", value.strip())
    if not match:
        return None
    return match.group(1)


def get_order(order_number: str) -> Order | None:
    normalized = normalize_order_number(order_number)
    if normalized is None:
        return None
    return ORDERS.get(normalized)


def lookup_order(order_number: str) -> OrderLookupResult:
    normalized = normalize_order_number(order_number)
    if normalized is None:
        return OrderLookupResult(
            order_number=None,
            found=False,
            status="invalid",
            message="Please provide a valid 3-digit order number so I can check the status.",
        )

    order = ORDERS.get(normalized)
    if order is None:
        return OrderLookupResult(
            order_number=normalized,
            found=False,
            status="invalid",
            message=f"I could not find order #{normalized}. Please check the order number or ask for a live agent.",
        )

    return OrderLookupResult(
        order_number=order.order_number,
        found=True,
        status=order.status,
        message=order.message,
        follow_up=order.follow_up,
    )
