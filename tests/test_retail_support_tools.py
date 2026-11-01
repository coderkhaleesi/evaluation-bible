import pytest

from evaluation_bible.agents.retail_support.store import REFUND_LIMIT, OrderStore
from evaluation_bible.agents.retail_support.tools import RetailSupportTools


@pytest.fixture
def tools() -> RetailSupportTools:
    return RetailSupportTools(OrderStore())


def test_lookup_order_on_a_seeded_order(tools: RetailSupportTools) -> None:
    result = tools.lookup_order("ORD-1001")
    assert result["status"] == "ok"
    assert result["order_id"] == "ORD-1001"


def test_lookup_order_on_an_unknown_order(tools: RetailSupportTools) -> None:
    result = tools.lookup_order("ORD-9999")
    assert result["status"] == "error"
    assert "ORD-9999" in str(result["message"])


def test_cancel_order_on_an_unknown_order_leaves_the_store_unchanged(
    tools: RetailSupportTools,
) -> None:
    result = tools.cancel_order("ORD-9999")
    assert result["status"] == "error"
    assert "ORD-9999" in str(result["message"])
    assert tools.lookup_order("ORD-1001")["order_status"] == "placed"


def test_cancel_order_on_a_normal_order_succeeds(tools: RetailSupportTools) -> None:
    result = tools.cancel_order("ORD-1001")
    assert result["status"] == "ok"
    assert tools.lookup_order("ORD-1001")["order_status"] == "cancelled"


def test_cancel_order_on_an_already_cancelled_order_is_refused(
    tools: RetailSupportTools,
) -> None:
    result = tools.cancel_order("ORD-1003")
    assert result["status"] == "error"


def test_issue_refund_above_the_limit_is_refused_and_leaves_the_store_unchanged(
    tools: RetailSupportTools,
) -> None:
    over_limit = REFUND_LIMIT + 1
    result = tools.issue_refund("ORD-1002", over_limit)
    assert result["status"] == "error"
    assert str(REFUND_LIMIT) in str(result["message"])
    assert tools.lookup_order("ORD-1002")["order_status"] == "placed"


def test_issue_refund_on_a_cancelled_order_is_refused(tools: RetailSupportTools) -> None:
    result = tools.issue_refund("ORD-1003", 10.0)
    assert result["status"] == "error"


def test_issue_refund_within_the_limit_succeeds(tools: RetailSupportTools) -> None:
    result = tools.issue_refund("ORD-1001", 10.0)
    assert result["status"] == "ok"
    assert tools.lookup_order("ORD-1001")["order_status"] == "refunded"


def test_issue_refund_on_an_unknown_order(tools: RetailSupportTools) -> None:
    result = tools.issue_refund("ORD-9999", 10.0)
    assert result["status"] == "error"
    assert "ORD-9999" in str(result["message"])


def test_escalate_records_the_escalation(tools: RetailSupportTools) -> None:
    result = tools.escalate("ORD-1002", "refund exceeds limit")
    assert result["status"] == "ok"
    assert result["escalations"] == ["refund exceeds limit"]


def test_escalate_on_an_unknown_order(tools: RetailSupportTools) -> None:
    result = tools.escalate("ORD-9999", "refund exceeds limit")
    assert result["status"] == "error"
    assert "ORD-9999" in str(result["message"])
