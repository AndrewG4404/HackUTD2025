"""
Interoperability Agent - Integration Architect
Enhanced with multi-step RAG for thorough integration research
"""
from services.agents.base_agent import BaseAgent
from services.document_processor import extract_texts_from_files, retrieve_relevant_context
from typing import Dict, Any, List


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
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate technical integration capabilities using enhanced RAG.
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
        
        # 1. SSO/Authentication
        self.emit_event("agent_thinking", {"action": "Researching SSO capabilities"})
        sso_info = self.research_requirement(
            f"{company_name} SAML SSO OAuth SCIM Okta Active Directory integration",
            company_name,
            website
        )
        sso_findings = self._analyze_sso(sso_info, company_name, required_integrations)
        findings.extend(sso_findings)
        
        # 2. APIs and SDKs
        self.emit_event("agent_thinking", {"action": "Researching API capabilities"})
        api_info = self.research_requirement(
            f"{company_name} REST API GraphQL SOAP API documentation developer SDK",
            company_name,
            website
        )
        api_findings = self._analyze_apis(api_info, company_name)
        findings.extend(api_findings)
        
        # 3. Webhooks/Events
        self.emit_event("agent_thinking", {"action": "Researching webhook support"})
        webhook_info = self.research_requirement(
            f"{company_name} webhooks outbound events event streams real-time notifications",
            company_name,
            website
        )
        webhook_findings = self._analyze_webhooks(webhook_info, company_name)
        findings.extend(webhook_findings)
        
        # 4. Specific integrations (if mentioned in use case)
        if "slack" in use_case.lower():
            self.emit_event("agent_progress", {"action": "Researching Slack integration"})
            slack_info = self.research_requirement(
                f"{company_name} Slack integration",
                company_name,
                website
            )
            findings.extend(self._analyze_specific_integration(slack_info, company_name, "Slack"))
        
        if "jira" in use_case.lower():
            self.emit_event("agent_progress", {"action": "Researching Jira integration"})
            jira_info = self.research_requirement(
                f"{company_name} Jira integration",
                company_name,
                website
            )
            findings.extend(self._analyze_specific_integration(jira_info, company_name, "Jira"))
        
        if "snowflake" in use_case.lower():
            self.emit_event("agent_progress", {"action": "Researching Snowflake integration"})
            snowflake_info = self.research_requirement(
                f"{company_name} Snowflake data integration analytics",
                company_name,
                website
            )
            findings.extend(self._analyze_specific_integration(snowflake_info, company_name, "Snowflake"))
        
        # Calculate score
        score = self._calculate_interoperability_score(findings, required_integrations)
        
        # Generate notes
        notes = self._generate_interoperability_notes(findings, company_name, required_integrations)
        
        # Create structured output
        output = self.create_structured_output(
            score=score,
            findings=findings,
            notes=notes,
            apis=self._extract_api_types(api_findings)
        )
        
        self.emit_event("agent_complete", {
            "status": "completed",
            "score": score,
            "findings_count": len(findings),
            "sources_count": len(self.sources)
        })
        
        return output
    
    def _extract_integration_requirements(self, use_case: str) -> List[str]:
        """Extract specific integration requirements from use case."""
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
