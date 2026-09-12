"""Order-status lookup tool."""
from tools._data import DataStoreError, find_by_id, load_records, normalize_identifier


def get_order_status(order_id: str) -> dict:
    """Return the matching order record for a valid order ID."""
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

    return {"success": True, "data": order}
