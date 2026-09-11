"""
Tool: get_order_status
Purpose: Check delivery/order status for a given order_id.
"""
import json
from tools._data import load_json


def get_order_status(order_id: str) -> dict:
    """
    Look up an order by ID.

    Args:
        order_id: The order identifier, e.g. "ORD1001"

    Returns:
        {"success": True, "data": {...order fields...}}
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

    return {"success": True, "data": order}


if __name__ == "__main__":
    print(get_order_status("ORD1001"))   
    print(get_order_status("ORD9999"))  
    print(get_order_status(""))        
