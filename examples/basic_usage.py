#!/usr/bin/env python3
"""
Basic Usage Example for Social Media Data Collection Agent

This script demonstrates how to use the social media agent programmatically.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.social_media_collector import SocialMediaCollector
from src.utils.logger import setup_logger


async def basic_collection_example():
    """Basic data collection example"""
    logger = setup_logger()
    
    # Initialize the collector
    collector = SocialMediaCollector("config/social_media_config.json")
    
    logger.info("Starting basic data collection...")
    
    # Collect data from all available platforms
    results = await collector.collect_data(
        keywords=["python", "programming", "AI", "machine learning"],
        max_posts=50,
        time_range=24  # Last 24 hours
    )
    
    # Print results
    total_posts = sum(len(posts) for posts in results.values())
    logger.info(f"Collected {total_posts} posts in total")
    
    for platform, posts in results.items():
        logger.info(f"{platform}: {len(posts)} posts")
        
        # Show first few posts
        for post in posts[:3]:
            logger.info(f"  - {post.author}: {post.content[:100]}...")
    
    return results


async def platform_specific_example():
    """Platform-specific collection example"""
    logger = setup_logger()
    
    collector = SocialMediaCollector("config/social_media_config.json")
    
    # Collect only from forums (since they don't require API keys)
    logger.info("Collecting from forums only...")
    
    results = await collector.collect_data(
        platforms=["forums"],
        keywords=["technology", "programming"],
        max_posts=20,
        time_range=12
    )
    
    for platform, posts in results.items():
        logger.info(f"Found {len(posts)} posts from {platform}")


async def data_analysis_example():
    """Example of analyzing collected data"""
    logger = setup_logger()
    
    collector = SocialMediaCollector("config/social_media_config.json")
    
    # Get statistics
    stats = collector.get_statistics()
    logger.info("Collection Statistics:")
    logger.info(f"Total posts: {stats.get('total_posts', 0)}")
    
    # Search for specific content
    posts = collector.get_collected_data(
        keywords=["python"],
        start_date=datetime.now() - timedelta(days=7)
    )
    
    logger.info(f"Found {len(posts)} posts containing 'python' in last 7 days")
    
    # Analyze by platform
    platform_counts = {}
    for post in posts:
        platform_counts[post.platform] = platform_counts.get(post.platform, 0) + 1
    
    logger.info("Posts by platform:")
    for platform, count in platform_counts.items():
        logger.info(f"  {platform}: {count}")


async def export_example():
    """Example of exporting collected data"""
    logger = setup_logger()
    
    collector = SocialMediaCollector("config/social_media_config.json")
    
    # Collect some data first
    await collector.collect_data(
        platforms=["forums"],
        keywords=["programming"],
        max_posts=30
    )
    
    # Export in different formats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON export
    json_path = f"exports/example_data_{timestamp}.json"
    collector.export_data(json_path, format='json')
    logger.info(f"Exported to JSON: {json_path}")
    
    # CSV export
    csv_path = f"exports/example_data_{timestamp}.csv"
    collector.export_data(csv_path, format='csv')
    logger.info(f"Exported to CSV: {csv_path}")


async def continuous_collection_example():
    """Example of continuous data collection"""
    logger = setup_logger()
    
    collector = SocialMediaCollector("config/social_media_config.json")
    
    logger.info("Starting continuous collection (will run for 5 minutes)...")
    
    # This would run indefinitely, but we'll stop it after a short time
    try:
        await asyncio.wait_for(
            collector.start_continuous_collection(
                platforms=["forums"],
                keywords=["technology"],
                interval_minutes=2  # Collect every 2 minutes
            ),
            timeout=300  # Stop after 5 minutes
        )
    except asyncio.TimeoutError:
        logger.info("Continuous collection example completed")


async def main():
    """Run all examples"""
    # Create necessary directories
    Path("exports").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    print("="*60)
    print("Social Media Data Collection Agent - Examples")
    print("="*60)
    
    # Run examples
    try:
        print("\n1. Basic Collection Example")
        print("-" * 30)
        await basic_collection_example()
        
        print("\n2. Platform-Specific Example")
        print("-" * 30)
        await platform_specific_example()
        
        print("\n3. Data Analysis Example")
        print("-" * 30)
        await data_analysis_example()
        
        print("\n4. Export Example")
        print("-" * 30)
        await export_example()
        
        print("\n5. Continuous Collection Example")
        print("-" * 30)
        await continuous_collection_example()
        
        print("\nAll examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())