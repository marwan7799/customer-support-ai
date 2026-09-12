"""Product-stock lookup tool."""

from numbers import Real

from tools._data import DataStoreError, find_by_id, load_records, normalize_identifier


def check_stock(product_id: str) -> dict:
    """Return current stock quantity and availability for a product."""
    product_id = normalize_identifier(product_id)
    if product_id is None:
        return {"success": False, "error": "product_id must be a non-empty string."}

    try:
        products = load_records("products.json")
    except DataStoreError:
        return {"success": False, "error": "Product database is currently unavailable."}

    product = find_by_id(products, "product_id", product_id)
    if product is None:
        return {"success": False, "error": f"No product found with ID '{product_id}'."}

    stock = product.get("stock")
    if isinstance(stock, bool) or not isinstance(stock, Real) or stock < 0:
        return {"success": False, "error": "Product has an invalid stock value."}

    return {
        "success": True,
        "data": {
            "product_id": product["product_id"],
            "name": product.get("name"),
            "stock": stock,
            "in_stock": stock > 0,
        },
    }
