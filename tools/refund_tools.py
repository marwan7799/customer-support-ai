"""Deterministic refund-eligibility tool."""

from datetime import date, datetime, timezone

from tools._data import DataStoreError, find_by_id, load_records, normalize_identifier

REFUND_WINDOW_DAYS = 14


def _utc_today() -> date:
    return datetime.now(timezone.utc).date()


def check_refund_eligibility(order_id: str) -> dict:
    """Check refund eligibility using delivery status and a 14-day window."""
    order_id = normalize_identifier(order_id)
    if order_id is None:
        return {"success": False, "error": "order_id must be a non-empty string."}

    try:
        orders = load_records("orders.json")
    except DataStoreError:
        return {"success": False, "error": "Order database is currently unavailable."}

    order = find_by_id(orders, "order_id", order_id)
    if order is None:
        return {"success": False, "error": f"No order found with ID '{order_id}'."}

    canonical_order_id = str(order.get("order_id", order_id))
    status = str(order.get("status") or "").strip()
    delivery_date = order.get("delivery_date")

    if status.casefold() != "delivered":
        return {
            "success": True,
            "data": {
                "order_id": canonical_order_id,
                "eligible": False,
                "reason": f"Order status is '{status or 'unknown'}', so it is not eligible for refund review yet.",
            },
        }

    if not isinstance(delivery_date, str) or not delivery_date.strip():
        return {"success": False, "error": "Delivered order is missing a delivery date."}

    try:
        delivered_on = date.fromisoformat(delivery_date)
    except ValueError:
        return {"success": False, "error": "Order has an invalid delivery date format."}

    days_since_delivery = (_utc_today() - delivered_on).days
    if days_since_delivery < 0:
        return {"success": False, "error": "Order has a delivery date in the future."}

    eligible = days_since_delivery <= REFUND_WINDOW_DAYS
    if eligible:
        reason = (
            f"Delivered {days_since_delivery} day(s) ago, within the "
            f"{REFUND_WINDOW_DAYS}-day refund window."
        )
    else:
        reason = (
            f"Delivered {days_since_delivery} day(s) ago, past the "
            f"{REFUND_WINDOW_DAYS}-day refund window."
        )

    return {
        "success": True,
        "data": {
            "order_id": canonical_order_id,
            "eligible": eligible,
            "reason": reason,
        },
    }
