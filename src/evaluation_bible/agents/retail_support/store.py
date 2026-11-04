"""In-memory order store for the retail_support reference agent."""

from __future__ import annotations

from dataclasses import dataclass, field

REFUND_LIMIT = 100.0


@dataclass
class Order:
    order_id: str
    customer: str
    total: float
    status: str
    escalations: list[str] = field(default_factory=list)


def seed_orders() -> dict[str, Order]:
    """Return a fresh set of orders covering the policy's edge cases."""
    return {
        "ORD-1001": Order(
            order_id="ORD-1001", customer="Ada Lovelace", total=42.50, status="placed"
        ),
        "ORD-1002": Order(
            order_id="ORD-1002", customer="Grace Hopper", total=250.00, status="placed"
        ),
        "ORD-1003": Order(
            order_id="ORD-1003", customer="Alan Turing", total=15.00, status="cancelled"
        ),
    }


class OrderStore:
    """Holds orders for the lifetime of the process."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = seed_orders()

    def get(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)
