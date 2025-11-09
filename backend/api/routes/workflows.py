"""
Agent Workflow API Routes (Teammate 2).
Handles running agent pipelines for application and assessment workflows.
"""
from database import client as mongo_client  # noqa: F401
from database.repository import get_evaluation
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from services.workflows.application_pipeline import run_application_pipeline
from services.workflows.assessment_pipeline import run_assessment_pipeline
from typing import AsyncGenerator
import asyncio
import json
from datetime import datetime

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


@router.get("/workflows/{evaluation_id}/stream")
async def stream_workflow_progress(evaluation_id: str):
    """
    Stream real-time workflow progress via Server-Sent Events (SSE).
    
    Returns live agent events as they occur during evaluation execution.
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for the workflow"""
        
        print(f"[SSE] Client connected for evaluation: {evaluation_id}")
        
        # Verify evaluation exists
        evaluation = get_evaluation(evaluation_id)
        if not evaluation:
            print(f"[SSE] Evaluation not found: {evaluation_id}")
            yield f"event: workflow_error\ndata: {json.dumps({'error': 'Evaluation not found'})}\n\n"
            return
        
        print(f"[SSE] Evaluation found: {evaluation_id}, status: {evaluation.get('status')}")
        
        # Event queue to collect agent events
        event_queue = asyncio.Queue()
        
        # Immediately tell the client the stream is alive
        await event_queue.put({
            "event": "connected",
            "data": {"evaluation_id": evaluation_id},
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        def event_callback(event_type: str, data: dict):
            """Callback function passed to agents for event emission"""
            event_data = {
                "event": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            # Use put_nowait which is synchronous and thread-safe
            try:
                event_queue.put_nowait(event_data)
            except Exception as e:
                print(f"[SSE] Error queuing event: {e}")
        
        # Start workflow in background with event callback
        async def run_workflow():
            try:
                if evaluation["type"] == "application":
                    from services.workflows.application_pipeline import run_application_pipeline_async
                    await run_application_pipeline_async(evaluation_id, event_callback)
                else:
                    from services.workflows.assessment_pipeline import run_assessment_pipeline_async
                    await run_assessment_pipeline_async(evaluation_id, event_callback)
                
                # Send completion event
                await event_queue.put({
                    "event": "workflow_complete",
                    "data": {"status": "completed", "evaluation_id": evaluation_id},
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                # Send error event
                await event_queue.put({
                    "event": "workflow_error",
                    "data": {"error": str(e)},
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Start workflow task
        workflow_task = asyncio.create_task(run_workflow())
        
        # Stream events as they arrive
        try:
            event_count = 0
            while True:
                # Wait for next event (with timeout to send keepalive)
                try:
                    event = await asyncio.wait_for(event_queue.get(), timeout=15.0)
                    event_count += 1
                    
                    print(f"[SSE] Sending event #{event_count}: {event['event']}")
                    
                    # Format as SSE
                    yield f"event: {event['event']}\n"
                    yield f"data: {json.dumps(event['data'])}\n"
                    yield f"id: {event['timestamp']}\n\n"
                    
                    # If workflow completed or errored, stop streaming
                    if event['event'] in ['workflow_complete', 'workflow_error']:
                        print(f"[SSE] Workflow ended. Total events: {event_count}")
                        break
                        
                except asyncio.TimeoutError:
                    # Send keepalive comment
                    print(f"[SSE] Sending keepalive (event count: {event_count})")
                    yield ": keepalive\n\n"
                    
        except asyncio.CancelledError:
            print(f"[SSE] Client disconnected (sent {event_count} events)")
            # Client disconnected
            workflow_task.cancel()
            raise
        except Exception as e:
            print(f"[SSE] Error in event stream: {e}")
            yield f"event: workflow_error\ndata: {json.dumps({'error': str(e)})}\n\n"
    
    # Allow CORS on the stream + hard no-transform for proxies/CDN
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin",
        }
    )

