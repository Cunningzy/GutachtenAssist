#!/usr/bin/env python3
"""
Setup script for downloading offline models for GutachtenAssist
"""

import os
import sys
from pathlib import Path
import subprocess
import urllib.request
import zipfile
import tarfile

def main():
    """Download and setup offline models"""
    print("🚀 Setting up GutachtenAssist offline models...")
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Download Whisper model
    print("📥 Downloading Whisper model...")
    try:
        import whisper
        model = whisper.load_model("base")
        print("✅ Whisper model downloaded successfully")
    except Exception as e:
        print(f"❌ Error downloading Whisper model: {e}")
    
    # Download Tesseract data
    print("📥 Setting up Tesseract...")
    try:
        import pytesseract
        # Check if Tesseract is available
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version {version} found")
    except Exception as e:
        print(f"❌ Tesseract not found: {e}")
        print("Please install Tesseract OCR:")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Linux: sudo apt-get install tesseract-ocr")
        print("  macOS: brew install tesseract")
    
    # Download EasyOCR models
    print("📥 Setting up EasyOCR...")
    try:
        import easyocr
        reader = easyocr.Reader(['de', 'en'], gpu=False)
        print("✅ EasyOCR models downloaded successfully")
    except Exception as e:
        print(f"❌ Error setting up EasyOCR: {e}")
    
    # Download local language model (optional)
    print("📥 Setting up local language model...")
    try:
        # This would download a local LLM like Llama2
        # For now, we'll use a placeholder
        print("ℹ️ Local language model setup skipped (requires manual download)")
    except Exception as e:
        print(f"❌ Error setting up language model: {e}")
    
    print("\n✅ Setup complete!")
    print("\nTo run GutachtenAssist:")
    print("  python main.py")
    
    print("\nNote: Some models may take time to download on first use.")

if __name__ == "__main__":
    main() 