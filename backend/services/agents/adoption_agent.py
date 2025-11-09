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
        Actively discovers and analyzes official support documentation.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        
        print(f"[{self.name}] Analyzing support and adoption for {company_name}...")
        
        # Extract document content
        files = vendor.get("files", [])
        doc_text = extract_texts_from_files(files) if files else ""
        
        # Discover and fetch support documentation
        doc_urls = vendor.get("doc_urls", [])
        
        # Use LLM to discover official support documentation URLs
        if website and not doc_urls:
            print(f"[{self.name}] Discovering support documentation URLs...")
            doc_urls = self.client.discover_documentation_urls(website, "support")
        
        # Fetch discovered support documentation
        for url in doc_urls[:3]:  # Limit to 3 URLs
            try:
                print(f"[{self.name}] Fetching: {url}")
                url_content = self.client.fetch_url(url, max_chars=12000)
                doc_text += f"\n\n=== Official Support Docs from {url} ===\n{url_content}"
            except Exception as e:
                print(f"[{self.name}] Error fetching {url}: {e}")
        
        # Use RAG for support documentation
        query = "implementation timeline training support SLA documentation onboarding customer success help resources community forum response time"
        relevant_context = retrieve_relevant_context(query, doc_text, max_context=4000)
        
        system_prompt = f"""You are a {self.role} evaluating vendor adoption and support capabilities.
Your task is to assess implementation ease, training, and support quality."""
        
        user_prompt = f"""As a {self.role}, evaluate the adoption and support capabilities of {company_name} based on their OFFICIAL documentation.

Official Support Documentation:
{relevant_context if relevant_context else "No support documentation available"}

Perform a comprehensive adoption and support evaluation:

**Implementation & Onboarding:**
- Typical implementation timeline
- Implementation methodology (self-service vs guided)
- Onboarding program availability
- Implementation success rate
- Go-live support
- Data migration assistance
- Dedicated implementation manager

**Training Resources:**
- Training program availability
- Training formats (online, in-person, webinar)
- Certification programs
- Knowledge base/documentation
- Video tutorials
- Train-the-trainer programs
- Training costs (included vs paid)

**Support Channels:**
- 24/7 support availability
- Support tiers (standard, premium, enterprise)
- Email support response time
- Phone support availability
- Live chat support
- Dedicated account manager
- Emergency hotline

**SLA & Response Times:**
- Support SLA commitments
- Response time guarantees by severity
- Resolution time targets
- Uptime guarantees
- Maintenance windows
- Escalation procedures

**Documentation & Resources:**
- User documentation quality
- Admin documentation
- API/developer documentation
- Troubleshooting guides
- FAQ/knowledge base
- Release notes
- Changelog transparency

**Community & Ecosystem:**
- User community forum
- Community activity level
- User conferences/events
- Partner ecosystem
- Third-party integrations marketplace
- User feedback incorporation

**Customer Success:**
- Proactive customer success engagement
- Regular business reviews
- Best practice sharing
- Benchmarking reports
- Health check services
- Success metrics tracking

**Ease of Adoption:**
- User interface intuitiveness
- Learning curve assessment
- Change management support
- User adoption tracking
- Champion/power user programs

Provide your assessment in JSON format:
{{
  "score": <float 0-5, where 5 is excellent support>,
  "implementation_timeline": "Estimated timeline with assumptions",
  "support_availability": "24/7|business-hours|limited - brief details",
  "training_quality": "excellent|good|basic|limited - brief assessment",
  "sla_commitment": "strong|moderate|weak|unclear - key details",
  "adoption_complexity": "low|medium|high - brief explanation",
  "notes": "Key insights about support and adoption readiness"
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

