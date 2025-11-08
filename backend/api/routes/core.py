"""
Core API Routes (Teammate 1)
Handles evaluation creation, file uploads, and CRUD operations
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import json

router = APIRouter()


@router.post("/evaluations/apply")
async def create_application_evaluation(
    name: str = Form(...),
    website: str = Form(...),
    contact_email: str = Form(...),
    hq_location: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_description: Optional[str] = Form(None),
    doc_urls: Optional[str] = Form(None),  # JSON string
    docs: Optional[List[UploadFile]] = File(None)
):
    """
    Create an application-type evaluation from vendor-submitted form.
    TODO: Implement file saving and MongoDB document creation
    """
    # Parse doc_urls if provided
    doc_urls_list = []
    if doc_urls:
        try:
            doc_urls_list = json.loads(doc_urls)
        except json.JSONDecodeError:
            pass
    
    # TODO: Save files, create MongoDB document
    # For now, return a placeholder
    return {
        "id": "placeholder_id",
        "status": "pending",
        "type": "application"
    }


@router.post("/evaluations/assess")
async def create_assessment_evaluation(
    name: str = Form(...),
    use_case: str = Form(...),
    weights: str = Form(...),  # JSON string
    vendors: str = Form(...),  # JSON string
    # Files will be handled per vendor (e.g., vendor-a_docs, vendor-b_docs)
):
    """
    Create an assessment-type evaluation for comparing vendors.
    TODO: Implement multipart file handling per vendor and MongoDB document creation
    """
    # Parse JSON fields
    try:
        weights_dict = json.loads(weights)
        vendors_list = json.loads(vendors)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    # TODO: Save files per vendor, create MongoDB document
    # For now, return a placeholder
    return {
        "id": "placeholder_id",
        "status": "pending",
        "type": "assessment"
    }


@router.get("/evaluations/{evaluation_id}")
async def get_evaluation(evaluation_id: str):
    """
    Get evaluation by ID.
    TODO: Implement MongoDB query
    """
    # TODO: Query MongoDB and return evaluation document
    raise HTTPException(status_code=404, detail="Evaluation not found")


@router.get("/evaluations")
async def list_evaluations():
    """
    List all evaluations.
    TODO: Implement MongoDB query with pagination
    """
    # TODO: Query MongoDB and return list of evaluations
    return []

