"""
MongoDB data models and schemas.
Based on the PRD data model specification.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from database import client as mongo_client  # noqa: F401
from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """File information model"""
    name: str
    path: str
    mime_type: str


class AgentOutputs(BaseModel):
    """Agent outputs structure"""
    intake: Optional[Dict[str, Any]] = None
    verification: Optional[Dict[str, Any]] = None
    compliance: Optional[Dict[str, Any]] = None
    interoperability: Optional[Dict[str, Any]] = None
    finance: Optional[Dict[str, Any]] = None
    adoption: Optional[Dict[str, Any]] = None


class Vendor(BaseModel):
    """Vendor model"""
    id: str
    name: str
    website: str
    contact_email: Optional[str] = None
    hq_location: Optional[str] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    files: List[FileInfo] = []
    doc_urls: List[str] = []
    agent_outputs: AgentOutputs = AgentOutputs()
    total_score: Optional[float] = None
    progress: Optional[str] = None  # For tracking pipeline progress


class Weights(BaseModel):
    """Weight configuration for assessment"""
    security: int = Field(ge=0, le=5)
    cost: int = Field(ge=0, le=5)
    interoperability: int = Field(ge=0, le=5)
    adoption: int = Field(ge=0, le=5)


class RequirementProfile(BaseModel):
    """Requirement profile from Use Case Context Agent"""
    critical_requirements: List[str] = []
    nice_to_haves: List[str] = []
    compliance_expectations: List[str] = []


class Recommendation(BaseModel):
    """Recommendation model"""
    vendor_id: str
    reason: str


class Evaluation(BaseModel):
    """Evaluation document model"""
    _id: Optional[str] = None
    type: str  # "application" | "assessment"
    name: str
    use_case: Optional[str] = None  # null for application workflow
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # "pending" | "running" | "completed" | "failed"
    weights: Optional[Weights] = None  # assessment only
    requirement_profile: Optional[RequirementProfile] = None  # assessment only
    vendors: List[Vendor] = []
    recommendation: Optional[Recommendation] = None
    onboarding_checklist: List[str] = []
    error: Optional[str] = None

