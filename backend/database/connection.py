"""
MongoDB connection and database utilities
"""
from pymongo import MongoClient
from pymongo.database import Database
import os
from typing import Optional

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_database() -> Database:
    """Get MongoDB database instance"""
    global _db
    if _db is None:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "vendorlens")
        
        client = MongoClient(mongodb_uri)
        _db = client[db_name]
    
    return _db


def close_database():
    """Close MongoDB connection"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None

