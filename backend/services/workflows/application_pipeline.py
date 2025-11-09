"""
Application Workflow Pipeline
Orchestrates all agents for vendor application workflow
"""
from typing import Dict, Any
from database.repository import get_evaluation, update_evaluation
from services.agents.intake_agent import IntakeAgent
from services.agents.verification_agent import VerificationAgent
from services.agents.compliance_agent import ComplianceAgent
from services.agents.interoperability_agent import InteroperabilityAgent
from services.agents.finance_agent import FinanceAgent
from services.agents.adoption_agent import AdoptionAgent
from services.agents.summary_agent import SummaryAgent


def run_application_pipeline(evaluation_id: str) -> Dict[str, Any]:
    """
    Run the complete application workflow pipeline.
    Executes agents sequentially in a ReAct-like pattern.
    """
    print(f"\n{'='*60}")
    print(f"Starting Application Pipeline for Evaluation: {evaluation_id}")
    print(f"{'='*60}\n")
    
    # Load evaluation
    evaluation = get_evaluation(evaluation_id)
    if not evaluation:
        raise ValueError(f"Evaluation {evaluation_id} not found")
    
    if evaluation["type"] != "application":
        raise ValueError(f"Evaluation {evaluation_id} is not an application type")
    
    # Update status to running
    update_evaluation(evaluation_id, {"status": "running"})
    
    try:
        # Get vendor (should be first vendor for application workflow)
        vendor = evaluation["vendors"][0] if evaluation["vendors"] else None
        if not vendor:
            raise ValueError("No vendor found in evaluation")
        
        company_name = vendor.get("name", "Unknown")
        print(f"Evaluating vendor: {company_name}\n")
        
        # Initialize agents
        agents = {
            "intake": IntakeAgent(),
            "verification": VerificationAgent(),
            "compliance": ComplianceAgent(),
            "interoperability": InteroperabilityAgent(),
            "finance": FinanceAgent(),
            "adoption": AdoptionAgent()
        }
        
        # Agent outputs storage
        agent_outputs = {}
        
        # Build initial context
        context = {
            "vendor": vendor,
            "evaluation": evaluation
        }
        
        # Run agents sequentially (ReAct pattern: Reason → Act → Observe)
        print("Executing agent pipeline...\n")
        
        # 1. Intake Agent
        print("[1/6] Running Intake Agent...")
        agent_outputs["intake"] = agents["intake"].execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        # 2. Verification Agent
        print("[2/6] Running Verification Agent...")
        agent_outputs["verification"] = agents["verification"].execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        # 3. Compliance Agent (with RAG)
        print("[3/6] Running Compliance Agent (with RAG)...")
        agent_outputs["compliance"] = agents["compliance"].execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        # 4. Interoperability Agent
        print("[4/6] Running Interoperability Agent...")
        agent_outputs["interoperability"] = agents["interoperability"].execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        # 5. Finance Agent
        print("[5/6] Running Finance Agent...")
        agent_outputs["finance"] = agents["finance"].execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        # 6. Adoption Agent
        print("[6/6] Running Adoption Agent...")
        agent_outputs["adoption"] = agents["adoption"].execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        # Calculate total score (average of dimension scores)
        scores = [
            agent_outputs.get("compliance", {}).get("score", 0),
            agent_outputs.get("interoperability", {}).get("score", 0),
            agent_outputs.get("finance", {}).get("score", 0),
            agent_outputs.get("adoption", {}).get("score", 0)
        ]
        total_score = sum(scores) / len(scores) if scores else 0
        
        print(f"\n Dimension scores calculated: {total_score:.2f}/5")
        
        # 7. Summary Agent (aggregates all outputs)
        print("[7/7] Running Summary Agent...")
        summary_agent = SummaryAgent()
        summary_output = summary_agent.execute(context)
        
        # Prepare update data
        update_data = {
            "status": "completed",
            "vendors": [{
                **vendor,
                "agent_outputs": agent_outputs,
                "total_score": round(total_score, 2)
            }],
            "onboarding_checklist": summary_output.get("onboarding_checklist", [])
        }
        
        # Add recommendation if this is for a single vendor
        update_data["recommendation"] = {
            "vendor_id": vendor.get("id", "vendor-1"),
            "reason": summary_output.get("recommendation", "Evaluation completed")
        }
        
        # Update MongoDB
        update_evaluation(evaluation_id, update_data)
        
        print(f"\n{'='*60}")
        print(f"Pipeline Complete!")
        print(f"Final Score: {total_score:.2f}/5")
        print(f"Recommendation: {summary_output.get('recommendation', 'N/A')}")
        print(f"{'='*60}\n")
        
        return {
            "status": "completed",
            "total_score": total_score,
            "recommendation": summary_output.get("recommendation")
        }
    
    except Exception as e:
        # Update status to failed
        print(f"\n❌ Pipeline failed: {str(e)}\n")
        update_evaluation(evaluation_id, {
            "status": "failed",
            "error": str(e)
        })
        raise


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
        # Get vendor
        vendor = evaluation["vendors"][0] if evaluation["vendors"] else None
        if not vendor:
            raise ValueError("No vendor found in evaluation")
        
        company_name = vendor.get("name", "Unknown")
        print(f"Evaluating vendor: {company_name}\n")
        
        # Initialize agents with event callback
        intake = IntakeAgent(event_callback=event_callback)
        verification = VerificationAgent(event_callback=event_callback)
        compliance = ComplianceAgent(event_callback=event_callback)
        interop = InteroperabilityAgent(event_callback=event_callback)
        finance = FinanceAgent(event_callback=event_callback)
        adoption = AdoptionAgent(event_callback=event_callback)
        summary = SummaryAgent(event_callback=event_callback)
        
        # Agent outputs storage
        agent_outputs = {}
        
        # Build initial context
        context = {
            "vendor": vendor,
            "evaluation": evaluation
        }
        
        # Execute pipeline
        print("Executing agent pipeline...\n")
        
        print("[1/6] Running Intake Agent...")
        agent_outputs["intake"] = intake.execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        print("[2/6] Running Verification Agent...")
        agent_outputs["verification"] = verification.execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        print("[3/6] Running Compliance Agent (with RAG)...")
        agent_outputs["compliance"] = await compliance.execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        print("[4/6] Running Interoperability Agent...")
        agent_outputs["interoperability"] = await interop.execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        print("[5/6] Running Finance Agent...")
        agent_outputs["finance"] = await finance.execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        print("[6/6] Running Adoption Agent...")
        agent_outputs["adoption"] = await adoption.execute(context)
        context["vendor"]["agent_outputs"] = agent_outputs
        
        # Calculate total score
        scores = [
            agent_outputs.get("compliance", {}).get("score", 0.0),
            agent_outputs.get("interoperability", {}).get("score", 0.0),
            agent_outputs.get("finance", {}).get("score", 0.0),
            agent_outputs.get("adoption", {}).get("score", 0.0)
        ]
        total_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        
        print(f"\n✅ Dimension scores calculated: {total_score:.2f}/5")
        
        # Summary Agent
        print("[7/7] Running Summary Agent...")
        summary_output = summary.execute(context)
        
        # Update vendor with results
        update_data = {
            "status": "completed",
            "vendors": [{
                **vendor,
                "agent_outputs": agent_outputs,
                "total_score": total_score
            }],
            "onboarding_checklist": summary_output.get("onboarding_checklist", []),
            "recommendation": {
                "vendor_id": vendor.get("id", "vendor-1"),
                "reason": summary_output.get("recommendation", "Evaluation completed")
            }
        }
        
        update_evaluation(evaluation_id, update_data)
        
        print(f"\n{'='*60}\nApplication Pipeline Complete!\nFinal Score: {total_score:.2f}/5\n{'='*60}\n")
        
        return {"status": "completed", "total_score": total_score}
        
    except Exception as e:
        print(f"\n❌ Application pipeline failed: {str(e)}\n")
        update_evaluation(evaluation_id, {"status": "failed", "error": str(e)})
        if event_callback:
            event_callback("workflow_error", {"error": str(e)})
        raise

