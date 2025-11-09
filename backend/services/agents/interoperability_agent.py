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
        Actively discovers and analyzes official technical documentation.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        
        print(f"[{self.name}] Analyzing technical integration for {company_name}...")
        
        # Extract document content
        files = vendor.get("files", [])
        doc_text = extract_texts_from_files(files) if files else ""
        
        # Discover and fetch technical documentation
        doc_urls = vendor.get("doc_urls", [])
        
        # Use LLM to discover official technical/API documentation URLs
        if website and not doc_urls:
            print(f"[{self.name}] Discovering technical documentation URLs...")
            doc_urls = self.client.discover_documentation_urls(website, "api")
            doc_urls.extend(self.client.discover_documentation_urls(website, "technical")[:2])
        
        # Fetch discovered technical documentation
        for url in doc_urls[:4]:  # Limit to 4 URLs
            try:
                print(f"[{self.name}] Fetching: {url}")
                url_content = self.client.fetch_url(url, max_chars=12000)
                doc_text += f"\n\n=== Official Technical Docs from {url} ===\n{url_content}"
            except Exception as e:
                print(f"[{self.name}] Error fetching {url}: {e}")
        
        # Use RAG for technical documentation
        query = "API REST GraphQL SDK SSO SAML OAuth authentication webhooks integration technical documentation endpoints rate limits"
        relevant_context = retrieve_relevant_context(query, doc_text, max_context=4000)
        
        system_prompt = f"""You are a {self.role} evaluating technical interoperability.
Your task is to assess integration capabilities and technical fit."""
        
        user_prompt = f"""As a {self.role}, evaluate the technical integration capabilities of {company_name} based on their OFFICIAL documentation.

Our Internal Technical Stack Requirements:
- Required: {', '.join(self.reference_stack['required'])}
- Preferred: {', '.join(self.reference_stack['preferred'])}

Official Technical Documentation:
{relevant_context if relevant_context else "No technical documentation available"}

Perform a comprehensive interoperability assessment:

**API Capabilities:**
- REST API availability and maturity
- GraphQL API support
- API versioning strategy
- Rate limits and quotas
- API documentation quality
- Sandbox/test environment
- API response times/SLAs

**Authentication & Security:**
- SSO support (SAML, OAuth 2.0, OpenID Connect)
- API key management
- JWT/token-based auth
- Multi-factor authentication (MFA)
- Role-based access control (RBAC)
- IP whitelisting support

**Integration Features:**
- Webhook/event notification system
- Real-time data sync capabilities
- Bulk data import/export
- Batch processing support
- Retry mechanisms
- Error handling and logging

**SDKs & Libraries:**
- Official SDK availability (Python, JavaScript, Java, etc.)
- SDK documentation and examples
- Community-maintained libraries
- Code samples and tutorials

**Data Exchange:**
- Supported data formats (JSON, XML, CSV)
- Data schema documentation
- Data validation requirements
- Custom field support
- Data transformation capabilities

**Technical Fit Analysis:**
- Compatibility with our required stack
- Integration complexity estimate
- Development effort (person-days)
- Maintenance requirements
- Breaking change policy

**Documentation Quality:**
- API reference completeness
- Integration guides availability
- Code examples quality
- Troubleshooting resources
- Community support/forums

Provide your assessment in JSON format:
{{
  "score": <float 0-5, where 5 is excellent interoperability>,
  "findings": [
    "List specific technical capabilities with evidence",
    "Example: 'RESTful API with comprehensive OpenAPI spec at /api/docs'"
  ],
  "compatibility": {{
    "rest_api": "available|limited|not-found",
    "sso_saml": "supported|not-supported|unclear",
    "webhooks": "supported|not-supported|unclear",
    "sdk_support": ["list of available SDKs"]
  }},
  "integration_complexity": "low|medium|high - brief explanation",
  "estimated_dev_effort": "Brief estimate in person-days with assumptions"
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

