# ticket_manager.py

import uuid
from datetime import datetime
from typing import Dict, Any

class TicketManager:
    @staticmethod
    def create_ticket(customer_name: str, email: str, issue_summary: str, priority: str = "Medium") -> Dict[str, Any]:
        ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
        return {
            "ticket_id": ticket_id,
            "customer_name": customer_name,
            "email": email,
            "issue_summary": issue_summary,
            "priority": priority,
            "status": "Open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }