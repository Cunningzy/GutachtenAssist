#!/usr/bin/env python3
"""
Test script to verify GutachtenAssist installation
"""

import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    required_packages = [
        ('streamlit', 'UI framework'),
        ('numpy', 'Numerical computing'),
        ('pandas', 'Data manipulation'),
        ('cv2', 'Computer vision'),
        ('PIL', 'Image processing'),
        ('pytesseract', 'OCR processing'),
        ('whisper', 'Speech recognition'),
        ('torch', 'Deep learning'),
        ('transformers', 'Language models'),
        ('docx', 'Document processing'),
    ]
    
    failed_imports = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} ({description})")
        except ImportError as e:
            print(f"❌ {package} ({description}): {e}")
            failed_imports.append(package)
    
    return failed_imports

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'src',
        'src/core',
        'src/ui',
        'src/utils',
        'models',
        'templates',
        'data',
        'logs'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} (missing)")
            missing_dirs.append(dir_path)
    
    return missing_dirs

def test_modules():
    """Test if core modules can be imported"""
    print("\n🔧 Testing core modules...")
    
    # Add src to path
    sys.path.append(str(Path(__file__).parent / "src"))
    
    core_modules = [
        'src.core.assistant',
        'src.core.document_learner',
        'src.core.ocr_processor',
        'src.core.speech_recognizer',
        'src.core.template_manager',
        'src.core.text_processor',
        'src.core.gutachten_generator',
        'src.ui.chat_interface',
        'src.utils.config',
        'src.utils.logger'
    ]
    
    failed_modules = []
    
    for module in core_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_modules.append(module)
    
    return failed_modules

def main():
    """Run all tests"""
    print("🚀 GutachtenAssist Installation Test")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test directories
    missing_dirs = test_directories()
    
    # Test modules
    failed_modules = test_modules()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    if not failed_imports and not missing_dirs and not failed_modules:
        print("✅ All tests passed! GutachtenAssist is ready to use.")
        print("\nTo start the application:")
        print("  python main.py")
    else:
        print("❌ Some tests failed:")
        
        if failed_imports:
            print(f"  - {len(failed_imports)} package imports failed")
            print("    Install missing packages with: pip install -r requirements.txt")
        
        if missing_dirs:
            print(f"  - {len(missing_dirs)} directories missing")
            print("    Run setup to create directories")
        
        if failed_modules:
            print(f"  - {len(failed_modules)} core modules failed to import")
            print("    Check the source code structure")

if __name__ == "__main__":
    main() 