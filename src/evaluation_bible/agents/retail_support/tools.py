"""Policy-enforcing tools over the in-memory order store.

See policy.md for the rules these tools enforce: a refund above REFUND_LIMIT
must be escalated rather than issued, and a cancelled order cannot be refunded.
"""

from __future__ import annotations

from evaluation_bible.agents.retail_support.store import REFUND_LIMIT, OrderStore


class RetailSupportTools:
    """Binds the four retail_support tools to one order store."""

    def __init__(self, store: OrderStore) -> None:
        self._store = store

    def lookup_order(self, order_id: str) -> dict[str, object]:
        """Look up an order by id."""
        order = self._store.get(order_id)
        if order is None:
            return {"status": "error", "message": f"no order found with id '{order_id}'"}
        return {
            "status": "ok",
            "order_id": order.order_id,
            "customer": order.customer,
            "total": order.total,
            "order_status": order.status,
        }

    def cancel_order(self, order_id: str) -> dict[str, object]:
        """Cancel an order that has not already been cancelled."""
        order = self._store.get(order_id)
        if order is None:
            return {"status": "error", "message": f"no order found with id '{order_id}'"}
        if order.status == "cancelled":
            return {"status": "error", "message": f"order '{order_id}' is already cancelled"}
        order.status = "cancelled"
        return {"status": "ok", "order_id": order_id, "order_status": order.status}

    def issue_refund(self, order_id: str, amount: float) -> dict[str, object]:
        """Refund an order, within policy limits."""
        order = self._store.get(order_id)
        if order is None:
            return {"status": "error", "message": f"no order found with id '{order_id}'"}
        if order.status == "cancelled":
            return {
                "status": "error",
                "message": f"order '{order_id}' is cancelled and cannot be refunded",
            }
        if amount <= 0:
            return {
                "status": "error",
                "message": f"refund of {amount} for order '{order_id}' must be a positive amount",
            }
        if amount > REFUND_LIMIT:
            return {
                "status": "error",
                "message": (
                    f"refund of {amount} for order '{order_id}' exceeds the limit of "
                    f"{REFUND_LIMIT}; escalate instead"
                ),
            }
        order.status = "refunded"
        return {"status": "ok", "order_id": order_id, "order_status": order.status}

    def escalate(self, order_id: str, reason: str) -> dict[str, object]:
        """Record an escalation on an order for a human to act on."""
        order = self._store.get(order_id)
        if order is None:
            return {"status": "error", "message": f"no order found with id '{order_id}'"}
        order.escalations.append(reason)
        return {"status": "ok", "order_id": order_id, "escalations": list(order.escalations)}
