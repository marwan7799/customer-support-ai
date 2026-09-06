import json
from pathlib import Path

PRODUCTS_PATH = Path(__file__).parents[1] / "data" / "products.json"


def _load_products():
    return json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))


def get_product_info(product_id: str) -> dict:
    """Return product information."""
    products = _load_products()
    product = next((p for p in products if p["product_id"] == str(product_id)), None)

    if not product:
        return {"ok": False, "error": "Product not found."}

    return {"ok": True, **product}


def check_stock(product_id: str) -> dict:
    """Return stock availability for a product."""
    products = _load_products()
    product = next((p for p in products if p["product_id"] == str(product_id)), None)

    if not product:
        return {"ok": False, "error": "Product not found."}

    return {
        "ok": True,
        "product_id": product["product_id"],
        "product_name": product["name"],
        "stock": product["stock"],
        "in_stock": product["stock"] > 0,
    }
