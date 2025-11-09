"""
Interoperability Agent - Integration Architect
Enhanced with multi-step RAG for thorough integration research
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any, List, Optional


class InteroperabilityAgent(BaseAgent):
    """
    Agent 4: Interoperability Agent
    
    Evaluates:
    - SSO/Authentication integration (SAML, OAuth, Okta)
    - APIs (REST, GraphQL, SOAP)
    - Webhooks and event systems
    - Out-of-box integrations (Slack, Jira, etc.)
    - Data integration (Snowflake, analytics)
    """
    
    def __init__(self, event_callback=None):
        super().__init__("InteroperabilityAgent", "Integration Architect", event_callback)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate technical integration capabilities using single comprehensive search.
        """
        vendor = context.get("vendor", {})
        evaluation = context.get("evaluation", {})
        company_name = vendor.get("name", "Unknown")
        website = vendor.get("website", "")
        use_case = evaluation.get("use_case", "")
        
        print(f"[{self.name}] Analyzing integrations for {company_name}...")
        self.emit_event("agent_start", {"status": "starting", "vendor": company_name})
        
        findings = []
        
        # Extract required integrations from use case
        required_integrations = self._extract_integration_requirements(use_case)
        
        # Build comprehensive query including specific integrations from use case
        specific_integrations = []
        if use_case:
            if "slack" in use_case.lower():
                specific_integrations.append("Slack")
            if "jira" in use_case.lower():
                specific_integrations.append("Jira")
            if "snowflake" in use_case.lower():
                specific_integrations.append("Snowflake")
        
        integration_str = " ".join(specific_integrations)
        
        # ONE comprehensive integration query
        self.emit_event("agent_thinking", {"action": "Researching comprehensive integration capabilities"})
        interop_info = await self.research_requirement(
            f"{company_name} SAML SSO OAuth SCIM Okta Active Directory "
            f"REST API GraphQL SOAP API documentation developer SDK "
            f"webhooks outbound events event streams notifications "
            f"{integration_str} integration marketplace",
            company_name,
            website
        )
        
        # Analyze all aspects from the single search
        sso_findings = self._analyze_sso(interop_info, company_name, required_integrations)
        findings.extend(sso_findings)
        
        api_findings = self._analyze_apis(interop_info, company_name)
        findings.extend(api_findings)
        
        webhook_findings = self._analyze_webhooks(interop_info, company_name)
        findings.extend(webhook_findings)
        
        # Analyze specific integrations if mentioned
        for integration in specific_integrations:
            findings.extend(self._analyze_specific_integration(interop_info, company_name, integration))
        
        # Determine status and score
        status, score = self._determine_status_and_score(findings, required_integrations)
        
        # Generate notes
        notes = self._generate_interoperability_notes(findings, company_name, required_integrations)
        
        # Generate management-friendly summary
        summary = self._generate_executive_summary(findings, score, company_name, required_integrations, status)
        
        # Extract key strengths and risks
        strengths = [f for f in findings if any(kw in f.lower() for kw in ["supports", "available", "native", "comprehensive", "documented"])][:4]
        risks = [f for f in findings if any(kw in f.lower() for kw in ["not", "unable", "unclear", "unavailable", "undocumented"])][:4]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(status, company_name, risks, required_integrations)
        
        # NEW: Determine requirement alignment from org_policy
        org_policy = context.get("org_policy", {})
        interop_targets = org_policy.get("interoperability_targets", [])
        
        # Check which integration targets are met based on findings
        normalized_findings = " ".join(findings).lower()
        requirements_alignment = {}
        unmet_requirements = []
        
        for target in interop_targets:
            target_lower = target.lower()
            # Check if integration target is mentioned in findings
            target_keywords = target_lower.replace("integration", "").strip().split()
            matched = any(keyword in normalized_findings for keyword in target_keywords if len(keyword) > 2)
            
            if matched:
                requirements_alignment[target] = "met"
            else:
                requirements_alignment[target] = "unmet"
                unmet_requirements.append(target)
        
        # Generate remediation steps for unmet integration targets
        remediation_steps = []
        if "Okta SSO" in unmet_requirements:
            remediation_steps.append("Implement Okta SSO integration using SAML 2.0 or OAuth 2.0 and provide setup documentation")
        if "REST API" in unmet_requirements:
            remediation_steps.append("Develop comprehensive REST API with documentation, rate limits, and authentication mechanisms")
        if "Webhooks" in unmet_requirements:
            remediation_steps.append("Implement outbound webhooks for event notifications with configurable endpoints and retry logic")
        if "Jira integration" in unmet_requirements or "Jira" in unmet_requirements:
            remediation_steps.append("Build native Jira integration or provide detailed API documentation for custom integration")
        if "ServiceNow integration" in unmet_requirements or "ServiceNow" in unmet_requirements:
            remediation_steps.append("Develop ServiceNow integration app or provide connector documentation for bi-directional sync")
        
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
            remediation_steps=remediation_steps,
            apis=self._extract_api_types(api_findings)
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
    
    def _determine_status_and_score(self, findings: List[str], requirements: List[str]) -> tuple[str, Optional[float]]:
        """
        Determine dimension status and score based on evidence quality.
        
        Returns:
            Tuple of (status, score) where status is "ok"/"insufficient_data"/"risk"
        """
        official_sources = [s for s in self.sources if s.get("credibility") == "official"]
        
        # No reliable sources = insufficient data
        if len(self.sources) == 0 or len(official_sources) == 0:
            return ("insufficient_data", None)
        
        positive = [f for f in findings if any(kw in f.lower() for kw in ["supports", "available", "provides", "native", "comprehensive", "documented"])]
        negative = [f for f in findings if any(kw in f.lower() for kw in ["not", "unable", "unclear", "unavailable", "undocumented"])]
        
        # Check if critical requirements are met
        if requirements:
            requirements_met = sum(1 for req in requirements if any(req.lower() in f.lower() for f in findings))
            requirements_ratio = requirements_met / len(requirements)
        else:
            requirements_ratio = 1.0  # No specific requirements
        
        # Mostly negative findings + missing requirements = risk
        if len(negative) > len(positive) and requirements_ratio < 0.5:
            return ("risk", 1.5)
        
        # Some positive findings = ok
        if len(positive) > 0:
            base_score = (len(positive) - len(negative) * 0.5) / len(findings) * 4.0
            requirement_bonus = requirements_ratio * 1.0
            score = base_score + requirement_bonus
            return ("ok", max(2.0, min(5.0, score)))
        
        # Not enough info
        return ("insufficient_data", None)
    
    def _generate_recommendations(self, status: str, vendor_name: str, risks: List[str], requirements: List[str]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if status == "insufficient_data":
            recommendations.append(
                f"Request API documentation, integration guides, and SSO setup instructions from {vendor_name}"
            )
            if requirements:
                recommendations.append(
                    f"Verify specific integrations: {', '.join(requirements[:3])}"
                )
            recommendations.append(
                "Schedule technical workshop with vendor to validate integration capabilities"
            )
        elif status == "risk":
            recommendations.append(
                f"Conduct comprehensive integration proof-of-concept before committing to {vendor_name}"
            )
            for risk in risks[:2]:
                recommendations.append(f"Address integration gap: {risk}")
        else:  # ok
            recommendations.append(
                f"Validate {vendor_name} API rate limits and SLAs for production use"
            )
            if risks:
                recommendations.append(f"Clarify: {'; '.join(risks[:2])}")
        
        return recommendations[:4]
    
    def _extract_integration_requirements(self, use_case: str) -> List[str]:
        """Extract specific integration requirements from use case."""
        if not use_case:
            return []  # No requirements if use_case is empty
        
        requirements = []
        use_case_lower = use_case.lower()
        
        integration_keywords = {
            "okta": "Okta SSO",
            "slack": "Slack",
            "jira": "Jira",
            "snowflake": "Snowflake",
            "o365": "Office 365",
            "email": "Email",
            "api": "API",
            "sso": "SSO",
            "webhook": "Webhooks"
        }
        
        for keyword, requirement in integration_keywords.items():
            if keyword in use_case_lower:
                requirements.append(requirement)
        
        return requirements
    
    def _analyze_sso(self, info: str, vendor_name: str, requirements: List[str]) -> List[str]:
        """Analyze SSO capabilities."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s SSO and authentication capabilities:

{info[:3000]}

Identify:
1. SAML 2.0 support
2. OAuth support
3. SCIM provisioning
4. Okta integration (if mentioned)
5. Active Directory integration

Return JSON: {{"sso_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing SSO with LLM"})
            result = self._call_llm_json(prompt, "You are an integration architect. Return valid JSON only.")
            sso_findings = result.get("sso_findings", [])
            
            if sso_findings:
                findings.extend(sso_findings)
            else:
                findings.append("SSO capabilities not clearly documented")
                self.add_ambiguity("SSO support (SAML/OAuth) requires vendor confirmation")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing SSO: {e}")
            findings.append("Unable to verify SSO capabilities")
        
        return findings
    
    def _analyze_apis(self, info: str, vendor_name: str) -> List[str]:
        """Analyze API capabilities."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s API capabilities:

{info[:3000]}

Identify:
1. REST API availability and version
2. GraphQL support
3. SOAP/legacy API support
4. API documentation quality
5. SDK availability (Python, JavaScript, etc.)
6. API rate limits mentioned

Return JSON: {{"api_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing APIs with LLM"})
            result = self._call_llm_json(prompt, "You are an API integration specialist. Return valid JSON only.")
            api_findings = result.get("api_findings", [])
            
            if api_findings:
                findings.extend(api_findings)
            else:
                findings.append("API documentation not accessible")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing APIs: {e}")
            findings.append("Unable to verify API capabilities")
        
        return findings
    
    def _analyze_webhooks(self, info: str, vendor_name: str) -> List[str]:
        """Analyze webhook and event capabilities."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s webhook and event capabilities:

{info[:3000]}

Identify:
1. Outbound webhook support
2. Event streaming/subscriptions
3. Real-time notifications
4. Custom event triggers

Return JSON: {{"webhook_findings": ["finding1", "finding2", ...]}}
"""
        
        try:
            self.emit_event("agent_thinking", {"action": "Analyzing webhooks with LLM"})
            result = self._call_llm_json(prompt, "You are an event-driven architecture specialist. Return valid JSON only.")
            webhook_findings = result.get("webhook_findings", [])
            
            if webhook_findings:
                findings.extend(webhook_findings)
            else:
                findings.append("Webhook/event capabilities not documented")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing webhooks: {e}")
            findings.append("Unable to verify webhook capabilities")
        
        return findings
    
    def _analyze_specific_integration(self, info: str, vendor_name: str, integration_name: str) -> List[str]:
        """Analyze a specific integration (Slack, Jira, etc.)."""
        findings = []
        
        prompt = f"""Analyze {vendor_name}'s integration with {integration_name}:

{info[:2000]}

Describe:
1. Native integration available?
2. Marketplace app or third-party connector?
3. Bi-directional sync capabilities?
4. Key features of the integration

Return JSON: {{"{integration_name.lower()}_integration": ["finding1", "finding2", ...]}}
"""
        
        try:
            result = self._call_llm_json(prompt, "You are an integration specialist. Return valid JSON only.")
            integration_findings = result.get(f"{integration_name.lower()}_integration", [])
            
            if integration_findings:
                findings.extend([f"{integration_name}: {f}" for f in integration_findings])
            else:
                findings.append(f"{integration_name} integration not documented")
                self.add_ambiguity(f"{integration_name} integration requires verification - may be available via marketplace or custom API")
        
        except Exception as e:
            print(f"[{self.name}] Error analyzing {integration_name}: {e}")
            findings.append(f"Unable to verify {integration_name} integration")
        
        return findings
    
    def _extract_api_types(self, api_findings: List[str]) -> List[str]:
        """Extract API types from findings."""
        api_types = []
        api_keywords = {"rest": "REST", "graphql": "GraphQL", "soap": "SOAP"}
        
        for finding in api_findings:
            finding_lower = finding.lower()
            for keyword, api_type in api_keywords.items():
                if keyword in finding_lower and api_type not in api_types:
                    api_types.append(api_type)
        
        return api_types
    
    def _calculate_interoperability_score(self, findings: List[str], requirements: List[str]) -> float:
        """Calculate interoperability score."""
        if not findings:
            return 1.0
        
        positive_keywords = ["supports", "available", "provides", "native", "comprehensive", "documented"]
        negative_keywords = ["not", "unable", "unclear", "unavailable", "undocumented"]
        
        positive_count = sum(1 for f in findings if any(kw in f.lower() for kw in positive_keywords))
        negative_count = sum(1 for f in findings if any(kw in f.lower() for kw in negative_keywords))
        
        # Bonus for meeting specific requirements
        requirements_met = sum(1 for req in requirements if any(req.lower() in f.lower() for f in findings))
        requirement_bonus = (requirements_met / len(requirements)) * 1.0 if requirements else 0
        
        base_score = (positive_count - negative_count * 0.5) / len(findings) * 4.0
        score = base_score + requirement_bonus
        
        return max(0.0, min(5.0, score))
    
    def _generate_interoperability_notes(self, findings: List[str], vendor_name: str, requirements: List[str]) -> str:
        """Generate summary notes."""
        if len(self.sources) == 0:
            return f"Limited integration documentation available for {vendor_name}. API and integration capabilities require direct vendor consultation."
        
        requirements_met = sum(1 for req in requirements if any(req.lower() in f.lower() for f in findings))
        
        if requirements:
            return f"Integration evaluation based on {len(self.sources)} sources. {requirements_met}/{len(requirements)} specified integrations verified. {len(findings)} total findings. Confidence: {self._calculate_confidence()}"
        else:
            return f"Integration evaluation based on {len(self.sources)} sources. {len(findings)} capabilities documented. Confidence: {self._calculate_confidence()}"
    
    def _generate_executive_summary(self, findings: List[str], score: Optional[float], vendor_name: str, requirements: List[str], status: str) -> str:
        """Generate a 2-3 sentence executive summary suitable for management."""
        requirements_met = sum(1 for req in requirements if any(req.lower() in f.lower() for f in findings))
        api_types = self._extract_api_types(findings)
        
        # Handle insufficient data
        if status == "insufficient_data":
            official_sources = [s for s in self.sources if s.get("credibility") == "official"]
            if len(self.sources) == 0:
                req_str = f" particularly {', '.join(requirements[:2])}" if requirements else ""
                return f"⚠️ **Insufficient public data** - Could not verify integration capabilities for {vendor_name} from accessible documentation{req_str}. API documentation, SSO setup guides, and integration examples must be obtained directly from vendor."
            elif len(official_sources) == 0:
                return f"⚠️ **Insufficient public data** - Found {len(self.sources)} community sources for {vendor_name}, but no official API documentation. Cannot verify integration capabilities or SSO support without official developer portal access."
            else:
                missing = len(requirements) - requirements_met if requirements else 0
                return f"⚠️ **Insufficient public data** - Limited integration documentation for {vendor_name} with {missing} critical integrations unverified. Detailed technical discovery required before commitment."
        
        # Handle risk
        if status == "risk":
            return f"🔴 **High Risk** - {vendor_name} integration posture is weak with minimal API documentation and unclear support for required systems. Not recommended without comprehensive integration workshop and proof of concept."
        
        # Handle OK cases
        if score and score >= 4.0:
            api_str = ", ".join(api_types) if api_types else "modern APIs"
            req_str = f" including {requirements_met}/{len(requirements)} required integrations" if requirements else ""
            return f"✅ {vendor_name} provides comprehensive integration capabilities with {api_str}{req_str}. Documentation is strong and implementation risk is low."
        elif score and score >= 3.0:
            return f"✅ {vendor_name} offers solid integration options with {len(api_types)} API types documented. {len(findings)} capabilities verified, though some integration patterns may require custom development."
        else:
            return f"⚠️ {vendor_name} has basic integration documentation. API capabilities exist but require detailed technical verification before commitment."
