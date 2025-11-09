"""
Base agent class for all workflow agents
Enhanced with structured outputs and event emission for SSE streaming
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from services.nemotron_client import get_nemotron_client
import json
from datetime import datetime


class BaseAgent(ABC):
    """
    Base class for all agents with structured outputs and event emission.
    
    Output Schema:
    {
        "score": float (0-5),
        "findings": List[str],
        "notes": str,
        "sources": List[{url, title, excerpt, credibility, accessed_at}],
        "ambiguities": List[str],
        "confidence": str ("high", "medium", "low")
    }
    """
    
    def __init__(self, name: str, role: str, event_callback: Optional[Callable] = None):
        self.name = name
        self.role = role
        self.client = get_nemotron_client()
        self.event_callback = event_callback  # For SSE streaming
        self.sources: List[Dict[str, Any]] = []
        self.ambiguities: List[str] = []
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task.
        
        Args:
            context: Context dictionary with vendor data, documents, etc.
        
        Returns:
            Structured agent output dictionary
        """
        pass
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event for SSE streaming (if callback is set).
        
        Args:
            event_type: Type of event (agent_start, agent_thinking, agent_progress, agent_complete)
            data: Event data dictionary
        """
        if self.event_callback:
            try:
                event_data = {
                    "agent_name": self.name,
                    "role": self.role,
                    "timestamp": datetime.utcnow().isoformat(),
                    **data
                }
                self.event_callback(event_type, event_data)
            except Exception as e:
                print(f"[{self.name}] Error emitting event: {e}")
    
    def create_structured_output(
        self,
        score: Optional[float],
        findings: List[str],
        notes: str = "",
        status: str = "ok",
        recommendations: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create standardized agent output with sources and confidence.
        
        Args:
            score: Numeric score (0-5) or None for insufficient data
            findings: List of key findings
            notes: Additional notes/summary
            status: Dimension status ("ok", "insufficient_data", or "risk")
            recommendations: List of actionable recommendations
            **kwargs: Additional agent-specific fields
        
        Returns:
            Structured output dictionary
        """
        # Calculate confidence based on sources
        confidence = self._calculate_confidence()
        
        output = {
            "score": round(score, 2) if score is not None else None,
            "status": status,
            "findings": findings,
            "notes": notes,
            "sources": self.sources,
            "ambiguities": self.ambiguities,
            "confidence": confidence,
            "recommendations": recommendations or [],
            **kwargs
        }
        
        return output
    
    def _calculate_confidence(self) -> str:
        """Calculate confidence level based on sources."""
        if not self.sources:
            return "low"
        
        official_count = sum(1 for s in self.sources if s.get("credibility") == "official")
        total_count = len(self.sources)
        
        if official_count >= 2 and total_count >= 3:
            return "high"
        elif official_count >= 1 or total_count >= 2:
            return "medium"
        else:
            return "low"
    
    def add_source(self, source: Dict[str, Any]):
        """Add a source to the agent's source list."""
        self.sources.append(source)
    
    def add_ambiguity(self, ambiguity: str):
        """Add an ambiguity/assumption to document."""
        self.ambiguities.append(ambiguity)
    
    async def research_requirement(
        self,
        requirement_query: str,
        vendor_name: str,
        vendor_website: str,
        context_description: str = ""
    ) -> str:
        """
        Research a specific requirement using single comprehensive search.
        
        Args:
            requirement_query: Specific query (e.g., "ServiceNow SAML SSO Okta support")
            vendor_name: Vendor name
            vendor_website: Vendor website
            context_description: Additional context for the search
        
        Returns:
            Summary text of findings
        """
        self.emit_event("agent_progress", {
            "action": "web_search_initiated",
            "query": requirement_query,
            "vendor": vendor_name,
            "message": f"🔍 Searching web for: {requirement_query[:100]}"
        })
        
        # Use single comprehensive search (saves API quota)
        sources = await self.client.search_with_followup(
            initial_query=requirement_query,
            vendor_name=vendor_name,
            base_website=vendor_website,
            max_hops=1  # Single search
        )
        
        # Add sources to agent's source list
        for source in sources:
            self.add_source(source)
        
        # Emit detailed results for judges to see
        self.emit_event("agent_progress", {
            "action": "sources_discovered",
            "count": len(sources),
            "urls": [s["url"] for s in sources[:3]],
            "message": f"✅ Found {len(sources)} documentation sources",
            "details": {
                "sources": [
                    {
                        "url": s["url"],
                        "title": s.get("title", ""),
                        "credibility": s.get("credibility", "unknown"),
                        "excerpt": s.get("excerpt", "")[:150] + "..." if s.get("excerpt") else ""
                    }
                    for s in sources[:3]
                ]
            }
        })
        
        # Synthesize findings from sources
        if not sources:
            self.emit_event("agent_progress", {
                "action": "no_sources_found",
                "message": "⚠️ No accessible documentation found - will use general knowledge",
                "query": requirement_query
            })
            return f"No accessible documentation found for: {requirement_query}"
        
        # Combine excerpts for analysis
        combined_content = "\n\n".join([
            f"[Source {i+1} - {s['credibility']}]: {s['excerpt']}"
            for i, s in enumerate(sources[:5])
        ])
        
        return combined_content
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Helper method to call Nemotron LLM"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return self.client.chat_completion(messages=messages)
    
    def _call_llm_json(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Helper method to call Nemotron LLM and get JSON response.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Parsed JSON response
        """
        # Emit event showing LLM is being called (for judges to see)
        self.emit_event("agent_progress", {
            "action": "llm_reasoning",
            "message": "🤖 Analyzing with Nemotron AI...",
            "details": {
                "system_prompt": (system_prompt[:200] + "...") if system_prompt and len(system_prompt) > 200 else system_prompt,
                "user_prompt": (prompt[:300] + "...") if len(prompt) > 300 else prompt
            }
        })
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response_text = self.client.chat_completion_json(messages=messages)
        
        # Try to parse JSON
        try:
            # Extract JSON if wrapped in code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            result = json.loads(response_text)
            
            # Emit event showing LLM completed analysis
            self.emit_event("agent_progress", {
                "action": "llm_complete",
                "message": "✅ AI analysis complete",
                "details": {
                    "response_preview": str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                }
            })
            
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response text: {response_text}")
            # Return a default structure
            return {}

