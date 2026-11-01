from evaluation_bible.agents.retail_support.store import OrderStore


def test_get_returns_a_seeded_order() -> None:
    store = OrderStore()
    order = store.get("ORD-1001")
    assert order is not None
    assert order.order_id == "ORD-1001"
    assert order.status == "placed"


def test_get_returns_none_for_an_unknown_order() -> None:
    store = OrderStore()
    assert store.get("ORD-9999") is None


def test_seed_includes_an_already_cancelled_order() -> None:
    store = OrderStore()
    order = store.get("ORD-1003")
    assert order is not None
    assert order.status == "cancelled"
