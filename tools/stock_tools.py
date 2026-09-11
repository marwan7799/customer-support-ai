"""
Tool: check_stock
Purpose: Check availability/quantity for a given product_id.
"""
import json
from tools._data import load_json


def check_stock(product_id: str) -> dict:
    """
    Check stock level for a product. Stock comes from Python/data, never guessed by the LLM.

    Args:
        product_id: The product identifier, e.g. "P100"

    Returns:
        {"success": True, "data": {"product_id": ..., "stock": <int>, "in_stock": <bool>}}
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

    stock = product.get("stock", 0)
    return {
        "success": True,
        "data": {
            "product_id": product["product_id"],
            "name": product.get("name"),
            "stock": stock,
            "in_stock": stock > 0,
        },
    }


if __name__ == "__main__":
    print(check_stock("P100"))   # in stock
    print(check_stock("P101"))   # out of stock (0 in demo data)
    print(check_stock("P999"))   # not found