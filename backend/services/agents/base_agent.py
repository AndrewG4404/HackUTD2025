"""
Base agent class for all workflow agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from services.nemotron_client import get_nemotron_client


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.client = get_nemotron_client()
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task.
        
        Args:
            context: Context dictionary with vendor data, documents, etc.
        
        Returns:
            Agent output dictionary
        """
        pass
    
    async def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Helper method to call Nemotron LLM"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat_completion(messages=messages)
        return response["choices"][0]["message"]["content"]

