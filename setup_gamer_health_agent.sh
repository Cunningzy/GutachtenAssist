#!/bin/bash

echo "🎮 Setting up Gamer Health Research Agent"
echo "========================================"

# Create required directories
echo "📁 Creating directories..."
mkdir -p data reports logs config

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install google beautifulsoup4 googlesearch-python schedule requests

# Check if installation was successful
echo "✅ Testing installation..."
python test_gamer_health_agent.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run a test: python gamer_health_research_agent.py --run-once"
echo "2. Start daily monitoring: python gamer_health_research_agent.py --schedule"
echo "3. Check reports in the 'reports/' folder"
echo ""
echo "📧 Email reports will be saved as HTML files"
echo "📊 Research data will be saved to 'data/gamer_health_research.json'"
echo ""
echo "For detailed instructions, see: README_GAMER_HEALTH_RESEARCH.md"