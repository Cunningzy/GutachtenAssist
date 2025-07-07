#!/usr/bin/env python3
"""
Test script for Social Media Data Collection Agent

This script performs basic tests to ensure the agent is working correctly.
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.core.social_media_collector import SocialMediaCollector, SocialMediaPost
        print("✓ Core modules imported successfully")
        
        from src.utils.config import SocialMediaConfig
        print("✓ Configuration module imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from src.utils.config import SocialMediaConfig
        
        # Create config directories
        Path("config").mkdir(exist_ok=True)
        
        # Test config loading
        config = SocialMediaConfig("config/test_config.json")
        print("✓ Configuration loaded successfully")
        
        # Check that at least forums are enabled by default
        if config.forums_enabled:
            print("✓ Forums collector is enabled")
        else:
            print("! Forums collector is disabled")
            
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

async def test_basic_collection():
    """Test basic data collection functionality"""
    print("\nTesting basic collection...")
    
    try:
        from src.core.social_media_collector import SocialMediaCollector
        
        # Create necessary directories
        for dir_name in ['config', 'data', 'logs', 'exports']:
            Path(dir_name).mkdir(exist_ok=True)
        
        # Initialize collector
        collector = SocialMediaCollector("config/test_config.json")
        print("✓ Collector initialized successfully")
        
        # Test basic collection (only forums since they don't need API keys)
        results = await collector.collect_data(
            platforms=["forums"],
            keywords=["programming"],
            max_posts=5,  # Small number for testing
            time_range=24
        )
        
        print(f"✓ Collection completed: {sum(len(posts) for posts in results.values())} posts collected")
        
        # Test statistics
        stats = collector.get_statistics()
        print(f"✓ Statistics retrieved: {stats.get('total_posts', 0)} total posts in database")
        
        return True
    except Exception as e:
        print(f"✗ Collection error: {e}")
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that optional dependencies are available"""
    print("\nTesting dependencies...")
    
    # Test required dependencies
    required_deps = {
        'requests': 'requests',
        'sqlite3': 'sqlite3',
        'asyncio': 'asyncio',
        'json': 'json',
        'datetime': 'datetime',
        'pathlib': 'pathlib'
    }
    
    for name, module in required_deps.items():
        try:
            __import__(module)
            print(f"✓ {name} available")
        except ImportError:
            print(f"✗ {name} not available")
    
    # Test optional dependencies
    optional_deps = {
        'beautifulsoup4': 'bs4',
        'requests': 'requests',
        'pandas': 'pandas'
    }
    
    print("\nOptional dependencies:")
    for name, module in optional_deps.items():
        try:
            __import__(module)
            print(f"✓ {name} available")
        except ImportError:
            print(f"! {name} not available (optional)")

async def main():
    """Run all tests"""
    print("="*60)
    print("Social Media Data Collection Agent - Test Suite")
    print("="*60)
    
    all_passed = True
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Dependency Test", test_dependencies),
        ("Basic Collection Test", test_basic_collection)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
                
            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All tests passed! The agent is ready to use.")
        print("\nNext steps:")
        print("1. Update config/social_media_config.json with your API credentials")
        print("2. Run: python social_media_agent.py collect --help")
        print("3. Start collecting: python social_media_agent.py collect --keywords 'python'")
    else:
        print("❌ Some tests failed. Please check the output above.")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that Python 3.7+ is being used")
        print("3. Verify network connectivity")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())