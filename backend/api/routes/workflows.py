"""
Agent Workflow API Routes (Teammate 2).
Handles running agent pipelines for application and assessment workflows.
"""
from database import client as mongo_client  # noqa: F401
from fastapi import APIRouter, BackgroundTasks, HTTPException
from services.workflows.application_pipeline import run_application_pipeline
from services.workflows.assessment_pipeline import run_assessment_pipeline

router = APIRouter()


@router.post("/workflows/application/{evaluation_id}/run")
def run_application_workflow_endpoint(evaluation_id: str, background_tasks: BackgroundTasks):
    """
    Run the application workflow pipeline.
    Executes the multi-agent evaluation pipeline for a single vendor application.
    """
    try:
        # Run pipeline in background (for MVP, we run synchronously for simplicity)
        # In production, you'd use background_tasks.add_task(run_application_pipeline, evaluation_id)
        result = run_application_pipeline(evaluation_id)
        
        return {
            "id": evaluation_id,
            "type": "application",
            "status": result.get("status", "running"),
            "message": "Application pipeline completed successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error in application workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@router.post("/workflows/assessment/{evaluation_id}/run")
def run_assessment_workflow_endpoint(evaluation_id: str, background_tasks: BackgroundTasks):
    """
    Run the assessment workflow pipeline.
    Executes the multi-agent comparison pipeline for multiple vendors.
    """
    try:
        # Run pipeline in background (for MVP, we run synchronously)
        result = run_assessment_pipeline(evaluation_id)
        
        return {
            "id": evaluation_id,
            "type": "assessment",
            "status": result.get("status", "running"),
            "message": "Assessment pipeline completed successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error in assessment workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

