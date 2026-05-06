# ============================================================
# api/tickets.py
# Employee Dashboard endpoint'leri — sıra yönetimi
# ============================================================

from fastapi import APIRouter, HTTPException, status, Depends
from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from models.user import User, Role
from core.dependencies import get_current_user, require_employee, require_admin

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# ── Ticket Modeli ──────────────────────────────────────────
class Ticket(Document):
    ticket_number:   str
    prefix:          str
    sequence_number: int
    status:          str = "waiting"   # waiting | serving | completed | cancelled
    counter:         Optional[int] = None
    called_by:       Optional[str] = None   # User ID
    called_at:       Optional[datetime] = None
    completed_at:    Optional[datetime] = None
    created_at:      datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tickets"


# ── GET /api/tickets/queue ─────────────────────────────────
@router.get("/queue")
async def get_queue(current_user: User = Depends(get_current_user)):
    """Bekleyen biletlerin listesi — Dashboard için."""
    queue = await Ticket.find(
        Ticket.status == "waiting"
    ).sort("+created_at").to_list()

    return {
        "queue": [
            {
                "id":             str(t.id),
                "ticket_number":  t.ticket_number,
                "status":         t.status,
                "created_at":     t.created_at.isoformat(),
            }
            for t in queue
        ],
        "total": len(queue)
    }


# ── GET /api/tickets/active ────────────────────────────────
@router.get("/active")
async def get_active(current_user: User = Depends(get_current_user)):
    """Çalışanın aktif olarak servis ettiği bilet."""
    active = await Ticket.find_one(
        Ticket.called_by == str(current_user.id),
        Ticket.status    == "serving"
    )
    return {"active": active.dict() if active else None}


# ── POST /api/tickets/call-next ────────────────────────────
@router.post("/call-next")
async def call_next(
    counter: int,
    current_user: User = Depends(get_current_user)
):
    """Sıradaki müşteriyi çağır (FIFO)."""

    # Çalışanın zaten aktif müşterisi var mı?
    already_serving = await Ticket.find_one(
        Ticket.called_by == str(current_user.id),
        Ticket.status    == "serving"
    )
    if already_serving:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Önce mevcut müşteriyi tamamlayın: {already_serving.ticket_number}"
        )

    # En eski bekleyen bileti al (FIFO)
    next_ticket = await Ticket.find(
        Ticket.status == "waiting"
    ).sort("+created_at").first_or_none()

    if not next_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sırada bekleyen müşteri yok."
        )

    # Bileti güncelle
    next_ticket.status    = "serving"
    next_ticket.counter   = counter
    next_ticket.called_by = str(current_user.id)
    next_ticket.called_at = datetime.utcnow()
    await next_ticket.save()

    print(f"[TICKET] {next_ticket.ticket_number} → {current_user.username} (Gişe {counter})")

    return {"message": "Müşteri çağrıldı.", "ticket": next_ticket.dict()}


# ── POST /api/tickets/{id}/complete ───────────────────────
@router.post("/{ticket_id}/complete")
async def complete_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user)
):
    """Servisi tamamla."""
    ticket = await Ticket.get(ticket_id)

    if not ticket:
        raise HTTPException(status_code=404, detail="Bilet bulunamadı.")

    # Sadece kendi aldığı bileti tamamlayabilir
    if ticket.called_by != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu bileti tamamlama yetkiniz yok."
        )

    ticket.status       = "completed"
    ticket.completed_at = datetime.utcnow()
    await ticket.save()

    return {"message": "İşlem tamamlandı.", "ticket": ticket.dict()}


# ── POST /api/tickets/new ──────────────────────────────────
@router.post("/new", status_code=status.HTTP_201_CREATED)
async def create_ticket(prefix: str = "B"):
    """QR form'dan yeni bilet oluştur (public endpoint)."""

    last = await Ticket.find(
        Ticket.prefix == prefix
    ).sort("-sequence_number").first_or_none()

    seq           = (last.sequence_number + 1) if last else 1
    ticket_number = f"{prefix}-{seq}"

    ticket = Ticket(
        ticket_number=ticket_number,
        prefix=prefix,
        sequence_number=seq
    )
    await ticket.insert()

    position = await Ticket.find(
        Ticket.status == "waiting"
    ).count()

    return {
        "message": "Biletiniz oluşturuldu.",
        "ticket": {"ticket_number": ticket_number, "position": position}
    }


# ── GET /api/tickets/stats ─────────────────────────────────
@router.get("/stats")
async def get_stats(current_user: User = Depends(require_admin)):
    """Admin istatistikleri."""
    waiting   = await Ticket.find(Ticket.status == "waiting").count()
    serving   = await Ticket.find(Ticket.status == "serving").count()
    completed = await Ticket.find(Ticket.status == "completed").count()

    return {
        "waiting":   waiting,
        "serving":   serving,
        "completed": completed,
        "total":     waiting + serving + completed
    }