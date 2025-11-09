"""
Compliance & Data Usage Agent - Compliance Officer
Enhanced with multi-step RAG for thorough compliance research
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any, List, Optional


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
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate compliance using single comprehensive search (saves API quota).
        """
        vendor = context.get("vendor", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        
        print(f"[{self.name}] Analyzing compliance for {company_name}...")
        self.emit_event("agent_start", {"status": "starting", "vendor": company_name})
        
        # Single comprehensive compliance search (instead of 4 separate searches)
        findings = []
        
        # ONE comprehensive compliance query
        self.emit_event("agent_thinking", {"action": "Researching comprehensive compliance"})
        compliance_info = await self.research_requirement(
            f"{company_name} SOC2 ISO27001 ISO27017 ISO27018 security certifications "
            f"GDPR CCPA HIPAA privacy compliance data protection "
            f"data retention policy data deletion data ownership "
            f"SSO SAML encryption audit logs RBAC MFA",
            company_name,
            website
        )
        
        # Analyze all aspects from the single search
        cert_findings = self._analyze_certifications(compliance_info, company_name)
        findings.extend(cert_findings)
        
        privacy_findings = self._analyze_privacy(compliance_info, company_name)
        findings.extend(privacy_findings)
        
        data_findings = self._analyze_data_handling(compliance_info, company_name)
        findings.extend(data_findings)
        
        security_findings = self._analyze_security_features(compliance_info, company_name)
        findings.extend(security_findings)
        
        # Determine status and score based on evidence quality
        status, score = self._determine_status_and_score(findings)
        
        # Generate comprehensive notes
        notes = self._generate_compliance_notes(findings, company_name)
        
        # Generate management-friendly summary
        summary = self._generate_executive_summary(findings, score, company_name, status)
        
        # Extract key strengths and risks for quick scanning
        strengths = [f for f in findings if any(kw in f.lower() for kw in ["certified", "compliant", "supports", "provides"])][:4]
        risks = [f for f in findings if any(kw in f.lower() for kw in ["not", "unable", "unclear", "unavailable", "no"])][:4]
        
        # Generate recommendations based on status
        recommendations = self._generate_recommendations(status, company_name, risks)
        
        # NEW: Determine requirement alignment from org_policy
        org_policy = context.get("org_policy", {})
        compliance_reqs = org_policy.get("compliance_needs", [])
        security_reqs = org_policy.get("security_needs", [])
        all_reqs = compliance_reqs + security_reqs
        
        # Check which requirements are met based on findings AND source content
        normalized_findings = " ".join(findings).lower()
        
        # Also check source content directly as fallback (in case LLM didn't extract properly)
        normalized_sources = " ".join([
            s.get("content", "").lower()[:5000]  # First 5000 chars per source
            for s in self.sources
        ])
        # Combine findings and sources for more comprehensive matching
        combined_content = normalized_findings + " " + normalized_sources
        
        requirements_alignment = {}
        unmet_requirements = []
        
        # Common variations mapping for certifications and standards
        variations_map = {
            "soc 2 type ii": ["soc2", "soc 2", "soc2 type", "soc type ii", "soc 2 type 2", "soc 2 (type Ⅱ)"],
            "sso/saml": ["sso", "saml", "saml 2.0", "single sign-on", "single sign on"],
            "iso 27001": ["iso27001", "iso/iec 27001", "iso/iec27001", "iso 27001:2013"],
            "gdpr": ["general data protection regulation", "eu gdpr"],
            "mfa": ["multi-factor", "multifactor", "two-factor", "2fa", "two factor"],
            "rbac": ["role-based", "role based", "role based access", "role-based access control"],
            "dpa (data processing agreement)": ["dpa", "data processing agreement", "data processing addendum"],
            "encryption at rest and in transit": ["encryption", "encrypted", "tls", "ssl", "aes-256", "encryption at rest", "encryption in transit"],
            "audit logs": ["audit log", "audit logging", "audit trail", "audit trail logs"]
        }
        
        for req in all_reqs:
            req_lower = req.lower()
            matched = False
            
            # Normalize common variations in requirement text
            normalized_req = req_lower.replace("soc2", "soc 2").replace("type Ⅱ", "type ii").replace("type 2", "type ii")
            
            # Strategy 1: Handle "/" separator (e.g., "SSO/SAML")
            if "/" in normalized_req:
                parts = [p.strip() for p in normalized_req.split("/")]
                # Check if any part appears in findings OR source content
                matched = any(
                    part in combined_content 
                    for part in parts 
                    if len(part) > 2
                )
            
            # Strategy 2: Check variations map for known patterns
            if not matched:
                req_normalized = normalized_req.replace("(", "").replace(")", "").replace("/", " ").strip()
                if req_normalized in variations_map:
                    matched = any(var in combined_content for var in variations_map[req_normalized])
            
            # Strategy 3: Phrase matching for multi-word requirements
            if not matched and len(normalized_req.split()) > 1:
                # Remove special chars and split into meaningful parts
                phrase = normalized_req.replace("(", "").replace(")", "").replace("/", " ").replace("-", " ")
                key_parts = [p for p in phrase.split() if len(p) > 2]  # Get meaningful words (> 2 chars)
                
                if len(key_parts) >= 2:
                    # Check if at least 2 key parts appear in findings OR source content
                    matches = sum(1 for part in key_parts if part in combined_content)
                    if matches >= min(2, len(key_parts)):  # At least 2 parts or all if < 2
                        matched = True
            
            # Strategy 4: Individual keyword matching (lower threshold to catch acronyms)
            if not matched:
                req_keywords = normalized_req.replace("(", "").replace(")", "").replace("/", " ").split()
                # Lower threshold to 2 chars to catch "SOC", "SSO", "MFA", "RBAC", etc.
                meaningful_keywords = [kw for kw in req_keywords if len(kw) > 2]
                if meaningful_keywords:
                    matched = any(keyword in combined_content for keyword in meaningful_keywords)
            
            if matched:
                requirements_alignment[req] = "met"
            else:
                requirements_alignment[req] = "unmet"
                unmet_requirements.append(req)
        
        # Generate remediation steps for unmet requirements
        remediation_steps = []
        if "SOC 2 Type II" in unmet_requirements:
            remediation_steps.append("Provide SOC 2 Type II attestation or undergo audit with accredited third-party auditor")
        if "ISO 27001" in unmet_requirements:
            remediation_steps.append("Provide current ISO 27001 certificate and Statement of Applicability (SoA)")
        if "GDPR" in unmet_requirements:
            remediation_steps.append("Document GDPR compliance measures and provide Data Protection Impact Assessment (DPIA)")
        if "DPA (Data Processing Agreement)" in unmet_requirements:
            remediation_steps.append("Provide signed DPA template addressing data ownership, retention, and deletion policies")
        if "SSO/SAML" in unmet_requirements:
            remediation_steps.append("Implement SAML 2.0 SSO support and provide integration documentation")
        if "Encryption at rest and in transit" in unmet_requirements:
            remediation_steps.append("Document encryption standards (AES-256, TLS 1.2+) and provide security architecture diagram")
        if "Audit logs" in unmet_requirements:
            remediation_steps.append("Enable comprehensive audit logging with tamper-proof storage and provide log retention policy")
        if "RBAC" in unmet_requirements:
            remediation_steps.append("Implement Role-Based Access Control with granular permissions and provide RBAC matrix")
        if "MFA" in unmet_requirements:
            remediation_steps.append("Implement Multi-Factor Authentication for all user accounts and provide MFA enforcement policy")
        
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
            requirements_alignment=requirements_alignment,
            unmet_requirements=unmet_requirements,
            remediation_steps=remediation_steps
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
        """
        Determine dimension status and score based on evidence quality.
        
        Returns:
            Tuple of (status, score) where status is "ok"/"insufficient_data"/"risk"
            and score is 0-5 or None for insufficient data
        """
        # Count official sources (most reliable)
        official_sources = [s for s in self.sources if s.get("credibility") == "official"]
        
        # Check if we have NO reliable sources at all
        if len(self.sources) == 0 or len(official_sources) == 0:
            return ("insufficient_data", None)
        
        # Analyze positive vs negative findings
        positive = [f for f in findings if any(kw in f.lower() for kw in ["certified", "compliant", "supports", "provides", "available"])]
        negative = [f for f in findings if any(kw in f.lower() for kw in ["not", "unable", "unclear", "unavailable", "no"])]
        
        # If we have mostly negative findings with official sources, this is RISK
        if len(negative) > len(positive) and len(official_sources) >= 1:
            score = 1.5
            return ("risk", score)
        
        # If we have positive findings, this is OK
        if len(positive) > 0:
            # Calculate score based on positive/negative ratio
            if len(positive) >= 4 and len(negative) == 0:
                score = 4.5
            elif len(positive) >= 3 and len(negative) <= 1:
                score = 3.5
            elif len(positive) >= 2:
                score = 3.0
            else:
                score = 2.5
            return ("ok", score)
        
        # Mixed or unclear - insufficient data
        return ("insufficient_data", None)
    
    def _generate_recommendations(self, status: str, vendor_name: str, risks: List[str]) -> List[str]:
        """Generate actionable recommendations based on status."""
        recommendations = []
        
        if status == "insufficient_data":
            recommendations.append(
                f"Request formal security & compliance pack from {vendor_name} (SOC 2 Type II, ISO 27001, DPA, data retention policies)"
            )
            recommendations.append(
                "Do not proceed with vendor selection until official compliance documentation is reviewed"
            )
            recommendations.append(
                "Schedule security review call with vendor to clarify compliance posture"
            )
        elif status == "risk":
            recommendations.append(
                f"Conduct formal security assessment of {vendor_name} before any procurement decision"
            )
            for risk in risks[:2]:  # Top 2 risks
                recommendations.append(f"Remediation required: {risk}")
            recommendations.append(
                "Consider alternative vendors with stronger compliance documentation"
            )
        else:  # ok
            recommendations.append(
                f"Verify {vendor_name} certifications directly (request latest audit reports)"
            )
            if risks:
                recommendations.append(
                    f"Clarify remaining gaps: {'; '.join(risks[:2])}"
                )
            recommendations.append(
                "Include compliance requirements in contract SLA"
            )
        
        return recommendations[:4]  # Max 4 recommendations
    
    def _analyze_certifications(self, info: str, vendor_name: str) -> List[str]:
        """Analyze certification information."""
        findings = []
        
        # Use LLM to extract certification details
        prompt = f"""Analyze this documentation about {vendor_name}'s security certifications:

{info[:3000]}

Extract specific certifications found. Use standard terminology:
- "SOC 2 Type II" (not "SOC2" or "SOC2 Type 2")
- "ISO 27001" (not "ISO27001")
- "SSO" or "SAML" for authentication
- "GDPR" for privacy compliance

List each certification found with a brief description. Include the exact certification name as it appears in the documentation.

Return JSON: {{"certifications": ["SOC 2 Type II: description", "ISO 27001: description", ...]}}
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

Identify and list each feature found. Use standard terminology:
1. SSO support (mention "SSO" or "SAML" or "SAML 2.0" if found)
2. Encryption (at rest, in transit)
3. Audit logging capabilities (mention "audit logs" or "audit logging")
4. Role-based access control (mention "RBAC" or "role-based access")
5. Multi-factor authentication (mention "MFA" or "multi-factor")

Return JSON: {{"security_features": ["SSO support via SAML 2.0", "Encryption at rest and in transit", ...]}}
Be specific and include the exact terminology used in the documentation.
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
    
    def _generate_executive_summary(self, findings: List[str], score: Optional[float], vendor_name: str, status: str) -> str:
        """Generate a 2-3 sentence executive summary suitable for management."""
        # Count positive vs negative findings
        positive = [f for f in findings if any(kw in f.lower() for kw in ["certified", "compliant", "supports", "provides", "available"])]
        negative = [f for f in findings if any(kw in f.lower() for kw in ["not", "unable", "unclear", "unavailable", "no"])]
        
        # Handle insufficient data case explicitly
        if status == "insufficient_data":
            official_sources = [s for s in self.sources if s.get("credibility") == "official"]
            if len(self.sources) == 0:
                return f"⚠️ **Insufficient public data** - Could not access compliance documentation for {vendor_name}. No reliable information about SOC 2, ISO 27001, or data handling practices could be verified from public sources. Formal security and compliance pack must be requested directly from vendor before evaluation can proceed."
            elif len(official_sources) == 0:
                return f"⚠️ **Insufficient public data** - Found {len(self.sources)} community/third-party sources for {vendor_name}, but no official compliance documentation. Cannot verify security certifications or data handling policies without official attestations. Request vendor's security pack (SOC 2 Type II, ISO 27001, DPA) for accurate assessment."
            else:
                return f"⚠️ **Insufficient public data** - Limited official documentation found for {vendor_name}. {len(negative)} critical gaps identified that require clarification. Cannot make safe recommendation without complete compliance picture."
        
        # Handle risk case
        if status == "risk":
            return f"🔴 **High Risk** - {vendor_name} compliance posture shows {len(negative)} significant concerns with minimal verifiable security controls ({len(positive)} positive findings). Not recommended for regulated financial services without substantial remediation and formal security assessment."
        
        # Handle OK cases (score-based)
        if score and score >= 4.0:
            return f"✅ {vendor_name} demonstrates strong compliance posture with {len(positive)} verified security controls and certifications. Documentation is comprehensive and confidence is high for enterprise deployment."
        elif score and score >= 3.0:
            return f"✅ {vendor_name} meets basic compliance requirements with {len(positive)} documented controls, though {len(negative)} gaps require clarification before deployment in a regulated environment."
        else:
            return f"⚠️ {vendor_name} shows limited compliance documentation with only {len(positive)} verified controls and {len(negative)} gaps. Formal security review required before consideration."
