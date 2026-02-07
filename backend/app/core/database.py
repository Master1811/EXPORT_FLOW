from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

async def get_database():
    """Get database instance for use in background tasks"""
    return db

async def close_db():
    client.close()
