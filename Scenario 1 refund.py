"""
Multi-tool demo scenario 1: "My headphones arrived broken. Can I get a refund?"

Expected tool sequence:
  get_order_status -> check_refund_eligibility -> create_support_ticket

This script calls the tools directly (bypassing the LLM) to prove the
underlying data/logic chain works correctly before testing it through
the actual agent + Ollama. Useful for isolating bugs: if this script
fails, the problem is in your tools/data. If only the live agent fails,
the problem is in the agent's tool-selection logic.

Assumes demo data has:
  - order ORD1001 belonging to customer CUST001, status "Delivered"
Adjust the IDs below to match your actual data/orders.json if different.
"""
from tools import get_order_status, check_refund_eligibility, create_support_ticket

ORDER_ID = "ORD1001"
CUSTOMER_ID = "CUST001"
ISSUE_DESCRIPTION = "Headphones arrived broken, customer is requesting a refund."


def run_scenario():
    print(f"Customer message: \"My headphones arrived broken. Can I get a refund?\" "
          f"(order {ORDER_ID}, customer {CUSTOMER_ID})\n")

    # Step 1: check the order exists / was delivered
    print("Step 1: get_order_status")
    order_result = get_order_status(ORDER_ID)
    print(order_result)
    if not order_result["success"]:
        print("STOPPED — order lookup failed, cannot continue.")
        return

    # Step 2: check refund eligibility for that order
    print("\nStep 2: check_refund_eligibility")
    refund_result = check_refund_eligibility(ORDER_ID)
    print(refund_result)
    if not refund_result["success"]:
        print("STOPPED — refund check failed, cannot continue.")
        return

    eligible = refund_result["data"]["eligible"]
    reason = refund_result["data"]["reason"]

    # Step 3: create a support ticket regardless of eligibility,
    # so a human can review/process it either way.
    print("\nStep 3: create_support_ticket")
    ticket_issue = f"{ISSUE_DESCRIPTION} Refund eligibility: {eligible} ({reason})"
    ticket_result = create_support_ticket(CUSTOMER_ID, ticket_issue)
    print(ticket_result)

    # Final response the agent should produce for the customer
    print("\n--- Final response the agent should give the customer ---")
    if eligible:
        print(f"I'm sorry to hear that. Your order is eligible for a refund ({reason}). "
              f"I've opened ticket {ticket_result['data']['ticket_id']} to process it.")
    else:
        print(f"I'm sorry to hear that. Unfortunately this order is outside our refund window "
              f"({reason}). I've still opened ticket {ticket_result['data']['ticket_id']} "
              f"so our team can review your case.")


if __name__ == "__main__":
    run_scenario()