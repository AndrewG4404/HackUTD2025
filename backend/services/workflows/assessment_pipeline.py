"""
Assessment Workflow Pipeline
Orchestrates agents for vendor assessment and comparison workflow
"""
from typing import Dict, Any
from database.repository import get_evaluation, update_evaluation
from services.agents.compliance_agent import ComplianceAgent
from services.agents.interoperability_agent import InteroperabilityAgent
from services.agents.finance_agent import FinanceAgent
from services.agents.adoption_agent import AdoptionAgent


def run_assessment_pipeline(evaluation_id: str) -> Dict[str, Any]:
    """
    Run the complete assessment workflow pipeline.
    Evaluates multiple vendors and provides weighted comparison.
    """
    print(f"\n{'='*60}")
    print(f"Starting Assessment Pipeline: {evaluation_id}")
    print(f"{'='*60}\n")
    
    # Load evaluation
    evaluation = get_evaluation(evaluation_id)
    if not evaluation:
        raise ValueError(f"Evaluation {evaluation_id} not found")
    
    if evaluation["type"] != "assessment":
        raise ValueError(f"Evaluation {evaluation_id} is not an assessment type")
    
    # Update status to running
    update_evaluation(evaluation_id, {"status": "running"})
    
    # Get weights (default to 3 if not provided)
    weights = evaluation.get("weights") or {
        "security": 3,
        "cost": 3,
        "interoperability": 3,
        "adoption": 3
    }
    
    try:
        # Initialize agents (reuse same agents for all vendors)
        agents = {
            "compliance": ComplianceAgent(),
            "interoperability": InteroperabilityAgent(),
            "finance": FinanceAgent(),
            "adoption": AdoptionAgent()
        }
        
        scored_vendors = []
        updated_vendors = []
        
        # Evaluate each vendor
        for vendor in evaluation.get("vendors", []):
            print(f"\n[Assessment] Evaluating vendor: {vendor.get('name', 'Unknown')}")
            
            context = {
                "vendor": vendor,
                "evaluation": evaluation
            }
            
            # Run agents for this vendor
            agent_outputs = {}
            
            print(f"  [1/4] Running Compliance Agent...")
            agent_outputs["compliance"] = agents["compliance"].execute(context)
            
            print(f"  [2/4] Running Interoperability Agent...")
            agent_outputs["interoperability"] = agents["interoperability"].execute(context)
            
            print(f"  [3/4] Running Finance Agent...")
            agent_outputs["finance"] = agents["finance"].execute(context)
            
            print(f"  [4/4] Running Adoption Agent...")
            agent_outputs["adoption"] = agents["adoption"].execute(context)
            
            # Calculate weighted score
            # Map: security=compliance, cost=finance, interoperability, adoption
            compliance_score = agent_outputs["compliance"].get("score", 0.0)
            finance_score = agent_outputs["finance"].get("score", 0.0)
            interop_score = agent_outputs["interoperability"].get("score", 0.0)
            adoption_score = agent_outputs["adoption"].get("score", 0.0)
            
            # Weighted average
            weight_sum = sum([
                weights["security"],
                weights["cost"],
                weights["interoperability"],
                weights["adoption"]
            ]) or 1
            
            weighted_score = (
                compliance_score * weights["security"] +
                finance_score * weights["cost"] +
                interop_score * weights["interoperability"] +
                adoption_score * weights["adoption"]
            ) / weight_sum
            
            print(f"  Weighted Score: {weighted_score:.2f}/5.0")
            
            # Update vendor data
            updated_vendors.append({
                **vendor,
                "agent_outputs": agent_outputs,
                "total_score": round(weighted_score, 2)
            })
            
            scored_vendors.append((vendor["id"], weighted_score, vendor.get("name", "Unknown")))
        
        # Select best vendor
        if scored_vendors:
            best_id, best_score, best_name = max(scored_vendors, key=lambda x: x[1])
            recommendation = {
                "vendor_id": best_id,
                "reason": f"{best_name} achieved the highest weighted score of {best_score:.2f}/5.0 based on your priorities"
            }
        else:
            recommendation = {
                "vendor_id": "",
                "reason": "No vendors evaluated"
            }
        
        # Generate simple onboarding checklist
        onboarding_checklist = [
            f"Review detailed evaluation results for {recommendation.get('vendor_id', 'selected vendor')}",
            "Schedule technical integration discussion",
            "Request security questionnaire and certifications",
            "Negotiate contract terms and pricing",
            "Plan implementation timeline"
        ]
        
        # Update evaluation with results
        update_evaluation(evaluation_id, {
            "status": "completed",
            "vendors": updated_vendors,
            "recommendation": recommendation,
            "onboarding_checklist": onboarding_checklist
        })
        
        print(f"\n{'='*60}")
        print(f"Assessment Complete!")
        print(f"Recommended Vendor: {recommendation['vendor_id']} ({best_score:.2f}/5.0)")
        print(f"{'='*60}\n")
        
        return {
            "status": "completed",
            "recommended": recommendation["vendor_id"],
            "score": best_score if scored_vendors else 0.0
        }
    
    except Exception as e:
        # Update status to failed
        print(f"\n❌ Assessment pipeline failed: {str(e)}\n")
        update_evaluation(evaluation_id, {
            "status": "failed",
            "error": str(e)
        })
        raise

