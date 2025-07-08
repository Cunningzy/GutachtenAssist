"""
Twitter Data Collector

This module handles data collection from Twitter using the tweepy library.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
import re

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

from loguru import logger
from .social_media_collector import SocialMediaPost


class TwitterCollector:
    """Twitter data collector using tweepy"""
    
    def __init__(self, config):
        """Initialize Twitter collector with configuration"""
        if not TWEEPY_AVAILABLE:
            raise ImportError("Tweepy library not available. Install with: pip install tweepy")
            
        self.config = config
        
        # Initialize Twitter API client
        if config.bearer_token:
            self.client = tweepy.Client(bearer_token=config.bearer_token)
        else:
            auth = tweepy.OAuthHandler(config.api_key, config.api_secret)
            auth.set_access_token(config.access_token, config.access_token_secret)
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            self.client = tweepy.Client(
                consumer_key=config.api_key,
                consumer_secret=config.api_secret,
                access_token=config.access_token,
                access_token_secret=config.access_token_secret,
                wait_on_rate_limit=True
            )
            
    async def collect_posts(self,
                          keywords: List[str] = None,
                          max_posts: int = 100,
                          time_range: int = 24) -> List[SocialMediaPost]:
        """
        Collect posts from Twitter
        
        Args:
            keywords: Keywords to search for
            max_posts: Maximum number of posts to collect
            time_range: Time range in hours
            
        Returns:
            List of SocialMediaPost objects
        """
        posts = []
        
        try:
            if keywords:
                # Search for tweets with keywords
                for keyword in keywords:
                    keyword_posts = await self._search_tweets(keyword, max_posts // len(keywords), time_range)
                    posts.extend(keyword_posts)
            else:
                # Get recent tweets from timeline
                posts = await self._get_timeline_tweets(max_posts, time_range)
                
        except Exception as e:
            logger.error(f"Error collecting from Twitter: {e}")
            
        return posts[:max_posts]
        
    async def _search_tweets(self, 
                           query: str,
                           max_posts: int,
                           time_range: int) -> List[SocialMediaPost]:
        """Search for tweets with specific query"""
        posts = []
        
        try:
            # Calculate start time for search
            start_time = datetime.utcnow() - timedelta(hours=time_range)
            
            # Search tweets
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                start_time=start_time,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                user_fields=['username', 'name'],
                expansions=['author_id'],
                max_results=min(max_posts, 100)  # Twitter API limit
            ).flatten(limit=max_posts)
            
            # Process tweets
            for tweet in tweets:
                post = self._tweet_to_post(tweet)
                if post:
                    posts.append(post)
                    
        except tweepy.TooManyRequests:
            logger.warning("Twitter API rate limit reached")
        except Exception as e:
            logger.error(f"Error searching Twitter for '{query}': {e}")
            
        return posts
        
    async def _get_timeline_tweets(self, max_posts: int, time_range: int) -> List[SocialMediaPost]:
        """Get tweets from user timeline"""
        posts = []
        
        try:
            # Get user's timeline
            tweets = tweepy.Paginator(
                self.client.get_home_timeline,
                tweet_fields=['created_at', 'author_id', 'public_metrics'],
                user_fields=['username', 'name'],
                expansions=['author_id'],
                max_results=min(max_posts, 100)
            ).flatten(limit=max_posts)
            
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
            
            for tweet in tweets:
                if tweet.created_at.replace(tzinfo=None) < cutoff_time:
                    continue
                    
                post = self._tweet_to_post(tweet)
                if post:
                    posts.append(post)
                    
        except Exception as e:
            logger.error(f"Error getting timeline tweets: {e}")
            
        return posts
        
    def _tweet_to_post(self, tweet) -> Optional[SocialMediaPost]:
        """Convert Twitter tweet to SocialMediaPost"""
        try:
            # Extract hashtags
            hashtags = re.findall(r'#\w+', tweet.text)
            
            post = SocialMediaPost(
                platform='twitter',
                post_id=tweet.id,
                author=tweet.author.username if hasattr(tweet, 'author') else 'unknown',
                content=tweet.text,
                timestamp=tweet.created_at.replace(tzinfo=None),
                url=f"https://twitter.com/user/status/{tweet.id}",
                likes=tweet.public_metrics.get('like_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                shares=tweet.public_metrics.get('retweet_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                comments=tweet.public_metrics.get('reply_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                tags=hashtags,
                metadata={
                    'quote_count': tweet.public_metrics.get('quote_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                    'lang': getattr(tweet, 'lang', 'unknown'),
                    'possibly_sensitive': getattr(tweet, 'possibly_sensitive', False),
                    'reply_settings': getattr(tweet, 'reply_settings', None)
                }
            )
            
            return post
            
        except Exception as e:
            logger.error(f"Error converting tweet to post: {e}")
            return None
            
    async def collect_user_tweets(self, 
                                username: str,
                                max_posts: int = 50) -> List[SocialMediaPost]:
        """
        Collect tweets from a specific user
        
        Args:
            username: Twitter username (without @)
            max_posts: Maximum number of tweets to collect
            
        Returns:
            List of SocialMediaPost objects
        """
        posts = []
        
        try:
            # Get user ID
            user = self.client.get_user(username=username)
            if not user.data:
                logger.warning(f"User {username} not found")
                return posts
                
            # Get user's tweets
            tweets = tweepy.Paginator(
                self.client.get_users_tweets,
                user.data.id,
                tweet_fields=['created_at', 'public_metrics'],
                max_results=min(max_posts, 100)
            ).flatten(limit=max_posts)
            
            for tweet in tweets:
                post = self._tweet_to_post(tweet)
                if post:
                    post.author = username  # Ensure correct username
                    posts.append(post)
                    
        except Exception as e:
            logger.error(f"Error collecting tweets from user {username}: {e}")
            
        return posts