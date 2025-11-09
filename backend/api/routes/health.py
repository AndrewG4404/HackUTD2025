"""
Health check endpoint.
"""
from database import client as mongo_client  # noqa: F401
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}

