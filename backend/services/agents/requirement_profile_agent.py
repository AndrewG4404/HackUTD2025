"""
Requirement Profile Agent - Product Owner
Infers dimension importance and extracts requirements from use case description
"""
from services.agents.base_agent import BaseAgent
from typing import Dict, Any
import json


class RequirementProfileAgent(BaseAgent):
    """Requirement Profile Agent for assessment workflow - infers priorities from use case"""
    
    def __init__(self, event_callback=None):
        super().__init__("RequirementProfileAgent", "Product Owner", event_callback)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate requirement profile from use case description.
        Infers dimension importance (security, cost, interoperability, adoption) from context.
        """
        evaluation = context.get("evaluation", {})
        use_case = evaluation.get("use_case", "")
        
        self.emit_event("agent_start", {
            "agent_name": self.name,
            "status": "starting"
        })
        
        if not use_case:
            # Return defaults if no use case provided
            return {
                "critical_requirements": [],
                "nice_to_haves": [],
                "compliance_expectations": [],
                "dimension_importance": {
                    "security": 3,
                    "cost": 3,
                    "interoperability": 3,
                    "adoption": 3
                },
                "integration_targets": [],
                "scale_assumptions": {}
            }
        
        # Build prompt to infer requirements and priorities from use case
        system_prompt = """You are a senior product owner at a tier-1 global investment bank (Goldman Sachs–like).
Your job is to analyze a vendor evaluation use case and extract:
1. Critical requirements (must-haves)
2. Nice-to-have features
3. Compliance expectations (GDPR, SOC2, HIPAA, etc.)
4. Dimension importance (0-5 scale):
   - security: how critical is security/compliance?
   - cost: how price-sensitive is this project?
   - interoperability: how important are integrations/APIs?
   - adoption: how important is ease-of-use/support?
5. Integration targets (specific systems mentioned: Okta, Slack, Jira, Snowflake, etc.)
6. Scale assumptions (number of users, org type, regions)

Infer importance scores based on context:
- If use case mentions "regulated", "financial", "SOC2", "ISO", etc. → security: 5
- If use case mentions "budget", "TCO", "cost-effective" → cost: 4-5
- If use case mentions specific integrations, APIs, SSO → interoperability: 4-5
- If use case mentions "training", "support", "rollout" → adoption: 4-5
- Default importance: 3

Return ONLY valid JSON matching this schema."""

        user_prompt = f"""Use Case:
{use_case}

Extract requirements and infer dimension importance (0-5 scale for each dimension).
Return JSON with this exact structure:
{{
  "critical_requirements": ["requirement 1", "requirement 2", ...],
  "nice_to_haves": ["feature 1", "feature 2", ...],
  "compliance_expectations": ["GDPR", "SOC2", ...],
  "dimension_importance": {{
    "security": 0-5,
    "cost": 0-5,
    "interoperability": 0-5,
    "adoption": 0-5
  }},
  "integration_targets": ["Okta", "Slack", ...],
  "scale_assumptions": {{
    "users": 300,
    "org_type": "financial institution",
    "regions": ["US", "EU"]
  }}
}}"""

        self.emit_event("agent_thinking", {
            "agent_name": self.name,
            "action": "Analyzing use case to infer priorities and requirements"
        })
        
        try:
            # Call LLM to extract requirements and infer priorities
            result = self._call_llm_json(user_prompt, system_prompt)
            
            # Validate dimension_importance scores
            dim_importance = result.get("dimension_importance", {})
            for dim in ["security", "cost", "interoperability", "adoption"]:
                if dim not in dim_importance:
                    dim_importance[dim] = 3
                else:
                    # Clamp to 0-5 range
                    dim_importance[dim] = max(0, min(5, dim_importance[dim]))
            
            result["dimension_importance"] = dim_importance
            
            self.emit_event("agent_complete", {
                "agent_name": self.name,
                "status": "completed",
                "dimension_importance": dim_importance,
                "critical_count": len(result.get("critical_requirements", [])),
                "integration_count": len(result.get("integration_targets", []))
            })
            
            print(f"[{self.name}] Inferred dimension importance:")
            print(f"  Security: {dim_importance['security']}/5")
            print(f"  Cost: {dim_importance['cost']}/5")
            print(f"  Interoperability: {dim_importance['interoperability']}/5")
            print(f"  Adoption: {dim_importance['adoption']}/5")
            print(f"  Critical requirements: {len(result.get('critical_requirements', []))}")
            
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            # Return defaults on error
            return {
                "critical_requirements": [],
                "nice_to_haves": [],
                "compliance_expectations": [],
                "dimension_importance": {
                    "security": 3,
                    "cost": 3,
                    "interoperability": 3,
                    "adoption": 3
                },
                "integration_targets": [],
                "scale_assumptions": {}
            }

