# Backend SSE Implementation Guide

## Overview

This guide provides step-by-step instructions to implement **Server-Sent Events (SSE)** for real-time agentic workflow visualization in the VendorLens backend.

## 🎯 What We're Building

An SSE endpoint (`GET /api/workflows/{evaluation_id}/stream`) that streams live agent progress events to the frontend, including:
- Agent start/completion notifications
- Real-time LLM reasoning outputs
- Document discovery progress
- Multi-step search hops
- Score calculations and findings

---

## 📋 Prerequisites

- Backend running with all agents implemented
- MongoDB connection configured
- Nemotron API configured and working

---

## 🔧 Step 1: Add SSE Route to FastAPI

### File: `backend/api/routes/workflows.py`

Add the SSE streaming endpoint at the **end of the file** (after existing workflow routes):

```python
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json

@router.get("/workflows/{evaluation_id}/stream")
async def stream_workflow_progress(evaluation_id: str):
    """
    Stream real-time workflow progress via Server-Sent Events (SSE).
    
    Returns live agent events as they occur during evaluation execution.
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for the workflow"""
        
        # Verify evaluation exists
        evaluation = get_evaluation(evaluation_id)
        if not evaluation:
            yield f"event: workflow_error\ndata: {json.dumps({'error': 'Evaluation not found'})}\n\n"
            return
        
        # Event queue to collect agent events
        event_queue = asyncio.Queue()
        
        def event_callback(event_type: str, data: dict):
            """Callback function passed to agents for event emission"""
            asyncio.create_task(event_queue.put({
                "event": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }))
        
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
            while True:
                # Wait for next event (with timeout to send keepalive)
                try:
                    event = await asyncio.wait_for(event_queue.get(), timeout=15.0)
                    
                    # Format as SSE
                    yield f"event: {event['event']}\n"
                    yield f"data: {json.dumps(event['data'])}\n"
                    yield f"id: {event['timestamp']}\n\n"
                    
                    # If workflow completed or errored, stop streaming
                    if event['event'] in ['workflow_complete', 'workflow_error']:
                        break
                        
                except asyncio.TimeoutError:
                    # Send keepalive comment
                    yield ": keepalive\n\n"
                    
        except asyncio.CancelledError:
            # Client disconnected
            workflow_task.cancel()
            raise
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
```

---

## 🔧 Step 2: Create Async Pipeline Wrappers

The current pipelines are synchronous. We need async wrappers that accept event callbacks.

### File: `backend/services/workflows/application_pipeline.py`

Add this **at the end** of the file:

```python
async def run_application_pipeline_async(evaluation_id: str, event_callback=None):
    """
    Async wrapper for application pipeline with event streaming.
    
    Args:
        evaluation_id: The evaluation ID
        event_callback: Optional callback function(event_type: str, data: dict)
    """
    print(f"\n{'='*60}\nStarting Application Pipeline (Async): {evaluation_id}\n{'='*60}\n")
    
    evaluation = get_evaluation(evaluation_id)
    if not evaluation:
        raise ValueError(f"Evaluation {evaluation_id} not found")
    
    if evaluation["type"] != "application":
        raise ValueError(f"Evaluation {evaluation_id} is not an application type")
    
    # Emit workflow start
    if event_callback:
        event_callback("workflow_start", {
            "evaluation_id": evaluation_id,
            "type": "application",
            "vendor": evaluation["vendors"][0]["name"]
        })
    
    update_evaluation(evaluation_id, {"status": "running"})
    
    try:
        # Initialize agents with event callback
        intake = IntakeAgent(event_callback=event_callback)
        verification = VerificationAgent(event_callback=event_callback)
        compliance = ComplianceAgent(event_callback=event_callback)
        interop = InteroperabilityAgent(event_callback=event_callback)
        finance = FinanceAgent(event_callback=event_callback)
        adoption = AdoptionAgent(event_callback=event_callback)
        summary = SummaryAgent(event_callback=event_callback)
        
        # Execute pipeline
        context = {"evaluation": evaluation}
        
        context = intake.execute(context)
        context = verification.execute(context)
        context = compliance.execute(context)
        context = interop.execute(context)
        context = finance.execute(context)
        context = adoption.execute(context)
        final_context = summary.execute(context)
        
        # Calculate total score
        agent_outputs = final_context.get("agent_outputs", {})
        scores = [
            agent_outputs.get("compliance", {}).get("score", 0.0),
            agent_outputs.get("interoperability", {}).get("score", 0.0),
            agent_outputs.get("finance", {}).get("score", 0.0),
            agent_outputs.get("adoption", {}).get("score", 0.0)
        ]
        total_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        
        # Update vendor with results
        vendor = evaluation["vendors"][0]
        vendor["agent_outputs"] = agent_outputs
        vendor["total_score"] = total_score
        
        update_evaluation(evaluation_id, {
            "status": "completed",
            "vendors": [vendor],
            "recommendation": final_context.get("recommendation", {}),
            "onboarding_checklist": final_context.get("onboarding_checklist", [])
        })
        
        print(f"\n✅ Application Pipeline Complete. Total Score: {total_score}\n")
        return {"status": "completed", "total_score": total_score}
        
    except Exception as e:
        print(f"\n❌ Application pipeline failed: {str(e)}\n")
        update_evaluation(evaluation_id, {"status": "failed", "error": str(e)})
        if event_callback:
            event_callback("workflow_error", {"error": str(e)})
        raise
```

