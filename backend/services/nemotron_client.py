"""
Nemotron API client
Wrapper for interacting with Nemotron LLM API
"""
import os
import httpx
from typing import Dict, Any, Optional


class NemotronClient:
    """Client for Nemotron API"""
    
    def __init__(self):
        self.api_url = os.getenv("NEMOTRON_API_URL", "https://api.nemotron.ai/v1")
        self.api_key = os.getenv("NEMOTRON_API_KEY", "")
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
    
    async def chat_completion(
        self,
        messages: list,
        model: str = "nemotron",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to Nemotron API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            API response dictionary
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def fetch_url(self, url: str) -> str:
        """
        Fetch content from a URL.
        TODO: Implement web scraping or use Nemotron's tool if available
        """
        # For now, this is a placeholder
        # In production, you might want to:
        # 1. Use httpx to fetch the URL
        # 2. Parse HTML with BeautifulSoup
        # 3. Extract text content
        # 4. Return cleaned text
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return response.text
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global client instance
_nemotron_client: Optional[NemotronClient] = None


def get_nemotron_client() -> NemotronClient:
    """Get or create Nemotron client instance"""
    global _nemotron_client
    if _nemotron_client is None:
        _nemotron_client = NemotronClient()
    return _nemotron_client

