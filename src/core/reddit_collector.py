"""
Reddit Data Collector

This module handles data collection from Reddit using the PRAW (Python Reddit API Wrapper).
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
import re

try:
    import praw
    from praw.exceptions import PRAWException
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

from loguru import logger
from .social_media_collector import SocialMediaPost


class RedditCollector:
    """Reddit data collector using PRAW"""
    
    def __init__(self, config):
        """Initialize Reddit collector with configuration"""
        if not PRAW_AVAILABLE:
            raise ImportError("PRAW library not available. Install with: pip install praw")
            
        self.config = config
        self.reddit = praw.Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            user_agent=config.user_agent,
            username=config.username,
            password=config.password
        )
        
    async def collect_posts(self,
                          keywords: List[str] = None,
                          max_posts: int = 100,
                          time_range: int = 24,
                          subreddits: List[str] = None) -> List[SocialMediaPost]:
        """
        Collect posts from Reddit
        
        Args:
            keywords: Keywords to search for
            max_posts: Maximum number of posts to collect
            time_range: Time range in hours
            subreddits: Specific subreddits to search in
            
        Returns:
            List of SocialMediaPost objects
        """
        posts = []
        
        try:
            if subreddits is None:
                subreddits = ['all']
                
            for subreddit_name in subreddits:
                subreddit_posts = await self._collect_from_subreddit(
                    subreddit_name, keywords, max_posts // len(subreddits), time_range
                )
                posts.extend(subreddit_posts)
                
                if len(posts) >= max_posts:
                    break
                    
        except Exception as e:
            logger.error(f"Error collecting from Reddit: {e}")
            
        return posts[:max_posts]
        
    async def _collect_from_subreddit(self,
                                    subreddit_name: str,
                                    keywords: List[str],
                                    max_posts: int,
                                    time_range: int) -> List[SocialMediaPost]:
        """Collect posts from a specific subreddit"""
        posts = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get recent posts
            submissions = subreddit.new(limit=max_posts * 2)  # Get more to filter
            
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
            
            for submission in submissions:
                # Check if post is within time range
                post_time = datetime.utcfromtimestamp(submission.created_utc)
                if post_time < cutoff_time:
                    continue
                    
                # Filter by keywords if provided
                if keywords and not self._matches_keywords(submission, keywords):
                    continue
                    
                # Create SocialMediaPost object
                post = SocialMediaPost(
                    platform='reddit',
                    post_id=submission.id,
                    author=str(submission.author) if submission.author else '[deleted]',
                    content=f"{submission.title}\n\n{submission.selftext}",
                    timestamp=post_time,
                    url=f"https://reddit.com{submission.permalink}",
                    likes=submission.score,
                    shares=0,  # Reddit doesn't have shares
                    comments=submission.num_comments,
                    tags=[subreddit_name],
                    metadata={
                        'subreddit': subreddit_name,
                        'upvote_ratio': submission.upvote_ratio,
                        'gilded': submission.gilded,
                        'locked': submission.locked,
                        'nsfw': submission.over_18,
                        'stickied': submission.stickied
                    }
                )
                
                posts.append(post)
                
                if len(posts) >= max_posts:
                    break
                    
        except PRAWException as e:
            logger.error(f"PRAW error for subreddit {subreddit_name}: {e}")
        except Exception as e:
            logger.error(f"Error collecting from subreddit {subreddit_name}: {e}")
            
        return posts
        
    def _matches_keywords(self, submission, keywords: List[str]) -> bool:
        """Check if submission matches any of the keywords"""
        text = f"{submission.title} {submission.selftext}".lower()
        
        for keyword in keywords:
            if keyword.lower() in text:
                return True
                
        return False
        
    async def collect_comments(self, 
                             submission_id: str,
                             max_comments: int = 50) -> List[SocialMediaPost]:
        """
        Collect comments from a specific Reddit post
        
        Args:
            submission_id: Reddit submission ID
            max_comments: Maximum number of comments to collect
            
        Returns:
            List of SocialMediaPost objects representing comments
        """
        comments = []
        
        try:
            submission = self.reddit.submission(id=submission_id)
            submission.comments.replace_more(limit=0)  # Remove "more comments" links
            
            for comment in submission.comments.list()[:max_comments]:
                if hasattr(comment, 'body') and comment.body != '[deleted]':
                    comment_post = SocialMediaPost(
                        platform='reddit',
                        post_id=comment.id,
                        author=str(comment.author) if comment.author else '[deleted]',
                        content=comment.body,
                        timestamp=datetime.utcfromtimestamp(comment.created_utc),
                        url=f"https://reddit.com{comment.permalink}",
                        likes=comment.score,
                        shares=0,
                        comments=0,
                        tags=[submission.subreddit.display_name],
                        metadata={
                            'parent_id': submission_id,
                            'is_comment': True,
                            'gilded': comment.gilded,
                            'controversial': comment.controversiality > 0
                        }
                    )
                    comments.append(comment_post)
                    
        except Exception as e:
            logger.error(f"Error collecting comments for {submission_id}: {e}")
            
        return comments