"""
Nemotron API client using NVIDIA API endpoints
Uses OpenAI-compatible interface
Enhanced with multi-step RAG capabilities using Brave Search API
Includes smart caching and rate limiting for production reliability
"""
import os
import httpx
import json
import asyncio
from typing import Dict, Any, Optional, List
from openai import OpenAI
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

# Vendor domain mappings for better official source targeting
VENDOR_DOMAINS = {
    "slack": ["slack.com"],
    "microsoft": ["microsoft.com", "learn.microsoft.com", "docs.microsoft.com"],
    "atlassian": ["atlassian.com", "support.atlassian.com", "confluence.atlassian.com"],
    "servicenow": ["servicenow.com", "docs.servicenow.com"],
    "google": ["cloud.google.com", "workspace.google.com", "support.google.com"],
    "zendesk": ["zendesk.com", "support.zendesk.com"],
    "freshservice": ["freshservice.com", "support.freshservice.com"],
    "jira": ["atlassian.com", "support.atlassian.com"],
    "salesforce": ["salesforce.com", "help.salesforce.com", "developer.salesforce.com"],
    "zoom": ["zoom.us", "support.zoom.us"],
    "dropbox": ["dropbox.com", "help.dropbox.com"],
    "box": ["box.com", "support.box.com"],
    "asana": ["asana.com", "asana.com/guide"],
    "monday": ["monday.com", "support.monday.com"],
    "notion": ["notion.so", "notion.com"],
    "hubspot": ["hubspot.com", "knowledge.hubspot.com"],
}

