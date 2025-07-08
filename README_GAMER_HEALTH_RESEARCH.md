# 🎮 Gamer Health Research Agent

**Specialized Market Research Tool for League of Legends Player Health Issues**

This agent is specifically designed to research health problems and pain points experienced by League of Legends players. It automatically searches Google, Reddit, Facebook, and review sites to identify:

- **Physical health issues** (back pain, wrist pain, eye strain)
- **Mental health challenges** (anxiety, stress, tilt)
- **Existing product solutions** and their problems
- **Unmet market needs** and product opportunities

Perfect for market research to identify product-market fit opportunities in the gaming health space.

## 🎯 What It Does

### Daily Automated Research
- Searches **75+ specific keywords** related to LoL player health issues
- Monitors **Reddit, Facebook, review sites, and forums**
- Uses **Google Search** to find the most relevant discussions
- **Categorizes findings** by health issue type
- **Extracts pain points** automatically from content
- **Generates HTML email reports** with clickable links to original sources

### Market Research Focus
- **Physical Health**: Back pain, wrist pain, carpal tunnel, eye strain, posture issues
- **Mental Health**: Anxiety, stress, rage, addiction, depression from gaming
- **Product Solutions**: Reviews and complaints about existing gaming chairs, mice, keyboards, etc.
- **Platform-Specific**: Reddit discussions, YouTube videos, forum posts

### Output for Analysis
- **Manual references** to original forum posts, Reddit threads, review sites
- **Categorized by issue type** for easy analysis
- **Pain point extraction** highlighting problems with existing solutions
- **Daily email reports** to kharninngz@gmail.com (configurable)

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
# Install the specific dependencies for gamer health research
pip install google beautifulsoup4 googlesearch-python schedule requests
```

### 2. Test the Setup
```bash
python test_gamer_health_agent.py
```

### 3. Run One-Time Research
```bash
python gamer_health_research_agent.py --run-once
```

### 4. Start Daily Monitoring
```bash
python gamer_health_research_agent.py --schedule
```

## 📊 Sample Output

### What You'll Get in Your Email Reports:

#### 📈 **Physical Health Issues (23 results found)**
- **REDDIT** - "Back pain from 8+ hour LoL sessions, need help" 
  - *Keyword: League of Legends back pain*
  - Link: https://reddit.com/r/leagueoflegends/comments/...
  - Pain Points: "my back hurts so bad after long gaming sessions", "can't find a chair that works"

- **AMAZON REVIEWS** - "Secret Lab Chair Review - Still have back pain"
  - *Keyword: gaming chair back pain recommendations* 
  - Link: https://amazon.com/product-reviews/...
  - Pain Points: "expensive but didn't help", "still uncomfortable after 3 months"

#### 🧠 **Mental Health Issues (18 results found)**
- **REDDIT** - "LoL ranked anxiety is destroying my life"
  - *Keyword: LoL ranked anxiety*
  - Pain Points: "can't sleep before ranked games", "heart racing during matches"

#### 🪑 **Product Solutions (31 results found)**
- **REVIEW SITE** - "Ergonomic Gaming Mouse Failed After 6 Months"
  - Pain Points: "waste of money", "doesn't actually help with wrist pain"

### 🔥 **Key Pain Points Discovered:**
- "Gaming chair doesn't actually help with back pain"
- "Wrist exercises don't work during long sessions"  
- "Blue light glasses made no difference"
- "Can't find affordable ergonomic solutions"
- "Existing products break quickly"

### 📱 **Platforms Searched:**
- **Reddit**: 45 results
- **Review Sites**: 12 results  
- **YouTube**: 8 results
- **Forums**: 15 results

## 🔧 Configuration

Edit `config/gamer_health_config.json` to customize:

```json
{
  "email": {
    "recipient": "kharninngz@gmail.com",
    "daily_run_time": "09:00"
  },
  "research": {
    "max_results_per_keyword": 10,
    "search_delay_seconds": 2
  }
}
```

## 📁 File Structure

```
├── gamer_health_research_agent.py    # Main agent script
├── test_gamer_health_agent.py        # Test script
├── config/gamer_health_config.json   # Configuration
├── data/gamer_health_research.json   # Raw research data
├── reports/                          # Daily HTML email reports
│   └── gamer_health_report_YYYYMMDD.html
└── logs/                            # Application logs
```

## 📧 Email Reports

Daily reports are saved as HTML files in the `reports/` folder. Each report contains:

- **Executive Summary** with total results found
- **Results by Category** (Physical Health, Mental Health, Product Solutions)  
- **Platform Breakdown** (Reddit, Facebook, Review Sites, etc.)
- **Key Pain Points** extracted from discussions
- **Direct links** to original sources for manual analysis

## 🔍 Keywords Monitored

The agent searches for 75+ specific keywords including:

### Physical Health
- "health issues League of Legends players"
- "League of Legends back pain"  
- "gaming wrist pain"
- "LoL carpal tunnel"
- "gaming posture problems"

### Mental Health  
- "LoL ranked anxiety"
- "League of Legends mental health"
- "gaming addiction LoL"
- "how to deal with tilt"

### Product Research
- "best gaming chair for back pain"
- "ergonomic gaming mouse reviews" 
- "wrist rest recommendations"
- "blue light glasses gaming"

### Platform-Specific
- "reddit LoL back pain"
- "YouTube gaming health exercises"
- "gaming forum wrist pain"

## 📈 Market Research Value

This tool helps identify:

1. **Unmet Needs**: Health problems without good solutions
2. **Product Gaps**: Where existing solutions fail
3. **Market Size**: How many people discuss these issues
4. **Customer Language**: How gamers describe their problems
5. **Competitor Weaknesses**: Problems with existing products
6. **Price Sensitivity**: "Waste of money" complaints about expensive products

## 🔒 Rate Limiting & Ethics

- **Respectful delays** between searches (2+ seconds)
- **Limited results** per keyword to avoid overloading servers
- **No personal data** collection - only public posts
- **Attribution preserved** with original URLs

## 🛠 Troubleshooting

### Common Issues:

1. **"No results found"**: Normal - Google may rate limit
2. **Import errors**: Run `pip install google beautifulsoup4 googlesearch-python`
3. **Empty reports**: Check internet connection and try again

### Getting Better Results:

1. **Run during off-peak hours** (less rate limiting)
2. **Adjust search delays** in config if needed
3. **Check logs** in `logs/` folder for detailed errors

## 📊 Usage Examples

### One-Time Market Research
```bash
# Run once and analyze results
python gamer_health_research_agent.py --run-once

