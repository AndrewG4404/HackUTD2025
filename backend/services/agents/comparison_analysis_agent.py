"""
Comparison Analysis Agent - Senior Vendor Risk Analyst
Generates Goldman-style detailed vendor analysis with narrative reasoning
"""
from services.agents.base_agent import BaseAgent
from typing import Dict, Any, List
import json


class ComparisonAnalysisAgent(BaseAgent):
    """
    Comparison Analysis Agent for assessment workflow.
    Generates detailed, Goldman-style vendor analysis with concrete findings.
    """
    
    def __init__(self, event_callback=None):
        super().__init__("ComparisonAnalysisAgent", "Senior Vendor Risk Analyst", event_callback)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed analysis comparing vendors across all dimensions.
        Returns Goldman-style narrative with concrete statements.
        """
        evaluation = context.get("evaluation", {})
        vendors = evaluation.get("vendors", [])
        requirement_profile = evaluation.get("requirement_profile", {})
        use_case = evaluation.get("use_case", "")
        
        self.emit_event("agent_start", {
            "agent_name": self.name,
            "status": "starting"
        })
        
        if not vendors or len(vendors) < 1:
            return self._empty_analysis()
        
        # Check if we have insufficient compliance data (critical for financial institutions)
        insufficient_data = self._check_insufficient_data(vendors)
        
        self.emit_event("agent_thinking", {
            "agent_name": self.name,
            "action": f"Generating detailed analysis for {len(vendors)} vendor(s)",
            "insufficient_data": insufficient_data
        })
        
        # Build comprehensive prompt with all agent outputs
        system_prompt = """You are a senior vendor risk analyst at a tier-1 global investment bank (Goldman Sachs–like).

Your job is to produce a detailed, business-friendly vendor assessment memo that executives can use to make procurement decisions.

Write in direct, professional language with concrete facts. Mention specific capabilities (e.g., "supports Okta SSO via SAML 2.0", "SOC 2 Type II certified", "REST API with rate limit of 1000 req/min").

Highlight both strengths and gaps/risks for each vendor. Be balanced but decisive.

Return ONLY valid JSON matching the exact schema provided."""

        # Build vendor summaries from agent outputs
        vendor_summaries = []
        for vendor in vendors:
            vendor_id = vendor.get("id", "")
            vendor_name = vendor.get("name", "Unknown")
            agent_outputs = vendor.get("agent_outputs", {})
            
            summary = f"""
**Vendor: {vendor_name}** (ID: {vendor_id})

**Compliance/Security Agent Output:**
{json.dumps(agent_outputs.get("compliance", {}), indent=2)}

**Interoperability Agent Output:**
{json.dumps(agent_outputs.get("interoperability", {}), indent=2)}

**Finance Agent Output:**
{json.dumps(agent_outputs.get("finance", {}), indent=2)}

**Adoption Agent Output:**
{json.dumps(agent_outputs.get("adoption", {}), indent=2)}
"""
            vendor_summaries.append(summary)
        
        user_prompt = f"""
**Use Case:**
{use_case}

**Requirement Profile:**
{json.dumps(requirement_profile, indent=2)}

**Vendor Data:**
{chr(10).join(vendor_summaries)}

---

Generate a detailed, Goldman-style vendor assessment. Return ONLY valid JSON with this exact structure:

{{
  "per_vendor": {{
    "{vendors[0].get('id', '')}": {{
      "overview": "2-3 sentence overview of vendor and market position",
      "security": {{
        "summary": "1-2 sentence summary of security posture",
        "strengths": ["Specific strength 1", "Specific strength 2", ...],
        "gaps": ["Specific gap or concern 1", "Specific gap 2", ...],
        "risks": ["Risk 1", "Risk 2", ...]
      }},
      "interoperability": {{
        "summary": "1-2 sentence summary of integration capabilities",
        "strengths": ["Specific API/integration strength", ...],
        "gaps": ["Missing integration or concern", ...]
      }},
      "finance": {{
        "summary": "1-2 sentence TCO/pricing summary",
        "strengths": ["Pricing advantage", ...],
        "gaps": ["Pricing concern", ...],
        "risks": ["Hidden cost risk", ...],
        "high_level_numbers": {{
          "year1_tco": "$XXk - $XXk",
          "ongoing_annual": "$XXk/year"
        }}
      }},
      "adoption": {{
        "summary": "1-2 sentence rollout/support summary",
        "strengths": ["Support strength", ...],
        "gaps": ["Training gap", ...],
        "risks": ["Adoption risk", ...]
      }},
      "key_strengths": ["Overall strength 1", "Overall strength 2", "Overall strength 3"],
      "key_risks": ["Overall risk 1", "Overall risk 2"]
    }}{', "' + vendors[1].get('id', '') + '": {...}' if len(vendors) > 1 else ''}
  }},
  "comparison": {{
    "security": "Direct comparison: which vendor better meets security requirements and why (2-3 sentences)",
    "interoperability": "Direct comparison: which vendor has better integrations and why",
    "cost": "Direct comparison: which vendor offers better value and why",
    "adoption": "Direct comparison: which vendor easier to adopt and why"
  }},
  "final_recommendation": {{
    "recommended_vendor_id": "{vendors[0].get('id', '')}",
    "short_reason": "1 sentence why this vendor wins",
    "detailed_reason": "2-3 sentences explaining the decision with specific justification"
  }}
}}

Use concrete facts from the agent outputs. Be specific about capabilities, certifications, and risks.
"""

        try:
            # Call LLM to generate detailed analysis
            result = self._call_llm_json(user_prompt, system_prompt)
            
            self.emit_event("agent_complete", {
                "agent_name": self.name,
                "status": "completed",
                "vendors_analyzed": len(vendors),
                "recommended": result.get("final_recommendation", {}).get("recommended_vendor_id", "")
            })
            
            print(f"[{self.name}] Generated detailed analysis for {len(vendors)} vendor(s)")
            print(f"  Recommended: {result.get('final_recommendation', {}).get('recommended_vendor_id', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error generating analysis: {e}")
            return self._empty_analysis()
    
    def _check_insufficient_data(self, vendors: List[Dict]) -> bool:
        """Check if we have insufficient data for a safe recommendation."""
        low_conf_count = 0
        for v in vendors:
            comp = v.get("agent_outputs", {}).get("compliance", {})
            # If compliance has low confidence AND low score, that's a red flag
            if comp.get("confidence") == "low" and comp.get("score", 0) < 2.0:
                low_conf_count += 1
        
        # If ALL vendors have low compliance data, that's insufficient for financial institutions
        return low_conf_count == len(vendors)
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            "per_vendor": {},
            "comparison": {
                "security": "No comparison available",
                "interoperability": "No comparison available",
                "cost": "No comparison available",
                "adoption": "No comparison available"
            },
            "final_recommendation": {
                "recommended_vendor_id": "",
                "short_reason": "Insufficient data for recommendation",
                "detailed_reason": "Unable to generate recommendation due to missing vendor data."
            }
        }

