from tools.order_tools import get_order_status
from tools.product_tools import get_product_info, check_stock
from tools.refund_tools import check_refund_eligibility


def test_get_order_status():
    result = get_order_status("10001")
    assert result["ok"] is True


def test_product_info():
    result = get_product_info("P1001")
    assert result["ok"] is True
    assert result["name"] == "Wireless Headphones"


def test_stock():
    result = check_stock("P1003")
    assert result["ok"] is True
    assert result["in_stock"] is False


def test_missing_order():
    result = get_order_status("99999")
    assert result["ok"] is False
