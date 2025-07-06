#!/usr/bin/env python3
"""
GutachtenAssist - Offline Expert Opinion Writing Assistant
Main application entry point
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.assistant import GutachtenAssistant
from src.ui.chat_interface import ChatInterface
from src.utils.config import Config
from src.utils.logger import setup_logger

def main():
    """Main application entry point"""
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting GutachtenAssist application")
    
    # Initialize configuration
    config = Config()
    
    # Initialize assistant
    assistant = GutachtenAssistant(config)
    
    # Setup Streamlit page
    st.set_page_config(
        page_title="GutachtenAssist",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize chat interface
    chat_interface = ChatInterface(assistant)
    
    # Run the chat interface
    chat_interface.run()

if __name__ == "__main__":
    main() 