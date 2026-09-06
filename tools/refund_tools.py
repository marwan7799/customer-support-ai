import json
from pathlib import Path
from datetime import date

ORDERS_PATH = Path(__file__).parents[1] / "data" / "orders.json"


def _load_orders():
    return json.loads(ORDERS_PATH.read_text(encoding="utf-8"))


def check_refund_eligibility(order_id: str) -> dict:
    """Check the demo refund policy for an order."""
    orders = _load_orders()
    order = next((o for o in orders if o["order_id"] == str(order_id)), None)

    if not order:
        return {"ok": False, "error": "Order not found."}

    delivered = date.fromisoformat(order["delivery_date"])
    days_since_delivery = (date.today() - delivered).days
    eligible = days_since_delivery <= 30

    return {
        "ok": True,
        "order_id": order["order_id"],
        "eligible": eligible,
        "days_since_delivery": days_since_delivery,
        "policy": "Refund requests are accepted within 30 days of delivery.",
    }
