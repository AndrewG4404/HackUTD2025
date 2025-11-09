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
        Actively discovers and analyzes official vendor documentation.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        
        print(f"[{self.name}] Analyzing compliance for {company_name}...")
        
        # Extract document content for RAG
        files = vendor.get("files", [])
        doc_text = extract_texts_from_files(files) if files else ""
        
        # Discover and fetch compliance-related documentation
        doc_urls = vendor.get("doc_urls", [])
        
        # Use LLM to discover official compliance/privacy documentation URLs
        if website and not doc_urls:
            print(f"[{self.name}] Discovering compliance documentation URLs...")
            doc_urls = self.client.discover_documentation_urls(website, "privacy")
            doc_urls.extend(self.client.discover_documentation_urls(website, "compliance"))
        
        # Fetch discovered documentation
        for url in doc_urls[:5]:  # Limit to 5 URLs
            try:
                print(f"[{self.name}] Fetching: {url}")
                url_content = self.client.fetch_url(url, max_chars=15000)
                doc_text += f"\n\n=== Official Documentation from {url} ===\n{url_content}"
            except Exception as e:
                print(f"[{self.name}] Error fetching {url}: {e}")
        
        # Use RAG to get relevant context
        query = "data retention policies, data usage, data ownership, regulatory compliance, GDPR, CCPA, HIPAA, SOC2, ISO27001, data sharing, third-party access"
        relevant_context = retrieve_relevant_context(query, doc_text, max_context=5000)
        
        system_prompt = f"""You are a {self.role} evaluating vendor compliance and data practices.
Your task is to assess data policies, regulatory compliance, and identify risks."""
        
        user_prompt = f"""As a {self.role}, analyze the compliance and data practices of {company_name} based on their OFFICIAL documentation.

Official Documentation Analyzed:
{relevant_context if relevant_context else "No documentation available"}

Perform a comprehensive compliance evaluation checking for:

**Data Ownership & Control:**
- Who owns the data (customer vs vendor)?
- Can customer export/delete data?
- Data portability guarantees

**Data Retention Policies:**
- How long is data stored?
- What happens after contract termination?
- Backup and archive policies

**Data Usage & Sharing:**
- How is customer data used?
- Is data shared with third parties?
- Marketing/analytics usage of data
- AI/ML training usage disclosure

**Regulatory Compliance:**
- GDPR compliance (EU data protection)
- CCPA compliance (California privacy)
- HIPAA compliance (healthcare)
- SOC 2 Type II certification
- ISO 27001 certification
- Industry-specific regulations

**Security & Privacy:**
- Encryption at rest and in transit
- Access controls and authentication
- Incident response procedures
- Regular security audits

**Vendor-Specific Checks:**
- Service-level agreements (SLAs)
- Data breach notification timeline
- Customer data access logs
- Subprocessor disclosure

Provide your assessment in JSON format:
{{
  "score": <float 0-5, where 5 is excellent compliance>,
  "findings": [
    "List specific positive findings with evidence from documentation",
    "Example: 'SOC 2 Type II certified as of 2024 according to /security page'"
  ],
  "risks": [
    "List specific concerns or missing compliance elements",
    "Example: 'No explicit HIPAA compliance mentioned in documentation'"
  ],
  "data_ownership": "clear|unclear|vendor-owned - brief summary",
  "data_retention": "clearly defined|vague|not mentioned - brief summary"
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

