"""
Compliance & Data Usage Agent - Compliance Officer
Enhanced with multi-step RAG for thorough compliance research
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any, List


class ComplianceAgent(BaseAgent):
    """
    Agent 3: Compliance & Data Usage Agent
    
    Evaluates:
    - Security certifications (SOC2, ISO27001, etc.)
    - Privacy compliance (GDPR, CCPA, HIPAA)
    - Data handling (ownership, retention, deletion)
    - Security features (SSO, encryption, audit logs)
    """
    
    def __init__(self, event_callback=None):
        super().__init__("ComplianceAgent", "Compliance Officer", event_callback)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate compliance using enhanced RAG with multi-step research.
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        
        print(f"[{self.name}] Analyzing compliance for {company_name}...")
        self.emit_event("agent_start", {"status": "starting", "vendor": company_name})
        
        # Research compliance requirements systematically
        findings = []
        
        # 1. Security Certifications
        self.emit_event("agent_thinking", {"action": "Researching security certifications"})
        cert_info = self.research_requirement(
            f"{company_name} SOC2 ISO27001 ISO27017 ISO27018 security certifications",
            company_name,
            website
        )
        cert_findings = self._analyze_certifications(cert_info, company_name)
        findings.extend(cert_findings)
        
        # 2. Privacy & Regulatory Compliance
        self.emit_event("agent_thinking", {"action": "Researching privacy compliance"})
        privacy_info = self.research_requirement(
            f"{company_name} GDPR CCPA HIPAA privacy compliance data protection",
            company_name,
            website
        )
        privacy_findings = self._analyze_privacy(privacy_info, company_name)
        findings.extend(privacy_findings)
        
        # 3. Data Handling & Retention
        self.emit_event("agent_thinking", {"action": "Researching data handling policies"})
        data_info = self.research_requirement(
            f"{company_name} data retention policy data deletion data ownership customer data",
            company_name,
            website
        )
        data_findings = self._analyze_data_handling(data_info, company_name)
        findings.extend(data_findings)
        
        # 4. Security Features (SSO, Encryption, Audit Logs)
        self.emit_event("agent_thinking", {"action": "Researching security features"})
        security_info = self.research_requirement(
            f"{company_name} SSO SAML encryption audit logs role-based access control RBAC",
            company_name,
            website
        )
        security_findings = self._analyze_security_features(security_info, company_name)
        findings.extend(security_findings)
        
        # Calculate score based on findings
        score = self._calculate_compliance_score(findings)
        
        # Generate comprehensive notes
        notes = self._generate_compliance_notes(findings, company_name)
        
        # Create structured output
        output = self.create_structured_output(
            score=score,
            findings=findings,
            notes=notes
        )
        
        self.emit_event("agent_complete", {
            "status": "completed",
            "score": score,
            "findings_count": len(findings),
            "sources_count": len(self.sources)
        })
        
        return output
    
    def _analyze_certifications(self, info: str, vendor_name: str) -> List[str]:
        """Analyze certification information."""
        findings = []
        
        # Use LLM to extract certification details
        prompt = f"""Analyze this documentation about {vendor_name}'s security certifications:

{info[:3000]}

Extract specific certifications found (SOC2 Type II, ISO27001, ISO27017, ISO27018, PCI-DSS, FedRAMP, etc.).
List each certification found with a brief description.

