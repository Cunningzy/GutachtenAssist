#!/bin/bash

echo "========================================"
echo "   GutachtenAssist Quick Start"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "Python found. Installing dependencies..."
pip3 install streamlit pandas numpy

echo
echo "Starting GutachtenAssist..."
echo "The application will open in your browser at http://localhost:8501"
echo
echo "Press Ctrl+C to stop the application"
echo

streamlit run simple_demo.py 