### File: `backend/services/workflows/assessment_pipeline.py`

Add this **at the end** of the file:

```python
async def run_assessment_pipeline_async(evaluation_id: str, event_callback=None):
    """
    Async wrapper for assessment pipeline with event streaming.
    
    Args:
        evaluation_id: The evaluation ID
        event_callback: Optional callback function(event_type: str, data: dict)
    """
    print(f"\n{'='*60}\nStarting Assessment Pipeline (Async): {evaluation_id}\n{'='*60}\n")
    
    evaluation = get_evaluation(evaluation_id)
    if not evaluation:
        raise ValueError(f"Evaluation {evaluation_id} not found")
    
    if evaluation["type"] != "assessment":
        raise ValueError(f"Evaluation {evaluation_id} is not an assessment type")
    
    # Emit workflow start
    if event_callback:
        event_callback("workflow_start", {
            "evaluation_id": evaluation_id,
            "type": "assessment",
            "vendor_count": len(evaluation.get("vendors", []))
        })
    
    update_evaluation(evaluation_id, {"status": "running"})
    
    weights = evaluation.get("weights") or {"security": 3, "cost": 3, "interoperability": 3, "adoption": 3}
    
    try:
        # Initialize agents with event callback
        agents = {
            "compliance": ComplianceAgent(event_callback=event_callback),
            "interoperability": InteroperabilityAgent(event_callback=event_callback),
            "finance": FinanceAgent(event_callback=event_callback),
            "adoption": AdoptionAgent(event_callback=event_callback)
        }
        
        scored_vendors = []
        updated_vendors = []
        
        for idx, vendor in enumerate(evaluation.get("vendors", [])):
            if event_callback:
                event_callback("vendor_start", {
                    "vendor_id": vendor["id"],
                    "vendor_name": vendor["name"],
                    "index": idx + 1,
                    "total": len(evaluation["vendors"])
                })
            
            ctx = {"vendor": vendor, "evaluation": evaluation}
            agent_outputs = {}
            
            agent_outputs["compliance"] = agents["compliance"].execute(ctx)
            agent_outputs["interoperability"] = agents["interoperability"].execute(ctx)
            agent_outputs["finance"] = agents["finance"].execute(ctx)
            agent_outputs["adoption"] = agents["adoption"].execute(ctx)
            
            # Calculate weighted score
            s = agent_outputs["compliance"].get("score", 0.0)
            c = agent_outputs["finance"].get("score", 0.0)
            i = agent_outputs["interoperability"].get("score", 0.0)
            a = agent_outputs["adoption"].get("score", 0.0)
            w_sum = sum([weights["security"], weights["cost"], weights["interoperability"], weights["adoption"]]) or 1
            weighted = (s*weights["security"] + c*weights["cost"] + i*weights["interoperability"] + a*weights["adoption"]) / w_sum
            
            updated_vendors.append({
                **vendor,
                "agent_outputs": agent_outputs,
                "total_score": round(weighted, 2)
            })
            scored_vendors.append((vendor["id"], weighted))
            
            if event_callback:
                event_callback("vendor_complete", {
                    "vendor_id": vendor["id"],
                    "vendor_name": vendor["name"],
                    "total_score": round(weighted, 2)
                })
        
        # Pick best vendor
        best_id, best_score = max(scored_vendors, key=lambda x: x[1]) if scored_vendors else ("", 0.0)
        recommendation = {"vendor_id": best_id, "reason": f"Highest weighted score: {best_score:.2f}"}
        
        update_evaluation(evaluation_id, {
            "status": "completed",
            "vendors": updated_vendors,
            "recommendation": recommendation,
            "onboarding_checklist": []
        })
        
        print(f"Assessment Complete. Recommended: {best_id} ({best_score:.2f})")
        return {"status": "completed", "recommended": best_id, "score": best_score}
        
    except Exception as e:
        print(f"\n❌ Assessment pipeline failed: {str(e)}\n")
        update_evaluation(evaluation_id, {"status": "failed", "error": str(e)})
        if event_callback:
            event_callback("workflow_error", {"error": str(e)})
        raise
```

---

## 🔧 Step 3: Update Agent Base Class (Already Done!)

The `BaseAgent` class already has `emit_event()` method and event callback support from the enhanced RAG implementation. No changes needed here.

All agents (Compliance, Interoperability, Finance, Adoption, Intake, Verification, Summary) already emit events:
- `agent_start`: When agent begins execution
- `agent_thinking`: When LLM is analyzing
- `agent_progress`: During multi-step searches
- `agent_complete`: When agent finishes

