"""
Tool: create_support_ticket
Purpose: Open a support ticket for a customer issue and store it.
"""
import json
import os
import uuid
from datetime import datetime, timezone
from tools._data import load_json, save_json, _DATA_DIR


def _ensure_tickets_file():
    """Create an empty tickets.json the first time this runs, if it doesn't exist yet."""
    path = os.path.join(_DATA_DIR, "tickets.json")
    if not os.path.exists(path):
        save_json("tickets.json", [])


def create_support_ticket(customer_id: str, issue: str) -> dict:
    """
    Create a support ticket for a customer.

    Args:
        customer_id: The customer identifier, e.g. "CUST001"
        issue: Description of the customer's issue.

    Returns:
        {"success": True, "data": {"ticket_id": ..., "customer_id": ..., "issue": ..., "created_at": ...}}
        or
        {"success": False, "error": "<reason>"}
    """
    if not customer_id or not isinstance(customer_id, str):
        return {"success": False, "error": "customer_id must be a non-empty string."}
    if not issue or not isinstance(issue, str) or not issue.strip():
        return {"success": False, "error": "issue must be a non-empty description."}

    try:
        customers = load_json("customers.json")
    except FileNotFoundError:
        return {"success": False, "error": "Customer database is currently unavailable."}
    except json.JSONDecodeError:
        return {"success": False, "error": "Customer database is corrupted."}

    customer = next((c for c in customers if c.get("customer_id") == customer_id.strip()), None)
    if customer is None:
        return {"success": False, "error": f"No customer found with ID '{customer_id}'."}

    try:
        _ensure_tickets_file()
        tickets = load_json("tickets.json")
    except json.JSONDecodeError:
        return {"success": False, "error": "Ticket storage is corrupted."}

    ticket_id = "TCKT" + uuid.uuid4().hex[:8].upper()
    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id.strip(),
        "issue": issue.strip(),
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    tickets.append(ticket)

    try:
        save_json("tickets.json", tickets)
    except OSError:
        return {"success": False, "error": "Failed to save the ticket. Please try again."}

    return {"success": True, "data": ticket}


if __name__ == "__main__":
    print(create_support_ticket("CUST001", "Headphones arrived broken, wants a refund."))
    print(create_support_ticket("CUST999", "Nonexistent customer test"))  
    print(create_support_ticket("CUST001", ""))  
