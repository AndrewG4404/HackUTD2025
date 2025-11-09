"""
Summary Agent - Onboarding Manager
Aggregates all agent outputs and provides final recommendation
"""
from services.agents.base_agent import BaseAgent
from typing import Dict, Any


class SummaryAgent(BaseAgent):
    """Agent 7: Summary Agent"""
    
    def __init__(self, event_callback=None):
        super().__init__("SummaryAgent", "Onboarding Manager", event_callback)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate all agent outputs and generate summary.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        agent_outputs = vendor.get("agent_outputs", {})
        
        # Extract scores from all agents
        scores = {
            "compliance": agent_outputs.get("compliance", {}).get("score", 0),
            "interoperability": agent_outputs.get("interoperability", {}).get("score", 0),
            "finance": agent_outputs.get("finance", {}).get("score", 0),
            "adoption": agent_outputs.get("adoption", {}).get("score", 0)
        }
        
        # Calculate overall score
        total_score = sum(scores.values()) / len(scores) if scores else 0
        
        # Build context for LLM
        context_summary = f"""Vendor: {company_name}

Dimension Scores (0-5):
- Compliance & Data: {scores['compliance']}/5
- Interoperability: {scores['interoperability']}/5
- Finance & TCO: {scores['finance']}/5
- Adoption & Support: {scores['adoption']}/5

Overall Average: {total_score:.2f}/5

Agent Findings:
- Compliance: {agent_outputs.get('compliance', {}).get('findings', [])}
- Compliance Risks: {agent_outputs.get('compliance', {}).get('risks', [])}
- Interoperability: {agent_outputs.get('interoperability', {}).get('findings', [])}
- Finance: {agent_outputs.get('finance', {}).get('notes', '')}
- Adoption: {agent_outputs.get('adoption', {}).get('notes', '')}
"""
        
        system_prompt = f"""You are an {self.role} synthesizing vendor evaluation results.
Your task is to provide a final recommendation and actionable onboarding checklist."""
        
        user_prompt = f"""Based on the multi-agent evaluation, provide a final assessment for onboarding {company_name}.

{context_summary}

Provide your recommendation in JSON format:
{{
  "overall_risk_score": <float 0-5, where 5 is highest risk>,
  "recommendation": "Go / Proceed with Caution / No-go recommendation with 2-3 sentence justification",
  "onboarding_checklist": [
    "3-7 specific action items for onboarding (e.g., 'Request security questionnaire', 'Set up SSO')"
  ]
}}"""
        
        try:
            result = self._call_llm_json(user_prompt, system_prompt)
            
            # Ensure required fields
            if "overall_risk_score" not in result:
                # Inverse the score: high overall score = low risk
                result["overall_risk_score"] = 5.0 - total_score
            if "recommendation" not in result:
                if total_score >= 4.0:
                    result["recommendation"] = "Go - Strong vendor profile across all dimensions"
                elif total_score >= 3.0:
                    result["recommendation"] = "Proceed with Caution - Address identified gaps"
                else:
                    result["recommendation"] = "No-go - Significant concerns identified"
            if "onboarding_checklist" not in result or not result["onboarding_checklist"]:
                result["onboarding_checklist"] = [
                    "Complete security assessment",
                    "Negotiate contract terms",
                    "Plan technical integration"
                ]
            
            # Ensure risk score is a number
            try:
                result["overall_risk_score"] = float(result["overall_risk_score"])
            except (ValueError, TypeError):
                result["overall_risk_score"] = 5.0 - total_score
            
            print(f"[{self.name}] Summary complete for {company_name}: {result['recommendation'][:50]}")
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return {
                "overall_risk_score": 5.0 - total_score,
                "recommendation": "Evaluation incomplete",
                "onboarding_checklist": ["Complete vendor evaluation"]
            }

