"""
Tool: get_product_info
Purpose: Retrieve product details (name, price, category, warranty), by ID or by name.
"""
from tools._data import load_records, find_by_id, normalize_identifier, DataStoreError


def get_product_info(product_id: str = None, product_name: str = None) -> dict:
    """
    Look up product details by ID or by name.

    Args:
        product_id: The product identifier, e.g. "P100" (optional if product_name is given)
        product_name: The product's name, e.g. "Bluetooth Speaker Mini" (optional if product_id is given)

    Returns:
        {"success": True, "data": {...product fields...}}
        or
        {"success": False, "error": "<reason>"}
    """
    product_id = normalize_identifier(product_id)
    product_name = normalize_identifier(product_name)

    if not product_id and not product_name:
        return {"success": False, "error": "Either product_id or product_name must be provided."}

    try:
        products = load_records("products.json")
    except DataStoreError as e:
        return {"success": False, "error": str(e)}

    product = find_by_id(products, "product_id", product_id) if product_id else None

    if product is None and product_name:
        needle = product_name.casefold()
        product = next(
            (p for p in products if needle in str(p.get("name", "")).casefold()),
            None,
        )

    if product is None:
        label = product_id or product_name
        return {"success": False, "error": f"No product found matching '{label}'."}

    return {"success": True, "data": product}


if __name__ == "__main__":
    print(get_product_info(product_id="P100"))
    print(get_product_info(product_name="Bluetooth Speaker Mini"))
    print(get_product_info(product_id="P999"))