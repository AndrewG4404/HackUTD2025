"""
Comparison Analysis Agent - Senior Vendor Risk Analyst
Generates Goldman-style detailed vendor analysis with narrative reasoning
"""
from services.agents.base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json


class ComparisonAnalysisAgent(BaseAgent):
    """
    Comparison Analysis Agent for assessment workflow.
    Generates detailed, Goldman-style vendor analysis with concrete findings.
    """
    
    def __init__(self, event_callback=None):
        super().__init__("ComparisonAnalysisAgent", "Senior Vendor Risk Analyst", event_callback)
    
    def _build_compact_vendor_snapshot(self, vendor: Dict[str, Any], use_case_summary: str) -> Dict[str, Any]:
        """
        Build a compact vendor snapshot with only essential information.
        This prevents token overflow (284k) by excluding raw HTML, full sources, etc.
        
        Returns compact dict with: status, score, summary, strengths[:5], gaps[:5], recommendations[:3]
        """
        ao = vendor.get("agent_outputs", {})
        
        def compact_dimension(dim_output: Dict[str, Any]) -> Dict[str, Any]:
            """Extract only essential fields from dimension output."""
            return {
                "status": dim_output.get("status", "unknown"),
                "score": dim_output.get("score"),  # Can be None
                "summary": dim_output.get("summary", "")[:500],  # Truncate to 500 chars
                "strengths": dim_output.get("strengths", [])[:5],  # Max 5
                "gaps": dim_output.get("risks", dim_output.get("gaps", []))[:5],  # Max 5
                "recommendations": dim_output.get("recommendations", [])[:3],  # Max 3
                "confidence": dim_output.get("confidence", "unknown")
            }
        
        snapshot = {
            "vendor_id": vendor.get("id", ""),
            "vendor_name": vendor.get("name", "Unknown"),
            "vendor_website": vendor.get("website", "")[:100],  # Truncate
            "total_score": vendor.get("total_score"),  # Can be None
            "use_case_context": use_case_summary[:400],  # Truncated use case
            "compliance": compact_dimension(ao.get("compliance", {})),
            "interoperability": compact_dimension(ao.get("interoperability", {})),
            "finance": compact_dimension(ao.get("finance", {})),
            "adoption": compact_dimension(ao.get("adoption", {}))
        }
        
        # Add TCO if available from finance
        finance_output = ao.get("finance", {})
        if "estimated_tco" in finance_output:
            tco = finance_output["estimated_tco"]
            snapshot["finance"]["tco_estimate"] = {
                "three_year_total": tco.get("three_year_total", 0),
                "per_user_per_month": tco.get("per_user_per_month_estimate", 0)
            }
        
        return snapshot
    
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
        insufficient_data_flags = self._check_insufficient_data_by_vendor(vendors)
        all_insufficient = all(insufficient_data_flags.values())
        
        self.emit_event("agent_thinking", {
            "agent_name": self.name,
            "action": f"Generating detailed analysis for {len(vendors)} vendor(s)",
            "all_insufficient_data": all_insufficient
        })
        
        # Build compact snapshots (prevent 284k token overflow)
        use_case_summary = use_case[:600] if use_case else "Enterprise vendor evaluation"
        vendor_snapshots = [
            self._build_compact_vendor_snapshot(v, use_case_summary)
            for v in vendors
        ]
        
        print(f"[{self.name}] Built {len(vendor_snapshots)} compact vendor snapshots")
        
        # Extract dimension scores for each vendor (for frontend display)
        dimension_scores_by_vendor = {}
        for vendor in vendors:
            vendor_id = vendor.get("id", "")
            ao = vendor.get("agent_outputs", {})
            dimension_scores_by_vendor[vendor_id] = {
                "security": ao.get("compliance", {}).get("score"),
                "interoperability": ao.get("interoperability", {}).get("score"),
                "finance": ao.get("finance", {}).get("score"),
                "adoption": ao.get("adoption", {}).get("score")
            }
        
        # Build compact prompt (no raw HTML, sources, or full agent outputs)
        system_prompt = """You are a senior vendor risk analyst at a tier-1 global investment bank (Goldman Sachs–like).

Your job is to produce a detailed, business-friendly vendor assessment memo that executives can use to make procurement decisions.

Write in direct, professional language with concrete facts. Mention specific capabilities (e.g., "supports Okta SSO via SAML 2.0", "SOC 2 Type II certified", "REST API with rate limit of 1000 req/min").

Highlight both strengths and gaps/risks for each vendor. Be balanced but decisive.

CRITICAL: If ANY vendor has compliance.status="insufficient_data", you MUST acknowledge this in your recommendation and explain that no safe recommendation can be made for regulated industries without official compliance documentation.

Return ONLY valid JSON matching the exact schema provided."""

        # Build compact user prompt with vendor snapshots (not raw outputs)
        user_prompt = f"""
**Use Case:**
{use_case_summary}

**Requirement Profile (Critical Requirements):**
{json.dumps(requirement_profile.get("critical_requirements", [])[:5], indent=2)}

**Vendor Snapshots (Compact):**
{json.dumps(vendor_snapshots, indent=2)}

---

Generate a detailed, Goldman-style vendor assessment. Return ONLY valid JSON with this exact structure:

{{
  "per_vendor": {{
    "{vendors[0].get('id', '')}": {{
      "headline": "2-3 sentence executive summary of vendor and market position",
      "dimension_scores": {{
        "security": {dimension_scores_by_vendor.get(vendors[0].get('id', ''), {}).get('security')},
        "interoperability": {dimension_scores_by_vendor.get(vendors[0].get('id', ''), {}).get('interoperability')},
        "finance": {dimension_scores_by_vendor.get(vendors[0].get('id', ''), {}).get('finance')},
        "adoption": {dimension_scores_by_vendor.get(vendors[0].get('id', ''), {}).get('adoption')}
      }},
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
            
            # Post-process LLM output to ensure required fields for frontend
            for vendor_id, vendor_data in result.get("per_vendor", {}).items():
                # Ensure dimension_scores exist (frontend requires this)
                if "dimension_scores" not in vendor_data:
                    scores = dimension_scores_by_vendor.get(vendor_id, {})
                    vendor_data["dimension_scores"] = {
                        "security": scores.get("security"),
                        "interoperability": scores.get("interoperability"),
                        "finance": scores.get("finance"),
                        "adoption": scores.get("adoption")
                    }
                
                # Rename "overview" to "headline" for frontend compatibility
                if "overview" in vendor_data and "headline" not in vendor_data:
                    vendor_data["headline"] = vendor_data.pop("overview")
                
                # Ensure all dimensions have required structure
                for dim in ["security", "interoperability", "finance", "adoption"]:
                    if dim not in vendor_data:
                        vendor_data[dim] = {
                            "summary": "Analysis pending",
                            "strengths": [],
                            "gaps": [],
                            "risks": []
                        }
                    else:
                        # Ensure each dimension has all required fields
                        dim_data = vendor_data[dim]
                        if "summary" not in dim_data:
                            dim_data["summary"] = "Analysis available"
                        if "strengths" not in dim_data:
                            dim_data["strengths"] = []
                        if "gaps" not in dim_data:
                            dim_data["gaps"] = []
                        if "risks" not in dim_data:
                            dim_data["risks"] = []
            
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
    
    def _check_insufficient_data_by_vendor(self, vendors: List[Dict]) -> Dict[str, bool]:
        """
        Check which vendors have insufficient data for a safe recommendation.
        
        Returns:
            Dict mapping vendor_id -> True if insufficient data
        """
        result = {}
        for v in vendors:
            vendor_id = v.get("id", "")
            comp = v.get("agent_outputs", {}).get("compliance", {})
            
            # Check if compliance has insufficient_data status or (low confidence AND None/low score)
            status = comp.get("status", "unknown")
            score = comp.get("score")
            confidence = comp.get("confidence", "unknown")
            
            insufficient = (
                status == "insufficient_data" or
                (confidence == "low" and (score is None or score < 2.0))
            )
            
            result[vendor_id] = insufficient
        
        return result
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure with proper frontend-compatible format"""
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

