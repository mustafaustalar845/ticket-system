from fastapi import APIRouter, Depends
from backend.core.dependencies import get_current_user, require_admin
from backend.models.ticket import Ticket, AuditLog
from backend.models.user import User
from backend.schemas.log_schema import TicketPublicOut, AuditLogOut
from beanie.operators import In

router = APIRouter(tags=["Logs & Public View"])

@router.get("/public/tickets", response_model=list[TicketPublicOut])
async def get_public_tickets():
    tickets = await Ticket.find(In(Ticket.status, ["waiting", "called"])).sort("+created_at").to_list()
    return tickets

@router.get("/public/last-called", response_model=TicketPublicOut | None)
async def get_last_called():
    ticket = await Ticket.find(Ticket.status == "called").sort("-called_at").first_or_none()
    return ticket

@router.get("/admin/logs", response_model=list[AuditLogOut])
async def get_audit_logs(
    current_user: User = Depends(require_admin),   
):
    logs = await AuditLog.find_all().sort("-timestamp").to_list()
    return logs

@router.get("/admin/logs/{event_type}", response_model=list[AuditLogOut])
async def get_logs_by_type(
    event_type: str,
    current_user: User = Depends(require_admin),
):
    """
    Belirli bir event tipine ait log'ları döner.
    Örnek: GET /admin/logs/login_failed
           GET /admin/logs/ticket_called
    """
    logs = await AuditLog.find(AuditLog.event_type == event_type).sort("-timestamp").to_list()
    return logs