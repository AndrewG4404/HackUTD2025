"""
Base agent class for all workflow agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from services.nemotron_client import get_nemotron_client
import json


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.client = get_nemotron_client()
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task.
        
        Args:
            context: Context dictionary with vendor data, documents, etc.
        
        Returns:
            Agent output dictionary
        """
        pass
    
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
            
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response text: {response_text}")
            # Return a default structure
            return {}

