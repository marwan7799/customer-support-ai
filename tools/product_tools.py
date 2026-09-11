"""
Tool: get_product_info
Purpose: Retrieve product details (name, price, category, warranty).
"""
import json
from tools._data import load_json


def get_product_info(product_id: str) -> dict:
    """
    Look up product details by ID.

    Args:
        product_id: The product identifier, e.g. "P100"

    Returns:
        {"success": True, "data": {...product fields...}}
        or
        {"success": False, "error": "<reason>"}
    """
    if not product_id or not isinstance(product_id, str):
        return {"success": False, "error": "product_id must be a non-empty string."}

    try:
        products = load_json("products.json")
    except FileNotFoundError:
        return {"success": False, "error": "Product database is currently unavailable."}
    except json.JSONDecodeError:
        return {"success": False, "error": "Product database is corrupted."}

    product = next((p for p in products if p.get("product_id") == product_id.strip()), None)
    if product is None:
        return {"success": False, "error": f"No product found with ID '{product_id}'."}

    return {"success": True, "data": product}


if __name__ == "__main__":
    print(get_product_info("P100"))  
    print(get_product_info("P999"))  