# Check the results
open reports/gamer_health_report_$(date +%Y%m%d).html
```

### Continuous Monitoring
```bash
# Start daily automated research (runs at 9 AM daily)
python gamer_health_research_agent.py --schedule

# Let it run in background for ongoing market intelligence
```

### Data Analysis
```python
# Load and analyze the raw data
import json

with open('data/gamer_health_research.json') as f:
    data = json.load(f)

# Analyze trends over time
for day in data:
    print(f"Date: {day['timestamp']}")
    print(f"Total results: {day['total_results']}")
    print(f"Categories: {list(day['by_category'].keys())}")
```

## 🎯 Perfect For

- **Product managers** researching gaming health market
- **Entrepreneurs** looking for product-market fit opportunities  
- **Investors** evaluating gaming health startups
- **Researchers** studying gamer health trends
- **Product designers** understanding user pain points

## ⚡ Next Steps

1. **Test the setup**: `python test_gamer_health_agent.py`
2. **Run initial research**: `python gamer_health_research_agent.py --run-once`  
3. **Review first report** in `reports/` folder
4. **Start daily monitoring**: `python gamer_health_research_agent.py --schedule`
5. **Analyze data** for product opportunities!

---

*This agent was specifically built for researching League of Legends player health issues and identifying market opportunities. The data collected will help understand what health problems gamers face and where existing solutions are failing.* 🎮💡