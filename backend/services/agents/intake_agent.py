"""
Intake Agent - Vendor Ops Analyst
Normalizes fields and extracts basic info from docs/website
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files
from typing import Dict, Any


class IntakeAgent(BaseAgent):
    """Agent 1: Intake Agent"""
    
    def __init__(self, event_callback=None):
        super().__init__("IntakeAgent", "Vendor Ops Analyst", event_callback)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize vendor fields and extract additional info.
        """
        vendor = context.get("vendor", {})
        
        self.emit_event("agent_start", {"status": "starting"})
        
        # Extract vendor basic info
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        product_name = vendor.get("product_name", "")
        product_description = vendor.get("product_description", "")
        
        # Get document content
        files = vendor.get("files", [])
        doc_text = extract_texts_from_files(files) if files else ""
        
        # Build prompt
        system_prompt = f"""You are a {self.role} conducting initial vendor intake.
Your task is to normalize vendor information and extract key details."""
        
        user_prompt = f"""Analyze this vendor submission and provide a structured summary.

Company: {company_name}
Website: {website}
Product: {product_name}
Description: {product_description}

Document Content:
{doc_text[:3000] if doc_text else "No documents provided"}

Provide the following in JSON format:
{{
  "summary": "2-3 sentence summary of the vendor and their offering",
  "fields": {{
    "regions_served": ["list of regions/countries they operate in"],
    "industries": ["list of industries they serve"],
    "product_category": "primary product category (e.g., CRM, Analytics, Security)"
  }}
}}"""
        
        try:
            result = self._call_llm_json(user_prompt, system_prompt)
            
            # Ensure required fields exist
            if not result.get("summary"):
                result["summary"] = f"{company_name} provides {product_description or 'software solutions'}"
            if not result.get("fields"):
                result["fields"] = {
                    "regions_served": ["Unknown"],
                    "industries": ["Unknown"],
                    "product_category": "Unknown"
                }
            
            print(f"[{self.name}] Successfully processed vendor {company_name}")
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            # Return default structure
            return {
                "summary": f"{company_name} - {product_description}",
                "fields": {
                    "regions_served": ["Unknown"],
                    "industries": ["Unknown"],
                    "product_category": product_name or "Unknown"
                }
            }

