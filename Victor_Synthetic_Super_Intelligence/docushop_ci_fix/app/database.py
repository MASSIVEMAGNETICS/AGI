from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings


class Database:
    """Database connection manager"""

    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        print(f"Connected to MongoDB at {settings.MONGODB_URL}")

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("Closed MongoDB connection")

    @classmethod
    def get_database(cls):
        """Get database instance"""
        if not cls.client:
            raise RuntimeError("Database not connected")
        return cls.client[settings.DATABASE_NAME]


async def get_db():
    """Dependency for getting database"""
    return Database.get_database()
