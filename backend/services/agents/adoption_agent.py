"""
Adoption & Support Agent - Customer Success Manager
Enhanced with multi-step RAG for support and implementation research
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any, List, Optional


class AdoptionAgent(BaseAgent):
    """
    Agent 6: Adoption & Support Agent
    
    Evaluates:
    - Implementation timeline
    - Support availability (24/7, SLAs)
    - Training resources (docs, courses, certifications)
    - User community and ecosystem
    - Change management considerations
    """
    
    def __init__(self, event_callback=None):
        super().__init__("AdoptionAgent", "Customer Success Manager", event_callback)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate adoption factors using single comprehensive search.
        """
        vendor = context.get("vendor", {})
        evaluation = context.get("evaluation", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        use_case = evaluation.get("use_case", "")
        
        print(f"[{self.name}] Analyzing adoption for {company_name}...")
        self.emit_event("agent_start", {"status": "starting", "vendor": company_name})
        
        findings = []
        
        # ONE comprehensive adoption query
        self.emit_event("agent_thinking", {"action": "Researching comprehensive adoption factors"})
        adoption_info = await self.research_requirement(
            f"{company_name} implementation timeline deployment time to value onboarding "
            f"customer support 24/7 support SLA response time "
            f"training documentation certification courses learning resources "
            f"user community forum partner ecosystem marketplace",
            company_name,
            website
        )
        
        # Analyze all aspects from the single search
        impl_findings = self._analyze_implementation(adoption_info, company_name)
        findings.extend(impl_findings)
        
        support_findings = self._analyze_support(adoption_info, company_name)
        findings.extend(support_findings)
        
        training_findings = self._analyze_training(adoption_info, company_name)
        findings.extend(training_findings)
        
        community_findings = self._analyze_community(adoption_info, company_name)
        findings.extend(community_findings)
        
        # Determine status and score
        status, score = self._determine_status_and_score(findings)
        
        # Generate notes
        notes = self._generate_adoption_notes(findings, company_name)
        
        # Generate management-friendly summary
        summary = self._generate_executive_summary(findings, score, company_name, impl_findings, status)
        
        # Extract key strengths and risks
        strengths = [f for f in findings if any(kw in f.lower() for kw in ["24/7", "comprehensive", "excellent", "extensive", "certification", "training"])][:4]
        risks = [f for f in findings if any(kw in f.lower() for kw in ["limited", "not", "unable", "unclear", "unavailable", "poor"])][:4]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(status, company_name, risks)
        
        # Create structured output
        output = self.create_structured_output(
            score=score,
            findings=findings,
            notes=notes,
            summary=summary,
            strengths=strengths,
            risks=risks,
            status=status,
            recommendations=recommendations,
            timeline=self._extract_timeline(impl_findings)
        )
        
        self.emit_event("agent_complete", {
            "status": "completed",
            "dimension_status": status,
            "score": score if score is not None else "N/A",
            "summary": summary,
            "findings_count": len(findings),
            "sources_count": len(self.sources)
        })
        
        return output
    
    def _determine_status_and_score(self, findings: List[str]) -> tuple[str, Optional[float]]:
        """Determine status and score based on adoption support quality."""
        official_sources = [s for s in self.sources if s.get("credibility") == "official"]
        
        # No reliable sources = insufficient data
        if len(self.sources) == 0 or len(official_sources) == 0:
            return ("insufficient_data", None)
        
        positive = [f for f in findings if any(kw in f.lower() for kw in ["24/7", "comprehensive", "excellent", "extensive", "robust", "available", "certification", "training"])]
        negative = [f for f in findings if any(kw in f.lower() for kw in ["limited", "not", "unable", "unclear", "unavailable", "poor"])]
        
        # Mostly negative = risk
        if len(negative) > len(positive):
            return ("risk", 1.5)
        
        # Some positive = ok
        if len(positive) > 0:
            score = (len(positive) - len(negative) * 0.5) / len(findings) * 5.0
            return ("ok", max(2.0, min(5.0, score)))
        
        return ("insufficient_data", None)
    
    def _generate_recommendations(self, status: str, vendor_name: str, risks: List[str]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if status == "insufficient_data":
            recommendations.append(
                f"Request {vendor_name} customer success program details, implementation timeline, and support SLAs"
            )
            recommendations.append(
                "Obtain training materials, certification programs, and documentation quality samples"
            )
            recommendations.append(
                "Schedule implementation workshop with vendor to assess onboarding complexity"
            )
        elif status == "risk":
            recommendations.append(
                f"{vendor_name} adoption support appears limited - plan for extensive internal training and change management"
            )
            for risk in risks[:2]:
                recommendations.append(f"Mitigate: {risk}")
        else:  # ok
            recommendations.append(
                f"Validate {vendor_name} support SLAs and escalation procedures"
            )
            if risks:
                recommendations.append(f"Clarify: {'; '.join(risks[:2])}")
        
        return recommendations[:4]
    
    def _analyze_implementation(self, info: str, vendor_name: str) -> List[str]:
        """Analyze implementation timeline and complexity."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s implementation timeline and process:

{info[:3000]}

Identify:
1. Typical implementation timeline (weeks/months)
2. Deployment complexity (simple, moderate, complex)
3. Data migration process
4. Configuration requirements
5. Time to value

Return JSON: {{"implementation_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing implementation with LLM"})
            result = self._call_llm_json(prompt, "You are a customer success expert. Return valid JSON only.")
            impl_findings = result.get("implementation_findings", [])
            
            if impl_findings:
                findings.extend(impl_findings)
            else:
                findings.append("Implementation timeline not clearly documented - estimate 3-6 months for mid-size deployment")
                self.add_ambiguity("Implementation timeline requires vendor consultation for accurate estimate")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing implementation: {e}")
            findings.append("Unable to determine implementation timeline")
        
        return findings
    
    def _analyze_support(self, info: str, vendor_name: str) -> List[str]:
        """Analyze support availability and SLAs."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s customer support:

{info[:3000]}

Identify:
1. Support availability (24/7, business hours)
2. Support channels (phone, email, chat, portal)
3. SLA response times for different severities
4. Premium support options
5. Regional support coverage

Return JSON: {{"support_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing support with LLM"})
            result = self._call_llm_json(prompt, "You are a customer success expert. Return valid JSON only.")
            support_findings = result.get("support_findings", [])
            
            if support_findings:
                findings.extend(support_findings)
            else:
                findings.append("Support details not clearly documented")
                self.add_ambiguity("Support SLAs and availability require clarification from vendor")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing support: {e}")
            findings.append("Unable to verify support options")
        
        return findings
    
    def _analyze_training(self, info: str, vendor_name: str) -> List[str]:
        """Analyze training resources and documentation."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s training and documentation:

{info[:3000]}

Identify:
1. Documentation quality and completeness
2. Online training courses/platforms
3. Certification programs
4. Video tutorials
5. Knowledge base/help center
6. API documentation

Return JSON: {{"training_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing training with LLM"})
            result = self._call_llm_json(prompt, "You are a training specialist. Return valid JSON only.")
            training_findings = result.get("training_findings", [])
            
            if training_findings:
                findings.extend(training_findings)
            else:
                findings.append("Training resources not well documented")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing training: {e}")
            findings.append("Unable to assess training resources")
        
        return findings
    
    def _analyze_community(self, info: str, vendor_name: str) -> List[str]:
        """Analyze community and ecosystem."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s user community and ecosystem:

{info[:3000]}

Identify:
1. User community forums/groups
2. Partner ecosystem size
3. Marketplace/app directory
4. Third-party integrations availability
5. Developer community

Return JSON: {{"community_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            result = self._call_llm_json(prompt, "You are an ecosystem analyst. Return valid JSON only.")
            community_findings = result.get("community_findings", [])
            
            if community_findings:
                findings.extend(community_findings)
            else:
                findings.append("Community and ecosystem information limited")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing community: {e}")
        
        return findings
    
    def _extract_timeline(self, impl_findings: List[str]) -> str:
        """Extract implementation timeline from findings."""
        import re
        findings_text = " ".join(impl_findings)
        
        # Look for time mentions
        months_match = re.search(r'(\d+)[-–](\d+)?\s*months?', findings_text, re.IGNORECASE)
        if months_match:
            low = months_match.group(1)
            high = months_match.group(2) if months_match.group(2) else low
            return f"{low}-{high} months"
        
        weeks_match = re.search(r'(\d+)[-–](\d+)?\s*weeks?', findings_text, re.IGNORECASE)
        if weeks_match:
            low = weeks_match.group(1)
            high = weeks_match.group(2) if weeks_match.group(2) else low
            return f"{low}-{high} weeks"
        
        return "3-6 months (estimated)"
    
    def _calculate_adoption_score(self, findings: List[str]) -> float:
        """Calculate adoption score based on support/training quality."""
        if not findings:
            return 2.0
        
        positive_keywords = [
            "24/7", "comprehensive", "excellent", "extensive", "robust", "available",
            "certification", "training", "documentation", "community", "support"
        ]
        negative_keywords = ["limited", "not", "unable", "unclear", "unavailable", "poor"]
        
        positive_count = sum(1 for f in findings if any(kw in f.lower() for kw in positive_keywords))
        negative_count = sum(1 for f in findings if any(kw in f.lower() for kw in negative_keywords))
        
        score = (positive_count - negative_count * 0.5) / len(findings) * 5.0
        return max(1.0, min(5.0, score))
    
    def _generate_adoption_notes(self, findings: List[str], vendor_name: str) -> str:
        """Generate summary notes."""
        if len(self.sources) == 0:
            return f"Limited adoption information available for {vendor_name}. Support, training, and implementation details require direct vendor consultation."
        
        return f"Adoption assessment based on {len(self.sources)} sources. {len(findings)} factors evaluated. Training and support resources {'well-documented' if len(self.sources) >= 3 else 'partially documented'}. Confidence: {self._calculate_confidence()}"
    
    def _generate_executive_summary(self, findings: List[str], score: Optional[float], vendor_name: str, impl_findings: List[str], status: str) -> str:
        """Generate a 2-3 sentence executive summary suitable for management."""
        timeline = self._extract_timeline(impl_findings)
        support_count = sum(1 for f in findings if "support" in f.lower() or "training" in f.lower())
        
        # Handle insufficient data
        if status == "insufficient_data":
            official_sources = [s for s in self.sources if s.get("credibility") == "official"]
            if len(self.sources) == 0:
                return f"⚠️ **Insufficient public data** - Adoption resources for {vendor_name} not accessible in public documentation. Support plans, training materials, implementation timelines, and customer success programs must be obtained directly from vendor."
            elif len(official_sources) == 0:
                return f"⚠️ **Insufficient public data** - Found {len(self.sources)} community sources for {vendor_name}, but no official support documentation. Cannot verify implementation timeline or training resources without official materials."
            else:
                return f"⚠️ **Insufficient public data** - {vendor_name} has limited adoption resources with {timeline} estimated timeline. Plan for significant internal training development and extended onboarding period."
        
        # Handle risk
        if status == "risk":
            return f"🔴 **High Risk** - {vendor_name} adoption posture is concerning with minimal training resources and unclear implementation support. High organizational risk for {timeline} deployment without substantial internal resources and vendor-led professional services."
        
        # Handle OK cases
        if score and score >= 4.0:
            return f"✅ {vendor_name} provides excellent adoption support with comprehensive training resources, {timeline} implementation timeline, and strong customer success programs. Low organizational change risk with well-documented onboarding path."
        elif score and score >= 3.0:
            return f"✅ {vendor_name} offers solid adoption resources with {support_count} documented support and training options. Implementation timeline of {timeline} is reasonable, though some organizational change management will be required."
        else:
            return f"⚠️ {vendor_name} has basic adoption resources. {timeline} implementation timeline; some organizational change management required."
