"""
Verification Agent - Fact Checker
Verifies vendor information against website and documents
"""
from services.agents.base_agent import BaseAgent
from typing import Dict, Any


class VerificationAgent(BaseAgent):
    """Agent 2: Verification Agent"""
    
    def __init__(self):
        super().__init__("Verification Agent", "Fact Checker")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify vendor information.
        
        TODO: Implement website fetching and fact-checking logic
        """
        # TODO: Fetch website content
        # TODO: Build prompt for fact-checking
        # TODO: Call LLM and parse verification flags
        
        return {
            "flags": {
                "name_match": "unknown",
                "website_match": "unknown",
                "location_match": "unknown"
            }
        }

