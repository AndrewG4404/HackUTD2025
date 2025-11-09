"""
Finance Agent - Finance Analyst
Enhanced with multi-step RAG for pricing and TCO research
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any, List


class FinanceAgent(BaseAgent):
    """
    Agent 5: Finance Agent
    
    Evaluates:
    - Pricing models and tiers
    - Total Cost of Ownership (TCO) for 200-500 users
    - Hidden costs (implementation, training, support)
    - ROI considerations
    """
    
    def __init__(self, event_callback=None):
        super().__init__("FinanceAgent", "Finance Analyst", event_callback)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate pricing and TCO using single comprehensive search.
        """
        vendor = context.get("vendor", {})
        evaluation = context.get("evaluation", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        use_case = evaluation.get("use_case", "")
        
        # Extract user count (default 200-500)
        user_count = self._extract_user_count(use_case)
        
        print(f"[{self.name}] Analyzing pricing for {company_name} ({user_count} users)...")
        self.emit_event("agent_start", {"status": "starting", "vendor": company_name})
        
        findings = []
        
        # ONE comprehensive pricing query
        self.emit_event("agent_thinking", {"action": "Researching comprehensive pricing"})
        finance_info = await self.research_requirement(
            f"{company_name} pricing plans cost per user enterprise pricing "
            f"implementation cost setup fees professional services "
            f"support plans premium support training costs TCO total cost ownership",
            company_name,
            website
        )
        
        # Analyze all aspects from the single search
        pricing_findings = self._analyze_pricing(finance_info, company_name, user_count)
        findings.extend(pricing_findings)
        
        impl_findings = self._analyze_implementation_costs(finance_info, company_name)
        findings.extend(impl_findings)
        
        support_findings = self._analyze_support_costs(finance_info, company_name)
        findings.extend(support_findings)
        
        # Calculate estimated TCO
        tco_estimate = self._estimate_tco(findings, user_count)
        
        # Calculate score (lower cost = higher score, with quality consideration)
        score = self._calculate_finance_score(findings, tco_estimate, user_count)
        
        # Generate notes
        notes = self._generate_finance_notes(findings, company_name, tco_estimate, user_count)
        
        # Generate management-friendly summary
        summary = self._generate_executive_summary(findings, score, company_name, tco_estimate, user_count)
        
        # Extract key strengths and risks
        strengths = [f for f in findings if any(kw in f.lower() for kw in ["competitive", "transparent", "volume discount", "flexible", "included"])][:4]
        risks = [f for f in findings if any(kw in f.lower() for kw in ["not available", "hidden", "additional", "requires quote", "unclear"])][:4]
        
        # Create structured output
        output = self.create_structured_output(
            score=score,
            findings=findings,
            notes=notes,
            summary=summary,
            strengths=strengths,
            risks=risks,
            pricing_model=self._extract_pricing_model(pricing_findings),
            estimated_tco=tco_estimate
        )
        
        self.emit_event("agent_complete", {
            "status": "completed",
            "score": score,
            "summary": summary,
            "tco_estimate": tco_estimate,
            "sources_count": len(self.sources)
        })
        
        return output
    
    def _extract_user_count(self, use_case: str) -> int:
        """Extract user count from use case, default to 300."""
        if not use_case:
            return 300  # Default for application workflow
        
        import re
        match = re.search(r'(\d+)[-–](\d+)\s*users', use_case.lower())
        if match:
            # Return midpoint
            return (int(match.group(1)) + int(match.group(2))) // 2
        
        match = re.search(r'(\d+)\s*users', use_case.lower())
        if match:
            return int(match.group(1))
        
        return 300  # Default
    
    def _analyze_pricing(self, info: str, vendor_name: str, user_count: int) -> List[str]:
        """Analyze pricing information."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s pricing information for ~{user_count} users:

{info[:3000]}

Extract:
1. Pricing model (per user, per month, annual, tiered, custom)
2. List prices if available
3. Enterprise pricing mentions
4. Price ranges or estimates

Return JSON: {{"pricing_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing pricing with LLM"})
            result = self._call_llm_json(prompt, "You are a financial analyst. Return valid JSON only.")
            pricing_findings = result.get("pricing_findings", [])
            
            if pricing_findings:
                findings.extend(pricing_findings)
            else:
                findings.append("Public pricing not available - enterprise pricing requires quote")
                self.add_ambiguity(f"Pricing for {user_count} users requires vendor quote - estimates based on industry averages")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing pricing: {e}")
            findings.append("Unable to determine pricing")
        
        return findings
    
    def _analyze_implementation_costs(self, info: str, vendor_name: str) -> List[str]:
        """Analyze implementation costs."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s implementation and setup costs:

{info[:2000]}

Identify:
1. Setup/onboarding fees
2. Implementation services costs
3. Data migration costs
4. Customization costs
5. Typical implementation timeline cost factors

Return JSON: {{"implementation_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            result = self._call_llm_json(prompt, "You are a financial analyst. Return valid JSON only.")
            impl_findings = result.get("implementation_findings", [])
            
            if impl_findings:
                findings.extend(impl_findings)
            else:
                findings.append("Implementation costs not publicly documented")
                self.add_ambiguity("Implementation costs typically 10-30% of annual license fees but require vendor quote")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing implementation: {e}")
        
        return findings
    
    def _analyze_support_costs(self, info: str, vendor_name: str) -> List[str]:
        """Analyze support and training costs."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s support and training costs:

{info[:2000]}

Identify:
1. Support tier pricing (basic, premium, enterprise)
2. Training costs (per user, per session)
3. Professional services rates
4. Annual maintenance fees

Return JSON: {{"support_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            result = self._call_llm_json(prompt, "You are a financial analyst. Return valid JSON only.")
            support_findings = result.get("support_findings", [])
            
            if support_findings:
                findings.extend(support_findings)
            else:
                findings.append("Support and training costs not detailed publicly")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing support costs: {e}")
        
        return findings
    
    def _extract_pricing_model(self, pricing_findings: List[str]) -> str:
        """Extract pricing model from findings."""
        findings_text = " ".join(pricing_findings).lower()
        
        if "per user" in findings_text or "per seat" in findings_text:
            return "per-user subscription"
        elif "tiered" in findings_text:
            return "tiered pricing"
        elif "custom" in findings_text or "quote" in findings_text:
            return "custom enterprise pricing"
        else:
            return "pricing model undetermined"
    
    def _estimate_tco(self, findings: List[str], user_count: int) -> Dict[str, Any]:
        """Estimate 3-year TCO based on findings."""
        # Extract any specific numbers from findings
        import re
        findings_text = " ".join(findings)
        
        # Look for per-user pricing
        per_user_match = re.search(r'\$(\d+)[-–]?\$?(\d+)?\s*(?:per user|/user|per month)', findings_text, re.IGNORECASE)
        
        if per_user_match:
            low = int(per_user_match.group(1))
            high = int(per_user_match.group(2)) if per_user_match.group(2) else low
            avg_monthly = (low + high) / 2
        else:
            # Industry average fallback: $50-150/user/month for enterprise SaaS
            avg_monthly = 100
            self.add_ambiguity(f"Using industry average of ${avg_monthly}/user/month as pricing not specified")
        
        # Calculate Year 1 (including implementation)
        year1_licenses = avg_monthly * user_count * 12
        year1_implementation = year1_licenses * 0.20  # 20% for implementation
        year1_total = year1_licenses + year1_implementation
        
        # Years 2-3 (ongoing)
        annual_ongoing = avg_monthly * user_count * 12
        
        three_year_total = year1_total + (annual_ongoing * 2)
        
        return {
            "year1": {
                "licenses": round(year1_licenses),
                "implementation": round(year1_implementation),
                "total": round(year1_total)
            },
            "annual_ongoing": round(annual_ongoing),
            "three_year_total": round(three_year_total),
            "per_user_per_month_estimate": round(avg_monthly, 2),
            "user_count": user_count
        }
    
    def _calculate_finance_score(self, findings: List[str], tco: Dict[str, Any], user_count: int) -> float:
        """Calculate finance score (lower cost = higher score, with value consideration)."""
        three_year_tco = tco["three_year_total"]
        
        # Benchmark: $50-200/user/month is typical for enterprise SaaS
        # Score inversely with cost
        per_user_monthly = three_year_tco / (user_count * 36)
        
        if per_user_monthly < 50:
            cost_score = 5.0
        elif per_user_monthly < 100:
            cost_score = 4.0
        elif per_user_monthly < 150:
            cost_score = 3.0
        elif per_user_monthly < 200:
            cost_score = 2.0
        else:
            cost_score = 1.0
        
        # Adjust for transparency (more documented info = higher confidence)
        transparency_bonus = 0.5 if len(self.sources) >= 3 else 0.0
        
        return min(5.0, cost_score + transparency_bonus)
    
    def _generate_finance_notes(self, findings: List[str], vendor_name: str, tco: Dict[str, Any], user_count: int) -> str:
        """Generate summary notes."""
        tco_val = tco["three_year_total"]
        per_user_monthly = tco["per_user_per_month_estimate"]
        
        if len(self.sources) == 0:
            return f"Pricing information for {vendor_name} not publicly available. Estimated 3-year TCO: ${tco_val:,} (~${per_user_monthly}/user/month for {user_count} users) based on industry averages. Recommend requesting formal quote."
        
        return f"3-year TCO estimate: ${tco_val:,} (~${per_user_monthly}/user/month for {user_count} users). Based on {len(self.sources)} sources. {len(findings)} cost factors identified. Confidence: {self._calculate_confidence()}"
    
    def _generate_executive_summary(self, findings: List[str], score: float, vendor_name: str, tco: Dict[str, Any], user_count: int) -> str:
        """Generate a 2-3 sentence executive summary suitable for management."""
        tco_val = tco["three_year_total"]
        per_user_monthly = tco["per_user_per_month_estimate"]
        year1_total = tco["year1"]["total"]
        
        if score >= 4.0:
            return f"{vendor_name} offers competitive pricing at ~${per_user_monthly}/user/month (${tco_val:,} 3-year TCO for {user_count} users). Transparent pricing model with Year 1 total of ${year1_total:,} including implementation."
        elif score >= 3.0:
            return f"{vendor_name} pricing is within market range at ~${per_user_monthly}/user/month (${tco_val:,} 3-year TCO). Some cost details require vendor quote, but overall financial profile is acceptable for {user_count}-user deployment."
        elif score >= 2.0:
            return f"{vendor_name} pricing lacks transparency with estimated ${tco_val:,} 3-year TCO based on industry averages. Year 1 costs (${year1_total:,}) include estimated implementation fees; formal quote required for budgeting."
        else:
            if len(self.sources) == 0:
                return f"Pricing information for {vendor_name} is not publicly available. Based on industry benchmarks for similar solutions, estimated 3-year TCO is ${tco_val:,} (~${per_user_monthly}/user/month for {user_count} users). Formal quote must be obtained for accurate budgeting."
            else:
                return f"{vendor_name} pricing structure is unclear or appears uncompetitive at estimated ~${per_user_monthly}/user/month. Hidden costs and setup fees may significantly impact TCO beyond the ${tco_val:,} estimate. Recommend exploring alternatives or negotiating volume pricing."
