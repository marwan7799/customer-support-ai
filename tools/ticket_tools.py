import uuid
from datetime import datetime, timezone

from tools._data import (
    load_records,
    load_json,
    save_json,
    find_by_id,
    normalize_identifier,
    DataStoreError,
    RUNTIME_DIR,
)

TICKETS_FILE = RUNTIME_DIR / "tickets.json"


def _load_tickets() -> list:
    """Load existing tickets, starting fresh (empty list) if the file doesn't exist yet."""
    try:
        return load_json(TICKETS_FILE)
    except DataStoreError:
        return []


def create_support_ticket(customer_id: str, issue: str) -> dict:
    """
    Create a support ticket for a customer.

    Args:
        customer_id: The customer identifier, e.g. "CUST001"
        issue: Description of the customer's issue.

    Returns:
        {"success": True, "data": {"ticket_id": ..., "customer_id": ..., "issue": ..., "status": ..., "created_at": ...}}
        or
        {"success": False, "error": "<reason>"}
    """
    customer_id = normalize_identifier(customer_id)
    issue = issue.strip() if isinstance(issue, str) else None

    if not customer_id:
        return {"success": False, "error": "customer_id must be a non-empty string."}
    if not issue:
        return {"success": False, "error": "issue must be a non-empty description."}

    try:
        customers = load_records("customers.json")
    except DataStoreError as e:
        return {"success": False, "error": str(e)}

    customer = find_by_id(customers, "customer_id", customer_id)
    if customer is None:
        return {"success": False, "error": f"No customer found with ID '{customer_id}'."}

    tickets = _load_tickets()
    ticket = {
        "ticket_id": "TCKT" + uuid.uuid4().hex[:8].upper(),
        "customer_id": customer_id,
        "issue": issue,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    tickets.append(ticket)

    try:
        save_json(TICKETS_FILE, tickets)
    except DataStoreError as e:
        return {"success": False, "error": str(e)}

    return {"success": True, "data": ticket}


if __name__ == "__main__":
    print(create_support_ticket("CUST001", "Headphones arrived broken, wants a refund."))
    print(create_support_ticket("CUST999", "Nonexistent customer test"))
    print(create_support_ticket("CUST001", ""))