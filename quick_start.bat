@echo off
echo ========================================
echo    GutachtenAssist Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
pip install streamlit pandas numpy

echo.
echo Starting GutachtenAssist...
echo The application will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run simple_demo.py

pause 