Return JSON: {{"certifications": ["cert1: description", "cert2: description", ...]}}
If no certifications found, return empty list.
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing certifications with LLM"})
            result = self._call_llm_json(prompt, "You are a compliance analyst. Return valid JSON only.")
            certs = result.get("certifications", [])
            
            if certs:
                findings.extend(certs)
            else:
                findings.append("No specific security certifications documented in accessible sources")
                self.add_ambiguity("Security certifications not verified - official attestations may exist but were not accessible")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing certifications: {e}")
            findings.append("Unable to verify security certifications")
        
        return findings
    
    def _analyze_privacy(self, info: str, vendor_name: str) -> List[str]:
        """Analyze privacy and regulatory compliance."""
        findings = []
        
        prompt = f"""Analyze this documentation about {vendor_name}'s privacy and regulatory compliance:

{info[:3000]}

Identify:
1. GDPR compliance features (data subject rights, BCRs, DPA)
2. CCPA compliance
3. HIPAA provisions (BAA availability)
4. Data residency options (US, EU, etc.)

Return JSON: {{"privacy_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing privacy compliance with LLM"})
            result = self._call_llm_json(prompt, "You are a privacy compliance analyst. Return valid JSON only.")
            privacy_findings = result.get("privacy_findings", [])
            
            if privacy_findings:
                findings.extend(privacy_findings)
            else:
                findings.append("Privacy compliance details not clearly documented")
                self.add_ambiguity("Regulatory compliance (GDPR/CCPA/HIPAA) requires vendor verification")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing privacy: {e}")
            findings.append("Unable to verify privacy compliance")
        
        return findings
    
    def _analyze_data_handling(self, info: str, vendor_name: str) -> List[str]:
        """Analyze data handling and retention policies."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s data handling policies from this documentation:

{info[:3000]}

Identify:
1. Data ownership (who owns customer data)
2. Data retention periods
3. Data deletion after contract termination
4. Backup and recovery policies

Return JSON: {{"data_handling_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing data handling with LLM"})
            result = self._call_llm_json(prompt, "You are a data governance analyst. Return valid JSON only.")
            data_findings = result.get("data_handling_findings", [])
            
            if data_findings:
                findings.extend(data_findings)
            else:
                findings.append("Data handling policies not clearly documented")
                self.add_ambiguity("Data retention and deletion policies require clarification from vendor")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing data handling: {e}")
            findings.append("Unable to verify data handling policies")
        
        return findings
    
    def _analyze_security_features(self, info: str, vendor_name: str) -> List[str]:
        """Analyze security features."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s security features from this documentation:

{info[:3000]}

Identify:
1. SSO support (SAML, OAuth, SCIM)
2. Encryption (at rest, in transit)
3. Audit logging capabilities
4. Role-based access control (RBAC)
5. Multi-factor authentication (MFA)

Return JSON: {{"security_features": ["feature1", "feature2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing security features with LLM"})
            result = self._call_llm_json(prompt, "You are a security analyst. Return valid JSON only.")
            sec_findings = result.get("security_features", [])
            
            if sec_findings:
                findings.extend(sec_findings)
            else:
                findings.append("Security features not clearly documented")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing security features: {e}")
            findings.append("Unable to verify security features")
        
        return findings
    
    def _calculate_compliance_score(self, findings: List[str]) -> float:
        """Calculate compliance score based on findings."""
        # Simple heuristic: more positive findings = higher score
        positive_keywords = ["certified", "compliant", "supports", "provides", "available", "certified", "attestation"]
        negative_keywords = ["not", "unable", "no", "unclear", "unavailable"]
        
        positive_count = sum(1 for f in findings if any(kw in f.lower() for kw in positive_keywords))
        negative_count = sum(1 for f in findings if any(kw in f.lower() for kw in negative_keywords))
        
        total_findings = len(findings)
        if total_findings == 0:
            return 1.0
        
        # Score: weighted by positive vs negative findings
        score = (positive_count * 1.0 - negative_count * 0.5) / total_findings * 5.0
        return max(0.0, min(5.0, score))
    
    def _generate_compliance_notes(self, findings: List[str], vendor_name: str) -> str:
        """Generate summary notes for compliance evaluation."""
        if len(self.sources) == 0:
            return f"Limited compliance information available for {vendor_name}. Official documentation was not accessible or did not contain detailed compliance data. Recommend requesting security questionnaire and attestations directly from vendor."
        
        official_sources = [s for s in self.sources if s.get("credibility") == "official"]
        
        if len(official_sources) >= 2:
            return f"Compliance evaluation based on {len(official_sources)} official sources. {len(findings)} specific findings documented. Confidence: {self._calculate_confidence()}"
        else:
            return f"Compliance evaluation based on {len(self.sources)} sources ({len(official_sources)} official). {len(findings)} findings. Additional verification recommended."
