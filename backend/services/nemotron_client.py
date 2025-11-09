"""
Nemotron API client using NVIDIA API endpoints
Uses OpenAI-compatible interface
Enhanced with multi-step RAG capabilities
"""
import os
import httpx
import json
from typing import Dict, Any, Optional, List, Tuple
from openai import OpenAI
from bs4 import BeautifulSoup
from datetime import datetime


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
    
    def fetch_url(self, url: str, max_chars: int = 10000) -> str:
        """
        Fetch and extract text content from a URL.
        
        Args:
            url: URL to fetch
            max_chars: Maximum characters to return
        
        Returns:
            Extracted text content
        """
        try:
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:max_chars]
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return f"Error fetching URL: {str(e)}"
    
    def discover_documentation_urls(self, base_website: str, doc_type: str) -> List[str]:
        """
        Discover relevant documentation URLs for a vendor.
        Uses LLM to intelligently find documentation links.
        
        Args:
            base_website: Vendor's main website URL
            doc_type: Type of documentation to find (e.g., "privacy", "pricing", "api", "support")
        
        Returns:
            List of discovered documentation URLs
        """
        try:
            # Fetch main website
            main_content = self.fetch_url(base_website, max_chars=5000)
            
            # Use LLM to extract relevant documentation URLs
            prompt = f"""Given the website content below, find and list URLs related to "{doc_type}" documentation.
            
Website: {base_website}
Content snippet: {main_content[:2000]}

Common patterns for {doc_type} documentation:
- Privacy: /privacy, /privacy-policy, /legal/privacy, /data-protection
- Pricing: /pricing, /plans, /cost, /pricing-plans
- API/Technical: /docs, /api, /developers, /documentation, /integration
- Support: /support, /help, /resources, /training, /getting-started
- Compliance: /security, /compliance, /certifications, /trust

Return a JSON array of 2-5 most likely URLs for {doc_type} documentation:
{{"urls": ["full_url_1", "full_url_2", ...]}}

If the base website is https://example.com and you find /pricing, return https://example.com/pricing"""
            
            messages = [
                {"role": "system", "content": "You are a web documentation discovery assistant. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.chat_completion_json(messages, temperature=0.3, max_tokens=500)
            
            # Parse response
            import json
            if isinstance(response, str):
                result = json.loads(response)
            else:
                result = response
            
            urls = result.get("urls", [])
            
            # Fallback: construct common paths if LLM didn't return anything
            if not urls:
                urls = self._get_fallback_urls(base_website, doc_type)
            
            print(f"[NemotronClient] Discovered {len(urls)} URLs for {doc_type} documentation")
            return urls[:5]  # Limit to 5 URLs
            
        except Exception as e:
            print(f"[NemotronClient] Error discovering URLs: {e}")
            return self._get_fallback_urls(base_website, doc_type)
    
    def _get_fallback_urls(self, base_website: str, doc_type: str) -> List[str]:
        """Generate fallback documentation URLs based on common patterns."""
        from urllib.parse import urljoin
        
        patterns = {
            "privacy": ["/privacy-policy", "/privacy", "/legal/privacy", "/data-protection"],
            "pricing": ["/pricing", "/plans", "/pricing-plans", "/cost"],
            "api": ["/docs", "/api", "/developers", "/api-docs", "/documentation"],
            "support": ["/support", "/help", "/resources", "/training"],
            "compliance": ["/security", "/compliance", "/trust", "/certifications"],
            "technical": ["/docs", "/documentation", "/technical-docs", "/integration"]
        }
        
        paths = patterns.get(doc_type, [f"/{doc_type}"])
        return [urljoin(base_website, path) for path in paths[:3]]
    
    def search_with_followup(
        self,
        initial_query: str,
        vendor_name: str,
        base_website: str,
        max_hops: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Multi-step search with intelligent follow-up queries.
        Max 3 hops to prevent infinite loops.
        
        Args:
            initial_query: Initial search query (e.g., "ServiceNow SAML SSO Okta")
            vendor_name: Vendor name for context
            base_website: Vendor website
            max_hops: Maximum follow-up searches (default 3)
        
        Returns:
            List of source dicts with {url, title, content, excerpt, credibility, accessed_at}
        """
        sources = []
        queries = [initial_query]
        
        for hop in range(max_hops):
            if hop >= len(queries):
                break
            
            query = queries[hop]
            print(f"[NemotronClient] Search hop {hop + 1}/{max_hops}: {query}")
            
            # Try to find relevant URLs
            urls = self._discover_urls_for_query(query, vendor_name, base_website)
            
            for url in urls[:2]:  # Limit to 2 URLs per hop
                try:
                    content = self.fetch_url(url, max_chars=8000)
                    
                    # Skip if error or very short
                    if "Error fetching URL" in content or len(content) < 100:
                        continue
                    
                    # Extract relevant excerpt
                    excerpt = self._extract_relevant_excerpt(content, query)
                    
                    # Judge credibility
                    credibility = self._judge_source_credibility(url, vendor_name)
                    
                    source = {
                        "url": url,
                        "title": self._extract_title(url, content),
                        "content": content,
                        "excerpt": excerpt,
                        "credibility": credibility,
                        "accessed_at": datetime.utcnow().isoformat(),
                        "query": query
                    }
                    sources.append(source)
                    
                    # Generate follow-up query if needed and we haven't hit max hops
                    if hop < max_hops - 1:
                        followup = self._generate_followup_query(query, excerpt, vendor_name)
                        if followup and followup not in queries:
                            queries.append(followup)
                    
                except Exception as e:
                    print(f"[NemotronClient] Error processing {url}: {e}")
                    continue
        
        print(f"[NemotronClient] Search complete: {len(sources)} sources found")
        return sources
    
    def _discover_urls_for_query(self, query: str, vendor_name: str, base_website: str) -> List[str]:
        """Discover URLs relevant to a specific query."""
        try:
            # Use LLM to suggest URLs based on query
            prompt = f"""Given this search query: "{query}" for vendor "{vendor_name}" (website: {base_website})

Suggest 2-3 most likely URLs where this information would be found.
Return JSON: {{"urls": ["url1", "url2", ...]}}

Examples:
- For "ServiceNow SAML SSO" -> ["https://docs.servicenow.com/bundle/...", "https://www.servicenow.com/security"]
- For "Salesforce pricing Enterprise" -> ["https://www.salesforce.com/editions-pricing/", "https://www.salesforce.com/pricing"]
"""
            
            messages = [
                {"role": "system", "content": "You are a documentation discovery assistant. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.chat_completion_json(messages, temperature=0.3, max_tokens=300)
            
            if isinstance(response, str):
                result = json.loads(response)
            else:
                result = response
            
            urls = result.get("urls", [])
            
            # If no URLs, try fallback based on query keywords
            if not urls:
                urls = self._query_to_fallback_urls(query, base_website)
            
            return urls[:3]
        except Exception as e:
            print(f"[NemotronClient] Error discovering URLs for query: {e}")
            return self._query_to_fallback_urls(query, base_website)
    
    def _query_to_fallback_urls(self, query: str, base_website: str) -> List[str]:
        """Generate fallback URLs based on query keywords."""
        from urllib.parse import urljoin
        
        query_lower = query.lower()
        paths = []
        
        if "price" in query_lower or "cost" in query_lower:
            paths = ["/pricing", "/plans", "/pricing-plans"]
        elif "api" in query_lower or "integration" in query_lower:
            paths = ["/docs", "/api", "/developers"]
        elif "security" in query_lower or "compliance" in query_lower or "sso" in query_lower:
            paths = ["/security", "/trust", "/compliance"]
        elif "support" in query_lower or "training" in query_lower:
            paths = ["/support", "/help", "/training"]
        else:
            paths = ["/docs", "/documentation"]
        
        return [urljoin(base_website, path) for path in paths[:3]]
    
    def _extract_relevant_excerpt(self, content: str, query: str, max_length: int = 500) -> str:
        """Extract most relevant excerpt from content based on query."""
        # Simple keyword matching
        query_words = query.lower().split()
        sentences = content.split('.')
        
        # Score sentences by query word matches
        scored = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            score = sum(1 for word in query_words if word in sentence.lower())
            if score > 0:
                scored.append((score, sentence))
        
        if not scored:
            return content[:max_length]
        
        # Return top sentences
        scored.sort(reverse=True, key=lambda x: x[0])
        excerpt = '. '.join([s[1] for s in scored[:3]])
        return excerpt[:max_length]
    
    def _extract_title(self, url: str, content: str) -> str:
        """Extract title from URL or content."""
        # Try to extract from first line/heading
        lines = content.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                return line
        
        # Fallback to URL path
        from urllib.parse import urlparse
        path = urlparse(url).path
        return path.strip('/').replace('/', ' > ').title() or "Documentation"
    
    def _judge_source_credibility(self, url: str, vendor_name: str) -> str:
        """
        Judge source credibility: official, third-party, or community.
        
        Returns:
            "official", "third-party-trusted", or "community"
        """
        url_lower = url.lower()
        vendor_lower = vendor_name.lower().replace(' ', '')
        
        # Check if official (vendor domain)
        if vendor_lower in url_lower:
            return "official"
        
        # Trusted third parties
        trusted_domains = [
            "gartner.com", "forrester.com", "g2.com", "techcrunch.com",
            "zdnet.com", "computerworld.com", "infoworld.com", "medium.com"
        ]
        
        if any(domain in url_lower for domain in trusted_domains):
            return "third-party-trusted"
        
        return "community"
    
    def _generate_followup_query(self, original_query: str, excerpt: str, vendor_name: str) -> Optional[str]:
        """
        Generate a follow-up query if the excerpt is incomplete or suggests deeper info exists.
        
        Returns:
            Follow-up query string or None
        """
        try:
            # Ask LLM if follow-up is needed
            prompt = f"""Given this search query: "{original_query}"
And this excerpt from documentation: "{excerpt[:300]}..."

Is additional information needed? If yes, suggest ONE specific follow-up query for {vendor_name}.
If no, return empty.

Return JSON: {{"followup": "specific follow-up query or empty string"}}

Examples:
- Original: "ServiceNow SSO" | Excerpt: "supports SAML" | Followup: "ServiceNow SAML 2.0 configuration Okta"
- Original: "Salesforce pricing" | Excerpt: "starting at $25/user" | Followup: ""  (already answered)
"""
            
            messages = [
                {"role": "system", "content": "You are a search query optimizer. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.chat_completion_json(messages, temperature=0.3, max_tokens=100)
            
            if isinstance(response, str):
                result = json.loads(response)
            else:
                result = response
            
            followup = result.get("followup", "").strip()
            return followup if followup and len(followup) > 5 else None
            
        except Exception as e:
            print(f"[NemotronClient] Error generating follow-up: {e}")
            return None


# Global client instance
_nemotron_client: Optional[NemotronClient] = None


def get_nemotron_client() -> NemotronClient:
    """Get or create Nemotron client instance"""
    global _nemotron_client
    if _nemotron_client is None:
        _nemotron_client = NemotronClient()
    return _nemotron_client

