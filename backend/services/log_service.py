
from sqlalchemy.orm import Session
from models.ticket import AuditLog


def write_log(db: Session, event_type: str, detail: str, actor: str = None):
   
    log = AuditLog(
        event_type=event_type,
        actor=actor,
        detail=detail,
    )
    db.add(log)
    db.commit()