"""
Adoption & Support Agent - Customer Success Manager
Enhanced with multi-step RAG for support and implementation research
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any, List


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
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate adoption factors using enhanced RAG.
        """
        vendor = context.get("vendor", {})
        evaluation = context.get("evaluation", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        use_case = evaluation.get("use_case", "")
        
        print(f"[{self.name}] Analyzing adoption for {company_name}...")
        self.emit_event("agent_start", {"status": "starting", "vendor": company_name})
        
        findings = []
        
        # 1. Implementation timeline
        self.emit_event("agent_thinking", {"action": "Researching implementation timeline"})
        impl_info = self.research_requirement(
            f"{company_name} implementation timeline deployment time to value onboarding",
            company_name,
            website
        )
        impl_findings = self._analyze_implementation(impl_info, company_name)
        findings.extend(impl_findings)
        
        # 2. Support availability
        self.emit_event("agent_thinking", {"action": "Researching support options"})
        support_info = self.research_requirement(
            f"{company_name} customer support 24/7 support SLA response time",
            company_name,
            website
        )
        support_findings = self._analyze_support(support_info, company_name)
        findings.extend(support_findings)
        
        # 3. Training and documentation
        self.emit_event("agent_thinking", {"action": "Researching training resources"})
        training_info = self.research_requirement(
            f"{company_name} training documentation certification courses learning resources",
            company_name,
            website
        )
        training_findings = self._analyze_training(training_info, company_name)
        findings.extend(training_findings)
        
        # 4. Community and ecosystem
        self.emit_event("agent_thinking", {"action": "Researching community"})
        community_info = self.research_requirement(
            f"{company_name} user community forum partner ecosystem marketplace",
            company_name,
            website
        )
        community_findings = self._analyze_community(community_info, company_name)
        findings.extend(community_findings)
        
        # Calculate score
        score = self._calculate_adoption_score(findings)
        
        # Generate notes
        notes = self._generate_adoption_notes(findings, company_name)
        
        # Create structured output
        output = self.create_structured_output(
            score=score,
            findings=findings,
            notes=notes,
            timeline=self._extract_timeline(impl_findings)
        )
        
        self.emit_event("agent_complete", {
            "status": "completed",
            "score": score,
            "findings_count": len(findings),
            "sources_count": len(self.sources)
        })
        
        return output
    
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
