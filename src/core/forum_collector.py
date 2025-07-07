"""
Forum Data Collector

This module handles data collection from various web forums using web scraping techniques.
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

try:
    import aiohttp
    from bs4 import BeautifulSoup
    import requests
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from loguru import logger
from .social_media_collector import SocialMediaPost


class ForumCollector:
    """Generic forum data collector using web scraping"""
    
    def __init__(self, config):
        """Initialize forum collector with configuration"""
        if not SCRAPING_AVAILABLE:
            raise ImportError("Required scraping libraries not available. Install with: pip install beautifulsoup4 aiohttp requests")
            
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    async def collect_posts(self,
                          keywords: List[str] = None,
                          max_posts: int = 100,
                          time_range: int = 24) -> List[SocialMediaPost]:
        """
        Collect posts from configured forums
        
        Args:
            keywords: Keywords to search for
            max_posts: Maximum number of posts to collect
            time_range: Time range in hours
            
        Returns:
            List of SocialMediaPost objects
        """
        all_posts = []
        
        for url in self.config.urls:
            try:
                forum_posts = await self._scrape_forum(
                    url, keywords, max_posts // len(self.config.urls), time_range
                )
                all_posts.extend(forum_posts)
                
                # Respect rate limiting
                await asyncio.sleep(self.config.request_delay)
                
            except Exception as e:
                logger.error(f"Error scraping forum {url}: {e}")
                
        return all_posts[:max_posts]
        
    async def _scrape_forum(self,
                          url: str,
                          keywords: List[str],
                          max_posts: int,
                          time_range: int) -> List[SocialMediaPost]:
        """Scrape posts from a specific forum"""
        posts = []
        
        try:
            # Determine forum type and use appropriate scraper
            if 'reddit.com' in url:
                posts = await self._scrape_reddit_json(url, keywords, max_posts, time_range)
            elif 'news.ycombinator.com' in url:
                posts = await self._scrape_hackernews(url, keywords, max_posts, time_range)
            elif 'discourse' in url.lower() or self._is_discourse_forum(url):
                posts = await self._scrape_discourse(url, keywords, max_posts, time_range)
            else:
                # Generic forum scraping
                posts = await self._scrape_generic_forum(url, keywords, max_posts, time_range)
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            
        return posts
        
    async def _scrape_reddit_json(self,
                                url: str,
                                keywords: List[str],
                                max_posts: int,
                                time_range: int) -> List[SocialMediaPost]:
        """Scrape Reddit using JSON API"""
        posts = []
        
        try:
            # Make sure URL ends with .json
            if not url.endswith('.json'):
                url += '.json'
                
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
            
            for item in data.get('data', {}).get('children', []):
                post_data = item.get('data', {})
                
                # Check timestamp
                created_time = datetime.utcfromtimestamp(post_data.get('created_utc', 0))
                if created_time < cutoff_time:
                    continue
                    
                # Check keywords
                title = post_data.get('title', '')
                text = post_data.get('selftext', '')
                if keywords and not self._matches_keywords(f"{title} {text}", keywords):
                    continue
                    
                post = SocialMediaPost(
                    platform='reddit',
                    post_id=post_data.get('id', ''),
                    author=post_data.get('author', 'unknown'),
                    content=f"{title}\n\n{text}",
                    timestamp=created_time,
                    url=f"https://reddit.com{post_data.get('permalink', '')}",
                    likes=post_data.get('score', 0),
                    shares=0,
                    comments=post_data.get('num_comments', 0),
                    tags=[post_data.get('subreddit', '')],
                    metadata={
                        'subreddit': post_data.get('subreddit', ''),
                        'upvote_ratio': post_data.get('upvote_ratio', 0),
                        'gilded': post_data.get('gilded', 0),
                        'from_scraper': True
                    }
                )
                
                posts.append(post)
                
                if len(posts) >= max_posts:
                    break
                    
        except Exception as e:
            logger.error(f"Error scraping Reddit JSON {url}: {e}")
            
        return posts
        
    async def _scrape_hackernews(self,
                               url: str,
                               keywords: List[str],
                               max_posts: int,
                               time_range: int) -> List[SocialMediaPost]:
        """Scrape Hacker News"""
        posts = []
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all story rows
            story_rows = soup.find_all('tr', class_='athing')
            
            for story in story_rows[:max_posts]:
                try:
                    # Get story details
                    title_link = story.find('span', class_='titleline').find('a')
                    title = title_link.text.strip()
                    story_url = title_link.get('href', '')
                    
                    # Get metadata from next row
                    story_id = story.get('id', '')
                    meta_row = story.find_next_sibling('tr')
                    
                    if meta_row:
                        score_span = meta_row.find('span', class_='score')
                        score = int(score_span.text.split()[0]) if score_span else 0
                        
                        user_link = meta_row.find('a', class_='hnuser')
                        author = user_link.text if user_link else 'unknown'
                        
                        # Get comments count
                        comments_link = meta_row.find('a', string=re.compile(r'\d+\s+comment'))
                        comments = 0
                        if comments_link:
                            comments = int(re.search(r'(\d+)', comments_link.text).group(1))
                    else:
                        score = 0
                        author = 'unknown'
                        comments = 0
                    
                    # Check keywords
                    if keywords and not self._matches_keywords(title, keywords):
                        continue
                        
                    post = SocialMediaPost(
                        platform='hackernews',
                        post_id=story_id,
                        author=author,
                        content=title,
                        timestamp=datetime.utcnow(),  # HN doesn't provide exact timestamps in listing
                        url=story_url if story_url.startswith('http') else f"https://news.ycombinator.com/{story_url}",
                        likes=score,
                        shares=0,
                        comments=comments,
                        tags=['hackernews'],
                        metadata={
                            'from_scraper': True,
                            'hn_id': story_id
                        }
                    )
                    
                    posts.append(post)
                    
                except Exception as e:
                    logger.error(f"Error parsing HN story: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Hacker News: {e}")
            
        return posts
        
    async def _scrape_discourse(self,
                              url: str,
                              keywords: List[str],
                              max_posts: int,
                              time_range: int) -> List[SocialMediaPost]:
        """Scrape Discourse forums"""
        posts = []
        
        try:
            # Try Discourse JSON API first
            api_url = f"{url.rstrip('/')}/latest.json"
            
            response = self.session.get(api_url)
            response.raise_for_status()
            
            data = response.json()
            
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
            
            for topic in data.get('topic_list', {}).get('topics', []):
                try:
                    # Parse creation time
                    created_at = datetime.fromisoformat(topic.get('created_at', '').replace('Z', '+00:00'))
                    created_at = created_at.replace(tzinfo=None)
                    
                    if created_at < cutoff_time:
                        continue
                        
                    title = topic.get('title', '')
                    
                    # Check keywords
                    if keywords and not self._matches_keywords(title, keywords):
                        continue
                        
                    post = SocialMediaPost(
                        platform='discourse',
                        post_id=str(topic.get('id', '')),
                        author='unknown',  # Would need additional API call
                        content=title,
                        timestamp=created_at,
                        url=f"{url}/t/{topic.get('slug', '')}/{topic.get('id', '')}",
                        likes=topic.get('like_count', 0),
                        shares=0,
                        comments=topic.get('reply_count', 0),
                        tags=topic.get('tags', []),
                        metadata={
                            'category_id': topic.get('category_id'),
                            'views': topic.get('views', 0),
                            'from_scraper': True
                        }
                    )
                    
                    posts.append(post)
                    
                    if len(posts) >= max_posts:
                        break
                        
                except Exception as e:
                    logger.error(f"Error parsing Discourse topic: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Discourse forum {url}: {e}")
            
        return posts
        
    async def _scrape_generic_forum(self,
                                  url: str,
                                  keywords: List[str],
                                  max_posts: int,
                                  time_range: int) -> List[SocialMediaPost]:
        """Generic forum scraping fallback"""
        posts = []
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find common forum post patterns
            post_selectors = [
                'article',
                '.post',
                '.topic',
                '.thread',
                'tr[id*="post"]',
                'div[id*="post"]'
            ]
            
            for selector in post_selectors:
                elements = soup.select(selector)
                if elements:
                    break
            else:
                # Fallback: look for any elements with text content
                elements = soup.find_all(['article', 'div', 'section'], limit=max_posts)
                
            for i, element in enumerate(elements[:max_posts]):
                try:
                    # Extract text content
                    text = element.get_text(strip=True)
                    
                    if len(text) < 10:  # Skip very short content
                        continue
                        
                    # Check keywords
                    if keywords and not self._matches_keywords(text, keywords):
                        continue
                        
                    # Try to find links
                    link = element.find('a')
                    post_url = ''
                    if link and link.get('href'):
                        post_url = urljoin(url, link.get('href'))
                        
                    post = SocialMediaPost(
                        platform='forum',
                        post_id=f"generic_{i}",
                        author='unknown',
                        content=text[:500] + ('...' if len(text) > 500 else ''),  # Truncate long content
                        timestamp=datetime.utcnow(),
                        url=post_url,
                        likes=0,
                        shares=0,
                        comments=0,
                        tags=[urlparse(url).netloc],
                        metadata={
                            'source_url': url,
                            'from_scraper': True,
                            'generic_scrape': True
                        }
                    )
                    
                    posts.append(post)
                    
                except Exception as e:
                    logger.error(f"Error parsing generic forum element: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping generic forum {url}: {e}")
            
        return posts
        
    def _is_discourse_forum(self, url: str) -> bool:
        """Check if URL is a Discourse forum"""
        try:
            response = self.session.head(url, timeout=10)
            return 'discourse' in response.headers.get('server', '').lower()
        except:
            return False
            
    def _matches_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text matches any of the keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)