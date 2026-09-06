import json
from pathlib import Path
from datetime import datetime

TICKETS_PATH = Path(__file__).parents[1] / "data" / "tickets_runtime.json"


def create_support_ticket(customer_id: str, issue: str) -> dict:
    """Create and persist a demo support ticket."""
    if not customer_id or not issue.strip():
        return {"ok": False, "error": "customer_id and issue are required."}

    tickets = []
    if TICKETS_PATH.exists():
        tickets = json.loads(TICKETS_PATH.read_text(encoding="utf-8"))

    ticket_id = f"T-{len(tickets) + 1001}"
    ticket = {
        "ticket_id": ticket_id,
        "customer_id": str(customer_id),
        "issue": issue.strip(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": "OPEN",
    }

    tickets.append(ticket)
    TICKETS_PATH.write_text(json.dumps(tickets, indent=2), encoding="utf-8")

    return {"ok": True, **ticket}
