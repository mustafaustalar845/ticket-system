from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.ticket_schema import TicketCreate, TicketResponse
from backend.services.queue_manager import QueueManager
from backend.models.user import User
from backend.api.dependencies import get_current_active_user
from backend.api.endpoints.monitor import manager

router = APIRouter()

@router.post("/take", response_model=TicketResponse)
async def take_ticket(ticket_in: TicketCreate):
    """Endpoint for normal users/kiosk to take a new ticket."""
    ticket = await QueueManager.create_ticket(ticket_in.tckn)
    
    # Broadcast to websocket that a new ticket was added
    await manager.broadcast(f"New ticket added: {ticket.ticket_number}")
    
    return ticket

@router.post("/call_next", response_model=TicketResponse)
async def call_next_ticket(current_user: User = Depends(get_current_active_user)):
    """Endpoint for employees/admins to call the next ticket in queue."""
    ticket = await QueueManager.call_next_ticket(str(current_user.id))
    if not ticket:
        raise HTTPException(status_code=404, detail="No waiting tickets in the queue")
    
    # Broadcast to websocket that a ticket was called
    await manager.broadcast(f"Ticket called: {ticket.ticket_number} to Desk")
    
    return ticket
