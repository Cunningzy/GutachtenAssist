# Social Media Data Collection Agent

A comprehensive Python agent for collecting data from various social media platforms including Reddit, Twitter, Facebook, and web forums. The agent supports both one-time data collection and continuous monitoring with configurable filtering and export options.

## Features

### 🌐 Multi-Platform Support
- **Reddit**: Using PRAW (Python Reddit API Wrapper)
- **Twitter**: Using Tweepy library with v2 API support
- **Facebook**: Using Facebook SDK (limited by API restrictions)
- **Web Forums**: Generic web scraping for various forum platforms
- **Extensible**: Easy to add new platforms

### 📊 Data Collection Capabilities
- Keyword-based filtering
- Time range filtering
- Configurable post limits
- Metadata extraction (likes, shares, comments, etc.)
- Author and timestamp information
- URL preservation for source tracking

### 💾 Data Storage & Export
- SQLite database for local storage
- JSON, CSV, and Excel export formats
- Duplicate detection and handling
- Data persistence across sessions

### ⚙️ Advanced Features
- Asynchronous data collection for better performance
- Rate limiting and API quota management
- Continuous monitoring mode
- Comprehensive logging
- Error handling and recovery
- Configurable user agents and request delays

## Installation

1. Clone or download the project files
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create configuration directories:
```bash
mkdir -p config data logs exports
```

## Quick Start

### 1. Configuration

The agent uses a JSON configuration file. A default configuration is created automatically at `config/social_media_config.json`. Update it with your API credentials:

```json
{
  "reddit": {
    "enabled": true,
    "credentials": {
      "client_id": "your_reddit_client_id",
      "client_secret": "your_reddit_client_secret",
      "user_agent": "SocialMediaCollector/1.0"
    }
  },
  "twitter": {
    "enabled": true,
    "credentials": {
      "bearer_token": "your_twitter_bearer_token"
    }
  }
}
```

### 2. Basic Usage

#### Command Line Interface

```bash
# Basic collection from all platforms
python social_media_agent.py collect

# Collect with specific keywords
python social_media_agent.py collect --keywords "python" "AI" "programming"

# Collect from specific platforms
python social_media_agent.py collect --platforms reddit forums --max-posts 200

# Continuous collection (every 30 minutes)
python social_media_agent.py collect --continuous --interval 30

# Search collected data
python social_media_agent.py search --keywords "machine learning" --days-back 7

# View statistics
python social_media_agent.py stats
```

#### Programmatic Usage

```python
import asyncio
from src.core.social_media_collector import SocialMediaCollector

async def collect_data():
    collector = SocialMediaCollector()
    
    # Collect data
    results = await collector.collect_data(
        keywords=["python", "programming"],
        max_posts=100,
        time_range=24
    )
    
    # Export results
    collector.export_data("my_data.json", format='json')
    
    return results

# Run collection
asyncio.run(collect_data())
```

## API Setup

### Reddit API
1. Go to https://www.reddit.com/prefs/apps
2. Create a new application (script type)
3. Note the client ID and secret
4. Update configuration file

### Twitter API
1. Go to https://developer.twitter.com/
2. Create a new project/app
3. Generate bearer token
4. Update configuration file

### Facebook API
1. Go to https://developers.facebook.com/
2. Create a new app
3. Generate access token
4. Update configuration file

Note: Facebook API has strict limitations for public data access.

## Configuration Options

### Platform Settings

```json
{
  "reddit": {
    "enabled": true,
    "credentials": { ... },
    "settings": {
      "default_subreddits": ["all", "programming"],
      "max_posts_per_subreddit": 50
    }
  },
  "forums": {
    "enabled": true,
    "settings": {
      "urls": [
        "https://news.ycombinator.com/newest",
        "https://www.reddit.com/r/programming/new.json"
      ],
      "request_delay": 2.0,
      "timeout": 30
    }
  }
}
```

### Collection Settings

```json
{
  "collection": {
    "default_max_posts": 100,
    "default_time_range_hours": 24,
    "export_formats": ["json", "csv"],
    "auto_export": true
  },
  "filtering": {
    "min_content_length": 10,
    "max_content_length": 10000,
    "blocked_keywords": ["spam"],
    "blocked_authors": []
  }
}
```

## Data Structure

Each collected post follows this structure:

```python
@dataclass
class SocialMediaPost:
    platform: str          # Source platform
    post_id: str           # Unique post identifier
    author: str            # Author username
    content: str           # Post content/text
    timestamp: datetime    # When the post was created
    url: str              # Link to original post
    likes: int            # Number of likes/upvotes
    shares: int           # Number of shares/retweets
    comments: int         # Number of comments/replies
    tags: List[str]       # Hashtags or categories
    metadata: Dict        # Additional platform-specific data
```

## Examples

### Basic Data Collection

```python
# Collect recent posts about AI
results = await collector.collect_data(
    keywords=["artificial intelligence", "AI", "machine learning"],
    max_posts=200,
    time_range=12  # Last 12 hours
)

print(f"Collected {sum(len(posts) for posts in results.values())} posts")
```

### Platform-Specific Collection

```python
# Collect only from Reddit
reddit_posts = await collector.collect_data(
    platforms=["reddit"],
    keywords=["python programming"],
    max_posts=100
)
```

### Continuous Monitoring

```python
# Monitor continuously (every hour)
await collector.start_continuous_collection(
    keywords=["bitcoin", "cryptocurrency"],
    interval_minutes=60
)
```

### Data Analysis

```python
# Get statistics
stats = collector.get_statistics()
print(f"Total posts: {stats['total_posts']}")

# Search collected data
posts = collector.get_collected_data(
    keywords=["python"],
    start_date=datetime.now() - timedelta(days=7)
)

# Export to different formats
collector.export_data("data.json", format='json')
collector.export_data("data.csv", format='csv')
collector.export_data("data.xlsx", format='xlsx')
```

## Database Schema

The agent uses SQLite for data storage:

```sql
CREATE TABLE posts (
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
    tags TEXT,  -- JSON array
    metadata TEXT,  -- JSON object
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, post_id)
);
```

## Logging

The agent provides comprehensive logging:

- Collection progress and statistics
- API rate limiting information
- Error handling and recovery
- Export operations
- Configuration loading

Logs are written to the `logs/` directory with rotating file handlers.

## Error Handling

The agent includes robust error handling for:

- API rate limits and quotas
- Network connectivity issues
- Invalid or expired credentials
- Malformed data from sources
- Database connection issues

## Legal and Ethical Considerations

⚠️ **Important**: Always comply with platform terms of service and applicable laws:

- Respect API rate limits
- Don't collect private or sensitive data
- Follow platform-specific guidelines
- Consider data privacy regulations (GDPR, CCPA, etc.)
- Use collected data responsibly

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Errors**: Check credentials and API quotas
3. **Empty Results**: Verify platform configuration and availability
4. **Rate Limiting**: Adjust request delays in configuration

### Debug Mode

Enable debug logging by modifying the logger configuration:

```python
logger = setup_logger(level='DEBUG')
```

## Contributing

The agent is designed to be extensible. To add a new platform:

1. Create a new collector class in `src/core/`
2. Implement the required interface methods
3. Add configuration options
4. Update the main collector to include the new platform

## License

This project is provided as-is for educational and research purposes. Users are responsible for complying with all applicable terms of service and laws.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review platform API documentation
3. Check configuration file syntax
4. Verify network connectivity and credentials

---

*Happy data collecting! 🚀*