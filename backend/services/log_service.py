from backend.models.ticket import AuditLog

async def write_log(event_type: str, detail: str, actor: str = None):
    log = AuditLog(
        event_type=event_type,
        actor=actor,
        detail=detail,
    )
    await log.insert()