---

## 📊 Step 4: Event Format Reference

### Event Types

**1. `workflow_start`**
```json
{
  "evaluation_id": "673abc...",
  "type": "application",
  "vendor": "ServiceNow"
}
```

**2. `agent_start`**
```json
{
  "agent": "ComplianceAgent",
  "status": "starting"
}
```

**3. `agent_thinking`**
```json
{
  "agent": "ComplianceAgent",
  "action": "Analyzing certifications with LLM",
  "context": "Found 3 sources (2 official, 1 third-party)"
}
```

**4. `agent_progress`**
```json
{
  "agent": "ComplianceAgent",
  "message": "Discovered 2 documentation URLs",
  "details": {
    "query": "ServiceNow SOC2 ISO27001",
    "urls_found": 2,
    "hop": 1
  }
}
```

**5. `agent_complete`**
```json
{
  "agent": "ComplianceAgent",
  "status": "completed",
  "score": 8.5,
  "source_count": 5,
  "confidence": "high"
}
```

**6. `vendor_start` (Assessment only)**
```json
{
  "vendor_id": "vendor-a",
  "vendor_name": "ServiceNow",
  "index": 1,
  "total": 2
}
```

**7. `vendor_complete` (Assessment only)**
```json
{
  "vendor_id": "vendor-a",
  "vendor_name": "ServiceNow",
  "total_score": 8.2
}
```

**8. `workflow_complete`**
```json
{
  "status": "completed",
  "evaluation_id": "673abc..."
}
```

**9. `workflow_error`**
```json
{
  "error": "Failed to fetch documentation: Connection timeout"
}
```

---

## 🧪 Step 5: Testing

### Test with cURL

```bash
# Start an evaluation first
EVAL_ID=$(curl -X POST http://localhost:8000/api/evaluations/apply \
  -F "name=ServiceNow" \
  -F "website=https://www.servicenow.com" \
  -F "contact_email=dev@servicenow.com" | jq -r '.id')

# Start workflow in background
curl -X POST "http://localhost:8000/api/workflows/application/${EVAL_ID}/run" &

# Stream live events (in separate terminal)
curl -N -H "Accept: text/event-stream" \
  "http://localhost:8000/api/workflows/${EVAL_ID}/stream"
```

### Expected Output

```
event: workflow_start
data: {"evaluation_id":"673abc...","type":"application","vendor":"ServiceNow"}
id: 2025-11-09T12:34:56.123Z

event: agent_start
data: {"agent":"IntakeAgent","status":"starting"}
id: 2025-11-09T12:34:56.456Z

event: agent_complete
data: {"agent":"IntakeAgent","status":"completed"}
id: 2025-11-09T12:34:57.789Z

event: agent_start
data: {"agent":"ComplianceAgent","status":"starting"}
id: 2025-11-09T12:34:58.012Z

event: agent_progress
data: {"agent":"ComplianceAgent","message":"Discovered 2 documentation URLs","details":{"query":"ServiceNow SOC2","urls_found":2,"hop":1}}
id: 2025-11-09T12:35:01.234Z

event: agent_thinking
data: {"agent":"ComplianceAgent","action":"Analyzing certifications with LLM"}
id: 2025-11-09T12:35:05.567Z

event: agent_complete
data: {"agent":"ComplianceAgent","status":"completed","score":8.5,"source_count":5,"confidence":"high"}
id: 2025-11-09T12:35:10.890Z

... (more events)

event: workflow_complete
data: {"status":"completed","evaluation_id":"673abc..."}
id: 2025-11-09T12:36:45.123Z
```

---

## 🔒 Error Handling

### Connection Loss
- If client disconnects, `asyncio.CancelledError` is raised
- Workflow task is cancelled to prevent orphaned processing

### Evaluation Not Found
```
event: workflow_error
data: {"error": "Evaluation not found"}
```

### Agent Failure
```
event: workflow_error
data: {"error": "ComplianceAgent failed: Connection timeout"}
```

---

## 📝 Notes

1. **Keepalive**: Every 15 seconds, send `: keepalive\n\n` to prevent connection timeout
2. **Buffering**: Set `X-Accel-Buffering: no` header to disable nginx buffering
3. **CORS**: Ensure CORS headers allow `text/event-stream` from frontend origin
4. **Async Context**: The workflow runs in an async task; events are collected via queue
5. **Event Order**: Events are guaranteed to be in chronological order (single queue)

---

## ✅ Verification Checklist

- [ ] SSE endpoint added to `workflows.py`
- [ ] Async pipeline wrappers created
- [ ] Agents emit events via `event_callback`
- [ ] Event format matches spec (event type + data + id)
- [ ] Keepalive prevents timeout
- [ ] Error events sent on failure
- [ ] Tested with cURL
- [ ] Frontend can connect and receive events

---

## 🚀 Next Steps

Once backend is complete, proceed to **FRONTEND_SSE_GUIDE.md** to implement the live visualization UI.

