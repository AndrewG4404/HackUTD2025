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
        Actively discovers and analyzes official pricing documentation.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        
        print(f"[{self.name}] Analyzing pricing for {company_name}...")
        
        # Extract document content
        files = vendor.get("files", [])
        doc_text = extract_texts_from_files(files) if files else ""
        
        # Discover and fetch pricing documentation
        doc_urls = vendor.get("doc_urls", [])
        
        # Use LLM to discover official pricing documentation URLs
        if website and not doc_urls:
            print(f"[{self.name}] Discovering pricing documentation URLs...")
            doc_urls = self.client.discover_documentation_urls(website, "pricing")
        
        # Fetch discovered pricing documentation
        for url in doc_urls[:3]:  # Limit to 3 URLs
            try:
                print(f"[{self.name}] Fetching: {url}")
                url_content = self.client.fetch_url(url, max_chars=12000)
                doc_text += f"\n\n=== Official Pricing from {url} ===\n{url_content}"
            except Exception as e:
                print(f"[{self.name}] Error fetching {url}: {e}")
        
        # Use RAG for pricing information
        query = "pricing cost pricing model subscription per user per seat enterprise pricing tiers volume discounts annual contracts ROI"
        relevant_context = retrieve_relevant_context(query, doc_text, max_context=4000)
        
        system_prompt = f"""You are a {self.role} evaluating vendor pricing and cost structure.
Your task is to analyze pricing models and estimate total cost of ownership."""
        
        user_prompt = f"""As a {self.role}, analyze the pricing structure of {company_name} based on their OFFICIAL pricing documentation.

Official Pricing Documentation:
{relevant_context if relevant_context else "No pricing documentation available"}

Perform a comprehensive enterprise finance evaluation:

**Pricing Model Analysis:**
- Per-seat/per-user pricing
- Usage-based pricing
- Tiered pricing structure
- Enterprise/custom pricing availability
- Free tier or trial period

**Cost Components:**
- Base subscription cost
- Implementation/onboarding fees
- Training costs
- Support tier costs
- API call/usage overages
- Data storage fees
- Premium feature add-ons

**Contract Terms:**
- Annual vs monthly pricing
- Multi-year discounts
- Volume discounts
- Cancellation terms
- Price lock guarantees

**Hidden Costs & Fees:**
- Data migration costs
- Integration costs
- Custom development fees
- Professional services
- Upgrade/downgrade penalties

**TCO Estimation (200-user mid-size deployment):**
- Year 1 total cost (including implementation)
- Annual recurring cost (years 2-3)
- Cost per user per month
- Cost predictability assessment

**ROI Indicators:**
- Time-to-value
- Efficiency gains potential
- Cost comparison to alternatives
- Value-for-money assessment

**Enterprise Considerations:**
- Procurement process complexity
- Payment terms flexibility
- Vendor lock-in risk
- Price transparency

Provide your assessment in JSON format:
{{
  "score": <float 0-5, where 5 is excellent value>,
  "tco_estimate": "Detailed TCO for 200 users including assumptions",
  "pricing_model": "Brief description of pricing structure",
  "annual_cost_range": "Estimated range (e.g., $40k-$60k/year)",
  "hidden_costs": ["List any hidden or unclear costs"],
  "value_assessment": "Brief value-for-money assessment",
  "notes": "Key insights about pricing and enterprise fit"
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

