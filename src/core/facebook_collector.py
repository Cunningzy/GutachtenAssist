"""
Facebook Data Collector

This module handles data collection from Facebook using the facebook-sdk library.
Note: Facebook's API has strict limitations and requires special permissions for most data.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
import re

try:
    import facebook
    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    FACEBOOK_SDK_AVAILABLE = False

from loguru import logger
from .social_media_collector import SocialMediaPost


class FacebookCollector:
    """Facebook data collector using facebook-sdk"""
    
    def __init__(self, config):
        """Initialize Facebook collector with configuration"""
        if not FACEBOOK_SDK_AVAILABLE:
            raise ImportError("Facebook SDK not available. Install with: pip install facebook-sdk")
            
        self.config = config
        self.graph = facebook.GraphAPI(access_token=config.access_token)
        
    async def collect_posts(self,
                          keywords: List[str] = None,
                          max_posts: int = 100,
                          time_range: int = 24) -> List[SocialMediaPost]:
        """
        Collect posts from Facebook
        
        Note: Due to Facebook API limitations, this mainly collects from pages
        that the app has access to, not general public posts.
        
        Args:
            keywords: Keywords to search for (limited functionality)
            max_posts: Maximum number of posts to collect
            time_range: Time range in hours
            
        Returns:
            List of SocialMediaPost objects
        """
        posts = []
        
        try:
            # Get user's own posts (requires appropriate permissions)
            user_posts = await self._get_user_posts(max_posts, time_range)
            posts.extend(user_posts)
            
            # Note: Public post search is very limited in Facebook API
            logger.warning("Facebook API has limited public data access. Only user's own posts are collected.")
            
        except Exception as e:
            logger.error(f"Error collecting from Facebook: {e}")
            
        return posts[:max_posts]
        
    async def _get_user_posts(self, max_posts: int, time_range: int) -> List[SocialMediaPost]:
        """Get posts from user's own timeline"""
        posts = []
        
        try:
            # Get user's posts
            user_posts = self.graph.get_object(
                'me/posts',
                fields='id,message,created_time,permalink_url,likes.summary(true),comments.summary(true),shares'
            )
            
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
            
            for post_data in user_posts.get('data', []):
                # Parse creation time
                created_time = datetime.strptime(
                    post_data['created_time'], 
                    '%Y-%m-%dT%H:%M:%S%z'
                ).replace(tzinfo=None)
                
                if created_time < cutoff_time:
                    continue
                    
                post = SocialMediaPost(
                    platform='facebook',
                    post_id=post_data['id'],
                    author='me',  # User's own posts
                    content=post_data.get('message', ''),
                    timestamp=created_time,
                    url=post_data.get('permalink_url', ''),
                    likes=post_data.get('likes', {}).get('summary', {}).get('total_count', 0),
                    shares=post_data.get('shares', {}).get('count', 0),
                    comments=post_data.get('comments', {}).get('summary', {}).get('total_count', 0),
                    tags=[],
                    metadata={
                        'type': post_data.get('type', 'status'),
                        'status_type': post_data.get('status_type', 'unknown')
                    }
                )
                
                posts.append(post)
                
                if len(posts) >= max_posts:
                    break
                    
        except facebook.GraphAPIError as e:
            logger.error(f"Facebook Graph API error: {e}")
        except Exception as e:
            logger.error(f"Error getting user posts: {e}")
            
        return posts
        
    async def collect_page_posts(self, 
                               page_id: str,
                               max_posts: int = 50) -> List[SocialMediaPost]:
        """
        Collect posts from a specific Facebook page
        
        Args:
            page_id: Facebook page ID
            max_posts: Maximum number of posts to collect
            
        Returns:
            List of SocialMediaPost objects
        """
        posts = []
        
        try:
            # Get page posts
            page_posts = self.graph.get_object(
                f'{page_id}/posts',
                fields='id,message,created_time,permalink_url,likes.summary(true),comments.summary(true),shares,from'
            )
            
            for post_data in page_posts.get('data', []):
                created_time = datetime.strptime(
                    post_data['created_time'], 
                    '%Y-%m-%dT%H:%M:%S%z'
                ).replace(tzinfo=None)
                
                post = SocialMediaPost(
                    platform='facebook',
                    post_id=post_data['id'],
                    author=post_data.get('from', {}).get('name', 'unknown'),
                    content=post_data.get('message', ''),
                    timestamp=created_time,
                    url=post_data.get('permalink_url', ''),
                    likes=post_data.get('likes', {}).get('summary', {}).get('total_count', 0),
                    shares=post_data.get('shares', {}).get('count', 0),
                    comments=post_data.get('comments', {}).get('summary', {}).get('total_count', 0),
                    tags=[],
                    metadata={
                        'page_id': page_id,
                        'type': post_data.get('type', 'status')
                    }
                )
                
                posts.append(post)
                
                if len(posts) >= max_posts:
                    break
                    
        except facebook.GraphAPIError as e:
            logger.error(f"Facebook Graph API error for page {page_id}: {e}")
        except Exception as e:
            logger.error(f"Error collecting from page {page_id}: {e}")
            
        return posts
        
    async def search_public_posts(self, query: str, max_posts: int = 50) -> List[SocialMediaPost]:
        """
        Search for public posts (very limited functionality)
        
        Note: This functionality is heavily restricted by Facebook API
        
        Args:
            query: Search query
            max_posts: Maximum number of posts
            
        Returns:
            List of SocialMediaPost objects
        """
        posts = []
        
        try:
            # Facebook search is very limited for posts
            logger.warning("Facebook public post search is heavily restricted and may not return results")
            
            # Attempt to search (likely to fail due to API restrictions)
            search_results = self.graph.search(
                type='post',
                q=query,
                fields='id,message,created_time,from'
            )
            
            for post_data in search_results.get('data', []):
                created_time = datetime.strptime(
                    post_data['created_time'], 
                    '%Y-%m-%dT%H:%M:%S%z'
                ).replace(tzinfo=None)
                
                post = SocialMediaPost(
                    platform='facebook',
                    post_id=post_data['id'],
                    author=post_data.get('from', {}).get('name', 'unknown'),
                    content=post_data.get('message', ''),
                    timestamp=created_time,
                    url='',  # Permalink not available in search
                    likes=0,  # Metrics not available in search
                    shares=0,
                    comments=0,
                    tags=[],
                    metadata={
                        'search_query': query,
                        'from_search': True
                    }
                )
                
                posts.append(post)
                
                if len(posts) >= max_posts:
                    break
                    
        except facebook.GraphAPIError as e:
            logger.error(f"Facebook search error: {e}")
        except Exception as e:
            logger.error(f"Error searching Facebook: {e}")
            
        return posts