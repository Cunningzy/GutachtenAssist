"""
Social Media Data Collection Agent

This module provides a unified interface for collecting data from various social media platforms
including Reddit, Twitter, Facebook, and web forums.
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

import aiohttp
import requests
from loguru import logger
from tqdm import tqdm

from ..utils.config import SocialMediaConfig
from .reddit_collector import RedditCollector
from .twitter_collector import TwitterCollector
from .facebook_collector import FacebookCollector
from .forum_collector import ForumCollector


@dataclass
class SocialMediaPost:
    """Data structure for social media posts"""
    platform: str
    post_id: str
    author: str
    content: str
    timestamp: datetime
    url: str
    likes: int = 0
    shares: int = 0
    comments: int = 0
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class SocialMediaCollector:
    """Main social media data collection coordinator"""
    
    def __init__(self, config_path: str = "config/social_media_config.json"):
        """Initialize the social media collector with configuration"""
        self.config = SocialMediaConfig(config_path)
        self.db_path = Path("data/social_media.db")
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Initialize platform collectors
        self.collectors = {}
        self._init_collectors()
        self._init_database()
        
    def _init_collectors(self):
        """Initialize collectors for each platform"""
        if self.config.reddit_enabled:
            self.collectors['reddit'] = RedditCollector(self.config.reddit_config)
            
        if self.config.twitter_enabled:
            self.collectors['twitter'] = TwitterCollector(self.config.twitter_config)
            
        if self.config.facebook_enabled:
            self.collectors['facebook'] = FacebookCollector(self.config.facebook_config)
            
        if self.config.forums_enabled:
            self.collectors['forums'] = ForumCollector(self.config.forums_config)
            
        logger.info(f"Initialized {len(self.collectors)} platform collectors")
        
    def _init_database(self):
        """Initialize SQLite database for storing collected data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    post_id TEXT NOT NULL,
                    author TEXT,
                    content TEXT,
                    timestamp DATETIME,
                    url TEXT,
                    likes INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    tags TEXT,
                    metadata TEXT,
                    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, post_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_platform_timestamp 
                ON posts(platform, timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_collected_at 
                ON posts(collected_at)
            """)
            
    async def collect_data(self, 
                          platforms: Optional[List[str]] = None,
                          keywords: Optional[List[str]] = None,
                          max_posts: int = 1000,
                          time_range: int = 24) -> Dict[str, List[SocialMediaPost]]:
        """
        Collect data from specified platforms
        
        Args:
            platforms: List of platforms to collect from (None for all)
            keywords: Keywords to search for
            max_posts: Maximum posts per platform
            time_range: Time range in hours to collect data from
            
        Returns:
            Dictionary mapping platform names to lists of posts
        """
        if platforms is None:
            platforms = list(self.collectors.keys())
            
        results = {}
        tasks = []
        
        for platform in platforms:
            if platform in self.collectors:
                task = self._collect_from_platform(
                    platform, keywords, max_posts, time_range
                )
                tasks.append(task)
                
        # Execute all collection tasks concurrently
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, platform in enumerate(platforms):
            if platform in self.collectors:
                if isinstance(platform_results[i], Exception):
                    logger.error(f"Error collecting from {platform}: {platform_results[i]}")
                    results[platform] = []
                else:
                    results[platform] = platform_results[i]
                    
        return results
        
    async def _collect_from_platform(self,
                                   platform: str,
                                   keywords: Optional[List[str]],
                                   max_posts: int,
                                   time_range: int) -> List[SocialMediaPost]:
        """Collect data from a specific platform"""
        collector = self.collectors[platform]
        
        try:
            logger.info(f"Starting data collection from {platform}")
            posts = await collector.collect_posts(
                keywords=keywords,
                max_posts=max_posts,
                time_range=time_range
            )
            
            # Store posts in database
            self._store_posts(posts)
            
            logger.info(f"Collected {len(posts)} posts from {platform}")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to collect from {platform}: {e}")
            raise
            
    def _store_posts(self, posts: List[SocialMediaPost]):
        """Store posts in the database"""
        with sqlite3.connect(self.db_path) as conn:
            for post in posts:
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO posts 
                        (platform, post_id, author, content, timestamp, url, 
                         likes, shares, comments, tags, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        post.platform,
                        post.post_id,
                        post.author,
                        post.content,
                        post.timestamp,
                        post.url,
                        post.likes,
                        post.shares,
                        post.comments,
                        json.dumps(post.tags) if post.tags else None,
                        json.dumps(post.metadata) if post.metadata else None
                    ))
                except sqlite3.IntegrityError:
                    # Post already exists, skip
                    continue
                    
    def get_collected_data(self,
                          platform: Optional[str] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          keywords: Optional[List[str]] = None) -> List[SocialMediaPost]:
        """
        Retrieve collected data from database
        
        Args:
            platform: Specific platform to filter by
            start_date: Start date for filtering
            end_date: End date for filtering
            keywords: Keywords to search in content
            
        Returns:
            List of SocialMediaPost objects
        """
        query = "SELECT * FROM posts WHERE 1=1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
            
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
            
        if keywords:
            keyword_conditions = " OR ".join(["content LIKE ?" for _ in keywords])
            query += f" AND ({keyword_conditions})"
            params.extend([f"%{keyword}%" for keyword in keywords])
            
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            posts = []
            for row in cursor.fetchall():
                post = SocialMediaPost(
                    platform=row['platform'],
                    post_id=row['post_id'],
                    author=row['author'],
                    content=row['content'],
                    timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None,
                    url=row['url'],
                    likes=row['likes'],
                    shares=row['shares'],
                    comments=row['comments'],
                    tags=json.loads(row['tags']) if row['tags'] else [],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
                posts.append(post)
                
        return posts
        
    def export_data(self, output_path: str, format: str = 'json'):
        """
        Export collected data to file
        
        Args:
            output_path: Path to output file
            format: Export format ('json', 'csv', 'xlsx')
        """
        posts = self.get_collected_data()
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(post) for post in posts], f, 
                         ensure_ascii=False, indent=2, default=str)
                         
        elif format == 'csv':
            import pandas as pd
            df = pd.DataFrame([asdict(post) for post in posts])
            df.to_csv(output_path, index=False, encoding='utf-8')
            
        elif format == 'xlsx':
            import pandas as pd
            df = pd.DataFrame([asdict(post) for post in posts])
            df.to_excel(output_path, index=False, engine='openpyxl')
            
        logger.info(f"Exported {len(posts)} posts to {output_path}")
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total posts by platform
            cursor = conn.execute("""
                SELECT platform, COUNT(*) as count 
                FROM posts 
                GROUP BY platform
            """)
            stats['posts_by_platform'] = dict(cursor.fetchall())
            
            # Posts by date
            cursor = conn.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM posts 
                WHERE timestamp IS NOT NULL
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            """)
            stats['posts_by_date'] = dict(cursor.fetchall())
            
            # Total posts
            cursor = conn.execute("SELECT COUNT(*) FROM posts")
            stats['total_posts'] = cursor.fetchone()[0]
            
            # Date range
            cursor = conn.execute("""
                SELECT MIN(timestamp), MAX(timestamp) 
                FROM posts 
                WHERE timestamp IS NOT NULL
            """)
            min_date, max_date = cursor.fetchone()
            stats['date_range'] = {'start': min_date, 'end': max_date}
            
        return stats
        
    async def start_continuous_collection(self,
                                        platforms: Optional[List[str]] = None,
                                        keywords: Optional[List[str]] = None,
                                        interval_minutes: int = 60):
        """
        Start continuous data collection
        
        Args:
            platforms: Platforms to collect from
            keywords: Keywords to search for
            interval_minutes: Collection interval in minutes
        """
        logger.info(f"Starting continuous collection every {interval_minutes} minutes")
        
        while True:
            try:
                await self.collect_data(platforms=platforms, keywords=keywords)
                logger.info(f"Collection cycle completed. Next cycle in {interval_minutes} minutes.")
                
                # Wait for next collection cycle
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Continuous collection stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous collection: {e}")
                # Wait before retrying
                await asyncio.sleep(300)  # 5 minutes