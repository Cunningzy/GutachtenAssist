#!/usr/bin/env python3
"""
Gamer Health Research Agent

Specialized agent for collecting information about League of Legends players' health issues
and pain points. Focuses on market research for product-market fit analysis.
"""

import asyncio
import json
import smtplib
import schedule
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import requests
    from bs4 import BeautifulSoup
    import praw
    from googlesearch import search
    from src.utils.logger import setup_logger
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install: pip install google beautifulsoup4 praw requests")
    DEPENDENCIES_AVAILABLE = False


class GamerHealthResearchAgent:
    """Agent specialized for researching League of Legends player health issues"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.keywords = [
            # Physical health issues
            "health issues League of Legends players",
            "League of Legends back pain",
            "back pain after long gaming sessions",
            "gaming posture problems",
            "neck pain from gaming",
            "wrist pain from gaming",
            "LoL carpal tunnel",
            "anyone else have wrist pain from gaming?",
            "League of Legends eye strain",
            
            # Mental health issues
            "League of Legends mental health",
            "anxiety when playing League of Legends",
            "LoL ranked anxiety",
            "League of Legends social anxiety",
            "how to handle stress from League of Legends",
            "how to deal with tilt in League of Legends",
            "I rage too much in League of Legends",
            "can't stop playing League of Legends",
            "League of Legends is making me depressed",
            
            # Product-related searches (existing solutions)
            "best chair for League of Legends gamers with back pain",
            "best gaming chair for back pain",
            "gaming chair back pain recommendations",
            "best gaming mouse for carpal tunnel",
            "vertical gaming mouse for wrist pain",
            "ergonomic keyboard for gaming",
            "wrist rest for gaming",
            "wrist brace for gaming carpal tunnel",
            "blue light glasses for gaming",
            "standing desk for gaming",
            
            # Platform-specific searches
            "reddit League of Legends health issues",
            "reddit LoL back pain",
            "reddit LoL wrist pain",
            "reddit LoL anxiety",
            "League of Legends forum health issues",
            "gaming forum wrist pain",
            "YouTube gaming wrist pain exercises",
            "YouTube League of Legends mental health"
        ]
        
        self.data_file = Path("data/gamer_health_research.json")
        self.data_file.parent.mkdir(exist_ok=True)
        
        # Email configuration
        self.email_recipient = "kharninngz@gmail.com"
        
    async def search_google(self, keyword: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search Google for a specific keyword"""
        results = []
        
        try:
            self.logger.info(f"Searching Google for: {keyword}")
            
            # Use googlesearch library
            search_results = search(keyword, num_results=num_results, sleep_interval=2)
            
            for url in search_results:
                try:
                    # Get page content
                    response = requests.get(url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; GamerHealthResearch/1.0)'
                    })
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        title = soup.find('title')
                        title_text = title.text.strip() if title else "No title"
                        
                        # Extract some content
                        content = ""
                        for p in soup.find_all('p')[:3]:  # First 3 paragraphs
                            content += p.get_text(strip=True) + " "
                        
                        result = {
                            'keyword': keyword,
                            'url': url,
                            'title': title_text,
                            'content_preview': content[:500] + "..." if len(content) > 500 else content,
                            'platform': self._identify_platform(url),
                            'timestamp': datetime.now().isoformat(),
                            'search_engine': 'google'
                        }
                        
                        results.append(result)
                        
                except Exception as e:
                    self.logger.error(f"Error processing URL {url}: {e}")
                    continue
                    
                # Rate limiting
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error searching for '{keyword}': {e}")
            
        return results
    
    def _identify_platform(self, url: str) -> str:
        """Identify the platform from URL"""
        url_lower = url.lower()
        
        if 'reddit.com' in url_lower:
            return 'reddit'
        elif 'facebook.com' in url_lower:
            return 'facebook'
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'amazon.com' in url_lower:
            return 'amazon_reviews'
        elif 'steelseries.com' in url_lower or 'razer.com' in url_lower or 'logitech.com' in url_lower:
            return 'product_site'
        elif 'trustpilot.com' in url_lower or 'reviews.com' in url_lower:
            return 'review_site'
        elif any(forum in url_lower for forum in ['forum', 'community', 'discussion']):
            return 'forum'
        else:
            return 'website'
    
    def _categorize_issue(self, keyword: str, content: str) -> str:
        """Categorize the health issue type"""
        keyword_lower = keyword.lower()
        content_lower = content.lower()
        
        physical_terms = ['back pain', 'neck pain', 'wrist pain', 'carpal tunnel', 'posture', 'eye strain']
        mental_terms = ['anxiety', 'stress', 'depression', 'rage', 'tilt', 'mental health', 'social anxiety']
        product_terms = ['chair', 'mouse', 'keyboard', 'desk', 'glasses', 'wrist rest', 'brace']
        
        if any(term in keyword_lower or term in content_lower for term in physical_terms):
            return 'Physical Health'
        elif any(term in keyword_lower or term in content_lower for term in mental_terms):
            return 'Mental Health'
        elif any(term in keyword_lower or term in content_lower for term in product_terms):
            return 'Product Solutions'
        else:
            return 'General Gaming Health'
    
    def _extract_pain_points(self, content: str) -> List[str]:
        """Extract pain points and problems from content"""
        pain_indicators = [
            'problem', 'issue', 'pain', 'hurt', 'ache', 'uncomfortable', 'difficult',
            'struggle', 'can\'t', 'unable', 'frustrated', 'annoyed', 'terrible',
            'awful', 'worst', 'bad experience', 'doesn\'t work', 'failed',
            'disappointed', 'waste of money', 'regret', 'mistake'
        ]
        
        pain_points = []
        sentences = content.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in pain_indicators):
                pain_points.append(sentence.strip())
        
        return pain_points[:3]  # Top 3 pain points
    
    async def search_reddit_specific(self, keyword: str) -> List[Dict[str, Any]]:
        """Search Reddit specifically for gaming health discussions"""
        results = []
        
        try:
            # Search Reddit via Google site search
            reddit_query = f"site:reddit.com {keyword}"
            google_results = await self.search_google(reddit_query, num_results=15)
            
            for result in google_results:
                if 'reddit.com' in result['url']:
                    # Extract additional Reddit-specific information
                    result['subreddit'] = self._extract_subreddit(result['url'])
                    result['pain_points'] = self._extract_pain_points(result['content_preview'])
                    results.append(result)
                    
        except Exception as e:
            self.logger.error(f"Error searching Reddit for '{keyword}': {e}")
            
        return results
    
    def _extract_subreddit(self, url: str) -> str:
        """Extract subreddit name from Reddit URL"""
        try:
            if '/r/' in url:
                return url.split('/r/')[1].split('/')[0]
            return 'unknown'
        except:
            return 'unknown'
    
    async def run_daily_research(self) -> Dict[str, Any]:
        """Run the daily research cycle"""
        self.logger.info("Starting daily gamer health research...")
        
        all_results = []
        
        # Search each keyword
        for keyword in self.keywords:
            try:
                # Google search
                google_results = await self.search_google(keyword, num_results=8)
                all_results.extend(google_results)
                
                # Reddit-specific search
                reddit_results = await self.search_reddit_specific(keyword)
                all_results.extend(reddit_results)
                
                # Rate limiting between keywords
                await asyncio.sleep(3)
                
            except Exception as e:
                self.logger.error(f"Error researching keyword '{keyword}': {e}")
                continue
        
        # Process and categorize results
        processed_results = self._process_results(all_results)
        
        # Save to file
        self._save_results(processed_results)
        
        # Send email report
        await self._send_email_report(processed_results)
        
        self.logger.info(f"Research completed. Found {len(all_results)} total results")
        
        return processed_results
    
    def _process_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and categorize the research results"""
        processed = {
            'timestamp': datetime.now().isoformat(),
            'total_results': len(results),
            'by_category': {},
            'by_platform': {},
            'top_pain_points': [],
            'product_mentions': [],
            'results': results
        }
        
        # Categorize results
        for result in results:
            # By category
            category = self._categorize_issue(result['keyword'], result['content_preview'])
            if category not in processed['by_category']:
                processed['by_category'][category] = []
            processed['by_category'][category].append(result)
            
            # By platform
            platform = result['platform']
            if platform not in processed['by_platform']:
                processed['by_platform'][platform] = []
            processed['by_platform'][platform].append(result)
            
            # Extract pain points
            pain_points = self._extract_pain_points(result['content_preview'])
            processed['top_pain_points'].extend(pain_points)
            
            # Look for product mentions
            if any(term in result['content_preview'].lower() for term in ['chair', 'mouse', 'keyboard']):
                processed['product_mentions'].append({
                    'url': result['url'],
                    'content': result['content_preview'][:200] + "..."
                })
        
        # Remove duplicate pain points
        processed['top_pain_points'] = list(set(processed['top_pain_points']))[:10]
        
        return processed
    
    def _save_results(self, results: Dict[str, Any]):
        """Save results to JSON file"""
        try:
            # Load existing data
            existing_data = []
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Add new results
            existing_data.append(results)
            
            # Keep only last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            existing_data = [
                data for data in existing_data 
                if datetime.fromisoformat(data['timestamp']) > cutoff_date
            ]
            
            # Save updated data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Results saved to {self.data_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
    
    async def _send_email_report(self, results: Dict[str, Any]):
        """Send daily email report"""
        try:
            # Create email content
            html_content = self._create_email_html(results)
            
            # Email configuration (you'll need to set up SMTP)
            # For now, save as HTML file
            report_file = Path(f"reports/gamer_health_report_{datetime.now().strftime('%Y%m%d')}.html")
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Email report saved to {report_file}")
            self.logger.info(f"Report should be sent to: {self.email_recipient}")
            
            # TODO: Implement actual email sending
            # self._send_actual_email(html_content)
            
        except Exception as e:
            self.logger.error(f"Error creating email report: {e}")
    
    def _create_email_html(self, results: Dict[str, Any]) -> str:
        """Create HTML email report"""
        html = f"""
        <html>
        <head>
            <title>Gamer Health Research Report - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .category {{ margin: 20px 0; }}
                .result {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 3px solid #007cba; }}
                .pain-point {{ background-color: #ffe6e6; padding: 5px; margin: 5px 0; border-radius: 3px; }}
                .url {{ color: #007cba; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>League of Legends Gamer Health Research Report</h1>
                <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <p><strong>Total Results Found:</strong> {results['total_results']}</p>
            </div>
            
            <h2>📊 Results by Category</h2>
        """
        
        # Add results by category
        for category, category_results in results['by_category'].items():
            html += f"""
            <div class="category">
                <h3>{category} ({len(category_results)} results)</h3>
            """
            
            for result in category_results[:5]:  # Top 5 per category
                html += f"""
                <div class="result">
                    <strong>{result['platform'].upper()}</strong> - 
                    <a href="{result['url']}" class="url">{result['title']}</a><br>
                    <em>Keyword: {result['keyword']}</em><br>
                    {result['content_preview'][:200]}...
                </div>
                """
            
            html += "</div>"
        
        # Add top pain points
        html += """
            <h2>🔥 Key Pain Points Discovered</h2>
        """
        
        for pain_point in results['top_pain_points'][:10]:
            html += f'<div class="pain-point">{pain_point}</div>'
        
        # Add platform breakdown
        html += """
            <h2>📱 Results by Platform</h2>
            <ul>
        """
        
        for platform, platform_results in results['by_platform'].items():
            html += f"<li><strong>{platform.title()}:</strong> {len(platform_results)} results</li>"
        
        html += """
            </ul>
            
            <hr>
            <p><em>This report was automatically generated by the Gamer Health Research Agent.</em></p>
            <p><em>For detailed analysis, check the saved JSON data file.</em></p>
        </body>
        </html>
        """
        
        return html
    
    def setup_daily_schedule(self):
        """Setup daily automated research"""
        # Schedule daily research at 9 AM
        schedule.every().day.at("09:00").do(lambda: asyncio.run(self.run_daily_research()))
        
        self.logger.info("Daily research scheduled for 9:00 AM")
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


async def main():
    """Main function"""
    if not DEPENDENCIES_AVAILABLE:
        print("Please install required dependencies first:")
        print("pip install google beautifulsoup4 praw requests schedule")
        return
    
    agent = GamerHealthResearchAgent()
    
    print("="*60)
    print("🎮 Gamer Health Research Agent")
    print("="*60)
    print("Specialized for League of Legends player health issues research")
    print()
    
    import argparse
    parser = argparse.ArgumentParser(description="Gamer Health Research Agent")
    parser.add_argument('--run-once', action='store_true', help='Run research once and exit')
    parser.add_argument('--schedule', action='store_true', help='Start daily scheduled research')
    
    args = parser.parse_args()
    
    if args.run_once:
        print("Running one-time research...")
        results = await agent.run_daily_research()
        print(f"✅ Research completed! Found {results['total_results']} results")
        print(f"📊 Categories found: {list(results['by_category'].keys())}")
        print(f"📱 Platforms searched: {list(results['by_platform'].keys())}")
        print(f"📧 Report saved for email to: {agent.email_recipient}")
        
    elif args.schedule:
        print("Starting daily scheduled research...")
        print("Will run every day at 9:00 AM")
        print("Press Ctrl+C to stop")
        agent.setup_daily_schedule()
        
    else:
        print("Usage:")
        print("  --run-once    Run research once and show results")
        print("  --schedule    Start daily automated research")
        print()
        print("Example: python gamer_health_research_agent.py --run-once")


if __name__ == "__main__":
    asyncio.run(main())