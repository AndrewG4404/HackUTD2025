"""
Search client with Brave Search API integration
Features:
- Brave Search API (free tier: 1 req/sec, 1000 req/month)
- Smart caching to minimize API calls
- Global throttling to respect rate limits
- Graceful degradation on errors
"""
import os
import time
import asyncio
from typing import List, Dict, Optional, Tuple
from functools import lru_cache
import httpx

# Configuration (checked at runtime for better .env loading compatibility)
def get_search_provider():
    return os.getenv("SEARCH_PROVIDER", "brave").lower()

def get_brave_api_key():
    return os.getenv("BRAVE_KEY", "")

def get_search_interval():
    return float(os.getenv("SEARCH_MIN_INTERVAL", "1.1"))  # 1.1s to stay under 1 req/sec

SEARCH_MIN_INTERVAL = get_search_interval()

# In-memory cache: {(query, max_results, site_hint) -> results}
_cache: Dict[Tuple[str, int, Optional[str]], List[Dict]] = {}

# Global throttle: timestamp of last actual HTTP request
_last_request_ts: float = 0.0
_request_lock = asyncio.Lock()


async def _throttle_if_needed() -> None:
    """
    Ensure at least SEARCH_MIN_INTERVAL seconds between actual HTTP calls.
    This is global across the process to respect Brave's 1 req/sec limit.
    """
    global _last_request_ts
    now = time.time()
    delta = now - _last_request_ts
    if delta < SEARCH_MIN_INTERVAL:
        sleep_time = SEARCH_MIN_INTERVAL - delta
        print(f"[SearchClient] ⏸️  Throttling: waiting {sleep_time:.2f}s to respect rate limit...")
        await asyncio.sleep(sleep_time)
    _last_request_ts = time.time()


async def _brave_search(
    query: str,
    max_results: int = 5,
    site_hint: Optional[str] = None,
) -> List[Dict]:
    """
    Call Brave Search API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results (default: 5)
        site_hint: Optional website domain to focus search on
    
    Returns:
        List of {title, url, snippet} dicts
    """
    brave_key = get_brave_api_key()
    if not brave_key:
        print("[SearchClient] ⚠️  BRAVE_KEY not configured")
        return []
    
    await _throttle_if_needed()
    
    headers = {
        "X-Subscription-Token": brave_key,
        "Accept": "application/json",
    }
    
    # Build query with optional site hint
    search_query = query
    if site_hint:
        # Extract domain from site_hint if it's a full URL
        from urllib.parse import urlparse
        parsed = urlparse(site_hint)
        domain = parsed.netloc or parsed.path
        domain = domain.replace("www.", "")
        # Add site: filter to focus on official docs
        search_query = f"{query} site:{domain}"
    
    params = {
        "q": search_query,
        "count": min(max_results, 20),  # Brave max is 20
    }
    
    print(f"[SearchClient] 🔍 BRAVE API CALL: query='{search_query[:80]}...', count={params['count']}")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params
            )
            resp.raise_for_status()
            data = resp.json()
        
        results: List[Dict] = []
        
        # Brave returns results in data["web"]["results"]
        for item in data.get("web", {}).get("results", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
            })
        
        print(f"[SearchClient] ✅ Found {len(results)} results from Brave")
        return results
        
    except httpx.HTTPStatusError as e:
        print(f"[SearchClient] ❌ Brave API error: {e.response.status_code}")
        if e.response.status_code == 429:
            print(f"[SearchClient] ⚠️  Rate limit hit - using cache or returning empty")
        return []
    except Exception as e:
        print(f"[SearchClient] ❌ Search error: {e}")
        return []


async def search_web(
    query: str,
    max_results: int = 5,
    site_hint: Optional[str] = None,
) -> List[Dict]:
    """
    Public search entry point with caching and throttling.
    
    Args:
        query: Search query string
        max_results: Maximum number of results
        site_hint: Optional website to focus search on
    
    Returns:
        List of {title, url, snippet} dicts
    """
    # Check cache first (before any throttling or API calls)
    cache_key = (query, max_results, site_hint or "")
    
    if cache_key in _cache:
        print(f"[SearchClient] ✅ Cache hit for '{query[:60]}...' (instant!) ⚡")
        return _cache[cache_key]
    
    print(f"[SearchClient] ℹ️  Cache miss, will query Brave API")
    
    # Not in cache - do throttled API call
    async with _request_lock:
        # Double-check cache in case another coroutine just populated it
        if cache_key in _cache:
            return _cache[cache_key]
        
        provider = get_search_provider()
        if provider == "brave":
            results = await _brave_search(query, max_results=max_results, site_hint=site_hint)
        else:
            print(f"[SearchClient] ⚠️  Unknown SEARCH_PROVIDER: {provider}")
            results = []
        
        # Cache the results
        _cache[cache_key] = results
        return results


def get_cache_stats() -> Dict:
    """Get cache statistics for debugging"""
    return {
        "cached_queries": len(_cache),
        "total_cached_results": sum(len(v) for v in _cache.values()),
    }


def clear_cache():
    """Clear the search cache (useful for testing)"""
    global _cache
    _cache.clear()
    print("[SearchClient] 🗑️  Cache cleared")

