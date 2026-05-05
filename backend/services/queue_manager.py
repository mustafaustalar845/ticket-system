from datetime import datetime
from typing import Optional
from backend.models.ticket import Ticket
from backend.core.security import encrypt_data

class QueueManager:
    @staticmethod
    async def generate_ticket_number() -> str:
        """Generate a sequential ticket number like A001, A002..."""
        # Count today's tickets
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        count = await Ticket.find({"created_at": {"$gte": today}}).count()
        next_number = count + 1
        return f"A{next_number:03d}"

    @staticmethod
    async def create_ticket(tckn: str) -> Ticket:
        """Encrypts TCKN, generates ticket number and saves to DB"""
        encrypted_tckn = encrypt_data(tckn)
        ticket_number = await QueueManager.generate_ticket_number()
        
        ticket = Ticket(
            ticket_number=ticket_number,
            encrypted_tckn=encrypted_tckn
        )
        await ticket.insert()
        return ticket

    @staticmethod
    async def get_next_ticket() -> Optional[Ticket]:
        """Gets the oldest waiting ticket in the queue"""
        ticket = await Ticket.find(Ticket.status == "waiting").sort("created_at").first_or_none()
        return ticket

    @staticmethod
    async def call_next_ticket(user_id: str) -> Optional[Ticket]:
        """Marks the next ticket as called and returns it"""
        ticket = await QueueManager.get_next_ticket()
        if ticket:
            ticket.status = "called"
            ticket.called_at = datetime.utcnow()
            ticket.called_by_user_id = user_id
            await ticket.save()
            return ticket
        return None
