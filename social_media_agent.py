#!/usr/bin/env python3
"""
Social Media Data Collection Agent

Main script to run the social media data collection agent.
This agent collects data from various social networks including Reddit, Twitter, Facebook, and forums.
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.core.social_media_collector import SocialMediaCollector
    from src.utils.logger import setup_logger
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def setup_directories():
    """Create necessary directories"""
    directories = ['config', 'data', 'logs', 'exports']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)


def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                 Social Media Data Collection Agent           ║
    ║                                                              ║
    ║  Collect data from Reddit, Twitter, Facebook, and Forums    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def run_collection(platforms: Optional[List[str]] = None,
                        keywords: Optional[List[str]] = None,
                        max_posts: int = 100,
                        time_range: int = 24,
                        continuous: bool = False,
                        interval: int = 60):
    """
    Run data collection
    
    Args:
        platforms: List of platforms to collect from
        keywords: Keywords to search for
        max_posts: Maximum posts to collect
        time_range: Time range in hours
        continuous: Whether to run continuously
        interval: Interval for continuous collection in minutes
    """
    logger = setup_logger()
    
    try:
        # Initialize collector
        collector = SocialMediaCollector()
        
        logger.info("Starting social media data collection...")
        
        if continuous:
            logger.info(f"Running in continuous mode (every {interval} minutes)")
            await collector.start_continuous_collection(
                platforms=platforms,
                keywords=keywords,
                interval_minutes=interval
            )
        else:
            # Single collection run
            results = await collector.collect_data(
                platforms=platforms,
                keywords=keywords,
                max_posts=max_posts,
                time_range=time_range
            )
            
            # Print results summary
            total_posts = sum(len(posts) for posts in results.values())
            logger.info(f"Collection completed! Total posts collected: {total_posts}")
            
            for platform, posts in results.items():
                logger.info(f"  {platform}: {len(posts)} posts")
                
            # Export results
            if total_posts > 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = f"exports/social_media_data_{timestamp}.json"
                collector.export_data(export_path, format='json')
                logger.info(f"Data exported to: {export_path}")
                
                # Also export as CSV
                csv_path = f"exports/social_media_data_{timestamp}.csv"
                collector.export_data(csv_path, format='csv')
                logger.info(f"Data exported to: {csv_path}")
                
    except KeyboardInterrupt:
        logger.info("Collection stopped by user")
    except Exception as e:
        logger.error(f"Error during collection: {e}")
        raise


async def show_statistics():
    """Show collection statistics"""
    logger = setup_logger()
    
    try:
        collector = SocialMediaCollector()
        stats = collector.get_statistics()
        
        print("\n" + "="*60)
        print("SOCIAL MEDIA DATA COLLECTION STATISTICS")
        print("="*60)
        
        print(f"\nTotal Posts: {stats.get('total_posts', 0)}")
        
        print("\nPosts by Platform:")
        for platform, count in stats.get('posts_by_platform', {}).items():
            print(f"  {platform.capitalize()}: {count}")
            
        print("\nRecent Posts by Date:")
        for date, count in list(stats.get('posts_by_date', {}).items())[:10]:
            print(f"  {date}: {count}")
            
        date_range = stats.get('date_range', {})
        if date_range.get('start') and date_range.get('end'):
            print(f"\nDate Range: {date_range['start']} to {date_range['end']}")
            
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")


async def search_collected_data(keywords: List[str],
                               platform: Optional[str] = None,
                               days_back: int = 7):
    """
    Search through collected data
    
    Args:
        keywords: Keywords to search for
        platform: Specific platform to search in
        days_back: How many days back to search
    """
    logger = setup_logger()
    
    try:
        collector = SocialMediaCollector()
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        posts = collector.get_collected_data(
            platform=platform,
            start_date=start_date,
            keywords=keywords
        )
        
        print(f"\nFound {len(posts)} posts matching your search:")
        print("-" * 50)
        
        for post in posts[:20]:  # Show first 20 results
            print(f"\nPlatform: {post.platform}")
            print(f"Author: {post.author}")
            print(f"Date: {post.timestamp}")
            print(f"Content: {post.content[:200]}...")
            print(f"URL: {post.url}")
            print(f"Likes: {post.likes}, Comments: {post.comments}")
            print("-" * 30)
            
        if len(posts) > 20:
            print(f"\n... and {len(posts) - 20} more results")
            
    except Exception as e:
        logger.error(f"Error searching data: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Social Media Data Collection Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic collection from all platforms
  python social_media_agent.py collect

  # Collect from specific platforms with keywords
  python social_media_agent.py collect --platforms reddit twitter --keywords "AI" "machine learning" --max-posts 200

  # Run continuous collection
  python social_media_agent.py collect --continuous --interval 30

  # Search collected data
  python social_media_agent.py search --keywords "python" "programming"

  # Show statistics
  python social_media_agent.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collection command
    collect_parser = subparsers.add_parser('collect', help='Collect social media data')
    collect_parser.add_argument('--platforms', nargs='+', 
                               choices=['reddit', 'twitter', 'facebook', 'forums'],
                               help='Platforms to collect from')
    collect_parser.add_argument('--keywords', nargs='+', 
                               help='Keywords to search for')
    collect_parser.add_argument('--max-posts', type=int, default=100,
                               help='Maximum posts to collect (default: 100)')
    collect_parser.add_argument('--time-range', type=int, default=24,
                               help='Time range in hours (default: 24)')
    collect_parser.add_argument('--continuous', action='store_true',
                               help='Run continuous collection')
    collect_parser.add_argument('--interval', type=int, default=60,
                               help='Collection interval in minutes (default: 60)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search collected data')
    search_parser.add_argument('--keywords', nargs='+', required=True,
                              help='Keywords to search for')
    search_parser.add_argument('--platform', 
                              choices=['reddit', 'twitter', 'facebook', 'forums'],
                              help='Platform to search in')
    search_parser.add_argument('--days-back', type=int, default=7,
                              help='Days back to search (default: 7)')
    
    # Statistics command
    subparsers.add_parser('stats', help='Show collection statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    # Setup
    setup_directories()
    print_banner()
    
    # Run command
    try:
        if args.command == 'collect':
            asyncio.run(run_collection(
                platforms=args.platforms,
                keywords=args.keywords,
                max_posts=args.max_posts,
                time_range=args.time_range,
                continuous=args.continuous,
                interval=args.interval
            ))
            
        elif args.command == 'search':
            asyncio.run(search_collected_data(
                keywords=args.keywords,
                platform=args.platform,
                days_back=args.days_back
            ))
            
        elif args.command == 'stats':
            asyncio.run(show_statistics())
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()