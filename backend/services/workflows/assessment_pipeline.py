"""
Assessment Workflow Pipeline
Orchestrates agents for vendor assessment and comparison workflow
"""
from typing import Dict, Any, List
from database.repository import get_evaluation, update_evaluation
from services.agents.requirement_profile_agent import RequirementProfileAgent
from services.agents.compliance_agent import ComplianceAgent
from services.agents.interoperability_agent import InteroperabilityAgent
from services.agents.finance_agent import FinanceAgent
from services.agents.adoption_agent import AdoptionAgent
from services.agents.comparison_analysis_agent import ComparisonAnalysisAgent


def generate_contextual_checklist(
    analysis: Dict[str, Any],
    vendors: List[Dict[str, Any]],
    requirement_profile: Dict[str, Any],
    recommended_vendor_id: str
) -> List[str]:
    """
    Generate a contextual onboarding checklist based on actual risks and gaps found.
    
    Args:
        analysis: The detailed analysis from ComparisonAnalysisAgent
        vendors: List of vendor dictionaries with agent_outputs
        requirement_profile: The requirement profile with use case details
        recommended_vendor_id: ID of recommended vendor (or empty if none)
    
    Returns:
        List of specific, actionable checklist items
    """
    checklist = []
    
    # Find the recommended vendor
    recommended_vendor = None
    if recommended_vendor_id:
        for v in vendors:
            if v.get("id") == recommended_vendor_id:
                recommended_vendor = v
                break
    
    # If no clear recommendation (insufficient data case)
    if not recommended_vendor_id or not recommended_vendor:
        # Focus on getting basic data
        checklist.append(
            "Request formal security & compliance pack from each vendor (SOC 2 Type II, ISO 27001, DPA, data retention policies)"
        )
        for v in vendors:
            comp = v.get("agent_outputs", {}).get("compliance", {})
            if comp.get("confidence") == "low":
                checklist.append(
                    f"Obtain complete compliance documentation from {v.get('name', 'vendor')} before any further evaluation"
                )
        checklist.append(
            "Re-evaluate all vendors once official documentation is obtained"
        )
        return checklist[:5]  # Cap at 5 items
    
    # For recommended vendor, generate specific items based on findings
    vendor_name = recommended_vendor.get("name", "selected vendor")
    agent_outputs = recommended_vendor.get("agent_outputs", {})
    
    # Always start with review
    checklist.append(f"Review comprehensive risk analysis for {vendor_name}")
    
    # Compliance-specific items
    compliance = agent_outputs.get("compliance", {})
    comp_risks = compliance.get("risks", [])
    if comp_risks:
        if any("not verified" in r.lower() or "not accessible" in r.lower() for r in comp_risks):
            checklist.append(
                f"Request and validate security attestations from {vendor_name} (SOC 2 Type II, ISO 27001, penetration test reports)"
            )
        if any("data retention" in r.lower() or "deletion" in r.lower() for r in comp_risks):
            checklist.append(
                f"Negotiate and document data ownership, retention, and deletion terms in Data Processing Agreement"
            )
    
    # Interoperability-specific items
    interop = agent_outputs.get("interoperability", {})
    interop_risks = interop.get("risks", [])
    integration_targets = requirement_profile.get("integration_targets", [])
    
    if integration_targets:
        # Check if specific integrations were mentioned as gaps
        for target in integration_targets[:2]:  # Top 2 integration requirements
            if any(target.lower() in r.lower() for r in interop_risks):
                checklist.append(
                    f"Conduct technical workshop with {vendor_name} to validate {target} integration and develop implementation plan"
                )
    
    if "API" in str(interop_risks) or "documentation" in str(interop_risks).lower():
        checklist.append(
            f"Request API documentation, rate limits, and SLAs from {vendor_name}; prototype critical integration flows"
        )
    
    # Finance-specific items
    finance = agent_outputs.get("finance", {})
    if finance.get("confidence") == "low":
        checklist.append(
            f"Obtain formal pricing quote from {vendor_name} with breakdown of licensing, implementation, training, and support costs"
        )
    
    # Adoption-specific items
    adoption = agent_outputs.get("adoption", {})
    if adoption.get("score", 0) < 3.0:
        checklist.append(
            f"Define change management and training plan; request {vendor_name} customer success program details and implementation timeline"
        )
    
    # Always end with implementation planning
    if "Plan phased implementation" not in " ".join(checklist):
        checklist.append(
            "Design phased rollout with pilot team, success metrics, and final cut-over plan"
        )
    
    return checklist[:6]  # Cap at 6 items to keep it actionable


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
    
    try:
        # Step 1: Generate requirement profile (infers dimension_importance from use case)
        print(f"[0/5] Running Requirement Profile Agent...")
        requirement_agent = RequirementProfileAgent()
        requirement_profile = requirement_agent.execute({"evaluation": evaluation})
        
        # Update evaluation with requirement profile
        update_evaluation(evaluation_id, {"requirement_profile": requirement_profile})
        evaluation["requirement_profile"] = requirement_profile
        
        # Use inferred dimension importance instead of UI sliders
        dimension_importance = requirement_profile.get("dimension_importance", {
            "security": 3,
            "cost": 3,
            "interoperability": 3,
            "adoption": 3
        })
        
        print(f"  Using inferred priorities: Security={dimension_importance['security']}, "
              f"Cost={dimension_importance['cost']}, Interoperability={dimension_importance['interoperability']}, "
              f"Adoption={dimension_importance['adoption']}")
        
        # Initialize vendor-specific agents (reuse same agents for all vendors)
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
            
            # Calculate weighted score using inferred dimension importance
            # Handle None scores (insufficient data) by excluding them from average
            compliance_score = agent_outputs["compliance"].get("score")
            finance_score = agent_outputs["finance"].get("score")
            interop_score = agent_outputs["interoperability"].get("score")
            adoption_score = agent_outputs["adoption"].get("score")
            
            # Build list of (score, weight) pairs, excluding None scores
            scored_dimensions = []
            if compliance_score is not None:
                scored_dimensions.append((compliance_score, dimension_importance["security"]))
            if finance_score is not None:
                scored_dimensions.append((finance_score, dimension_importance["cost"]))
            if interop_score is not None:
                scored_dimensions.append((interop_score, dimension_importance["interoperability"]))
            if adoption_score is not None:
                scored_dimensions.append((adoption_score, dimension_importance["adoption"]))
            
            # Calculate weighted average (or None if all dimensions have insufficient data)
            if scored_dimensions:
                total_weighted = sum(score * weight for score, weight in scored_dimensions)
                total_weight = sum(weight for _, weight in scored_dimensions)
                if total_weight > 0:
                    weighted_score = total_weighted / total_weight
                else:
                    # All weights are 0, use simple average
                    weighted_score = sum(score for score, _ in scored_dimensions) / len(scored_dimensions)
            else:
                weighted_score = None
            
            if weighted_score is not None:
                print(f"  Weighted Score: {weighted_score:.2f}/5.0")
            else:
                print(f"  Weighted Score: N/A (insufficient data for all dimensions)")
            
            # Update vendor data
            updated_vendors.append({
                **vendor,
                "agent_outputs": agent_outputs,
                "total_score": round(weighted_score, 2) if weighted_score is not None else None
            })
            
            scored_vendors.append((vendor["id"], weighted_score if weighted_score is not None else 0.0, vendor.get("name", "Unknown")))
        
        # Update evaluation with vendor scores before running comparison
        update_evaluation(evaluation_id, {"vendors": updated_vendors})
        evaluation["vendors"] = updated_vendors
        
        # Step 2: Generate Goldman-style detailed analysis
        print(f"\n[5/5] Running Comparison Analysis Agent...")
        comparison_agent = ComparisonAnalysisAgent()
        analysis = comparison_agent.execute({"evaluation": evaluation})
        
        # Extract recommendation from analysis
        final_rec = analysis.get("final_recommendation", {})
        recommendation = {
            "vendor_id": final_rec.get("recommended_vendor_id", ""),
            "reason": final_rec.get("short_reason", "No recommendation available")
        }
        
        # Generate contextual onboarding checklist based on actual findings
        onboarding_checklist = generate_contextual_checklist(
            analysis=analysis,
            vendors=updated_vendors,
            requirement_profile=requirement_profile,
            recommended_vendor_id=final_rec.get("recommended_vendor_id", "")
        )
        
        # Update evaluation with final results including detailed analysis
        update_evaluation(evaluation_id, {
            "status": "completed",
            "vendors": updated_vendors,
            "recommendation": recommendation,
            "analysis": analysis,
            "onboarding_checklist": onboarding_checklist
        })
        
        # Get best score for logging
        best_score = max([s[1] for s in scored_vendors]) if scored_vendors else 0.0
        
        print(f"\n{'='*60}")
        print(f"Assessment Complete!")
        print(f"Recommended Vendor: {recommendation['vendor_id']} ({best_score:.2f}/5.0)")
        print(f"{'='*60}\n")
        
        return {
            "status": "completed",
            "recommended": recommendation["vendor_id"],
            "score": best_score
        }
    
    except Exception as e:
        # Update status to failed
        print(f"\n❌ Assessment pipeline failed: {str(e)}\n")
        update_evaluation(evaluation_id, {
            "status": "failed",
            "error": str(e)
        })
        raise


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
    
    try:
        # Step 1: Generate requirement profile
        print(f"[0/6] Running Requirement Profile Agent...")
        requirement_agent = RequirementProfileAgent(event_callback=event_callback)
        requirement_profile = requirement_agent.execute({"evaluation": evaluation})
        
        update_evaluation(evaluation_id, {"requirement_profile": requirement_profile})
        evaluation["requirement_profile"] = requirement_profile
        
        # Use inferred dimension importance
        dimension_importance = requirement_profile.get("dimension_importance", {
            "security": 3,
            "cost": 3,
            "interoperability": 3,
            "adoption": 3
        })
        
        print(f"  Using inferred priorities: Security={dimension_importance['security']}, "
              f"Cost={dimension_importance['cost']}, Interoperability={dimension_importance['interoperability']}, "
              f"Adoption={dimension_importance['adoption']}")
        
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
            
            print(f"\n[Assessment] Evaluating vendor: {vendor.get('name', 'Unknown')}")
            
            ctx = {"vendor": vendor, "evaluation": evaluation}
            agent_outputs = {}
            
            print(f"  [1/4] Running Compliance Agent...")
            agent_outputs["compliance"] = await agents["compliance"].execute(ctx)
            
            print(f"  [2/4] Running Interoperability Agent...")
            agent_outputs["interoperability"] = await agents["interoperability"].execute(ctx)
            
            print(f"  [3/4] Running Finance Agent...")
            agent_outputs["finance"] = await agents["finance"].execute(ctx)
            
            print(f"  [4/4] Running Adoption Agent...")
            agent_outputs["adoption"] = await agents["adoption"].execute(ctx)
            
            # Calculate weighted score using inferred dimension importance
            # Handle None scores (insufficient data) by excluding them from average
            s = agent_outputs["compliance"].get("score")
            c = agent_outputs["finance"].get("score")
            i = agent_outputs["interoperability"].get("score")
            a = agent_outputs["adoption"].get("score")
            
            # Build list of (score, weight) pairs, excluding None scores
            scored = []
            if s is not None:
                scored.append((s, dimension_importance["security"]))
            if c is not None:
                scored.append((c, dimension_importance["cost"]))
            if i is not None:
                scored.append((i, dimension_importance["interoperability"]))
            if a is not None:
                scored.append((a, dimension_importance["adoption"]))
            
            # Calculate weighted average (or None if all dimensions insufficient)
            if scored:
                total_weight = sum(w for _, w in scored)
                if total_weight > 0:
                    weighted = sum(score * w for score, w in scored) / total_weight
                else:
                    # All weights are 0, use simple average
                    weighted = sum(score for score, _ in scored) / len(scored)
            else:
                weighted = None
            
            if weighted is not None:
                print(f"  Weighted Score: {weighted:.2f}/5.0")
            else:
                print(f"  Weighted Score: N/A (insufficient data)")
            
            updated_vendors.append({
                **vendor,
                "agent_outputs": agent_outputs,
                "total_score": round(weighted, 2) if weighted is not None else None
            })
            scored_vendors.append((vendor["id"], weighted if weighted is not None else 0.0, vendor.get("name", "Unknown")))
            
            if event_callback:
                event_callback("vendor_complete", {
                    "vendor_id": vendor["id"],
                    "vendor_name": vendor["name"],
                    "total_score": round(weighted, 2) if weighted is not None else None
                })
        
        # Update evaluation with vendor scores before running comparison
        update_evaluation(evaluation_id, {"vendors": updated_vendors})
        evaluation["vendors"] = updated_vendors
        
        # Step 2: Generate Goldman-style detailed analysis
        print(f"\n[6/6] Running Comparison Analysis Agent...")
        comparison_agent = ComparisonAnalysisAgent(event_callback=event_callback)
        analysis = comparison_agent.execute({"evaluation": evaluation})
        
        # Extract recommendation from analysis
        final_rec = analysis.get("final_recommendation", {})
        recommendation = {
            "vendor_id": final_rec.get("recommended_vendor_id", ""),
            "reason": final_rec.get("short_reason", "No recommendation available")
        }
        
        # Generate contextual onboarding checklist based on actual findings
        onboarding_checklist = generate_contextual_checklist(
            analysis=analysis,
            vendors=updated_vendors,
            requirement_profile=requirement_profile,
            recommended_vendor_id=final_rec.get("recommended_vendor_id", "")
        )
        
        # Get best score for logging
        best_score = max([s[1] for s in scored_vendors]) if scored_vendors else 0.0
        
        update_evaluation(evaluation_id, {
            "status": "completed",
            "vendors": updated_vendors,
            "recommendation": recommendation,
            "analysis": analysis,
            "onboarding_checklist": onboarding_checklist
        })
        
        print(f"\n{'='*60}\nAssessment Complete! Recommended: {recommendation['vendor_id']} ({best_score:.2f}/5.0)\n{'='*60}\n")
        
        return {"status": "completed", "recommended": recommendation["vendor_id"], "score": best_score}
        
    except Exception as e:
        print(f"\n❌ Assessment pipeline failed: {str(e)}\n")
        update_evaluation(evaluation_id, {"status": "failed", "error": str(e)})
        if event_callback:
            event_callback("workflow_error", {"error": str(e)})
        raise

