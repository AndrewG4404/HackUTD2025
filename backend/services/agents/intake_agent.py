"""
Intake Agent - Vendor Ops Analyst
Normalizes fields and extracts basic info from docs/website
"""
from services.agents.base_agent import BaseAgent
from typing import Dict, Any


class IntakeAgent(BaseAgent):
    """Agent 1: Intake Agent"""
    
    def __init__(self):
        super().__init__("Intake Agent", "Vendor Ops Analyst")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize vendor fields and extract additional info.
        
        TODO: Implement prompt template and LLM call
        """
        # TODO: Build prompt with vendor data and documents
        # TODO: Call LLM with structured output schema
        # TODO: Parse and return structured vendor_profile
        
        return {
            "summary": "Vendor profile summary",
            "fields": {
                "regions_served": [],
                "industries": [],
                "product_category": ""
            }
        }

