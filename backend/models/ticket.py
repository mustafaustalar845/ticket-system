from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field

class Ticket(Document):
    ticket_number: str = Field(index=True) # e.g., A001
    encrypted_tckn: str # AES-256 encrypted string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="waiting") # "waiting", "called", "completed"
    called_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    called_by_user_id: Optional[str] = None # Reference to the user who called it

    class Settings:
        name = "tickets"
