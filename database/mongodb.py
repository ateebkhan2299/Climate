"""
MongoDB Client and Collection Management
Provides centralized database connection, index management, and querying helpers.
Supports MONGO_URI environment variable for cloud/Vercel deployment.
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
import logging
import os

logger = logging.getLogger("EarthScapeMongoDB")

DB_NAME = "earthscape_climate_db"

def get_db(uri: str = None, db_name: str = DB_NAME):
    """Obtain a connected pymongo Database instance.
    Uses MONGO_URI env variable first, then falls back to provided uri or localhost.
    Returns None safely if connection fails - app continues working without DB.
    """
    if uri is None:
        uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    try:
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        # Verify connection
        client.admin.command('ping')
        logger.info("MongoDB connected successfully.")
        return client[db_name]
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None

def create_indexes(db):
    """Create optimal indexes on collections for sub-second query performance."""
    if db is None:
        return
    
    # 1. users indexes
    db['users'].create_index([("username", ASCENDING)], unique=True)

    # 2. weather_events_cleaned indexes
    db['weather_events_cleaned'].create_index([("State", ASCENDING)])
    db['weather_events_cleaned'].create_index([("Type", ASCENDING)])
    db['weather_events_cleaned'].create_index([("Severity", ASCENDING)])
    db['weather_events_cleaned'].create_index([("Year", ASCENDING)])
    db['weather_events_cleaned'].create_index([("Month", ASCENDING)])
    db['weather_events_cleaned'].create_index([("StartTime(UTC)", DESCENDING)])
    db['weather_events_cleaned'].create_index([("State", ASCENDING), ("Year", ASCENDING)])

    # 3. anomalies indexes
    db['anomalies'].create_index([("State", ASCENDING)])
    db['anomalies'].create_index([("Year", ASCENDING)])
    db['anomalies'].create_index([("anomaly_score", ASCENDING)])

    # 4. alerts indexes
    db['alerts'].create_index([("status", ASCENDING)])
    db['alerts'].create_index([("timestamp", DESCENDING)])
    db['alerts'].create_index([("state", ASCENDING)])

    # 5. feedback & system_logs indexes
    db['feedback'].create_index([("created_at", DESCENDING)])
    db['system_logs'].create_index([("timestamp", DESCENDING)])

    logger.info("MongoDB indexes successfully verified/created.")
