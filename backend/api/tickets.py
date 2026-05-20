from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from backend.models.user import User
from backend.models.ticket import Ticket
from backend.core.dependencies import get_current_user, require_employee, require_admin
from backend.core.security import encrypt_data

router = APIRouter(prefix="/tickets", tags=["Tickets"])

class TicketCreate(BaseModel):
    tckn: str = Field(..., min_length=11, max_length=11, description="11 haneli TCKN")
    prefix: str = "A"

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

@router.get("/active")
async def get_active(current_user: User = Depends(get_current_user)):
    """Çalışanın aktif olarak servis ettiği bilet."""
    active = await Ticket.find_one(
        Ticket.called_by == str(current_user.id),
        Ticket.status    == "serving"
    )
    if not active:
        return {"active": None}
    return {
        "active": {
            "id": str(active.id),
            "ticket_number": active.ticket_number,
            "status": active.status,
            "counter": active.counter
        }
    }

@router.post("/call-next")
async def call_next(
    counter: int,
    current_user: User = Depends(get_current_user)
):
    """Sıradaki müşteriyi çağır (FIFO)."""
    already_serving = await Ticket.find_one(
        Ticket.called_by == str(current_user.id),
        Ticket.status    == "serving"
    )
    if already_serving:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Önce mevcut müşteriyi tamamlayın: {already_serving.ticket_number}"
        )

    next_ticket = await Ticket.find(
        Ticket.status == "waiting"
    ).sort("+created_at").first_or_none()

    if not next_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sırada bekleyen müşteri yok."
        )

    next_ticket.status    = "serving"
    next_ticket.counter   = counter
    next_ticket.called_by = str(current_user.id)
    next_ticket.called_at = datetime.utcnow()
    await next_ticket.save()

    print(f"[TICKET] {next_ticket.ticket_number} → {current_user.username} (Gişe {counter})")
    return {
        "message": "Müşteri çağrıldı.",
        "ticket": {
            "id": str(next_ticket.id),
            "ticket_number": next_ticket.ticket_number,
            "status": next_ticket.status,
            "counter": next_ticket.counter
        }
    }

@router.post("/{ticket_id}/complete")
async def complete_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user)
):
    """Servisi tamamla."""
    from beanie import PydanticObjectId
    ticket = await Ticket.get(PydanticObjectId(ticket_id))

    if not ticket:
        raise HTTPException(status_code=404, detail="Bilet bulunamadı.")

    if ticket.called_by != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu bileti tamamlama yetkiniz yok."
        )

    ticket.status       = "completed"
    ticket.completed_at = datetime.utcnow()
    await ticket.save()

    return {
        "message": "İşlem tamamlandı.",
        "ticket": {
            "id": str(ticket.id),
            "ticket_number": ticket.ticket_number,
            "status": ticket.status,
            "counter": ticket.counter
        }
    }

@router.post("/new", status_code=status.HTTP_201_CREATED)
async def create_ticket(body: TicketCreate):
    """QR form'dan yeni bilet oluştur (public endpoint). TCKN şifrelenerek kaydedilir."""
    last = await Ticket.find(
        Ticket.prefix == body.prefix
    ).sort("-sequence_number").first_or_none()

    seq           = (last.sequence_number + 1) if last else 1
    ticket_number = f"{body.prefix}-{seq}"
    
    # TCKN Şifreleme (AES-256 Fernet)
    encrypted_tckn = encrypt_data(body.tckn)

    ticket = Ticket(
        ticket_number=ticket_number,
        prefix=body.prefix,
        sequence_number=seq,
        encrypted_tckn=encrypted_tckn
    )
    await ticket.insert()

    position = await Ticket.find(
        Ticket.status == "waiting"
    ).count()

    return {
        "message": "Biletiniz oluşturuldu.",
        "ticket": {"ticket_number": ticket_number, "position": position}
    }

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