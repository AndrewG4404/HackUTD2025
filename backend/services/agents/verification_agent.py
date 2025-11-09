"""
Verification Agent - Fact Checker
Verifies vendor information against website and documents
"""
from services.agents.base_agent import BaseAgent
from typing import Dict, Any


class VerificationAgent(BaseAgent):
    """Agent 2: Verification Agent"""
    
    def __init__(self, event_callback=None):
        super().__init__("VerificationAgent", "Fact Checker", event_callback)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify vendor information against website.
        """
        vendor = context.get("vendor", {})
        self.emit_event("agent_start", {"status": "starting"})
        
        company_name = vendor.get("name", "")
        website = vendor.get("website", "")
        hq_location = vendor.get("hq_location", "")
        
        # Fetch website content
        website_content = ""
        if website:
            try:
                website_content = self.client.fetch_url(website)
            except Exception as e:
                print(f"[{self.name}] Error fetching website: {e}")
        
        system_prompt = f"""You are a {self.role} verifying vendor information.
Your task is to check if claimed information matches what's found on their website."""
        
        user_prompt = f"""Verify the following vendor information against their website content.

Claimed Information:
- Company Name: {company_name}
- Website: {website}
- HQ Location: {hq_location}

Website Content:
{website_content[:2000] if website_content else "Unable to fetch website content"}

For each field, determine if there is a match, mismatch, or if it's unknown.
Provide your assessment in JSON format:
{{
  "flags": {{
    "name_match": "match" or "mismatch" or "unknown",
    "website_match": "match" or "mismatch" or "unknown",
    "location_match": "match" or "mismatch" or "unknown"
  }}
}}"""
        
        try:
            result = self._call_llm_json(user_prompt, system_prompt)
            
            # Ensure flags exist
            if not result.get("flags"):
                result["flags"] = {
                    "name_match": "unknown",
                    "website_match": "unknown",
                    "location_match": "unknown"
                }
            
            print(f"[{self.name}] Verification complete for {company_name}")
            self.emit_event("agent_complete", {"status": "completed"})
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return {
                "flags": {
                    "name_match": "unknown",
                    "website_match": "unknown",
                    "location_match": "unknown"
                }
            }