# Community/noise domains to filter out or downweight
COMMUNITY_DOMAINS = [
    "reddit.com", "medium.com", "dev.to", "quora.com", 
    "stackexchange.com", "stackoverflow.com", "community.",
    "forum.", "discuss.", "youtube.com", "twitter.com",
    "facebook.com", "linkedin.com/pulse"
]


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
        Fetch and extract text content from a URL with browser-like headers.
        Robust against blocks, timeouts, and HTTP/2 issues.
        
        Args:
            url: URL to fetch
            max_chars: Maximum characters to return
        
        Returns:
            Extracted text content
        """
        try:
            # Use realistic browser headers to avoid 403s/blocks
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0",
            }
            
            # Always start with HTTP/1.1 (more reliable for hackathon)
            # HTTP/2 can cause StreamReset issues with CDNs/WAFs
            response = None
            try:
                with httpx.Client(
                    timeout=20.0,
                    follow_redirects=True,
                    headers=headers,
                    http2=False,  # Use HTTP/1.1 for reliability
                    limits=httpx.Limits(max_connections=10)
                ) as client:
                    response = client.get(url)
                    response.raise_for_status()
                    
                    # Parse HTML and extract text
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove script and style elements
                    for el in soup(["script", "style", "nav", "footer", "header"]):
                        el.decompose()
                    
                    # Get text with separator
                    text = soup.get_text(separator=" ")
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    return text[:max_chars]
                    
            except httpx.HTTPStatusError as e:
                print(f"[fetch_url] HTTP error for {url}: {e.response.status_code}")
                return f"Error fetching URL: HTTP {e.response.status_code}"
            except httpx.TimeoutException:
                print(f"[fetch_url] Timeout fetching {url}")
                return "Error fetching URL: Timeout"
            except Exception as e:
                print(f"[fetch_url] Error fetching {url}: {e}")
                return f"Error fetching URL: {str(e)}"
                
        except Exception as e:
            print(f"[fetch_url] Unexpected error for {url}: {e}")
            return f"Error fetching URL: {str(e)}"
    
    async def search_web(
        self,
        query: str,
        max_results: int = 5,
        site_hint: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Perform web search using Brave Search API (1 req/sec, 1000 req/month).
        
        Features:
        - Smart caching: identical queries reuse cached results
        - Global throttling: respects 1 req/sec rate limit
        - Graceful degradation: returns empty list on errors
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 5)
            site_hint: Optional website to focus search on
        
        Returns:
            List of dicts with keys: title, url, snippet
        """
        from services import search_client
        
        print(f"[NemotronClient] 🔍 Web search: {query[:80]}...")
        
        results = await search_client.search_web(
            query=query,
            max_results=max_results,
            site_hint=site_hint
        )
        
        print(f"[NemotronClient] ✅ Search complete: {len(results)} results")
        
        # Convert to format expected by rest of code (url/href compatibility)
        for r in results:
            r["href"] = r.get("url", "")
            r["body"] = r.get("snippet", "")
        
        return results
    
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
    
    def _base_domain(self, base_website: str) -> str:
        """Extract base domain from website URL, stripping www."""
        parsed = urlparse(base_website)
        host = parsed.netloc or parsed.path
        # Strip www. prefix
        return host.replace("www.", "")
    
    def _vendor_subdomains(self, base_website: str) -> List[str]:
        """
        Generate list of common vendor subdomains for documentation discovery.
        Returns full URLs with https:// for common doc subdomains.
        """
        d = self._base_domain(base_website)
        # Common documentation/official subdomains across SaaS vendors
        subs = [
            f"https://docs.{d}",
            f"https://developer.{d}",
            f"https://developers.{d}",
            f"https://help.{d}",
            f"https://support.{d}",
            f"https://community.{d}",
            f"https://trust.{d}",
            f"https://resources.{d}",
            f"https://learn.{d}",
            f"https://customers.{d}",
            f"https://status.{d}",
            # Keep the original root as last resort
            f"https://www.{d}",
            f"https://{d}",
        ]
        # De-duplicate while preserving order
        seen, out = set(), []
        for s in subs:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out
    
    def _get_fallback_urls(self, base_website: str, doc_type: str) -> List[str]:
        """Generate fallback documentation URLs based on common patterns and subdomains."""
        from urllib.parse import urljoin
        
        patterns = {
            "privacy": ["/privacy-policy", "/privacy", "/legal/privacy", "/data-protection"],
            "pricing": ["/pricing", "/plans", "/pricing-plans", "/editions-pricing"],
            "api": ["/docs", "/api", "/developers", "/developer", "/documentation"],
            "support": ["/support", "/help", "/resources", "/training", "/knowledge"],
            "compliance": ["/security", "/compliance", "/trust", "/certifications"],
            "technical": ["/docs", "/documentation", "/technical-docs", "/integration"]
        }
        
        paths = patterns.get(doc_type, [f"/{doc_type}"])[:3]
        
        # Generate URLs across multiple subdomains
        urls = []
        for root in self._vendor_subdomains(base_website):
            for p in paths:
                urls.append(urljoin(root, p))
        return urls[:10]  # Limit to 10 URLs
    
    async def search_with_followup(
        self,
        initial_query: str,
        vendor_name: str,
        base_website: str,
        max_hops: int = 1  # Now defaults to 1 to save API calls
    ) -> List[Dict[str, Any]]:
        """
        Tiered search strategy: prefer official vendor docs, fallback to broader web.
        
        Args:
            initial_query: Search query (e.g., "ServiceNow SAML SSO Okta")
            vendor_name: Vendor name for context
            base_website: Vendor website
            max_hops: Ignored (kept for backward compatibility)
        
        Returns:
            List of source dicts with {url, title, content, excerpt, credibility, accessed_at}
        """
        sources = []
        
        print(f"[NemotronClient] Single comprehensive search: {initial_query}")
        
        # Extract base domain from website
        vendor_domain = self._extract_base_domain(base_website)
        
        # Check if we have known subdomains for this vendor
        vendor_key = vendor_name.lower().split()[0]  # "Slack Technologies" -> "slack"
        known_domains = VENDOR_DOMAINS.get(vendor_key, [vendor_domain])
        
        # Strategy 1: Domain-restricted search (official sources)
        print(f"[NemotronClient] 🔍 Searching official domains: {known_domains}")
        for domain in known_domains[:2]:  # Try top 2 known domains
            site_restricted_query = f"site:{domain} {initial_query}"
            search_results = await self.search_web(
                query=site_restricted_query,
                max_results=3
            )
            
            for result in search_results[:2]:  # Take top 2 from each domain
                url = result.get("href") or result.get("url", "")
                if not url or self._is_noise_domain(url):
                    continue
                
                try:
                    content = self.fetch_url(url, max_chars=8000)
                    
                    if "Error fetching URL" in content or len(content) < 100:
                        continue
                    
                    excerpt = self._extract_relevant_excerpt(content, initial_query)
                    credibility = self._judge_source_credibility(url, vendor_name, vendor_domain)
                    
                    source = {
                        "url": url,
                        "title": result.get("title", "") or self._extract_title(url, content),
                        "content": content,
                        "excerpt": excerpt,
                        "credibility": credibility,
                        "accessed_at": datetime.utcnow().isoformat(),
                        "query": initial_query
                    }
                    sources.append(source)
                    
                except Exception as e:
                    print(f"[NemotronClient] Error processing {url}: {e}")
                    continue
        
        # Strategy 2: If insufficient official sources, do broader search
        official_count = len([s for s in sources if s["credibility"] == "official"])
        if official_count < 2:
            print(f"[NemotronClient] ℹ️  Only {official_count} official sources, broadening search...")
            broader_results = await self.search_web(
                query=f"{vendor_name} {initial_query}",
                max_results=5
            )
            
            for result in broader_results[:3]:
                url = result.get("href") or result.get("url", "")
                if not url or self._is_noise_domain(url):
                    continue
                
                # Skip if already have this URL
                if any(s["url"] == url for s in sources):
                    continue
                
                try:
                    content = self.fetch_url(url, max_chars=8000)
                    
                    if "Error fetching URL" in content or len(content) < 100:
                        continue
                    
                    excerpt = self._extract_relevant_excerpt(content, initial_query)
                    credibility = self._judge_source_credibility(url, vendor_name, vendor_domain)
                    
                    source = {
                        "url": url,
                        "title": result.get("title", "") or self._extract_title(url, content),
                        "content": content,
                        "excerpt": excerpt,
                        "credibility": credibility,
                        "accessed_at": datetime.utcnow().isoformat(),
                        "query": initial_query
                    }
                    sources.append(source)
                    
                except Exception as e:
                    print(f"[NemotronClient] Error processing {url}: {e}")
                    continue
        
        official_final = len([s for s in sources if s["credibility"] == "official"])
        print(f"[NemotronClient] Search complete: {len(sources)} sources found ({official_final} official)")
        return sources
    
    # _discover_urls_for_query removed - now using direct Brave Search with site_hint
    
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
    
    def _query_intent_fallback(self, query: str, base_website: str) -> List[str]:
        """
        Smart subdomain-based fallback using query intent detection.
        Tries multiple vendor subdomains with paths matching query intent.
        """
        from urllib.parse import urljoin
        
        roots = self._vendor_subdomains(base_website)
        q = query.lower()
        candidate_paths = []
        
        # Match query intent to likely documentation paths
        if any(k in q for k in ["sso", "saml", "oauth", "scim", "okta", "mfa", "authentication"]):
            candidate_paths = ["/security", "/trust", "/sso", "/identity", "/docs", "/api"]
        elif any(k in q for k in ["api", "graphql", "sdk", "webhook", "developer", "rest"]):
            candidate_paths = ["/docs", "/api", "/developers", "/developer", "/documentation", "/webhooks"]
        elif any(k in q for k in ["pricing", "cost", "editions", "plans"]):
            candidate_paths = ["/pricing", "/plans", "/pricing-plans", "/editions-pricing"]
        elif any(k in q for k in ["privacy", "gdpr", "ccpa", "hipaa", "data retention", "deletion"]):
            candidate_paths = ["/privacy", "/legal/privacy", "/security", "/trust", "/compliance", "/data-protection"]
        elif any(k in q for k in ["support", "training", "help", "implementation"]):
            candidate_paths = ["/support", "/help", "/training", "/resources", "/learn"]
        elif any(k in q for k in ["compliance", "certification", "soc2", "iso"]):
            candidate_paths = ["/trust", "/security", "/compliance", "/certifications"]
        else:
            # Generic fallback
            candidate_paths = ["/docs", "/documentation", "/resources", "/support", "/help"]
        
        # Generate URLs across subdomains
        urls = []
        for root in roots:
            for path in candidate_paths[:3]:  # Top 3 paths per subdomain
                urls.append(urljoin(root, path))
        
        return urls[:10]  # Return top 10
    
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
    
    def _extract_base_domain(self, url: str) -> str:
        """
        Extract registrable domain from URL (e.g., slack.com from https://trust.slack.com).
        
        Args:
            url: Full URL or domain
        
        Returns:
            Base domain (e.g., "slack.com")
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            parsed = urlparse(url)
            # Get hostname and extract registrable domain
            hostname = parsed.netloc or parsed.path
            # Remove www.
            hostname = hostname.replace('www.', '')
            # For subdomains, extract base domain (last 2 parts)
            parts = hostname.split('.')
            if len(parts) >= 2:
                return '.'.join(parts[-2:])
            return hostname
        except:
            return url
    
    def _is_noise_domain(self, url: str) -> bool:
        """
        Check if URL is from a community/noise domain that should be filtered.
        
        Args:
            url: URL to check
        
        Returns:
            True if noise domain
        """
        url_lower = url.lower()
        return any(noise in url_lower for noise in COMMUNITY_DOMAINS)
    
    def _judge_source_credibility(self, url: str, vendor_name: str, vendor_domain: str = "") -> str:
        """
        Judge source credibility: official, third-party, or community.
        NOW: Treats any URL on vendor's registrable domain as official.
        
        Args:
            url: Source URL
            vendor_name: Vendor name
            vendor_domain: Base vendor domain (e.g., "slack.com")
        
        Returns:
            "official", "third-party-trusted", or "community"
        """
        url_lower = url.lower()
        
        # Check if on vendor's domain (most reliable indicator)
        if vendor_domain and vendor_domain in url_lower:
            return "official"
        
        # Fallback: check vendor name (less reliable)
        vendor_lower = vendor_name.lower().replace(' ', '').replace('-', '')
        if vendor_lower in url_lower.replace('-', ''):
            return "official"
        
        # Trusted third parties (analyst firms, tech media)
        trusted_domains = [
            "gartner.com", "forrester.com", "g2.com", "capterra.com",
            "techcrunch.com", "zdnet.com", "computerworld.com", "infoworld.com"
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
            
            if response is None:
                return None
            
            if isinstance(response, str):
                result = json.loads(response)
            else:
                result = response
            
            if not isinstance(result, dict):
                return None
            
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


def get_search_cache_stats() -> Dict[str, Any]:
    """Get statistics about the search cache (useful for debugging)"""
    from services import search_client
    return search_client.get_cache_stats()


def clear_search_cache():
    """Clear the search cache (useful for testing)"""
    from services import search_client
    search_client.clear_cache()
    print("[NemotronClient] 🗑️  Search cache cleared")

