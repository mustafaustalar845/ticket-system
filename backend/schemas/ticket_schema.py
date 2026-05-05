from pydantic import BaseModel, constr
from typing import Optional
from datetime import datetime

class TicketCreate(BaseModel):
    # Expect a valid TCKN pattern (usually 11 digits in Turkey)
    tckn: constr(min_length=11, max_length=11, pattern=r'^\d+$')

class TicketResponse(BaseModel):
    ticket_number: str
    status: str
    created_at: datetime
    called_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }
