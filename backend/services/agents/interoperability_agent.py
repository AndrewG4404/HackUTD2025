"""
Interoperability Agent - Solutions Architect
Evaluates technical fit and integration capabilities
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any


class InteroperabilityAgent(BaseAgent):
    """Agent 4: Interoperability Agent"""
    
    def __init__(self):
        super().__init__("Interoperability Agent", "Solutions Architect")
        # Internal reference stack for MVP
        self.reference_stack = {
            "required": ["REST API", "SSO/SAML", "Webhooks"],
            "preferred": ["OAuth 2.0", "SDK support", "GraphQL", "API documentation"]
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate interoperability and technical fit using RAG.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        
        # Extract document content
        files = vendor.get("files", [])
        doc_text = extract_texts_from_files(files) if files else ""
        
        # Use RAG for technical documentation
        query = "API REST SDK SSO authentication webhooks integration technical documentation"
        relevant_context = retrieve_relevant_context(query, doc_text, max_context=3000)
        
        system_prompt = f"""You are a {self.role} evaluating technical interoperability.
Your task is to assess integration capabilities and technical fit."""
        
        user_prompt = f"""Evaluate the technical integration capabilities of {company_name}.

Our Internal Requirements:
Required: {', '.join(self.reference_stack['required'])}
Preferred: {', '.join(self.reference_stack['preferred'])}

Vendor Technical Documentation:
{relevant_context if relevant_context else "No technical documentation available"}

Assess:
1. API availability and quality
2. Authentication methods (SSO, OAuth, SAML)
3. Webhook/event system
4. SDK support
5. Integration ease
6. Documentation quality

Provide your assessment in JSON format:
{{
  "score": <float 0-5, where 5 is excellent interoperability>,
  "findings": [
    "list of integration capabilities, supported technologies, and technical strengths"
  ]
}}"""
        
        try:
            result = self._call_llm_json(user_prompt, system_prompt)
            
            # Ensure required fields
            if "score" not in result:
                result["score"] = 2.5
            if "findings" not in result:
                result["findings"] = []
            
            # Ensure score is a number
            try:
                result["score"] = float(result["score"])
            except (ValueError, TypeError):
                result["score"] = 2.5
            
            print(f"[{self.name}] Interoperability evaluation complete for {company_name}: {result['score']}/5")
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return {
                "score": 2.5,
                "findings": ["Unable to complete technical assessment"]
            }

