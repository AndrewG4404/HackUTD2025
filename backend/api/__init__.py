"""
API package initialization.

Ensures MongoDB client is initialized when API routes are imported.
"""
from database import client as mongo_client  # noqa: F401