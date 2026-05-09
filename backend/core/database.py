from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.core.config import settings
from backend.models.user import User
from backend.models.ticket import Ticket, AuditLog

async def init_db():
    # Initialize MongoDB Client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize Beanie with our document models
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            User,
            Ticket,
            AuditLog
        ]
    )
