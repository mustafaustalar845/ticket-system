from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field

class Ticket(Document):
    ticket_number: str = Field(index=True) # e.g., A-1
    prefix: str = "A"
    sequence_number: int = 1
    encrypted_tckn: str # AES-256 encrypted string
    status: str = Field(default="waiting") # "waiting", "serving", "called", "completed", "cancelled"
    counter: Optional[int] = None
    called_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    called_by: Optional[str] = None # Reference to the user ID who called it
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tickets"

class AuditLog(Document):
    event_type: str
    actor: Optional[str] = None
    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "audit_logs"
