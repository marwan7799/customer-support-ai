"""Support-ticket creation tool."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone

from tools._data import (
    RUNTIME_DIR,
    DataStoreError,
    find_by_id,
    load_json,
    load_records,
    normalize_identifier,
    save_json,
)

TICKETS_PATH = RUNTIME_DIR / "tickets.json"
_TICKET_WRITE_LOCK = threading.Lock()


def _load_tickets() -> list[dict]:
    if not TICKETS_PATH.exists():
        return []

    tickets = load_json(TICKETS_PATH)
    if not isinstance(tickets, list) or not all(isinstance(ticket, dict) for ticket in tickets):
        raise DataStoreError("Ticket storage has an invalid structure.")
    return tickets


def create_support_ticket(customer_id: str, issue: str) -> dict:
    """Create and persist a support ticket for an existing customer."""
    customer_id = normalize_identifier(customer_id)
    if customer_id is None:
        return {"success": False, "error": "customer_id must be a non-empty string."}

    if not isinstance(issue, str) or not issue.strip():
        return {"success": False, "error": "issue must be a non-empty description."}
    cleaned_issue = issue.strip()

    try:
        customers = load_records("customers.json")
    except DataStoreError:
        return {"success": False, "error": "Customer database is currently unavailable."}

    customer = find_by_id(customers, "customer_id", customer_id)
    if customer is None:
        return {"success": False, "error": f"No customer found with ID '{customer_id}'."}

    canonical_customer_id = str(customer["customer_id"])
    ticket = {
        "ticket_id": "TCKT" + uuid.uuid4().hex[:8].upper(),
        "customer_id": canonical_customer_id,
        "issue": cleaned_issue,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        with _TICKET_WRITE_LOCK:
            tickets = _load_tickets()
            tickets.append(ticket)
            save_json(TICKETS_PATH, tickets)
    except DataStoreError:
        return {"success": False, "error": "Ticket storage is currently unavailable."}

    return {"success": True, "data": ticket}
