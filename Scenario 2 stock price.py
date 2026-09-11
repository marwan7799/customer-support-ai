from tools import get_product_info, check_stock

PRODUCT_ID = "P101"


def run_scenario():
    print(f"Customer message: \"Is the Bluetooth Speaker Mini in stock, and how much is it?\" "
          f"(product {PRODUCT_ID})\n")

    # Step 1: get product info (name, price, category, warranty)
    print("Step 1: get_product_info")
    product_result = get_product_info(PRODUCT_ID)
    print(product_result)
    if not product_result["success"]:
        print("STOPPED — product lookup failed, cannot continue.")
        return

    # Step 2: check stock for the same product
    print("\nStep 2: check_stock")
    stock_result = check_stock(PRODUCT_ID)
    print(stock_result)
    if not stock_result["success"]:
        print("STOPPED — stock check failed, cannot continue.")
        return

    name = product_result["data"]["name"]
    price = product_result["data"]["price"]
    in_stock = stock_result["data"]["in_stock"]
    stock_qty = stock_result["data"]["stock"]

    # Final response the agent should produce for the customer
    print("\n--- Final response the agent should give the customer ---")
    if in_stock:
        print(f"The {name} is priced at {price} EGP and currently in stock ({stock_qty} available).")
    else:
        print(f"The {name} is priced at {price} EGP but is currently out of stock. "
              f"I can let you know if it becomes available again.")


if __name__ == "__main__":
    run_scenario()