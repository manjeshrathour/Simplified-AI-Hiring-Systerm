# MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
from config.settings import settings
from utils.logger import log


class MongoDB:
    """MongoDB client for async operations"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            log.info(f"Connected to MongoDB at {settings.MONGODB_URL}")
            
            # Create indexes
            await self.create_indexes()
            
        except Exception as e:
            log.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def create_indexes(self):
        """Create necessary indexes"""
        try:
            # Candidates collection indexes
            await self.db.candidates.create_index("email", unique=True)
            await self.db.candidates.create_index("uploaded_at")
            await self.db.candidates.create_index("score")
            
            # Jobs collection indexes
            await self.db.jobs.create_index("job_id", unique=True)
            await self.db.jobs.create_index("status")
            await self.db.jobs.create_index("created_at")
            
            # Interviews collection indexes
            await self.db.interviews.create_index("candidate_id")
            await self.db.interviews.create_index("job_id")
            await self.db.interviews.create_index("scheduled_time")
            
            log.info("Database indexes created successfully")
            
        except Exception as e:
            log.error(f"Failed to create indexes: {e}")
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            log.info("MongoDB connection closed")
    
    def get_collection(self, collection_name: str):
        """Get a collection"""
        return self.db[collection_name]


class MongoDBSync:
    """Synchronous MongoDB client for non-async contexts"""
    
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
    
    def get_collection(self, collection_name: str):
        """Get a collection"""
        return self.db[collection_name]
    
    def close(self):
        """Close connection"""
        self.client.close()


# Global instances
mongodb = MongoDB()
mongodb_sync = MongoDBSync()