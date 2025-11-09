#!/usr/bin/env python3
"""
Test script for Brave Search API integration
Run this to verify your BRAVE_KEY is working correctly
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import services
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables FIRST (before importing search_client)
load_dotenv()

from services import search_client


async def test_brave_search():
    """Test Brave Search API with a simple query"""
    
    print("\n" + "="*70)
    print("🧪 Testing Brave Search API Integration")
    print("="*70 + "\n")
    
    # Check if API key is configured
    brave_key = os.getenv("BRAVE_KEY", "")
    if not brave_key or brave_key == "your-brave-api-key-here":
        print("❌ ERROR: BRAVE_KEY not configured in .env")
        print("\n📝 To fix:")
        print("   1. Add BRAVE_KEY=your-actual-key to .env")
        print("   2. Get key from: https://brave.com/search/api/")
        return False
    
    print(f"✅ BRAVE_KEY configured (key length: {len(brave_key)} chars)\n")
    
    # Test query
    test_query = "ServiceNow ITSM SOC2 ISO27001 security certifications"
    print(f"📋 Test Query: {test_query}\n")
    
    try:
        # Run search
        results = await search_client.search_web(
            query=test_query,
            max_results=3,
            site_hint="https://www.servicenow.com"
        )
        
        print(f"\n{'='*70}")
        print(f"📊 Results Summary")
        print(f"{'='*70}\n")
        
        if not results:
            print("⚠️  No results found (this might be normal for test queries)")
            return True  # Not necessarily an error
        
        print(f"✅ Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('title', 'No title')}")
            print(f"     URL: {result.get('url', 'No URL')}")
            print(f"     Snippet: {result.get('snippet', 'No snippet')[:100]}...")
            print()
        
        # Test caching
        print(f"\n{'='*70}")
        print("🔄 Testing Cache (second call should be instant)")
        print(f"{'='*70}\n")
        
        import time
        start = time.time()
        cached_results = await search_client.search_web(
            query=test_query,
            max_results=3,
            site_hint="https://www.servicenow.com"
        )
        elapsed = time.time() - start
        
        if elapsed < 0.1:
            print(f"✅ Cache working! Second call took {elapsed*1000:.1f}ms (should be instant)")
        else:
            print(f"⚠️  Cache may not be working (took {elapsed:.2f}s)")
        
        # Show cache stats
        stats = search_client.get_cache_stats()
        print(f"\n📊 Cache Stats: {stats}\n")
        
        print(f"{'='*70}")
        print("✅ Brave Search Integration Test PASSED")
        print(f"{'='*70}\n")
        
        return True
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERROR: Test failed")
        print(f"{'='*70}\n")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}\n")
        
        if "401" in str(e) or "403" in str(e):
            print("💡 This looks like an authentication error.")
            print("   Check that your BRAVE_KEY is correct.\n")
        elif "429" in str(e):
            print("💡 Rate limit hit.")
            print("   Wait a few seconds and try again.\n")
        else:
            print("💡 Unexpected error. Check your network connection.\n")
        
        return False


async def test_throttling():
    """Test that throttling is working"""
    print(f"\n{'='*70}")
    print("⏱️  Testing Throttling (should enforce 1+ second between calls)")
    print(f"{'='*70}\n")
    
    import time
    
    # Clear cache first
    search_client.clear_cache()
    
    queries = [
        "ServiceNow pricing",
        "Jira API documentation",
        "Salesforce SSO SAML"
    ]
    
    print("Running 3 different searches back-to-back...\n")
    
    start = time.time()
    for i, query in enumerate(queries, 1):
        print(f"  Search {i}/3: {query}...")
        try:
            await search_client.search_web(query, max_results=1)
        except:
            pass  # Ignore errors for throttling test
    elapsed = time.time() - start
    
    expected_min = (len(queries) - 1) * 1.0  # Should be at least 2 seconds for 3 calls
    
    print(f"\n⏱️  Total time: {elapsed:.2f}s")
    print(f"⏱️  Expected minimum: {expected_min:.2f}s")
    
    if elapsed >= expected_min:
        print(f"✅ Throttling working correctly!")
    else:
        print(f"⚠️  Throttling may not be working (too fast)")
    
    print()


async def main():
    """Run all tests"""
    success = await test_brave_search()
    
    if success:
        await test_throttling()
    
    # Clear cache for next run
    search_client.clear_cache()
    
    print("\n💡 Next steps:")
    print("   1. Run a full assessment: python main.py")
    print("   2. Watch backend logs for search API calls")
    print("   3. Check frontend for real-time event visualization\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user\n")
        sys.exit(0)

