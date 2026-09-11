"""
Tool: check_refund_eligibility
Purpose: Determine refund eligibility for an order using a deterministic policy rule
         (not left to the LLM to decide/guess).

Demo policy (edit freely to match what you and Kareem agree on):
  - Eligible if the order status is "Delivered" AND it was delivered within the last 14 days.
  - Orders that are "In Transit" or "Cancelled" are not eligible yet / not applicable.
"""
import json
from datetime import datetime, timezone
from tools._data import load_json

REFUND_WINDOW_DAYS = 14


def check_refund_eligibility(order_id: str) -> dict:
    """
    Check whether an order is eligible for a refund under the demo policy.

    Args:
        order_id: The order identifier, e.g. "ORD1001"

    Returns:
        {"success": True, "data": {"order_id": ..., "eligible": <bool>, "reason": "<explanation>"}}
        or
        {"success": False, "error": "<reason>"}
    """
    if not order_id or not isinstance(order_id, str):
        return {"success": False, "error": "order_id must be a non-empty string."}

    try:
        orders = load_json("orders.json")
    except FileNotFoundError:
        return {"success": False, "error": "Order database is currently unavailable."}
    except json.JSONDecodeError:
        return {"success": False, "error": "Order database is corrupted."}

    order = next((o for o in orders if o.get("order_id") == order_id.strip()), None)
    if order is None:
        return {"success": False, "error": f"No order found with ID '{order_id}'."}

    status = order.get("status")
    delivery_date = order.get("delivery_date")

    if status != "Delivered" or not delivery_date:
        return {
            "success": True,
            "data": {
                "order_id": order_id,
                "eligible": False,
                "reason": f"Order status is '{status}', which is not eligible for refund review yet.",
            },
        }

    try:
        delivered = datetime.strptime(delivery_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return {"success": False, "error": "Order has an invalid delivery date format."}

    days_since_delivery = (datetime.now(timezone.utc) - delivered).days
    eligible = days_since_delivery <= REFUND_WINDOW_DAYS

    reason = (
        f"Delivered {days_since_delivery} day(s) ago, within the {REFUND_WINDOW_DAYS}-day refund window."
        if eligible
        else f"Delivered {days_since_delivery} day(s) ago, past the {REFUND_WINDOW_DAYS}-day refund window."
    )

    return {
        "success": True,
        "data": {"order_id": order_id, "eligible": eligible, "reason": reason},
    }


if __name__ == "__main__":
    print(check_refund_eligibility("ORD1001"))  # delivered order — check window
    print(check_refund_eligibility("ORD1002"))  # in transit — not eligible
    print(check_refund_eligibility("ORD9999"))  # not found
