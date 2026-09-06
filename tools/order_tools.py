import json
from pathlib import Path

ORDERS_PATH = Path(__file__).parents[1] / "data" / "orders.json"


def _load_orders():
    return json.loads(ORDERS_PATH.read_text(encoding="utf-8"))


def get_order_status(order_id: str) -> dict:
    """Return the status information for an order."""
    orders = _load_orders()
    order = next((o for o in orders if o["order_id"] == str(order_id)), None)

    if not order:
        return {"ok": False, "error": "Order not found."}

    return {
        "ok": True,
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "status": order["status"],
        "delivery_date": order["delivery_date"],
    }
