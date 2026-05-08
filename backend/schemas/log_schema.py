
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TicketPublicOut(BaseModel):
    """Public TV View'a gönderilen bilet verisi."""
    ticket_number : str
    status        : str          
    counter       : Optional[int] = None

    class Config:
        from_attributes = True


class AuditLogOut(BaseModel):
    """Admin paneline gönderilen audit log verisi."""
    id         : int
    event_type : str
    actor      : Optional[str] = None
    detail     : str
    timestamp  : datetime

    class Config:
        from_attributes = True