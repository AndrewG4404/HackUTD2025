"""
Nemotron API client using NVIDIA API endpoints
Uses OpenAI-compatible interface
"""
import os
import httpx
from typing import Dict, Any, Optional, List
from openai import OpenAI
from bs4 import BeautifulSoup


class NemotronClient:
    """
    Client for NVIDIA Nemotron API using OpenAI-compatible interface.
    Supports both cloud API and local NIM deployment.
    """
    
    def __init__(self):
        self.api_key = os.getenv("NEMOTRON_API_KEY", "")
        self.model = os.getenv("NEMOTRON_MODEL", "nvidia/nvidia-nemotron-nano-9b-v2")
        
        # Support both cloud API and local NIM deployment
        # Default to cloud API if not specified
        self.base_url = os.getenv("NEMOTRON_API_URL", "https://integrate.api.nvidia.com/v1")
        
        # Initialize OpenAI client with configured endpoint
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key if self.api_key else "not-needed-for-local"
        )
        
        # Log configuration for debugging
        is_local = "localhost" in self.base_url or "127.0.0.1" in self.base_url
        print(f"[NemotronClient] Initialized with {'LOCAL NIM' if is_local else 'CLOUD API'}")
        print(f"[NemotronClient] Endpoint: {self.base_url}")
        print(f"[NemotronClient] Model: {self.model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Send chat completion request to Nemotron API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text response
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False  # Simple non-streaming for MVP
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error calling Nemotron API: {e}")
            raise
    
    def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Request JSON-formatted response from Nemotron.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated JSON response as string
        """
        # Add JSON instruction to system message
        json_instruction = "\nYou must respond with valid JSON only. No other text."
        
        modified_messages = messages.copy()
        if modified_messages and modified_messages[0]["role"] == "system":
            modified_messages[0]["content"] += json_instruction
        else:
            modified_messages.insert(0, {"role": "system", "content": json_instruction})
        
        return self.chat_completion(modified_messages, temperature, max_tokens)
    
    def fetch_url(self, url: str) -> str:
        """
        Fetch and extract text content from a URL.
        
        Args:
            url: URL to fetch
        
        Returns:
            Extracted text content
        """
        try:
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:10000]  # Limit to first 10k chars for MVP
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return f"Error fetching URL: {str(e)}"


# Global client instance
_nemotron_client: Optional[NemotronClient] = None


def get_nemotron_client() -> NemotronClient:
    """Get or create Nemotron client instance"""
    global _nemotron_client
    if _nemotron_client is None:
        _nemotron_client = NemotronClient()
    return _nemotron_client

