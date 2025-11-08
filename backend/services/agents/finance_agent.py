"""
Finance Agent - Finance Analyst
Evaluates pricing model and estimates TCO
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any


class FinanceAgent(BaseAgent):
    """Agent 5: Finance Agent"""
    
    def __init__(self):
        super().__init__("Finance Agent", "Finance Analyst")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate pricing and estimate TCO using RAG.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        
        # Extract document content
        files = vendor.get("files", [])
        doc_text = extract_texts_from_files(files) if files else ""
        
        # Use RAG for pricing information
        query = "pricing cost pricing model subscription per user per seat enterprise pricing"
        relevant_context = retrieve_relevant_context(query, doc_text, max_context=3000)
        
        system_prompt = f"""You are a {self.role} evaluating vendor pricing and cost structure.
Your task is to analyze pricing models and estimate total cost of ownership."""
        
        user_prompt = f"""Analyze the pricing structure of {company_name}.

Pricing Documentation:
{relevant_context if relevant_context else "No pricing documentation available"}

Evaluate:
1. Pricing model (per seat, per usage, tiered, enterprise, etc.)
2. Cost predictability
3. Hidden costs or fees
4. Value for money
5. TCO estimate for a typical mid-size deployment (200 users)

Provide your assessment in JSON format:
{{
  "score": <float 0-5, where 5 is excellent value>,
  "tco_estimate": "estimated annual cost with assumptions",
  "notes": "brief summary of pricing model and value assessment"
}}"""
        
        try:
            result = self._call_llm_json(user_prompt, system_prompt)
            
            # Ensure required fields
            if "score" not in result:
                result["score"] = 2.5
            if "tco_estimate" not in result:
                result["tco_estimate"] = "Unable to estimate from available information"
            if "notes" not in result:
                result["notes"] = "Pricing information not available"
            
            # Ensure score is a number
            try:
                result["score"] = float(result["score"])
            except (ValueError, TypeError):
                result["score"] = 2.5
            
            print(f"[{self.name}] Finance evaluation complete for {company_name}: {result['score']}/5")
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return {
                "score": 2.5,
                "tco_estimate": "Unable to estimate",
                "notes": "Insufficient pricing information"
            }

