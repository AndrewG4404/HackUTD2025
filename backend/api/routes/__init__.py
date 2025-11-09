"""
Routes package initialization.

Ensures MongoDB client is initialized when route modules load.
"""
from database import client as mongo_client  # noqa: F401