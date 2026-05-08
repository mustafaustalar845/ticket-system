

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from api.dependencies import get_current_user, require_admin
from models.ticket import Ticket, AuditLog
from models.user import User
from schemas.log_schema import TicketPublicOut, AuditLogOut

router = APIRouter(tags=["Logs & Public View"])



@router.get("/public/tickets", response_model=list[TicketPublicOut])
def get_public_tickets(db: Session = Depends(get_db)):
   
    tickets = (
        db.query(Ticket)
        .filter(Ticket.status.in_(["waiting", "called"]))
        .order_by(Ticket.created_at.asc())
        .all()
    )
    return tickets



@router.get("/public/last-called", response_model=TicketPublicOut | None)
def get_last_called(db: Session = Depends(get_db)):
    
    ticket = (
        db.query(Ticket)
        .filter(Ticket.status == "called")
        .order_by(Ticket.called_at.desc())
        .first()
    )
    return ticket



@router.get("/admin/logs", response_model=list[AuditLogOut])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),   
):
    
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return logs



@router.get("/admin/logs/{event_type}", response_model=list[AuditLogOut])
def get_logs_by_type(
    event_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Belirli bir event tipine ait log'ları döner.
    Örnek: GET /admin/logs/login_failed
           GET /admin/logs/ticket_called
    """
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.event_type == event_type)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )
    return logs