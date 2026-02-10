"""
High-Performance Database Layer
- Motor-based connection pooling with configurable pool sizes
- Compound indexes for common query patterns
- Optimized for 10,000+ concurrent users
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, IndexModel
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Connection pooling settings for high concurrency
POOL_SETTINGS = {
    "maxPoolSize": 100,  # Maximum connections in pool
    "minPoolSize": 10,   # Minimum connections to keep open
    "maxIdleTimeMS": 30000,  # Close idle connections after 30s
    "waitQueueTimeoutMS": 5000,  # Timeout waiting for connection
    "serverSelectionTimeoutMS": 5000,  # Server selection timeout
    "connectTimeoutMS": 10000,  # Connection timeout
    "socketTimeoutMS": 20000,  # Socket timeout
    "retryWrites": True,  # Retry failed writes
    "retryReads": True,  # Retry failed reads
}

# Create client with connection pooling
client = AsyncIOMotorClient(settings.MONGO_URL, **POOL_SETTINGS)
db = client[settings.DB_NAME]


# Index definitions for high-performance queries
INDEXES = {
    "shipments": [
        IndexModel([("company_id", ASCENDING), ("created_at", DESCENDING)], name="company_created_idx"),
        IndexModel([("company_id", ASCENDING), ("status", ASCENDING)], name="company_status_idx"),
        IndexModel([("company_id", ASCENDING), ("ebrc_status", ASCENDING)], name="company_ebrc_idx"),
        IndexModel([("id", ASCENDING)], unique=True, name="shipment_id_idx"),
    ],
    "documents": [
        IndexModel([("shipment_id", ASCENDING), ("document_type", ASCENDING)], name="shipment_doctype_idx"),
        IndexModel([("company_id", ASCENDING), ("created_at", DESCENDING)], name="company_created_idx"),
        IndexModel([("id", ASCENDING)], unique=True, name="document_id_idx"),
    ],
    "gst_credits": [
        IndexModel([("company_id", ASCENDING), ("created_at", DESCENDING)], name="company_created_idx"),
        IndexModel([("company_id", ASCENDING), ("status", ASCENDING)], name="company_status_idx"),
    ],
    "payments": [
        IndexModel([("company_id", ASCENDING), ("created_at", DESCENDING)], name="company_created_idx"),
        IndexModel([("shipment_id", ASCENDING)], name="shipment_idx"),
        IndexModel([("company_id", ASCENDING), ("status", ASCENDING)], name="company_status_idx"),
    ],
    "connectors": [
        IndexModel([("iec_code", ASCENDING), ("company_id", ASCENDING)], name="iec_company_idx"),
        IndexModel([("company_id", ASCENDING), ("connector_type", ASCENDING)], name="company_type_idx"),
    ],
    "users": [
        IndexModel([("email", ASCENDING)], unique=True, name="email_idx"),
        IndexModel([("company_id", ASCENDING)], name="company_idx"),
    ],
    "companies": [
        IndexModel([("id", ASCENDING)], unique=True, name="company_id_idx"),
    ],
    "audit_logs": [
        IndexModel([("company_id", ASCENDING), ("timestamp", DESCENDING)], name="company_timestamp_idx"),
        IndexModel([("user_id", ASCENDING), ("timestamp", DESCENDING)], name="user_timestamp_idx"),
        IndexModel([("action_type", ASCENDING), ("timestamp", DESCENDING)], name="action_timestamp_idx"),
        IndexModel([("resource_type", ASCENDING), ("resource_id", ASCENDING)], name="resource_idx"),
    ],
    "incentives": [
        IndexModel([("company_id", ASCENDING), ("created_at", DESCENDING)], name="company_created_idx"),
    ],
    "compliance": [
        IndexModel([("company_id", ASCENDING), ("type", ASCENDING)], name="company_type_idx"),
    ],
    "uploaded_files": [
        IndexModel([("company_id", ASCENDING), ("created_at", DESCENDING)], name="company_created_idx"),
    ],
    "ocr_jobs": [
        IndexModel([("company_id", ASCENDING), ("status", ASCENDING)], name="company_status_idx"),
    ],
    "refresh_tokens": [
        IndexModel([("token", ASCENDING)], unique=True, name="token_idx"),
        IndexModel([("user_id", ASCENDING)], name="user_idx"),
        IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0, name="ttl_idx"),
    ],
    "blacklisted_tokens": [
        IndexModel([("jti", ASCENDING)], unique=True, name="jti_idx"),
        IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0, name="ttl_idx"),
    ],
    # NEW: Security-related collections
    "login_attempts": [
        IndexModel([("identifier", ASCENDING), ("type", ASCENDING)], unique=True, name="identifier_type_idx"),
        IndexModel([("lockout_until", ASCENDING)], name="lockout_idx"),
    ],
    "user_sessions": [
        IndexModel([("user_id", ASCENDING), ("is_active", ASCENDING)], name="user_active_idx"),
        IndexModel([("token_hash", ASCENDING)], name="token_hash_idx"),
        IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0, name="ttl_idx"),
    ],
    "email_verifications": [
        IndexModel([("token_hash", ASCENDING)], unique=True, name="token_hash_idx"),
        IndexModel([("user_id", ASCENDING)], name="user_idx"),
        IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0, name="ttl_idx"),
    ],
    # NEW: Forex collections
    "forex_rates": [
        IndexModel([("currency", ASCENDING), ("timestamp", DESCENDING)], name="currency_time_idx"),
        IndexModel([("company_id", ASCENDING), ("timestamp", DESCENDING)], name="company_time_idx"),
    ],
    "forex_alerts": [
        IndexModel([("company_id", ASCENDING), ("acknowledged", ASCENDING)], name="company_ack_idx"),
        IndexModel([("timestamp", DESCENDING)], name="time_idx"),
    ],
    # AI usage tracking
    "ai_usage": [
        IndexModel([("company_id", ASCENDING), ("created_at", DESCENDING)], name="company_time_idx"),
        IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)], name="user_time_idx"),
    ],
    "ai_chat_history": [
        IndexModel([("user_id", ASCENDING), ("session_id", ASCENDING)], name="user_session_idx"),
        IndexModel([("session_id", ASCENDING), ("created_at", DESCENDING)], name="session_time_idx"),
        IndexModel([("company_id", ASCENDING)], name="company_idx"),
    ],
}


async def ensure_indexes():
    """Create all indexes - call on application startup"""
    logger.info("Creating database indexes for high-performance queries...")
    
    for collection_name, indexes in INDEXES.items():
        try:
            collection = db[collection_name]
            # Create indexes (skips if already exists)
            await collection.create_indexes(indexes)
            logger.info(f"Indexes ensured for collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Index creation for {collection_name}: {e}")
    
    logger.info("Database indexes setup complete")


async def get_database():
    """Get database instance for use in background tasks"""
    return db


async def close_db():
    """Close database connection"""
    client.close()


async def get_pool_stats():
    """Get connection pool statistics for monitoring"""
    try:
        # Get server status
        server_status = await db.command("serverStatus")
        connections = server_status.get("connections", {})
        return {
            "current": connections.get("current", 0),
            "available": connections.get("available", 0),
            "total_created": connections.get("totalCreated", 0),
            "pool_size": POOL_SETTINGS["maxPoolSize"],
            "min_pool_size": POOL_SETTINGS["minPoolSize"],
        }
    except Exception as e:
        logger.error(f"Failed to get pool stats: {e}")
        return {"error": str(e)}
