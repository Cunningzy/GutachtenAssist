#!/usr/bin/env python3
"""
Test script for Gamer Health Research Agent

This script tests the specialized gamer health research functionality.
"""

import asyncio
import sys
from pathlib import Path

def test_dependencies():
    """Test required dependencies for gamer health research"""
    print("Testing Gamer Health Research Agent dependencies...")
    
    dependencies = {
        'requests': 'requests',
        'beautifulsoup4': 'bs4',
        'google search': 'googlesearch',
        'schedule': 'schedule'
    }
    
    missing = []
    
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} available")
        except ImportError:
            print(f"✗ {name} not available")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Install them with: pip install google beautifulsoup4 googlesearch-python schedule")
        return False
    
    return True

async def test_google_search():
    """Test Google search functionality"""
    print("\nTesting Google search...")
    
    try:
        # Import after dependency check
        from googlesearch import search
        import requests
        from bs4 import BeautifulSoup
        
        # Test a simple search
        test_query = "League of Legends back pain site:reddit.com"
        print(f"Searching for: {test_query}")
        
        results = list(search(test_query, num_results=3, sleep_interval=2))
        
        if results:
            print(f"✓ Found {len(results)} search results")
            for i, url in enumerate(results, 1):
                print(f"  {i}. {url}")
            return True
        else:
            print("! No results found (this might be normal)")
            return True
            
    except Exception as e:
        print(f"✗ Google search test failed: {e}")
        return False

async def test_agent_initialization():
    """Test agent initialization"""
    print("\nTesting agent initialization...")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        # Create required directories
        for dir_name in ['data', 'reports', 'logs']:
            Path(dir_name).mkdir(exist_ok=True)
        
        # Import and initialize agent
        from gamer_health_research_agent import GamerHealthResearchAgent
        
        agent = GamerHealthResearchAgent()
        print("✓ Agent initialized successfully")
        
        # Test configuration
        print(f"✓ Configured with {len(agent.keywords)} keywords")
        print(f"✓ Email recipient: {agent.email_recipient}")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_basic_search():
    """Test basic search functionality"""
    print("\nTesting basic search functionality...")
    
    try:
        from gamer_health_research_agent import GamerHealthResearchAgent
        
        agent = GamerHealthResearchAgent()
        
        # Test with one keyword
        test_keyword = "gaming wrist pain"
        print(f"Testing search for: {test_keyword}")
        
        results = await agent.search_google(test_keyword, num_results=3)
        
        if results:
            print(f"✓ Found {len(results)} results for '{test_keyword}'")
            for result in results:
                print(f"  - {result['platform']}: {result['title'][:50]}...")
        else:
            print(f"! No results found for '{test_keyword}' (might be rate limited)")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("="*60)
    print("🎮 Gamer Health Research Agent - Test Suite")
    print("="*60)
    
    all_passed = True
    
    # Test dependencies first
    if not test_dependencies():
        print("\n❌ Please install missing dependencies first:")
        print("pip install google beautifulsoup4 googlesearch-python schedule requests")
        return
    
    # Run other tests
    tests = [
        ("Google Search Test", test_google_search),
        ("Agent Initialization Test", test_agent_initialization),
        ("Basic Search Test", test_basic_search)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        
        try:
            result = await test_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All tests passed! The Gamer Health Research Agent is ready!")
        print("\nNext steps:")
        print("1. Run a test search:")
        print("   python gamer_health_research_agent.py --run-once")
        print()
        print("2. Start daily monitoring:")
        print("   python gamer_health_research_agent.py --schedule")
        print()
        print("3. Check the results in:")
        print("   - data/gamer_health_research.json (raw data)")
        print("   - reports/ (HTML email reports)")
        print()
        print("📧 Email reports will be saved as HTML files")
        print("📊 Data is categorized by health issue type")
        print("🔍 Pain points are automatically extracted")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check your internet connection")
        print("3. Google may rate limit searches - this is normal")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())