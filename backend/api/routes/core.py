"""
Core API Routes (Teammate 1)
Handles evaluation creation, file uploads, and CRUD operations
"""
import json
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel, ValidationError

from database import client as mongo_client  # noqa: F401
from database.models import Evaluation, FileInfo, Vendor, Weights
from database.repository import (
    create_evaluation as repo_create_evaluation,
    get_evaluation as repo_get_evaluation,
    list_evaluations as repo_list_evaluations,
    update_evaluation as repo_update_evaluation,
    update_vendor_decision as repo_update_vendor_decision,
)
from services.file_service import save_uploaded_files

router = APIRouter()


def _parse_doc_urls(raw_value: Optional[str]) -> List[str]:
    """Parse document URLs from JSON string or comma-separated string."""
    if not raw_value:
        return []

    value = raw_value.strip()
    if not value:
        return []

    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(url).strip() for url in parsed if isinstance(url, str) and url.strip()]
        if isinstance(parsed, str):
            value = parsed
    except json.JSONDecodeError:
        # Fallback to comma-separated parsing below
        pass

    return [part.strip() for part in value.split(",") if part.strip()]


async def _persist_vendor_files(
    evaluation_id: str,
    vendor: Vendor,
    uploads: Optional[List[UploadFile]],
) -> List[FileInfo]:
    """Save vendor uploads and return file metadata."""
    if not uploads:
        return []

    try:
        saved_files = await save_uploaded_files(uploads, evaluation_id, vendor.id)
    except Exception as exc:
        repo_update_evaluation(
            evaluation_id,
            {"status": "failed", "error": f"File save failed for vendor {vendor.id}: {exc}"},
        )
        raise HTTPException(status_code=500, detail=f"Failed to save documents: {exc}") from exc

    return [FileInfo(**file_info) for file_info in saved_files]


@router.post("/evaluations/apply")
async def create_application_evaluation(
    name: str = Form(...),
    website: str = Form(...),
    contact_email: str = Form(...),
    hq_location: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_description: Optional[str] = Form(None),
    doc_urls: Optional[str] = Form(None),
    docs: Optional[List[UploadFile]] = File(None),
):
    """
    Create an application-type evaluation from vendor-submitted form.
    """
    vendor = Vendor(
        id="primary",
        name=name,
        website=website,
        contact_email=contact_email,
        hq_location=hq_location,
        product_name=product_name,
        product_description=product_description,
        doc_urls=_parse_doc_urls(doc_urls),
    )

    evaluation = Evaluation(
        type="application",
        name=name,
        vendors=[vendor],
    )

    evaluation_id = repo_create_evaluation(evaluation)

    if docs:
        vendor.files = await _persist_vendor_files(evaluation_id, vendor, docs)
        repo_update_evaluation(evaluation_id, {"vendors": [vendor.model_dump()]})

    return {
        "id": evaluation_id,
        "status": evaluation.status,
        "type": evaluation.type,
    }


