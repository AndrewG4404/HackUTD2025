"""
MongoDB data models and schemas.
Based on the PRD data model specification.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from database import client as mongo_client  # noqa: F401
from pydantic import BaseModel, Field


class DimensionStatus(str, Enum):
    """Status of a dimension evaluation"""
    OK = "ok"
    INSUFFICIENT_DATA = "insufficient_data"
    RISK = "risk"


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


class VendorDecision(BaseModel):
    """Vendor onboarding decision and lifecycle tracking"""
    status: str = "pending"  # "pending" | "approved_pending_actions" | "approved" | "declined"
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    notes: Optional[str] = None
    pending_actions: List[str] = []


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
    decision: VendorDecision = Field(default_factory=VendorDecision)  # Onboarding lifecycle state


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
    dimension_importance: Optional[Dict[str, int]] = None  # Inferred from use case
    integration_targets: List[str] = []
    scale_assumptions: Optional[Dict[str, Any]] = None


class Recommendation(BaseModel):
    """Recommendation model"""
    vendor_id: str
    reason: str


class DimensionAnalysis(BaseModel):
    """Analysis for a single dimension (security, interoperability, etc.)"""
    summary: str
    strengths: List[str] = []
    gaps: List[str] = []
    risks: Optional[List[str]] = None
    high_level_numbers: Optional[Dict[str, str]] = None  # For finance dimension


class VendorAnalysis(BaseModel):
    """Detailed analysis for a single vendor"""
    overview: str
    security: Optional[DimensionAnalysis] = None
    interoperability: Optional[DimensionAnalysis] = None
    finance: Optional[DimensionAnalysis] = None
    adoption: Optional[DimensionAnalysis] = None
    key_strengths: List[str] = []
    key_risks: List[str] = []


class ComparisonAnalysis(BaseModel):
    """Side-by-side comparison between vendors"""
    security: Optional[str] = None
    interoperability: Optional[str] = None
    cost: Optional[str] = None
    adoption: Optional[str] = None


class FinalRecommendation(BaseModel):
    """Final recommendation with detailed reasoning"""
    recommended_vendor_id: str
    short_reason: str
    detailed_reason: str


class Analysis(BaseModel):
    """Complete Goldman-style analysis with narrative"""
    per_vendor: Dict[str, VendorAnalysis] = {}
    comparison: Optional[ComparisonAnalysis] = None
    final_recommendation: Optional[FinalRecommendation] = None


class Evaluation(BaseModel):
    """Evaluation document model"""
    _id: Optional[str] = None
    type: str  # "application" | "assessment"
    name: str
    use_case: Optional[str] = None  # null for application workflow
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # "pending" | "running" | "completed" | "failed"
    weights: Optional[Weights] = None  # assessment only (legacy, overridden by dimension_importance)
    requirement_profile: Optional[RequirementProfile] = None  # assessment only
    vendors: List[Vendor] = []
    recommendation: Optional[Recommendation] = None
    analysis: Optional[Analysis] = None  # Goldman-style detailed analysis
    onboarding_checklist: List[str] = []
    error: Optional[str] = None

