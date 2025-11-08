"""
Compliance & Data Usage Agent - Compliance Officer
Evaluates compliance, data retention, and regulatory mentions
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any


class ComplianceAgent(BaseAgent):
    """Agent 3: Compliance & Data Usage Agent"""
    
    def __init__(self):
        super().__init__("Compliance Agent", "Compliance Officer")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate compliance and data usage policies using RAG.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        
        # Extract document content for RAG
        files = vendor.get("files", [])
        doc_text = extract_texts_from_files(files) if files else ""
        
        # Fetch privacy/security pages if URLs provided
        doc_urls = vendor.get("doc_urls", [])
        for url in doc_urls[:2]:  # Limit to first 2 URLs for MVP
            try:
                url_content = self.client.fetch_url(url)
                doc_text += f"\n\n=== Content from {url} ===\n{url_content}"
            except Exception as e:
                print(f"[{self.name}] Error fetching {url}: {e}")
        
        # Use RAG to get relevant context
        query = "data retention policies, data usage, regulatory compliance, GDPR, CCPA, HIPAA, SOC2, ISO27001"
        relevant_context = retrieve_relevant_context(query, doc_text, max_context=3000)
        
        system_prompt = f"""You are a {self.role} evaluating vendor compliance and data practices.
Your task is to assess data policies, regulatory compliance, and identify risks."""
        
        user_prompt = f"""Analyze the compliance and data practices of {company_name} based on their documentation.

Relevant Documentation:
{relevant_context if relevant_context else "No documentation available"}

Evaluate the following:
1. Data retention policies
2. Data usage and sharing practices
3. Regulatory compliance (GDPR, CCPA, HIPAA, SOC2, ISO27001, etc.)
4. Security practices
5. Privacy protections

Provide your assessment in JSON format:
{{
  "score": <float 0-5, where 5 is excellent compliance>,
  "findings": [
    "list of positive findings (certifications, compliance mentions, good practices)"
  ],
  "risks": [
    "list of concerns or missing elements"
  ]
}}"""
        
        try:
            result = self._call_llm_json(user_prompt, system_prompt)
            
            # Ensure required fields
            if "score" not in result:
                result["score"] = 2.5
            if "findings" not in result:
                result["findings"] = []
            if "risks" not in result:
                result["risks"] = []
            
            # Ensure score is a number
            try:
                result["score"] = float(result["score"])
            except (ValueError, TypeError):
                result["score"] = 2.5
            
            print(f"[{self.name}] Compliance evaluation complete for {company_name}: {result['score']}/5")
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error: {e}")
            return {
                "score": 2.5,
                "findings": ["Unable to complete full compliance assessment"],
                "risks": ["Insufficient documentation for thorough evaluation"]
            }

