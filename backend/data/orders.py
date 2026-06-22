from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_number: str
    status: str
    message: str
    follow_up: str | None = None


ORDERS: dict[str, Order] = {
    "111": Order(
        order_number="111",
        status="shipped",
        message="Order #111 has shipped and is arriving tomorrow.",
    ),
    "222": Order(
        order_number="222",
        status="processing",
        message="Order #222 is processing and will ship in 24 hours.",
    ),
    "333": Order(
        order_number="333",
        status="delivered",
        message="Order #333 was delivered.",
        follow_up="Did everything arrive in good shape, or would you like help with a return or live agent?",
    ),
}
