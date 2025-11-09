"""
MongoDB connection and database utilities.

Uses the provided MongoDB Atlas connection string to create a client and
returns the `vendorlens` database for downstream operations.
"""
from typing import Optional

from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MONGODB_URI = (
    "mongodb+srv://admin:48aX6qgzAjf9uZ2Y@hackutd2025.3wkesnl.mongodb.net/"
    "?appName=HackUTD2025"
)
DATABASE_NAME = "vendorlens"

_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def _ensure_client() -> MongoClient:
    """Create and cache a MongoDB client using the provided Atlas URI."""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
        try:
            _client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as exc:  # pragma: no cover - log connection issues
            print(exc)
    return _client


def get_database() -> Database:
    """Get the MongoDB database instance."""
    global _db
    if _db is None:
        client = _ensure_client()
        _db = client[DATABASE_NAME]
    return _db


def close_database():
    """Close the cached MongoDB client and database references."""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None