"""
Adoption & Support Agent - Customer Success
Evaluates implementation timeline, training, and support
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any


class AdoptionAgent(BaseAgent):
    """Agent 6: Adoption & Support Agent"""
    
    def __init__(self):
        super().__init__("Adoption Agent", "Customer Success")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate adoption and support capabilities using RAG.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        
        # Extract document content
        files = vendor.get("files", [])
        doc_text = extract_texts_from_files(files) if files else ""
        
        # Use RAG for support documentation
        query = "implementation timeline training support SLA documentation onboarding customer success"
        relevant_context = retrieve_relevant_context(query, doc_text, max_context=3000)
        
        system_prompt = f"""You are a {self.role} evaluating vendor adoption and support capabilities.
Your task is to assess implementation ease, training, and support quality."""
        
        user_prompt = f"""Evaluate the adoption and support capabilities of {company_name}.

Support Documentation:
{relevant_context if relevant_context else "No support documentation available"}

Assess:
1. Implementation timeline and complexity
2. Training resources and documentation
3. Support channels (24/7, email, phone, chat)
4. SLA commitments
5. Onboarding process
6. Customer success resources

Provide your assessment in JSON format:
{{
  "score": <float 0-5, where 5 is excellent support>,
  "notes": "summary of support capabilities and adoption considerations"
}}"""
        
        try:
            result = self._call_llm_json(user_prompt, system_prompt)
            
            # Ensure required fields
            if "score" not in result:
                result["score"] = 2.5
            if "notes" not in result:
                result["notes"] = "Support information not available"
            
            # Ensure score is a number
            try:
                result["score"] = float(result["score"])
            except (ValueError, TypeError):
                result["score"] = 2.5
            
            print(f"[{self.name}] Adoption evaluation complete for {company_name}: {result['score']}/5")
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return {
                "score": 2.5,
                "notes": "Unable to complete support assessment"
            }