@router.post("/evaluations/assess")
async def create_assessment_evaluation(
    request: Request,
    name: str = Form(...),
    use_case: str = Form(...),
    weights: str = Form(...),
    vendors: str = Form(...),
):
    """
    Create an assessment-type evaluation for comparing vendors.
    """
    try:
        weights_dict = json.loads(weights)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON for weights: {exc}") from exc

    if not isinstance(weights_dict, dict):
        raise HTTPException(status_code=400, detail="Weights payload must be a JSON object")

    try:
        weights_model = Weights(**weights_dict)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid weights payload: {exc.errors()}") from exc

    try:
        vendors_list = json.loads(vendors)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON for vendors: {exc}") from exc

    if not isinstance(vendors_list, list) or not vendors_list:
        raise HTTPException(status_code=400, detail="Vendors payload must be a non-empty array")

    form_data = await request.form()
    vendor_docs_map: Dict[str, List[UploadFile]] = {}
    vendor_doc_urls_map: Dict[str, List[str]] = {}

    for key, value in form_data.multi_items():
        if key.endswith("_docs") and isinstance(value, UploadFile):
            vendor_id = key[:-5]
            vendor_docs_map.setdefault(vendor_id, []).append(value)
        elif key.endswith("_doc_urls") and isinstance(value, str):
            vendor_id = key[:-9]
            vendor_doc_urls_map[vendor_id] = _parse_doc_urls(value)

    vendor_models: List[Vendor] = []
    for vendor_info in vendors_list:
        vendor_id = vendor_info.get("id")
        vendor_name = vendor_info.get("name")
        vendor_website = vendor_info.get("website")

        if not vendor_id or not vendor_name or not vendor_website:
            raise HTTPException(status_code=400, detail="Each vendor must include id, name, and website")

        vendor_models.append(
            Vendor(
                id=str(vendor_id),
                name=str(vendor_name),
                website=str(vendor_website),
                doc_urls=vendor_doc_urls_map.get(vendor_id, []),
            )
        )

    evaluation = Evaluation(
        type="assessment",
        name=name,
        use_case=use_case,
        weights=weights_model,
        vendors=vendor_models,
    )

    evaluation_id = repo_create_evaluation(evaluation)

    files_saved = False
    for vendor in vendor_models:
        uploads = vendor_docs_map.get(vendor.id)
        if uploads:
            vendor.files = await _persist_vendor_files(evaluation_id, vendor, uploads)
            files_saved = True

    if files_saved:
        repo_update_evaluation(
            evaluation_id,
            {"vendors": [vendor.model_dump() for vendor in vendor_models]},
        )

    return {
        "id": evaluation_id,
        "status": evaluation.status,
        "type": evaluation.type,
    }


@router.get("/evaluations/{evaluation_id}")
async def get_evaluation(evaluation_id: str):
    """
    Get evaluation by ID.
    """
    evaluation = repo_get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation


@router.get("/evaluations")
async def list_evaluations(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
):
    """
    List all evaluations with pagination.
    """
    return repo_list_evaluations(limit=limit, skip=skip)


class VendorDecisionUpdate(BaseModel):
    """Request model for updating vendor decision"""
    status: str
    notes: Optional[str] = None
    pending_actions: List[str] = []


@router.post("/evaluations/{evaluation_id}/vendors/{vendor_id}/decision")
async def set_vendor_decision(
    evaluation_id: str,
    vendor_id: str,
    update: VendorDecisionUpdate,
):
    """
    Update vendor onboarding decision status.
    Allows marking vendors as approved (with/without pending actions) or declined.
    """
    # Validate status
    valid_statuses = ["approved_pending_actions", "approved", "declined"]
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Get evaluation to validate vendor exists and check compliance
    evaluation = repo_get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    # Find vendor
    vendor = next((v for v in evaluation.get("vendors", []) if v["id"] == vendor_id), None)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found in evaluation")
    
    # Compliance gating: prevent full approval if compliance status is not "ok"
    if update.status == "approved":
        compliance = vendor.get("agent_outputs", {}).get("compliance", {})
        compliance_status = compliance.get("status", "insufficient_data")
        if compliance_status != "ok":
            raise HTTPException(
                status_code=400,
                detail="Cannot fully approve vendor with incomplete or failing compliance. Use 'approved_pending_actions' instead."
            )
    
    # Build decision object
    decision = {
        "status": update.status,
        "decided_by": None,  # Can be extended to track user when auth is added
        "decided_at": datetime.utcnow(),
        "notes": update.notes,
        "pending_actions": update.pending_actions,
    }
    
    # Update in database
    updated_evaluation = repo_update_vendor_decision(evaluation_id, vendor_id, decision)
    
    if not updated_evaluation:
        raise HTTPException(status_code=500, detail="Failed to update vendor decision")
    
    # Optionally update evaluation status to "finalized" if any vendor is approved/approved_pending_actions
    vendors = updated_evaluation.get("vendors", [])
    any_approved = any(
        v.get("decision", {}).get("status") in ["approved", "approved_pending_actions"]
        for v in vendors
    )
    
    if any_approved and updated_evaluation.get("status") == "completed":
        repo_update_evaluation(evaluation_id, {"status": "finalized"})
        updated_evaluation["status"] = "finalized"
    
    return updated_evaluation

