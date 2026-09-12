from datetime import date

import tools.refund_tools as refund_tools
import tools.ticket_tools as ticket_tools
from tools.order_tools import get_order_status
from tools.product_tools import get_product_info
from tools.stock_tools import check_stock


def test_get_order_status():
    result = get_order_status("10001")
    assert result["success"] is True
    assert result["data"]["status"] == "DELIVERED"


def test_order_lookup_trims_input():
    result = get_order_status(" 10001 ")
    assert result["success"] is True
    assert result["data"]["order_id"] == "10001"


def test_product_info():
    result = get_product_info("P1001")
    assert result["success"] is True
    assert result["data"]["name"] == "Wireless Headphones"


def test_stock():
    result = check_stock("P1003")
    assert result["success"] is True
    assert result["data"]["in_stock"] is False
    assert result["data"]["stock"] == 0


def test_missing_order():
    result = get_order_status("99999")
    assert result["success"] is False


def test_empty_identifier_is_rejected():
    result = get_product_info("   ")
    assert result == {"success": False, "error": "product_id must be a non-empty string."}


def test_refund_within_window(monkeypatch):
    monkeypatch.setattr(refund_tools, "_utc_today", lambda: date(2026, 9, 12))
    result = refund_tools.check_refund_eligibility("10001")
    assert result["success"] is True
    assert result["data"]["eligible"] is True


def test_refund_outside_window(monkeypatch):
    monkeypatch.setattr(refund_tools, "_utc_today", lambda: date(2026, 9, 12))
    result = refund_tools.check_refund_eligibility("10003")
    assert result["success"] is True
    assert result["data"]["eligible"] is False


def test_future_delivery_date_is_not_treated_as_eligible(monkeypatch):
    monkeypatch.setattr(refund_tools, "_utc_today", lambda: date(2026, 9, 1))
    result = refund_tools.check_refund_eligibility("10001")
    assert result["success"] is False
    assert "future" in result["error"].lower()


def test_create_ticket_uses_runtime_storage_and_canonical_customer_id(tmp_path, monkeypatch):
    tickets_path = tmp_path / "tickets.json"
    monkeypatch.setattr(ticket_tools, "TICKETS_PATH", tickets_path)

    result = ticket_tools.create_support_ticket(" c1001 ", "  Headphones arrived broken.  ")

    assert result["success"] is True
    assert result["data"]["customer_id"] == "C1001"
    assert result["data"]["issue"] == "Headphones arrived broken."
    assert tickets_path.exists()
