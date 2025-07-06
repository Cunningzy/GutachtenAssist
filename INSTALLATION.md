# GutachtenAssist Installation Guide

This guide will help you install and set up GutachtenAssist for offline expert opinion writing.

## Prerequisites

### System Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: Minimum 8GB, recommended 16GB
- **Storage**: At least 5GB free space for models
- **Internet**: Required only for initial download of models

### Required Software

#### 1. Python Installation
Download and install Python 3.8+ from [python.org](https://python.org)

#### 2. Tesseract OCR (Required for image processing)
- **Windows**: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

#### 3. Git (Optional)
For cloning the repository: `git clone https://github.com/your-repo/gutachten-assist.git`

## Installation Steps

### Step 1: Clone or Download
```bash
# Option 1: Clone repository
git clone https://github.com/your-repo/gutachten-assist.git
cd gutachten-assist

# Option 2: Download and extract ZIP file
# Then navigate to the extracted folder
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 4: Download Offline Models
```bash
# Download and setup offline models
python setup_models.py
```

### Step 5: Verify Installation
```bash
# Run installation test
python test_installation.py
```

## Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root:

```env
# Logging level
LOG_LEVEL=INFO

# Model paths (auto-detected)
WHISPER_MODEL=base
TESSERACT_LANG=deu+eng

# Processing settings
MAX_IMAGE_SIZE=4096
GRAMMAR_CORRECTION=true
```

### Directory Structure
After installation, you should have:
```
GutachtenAssist/
├── src/                    # Source code
├── models/                 # Downloaded models
├── templates/              # Learned templates
├── data/                   # Data storage
├── logs/                   # Application logs
├── main.py                 # Main application
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

## Troubleshooting

### Common Issues

#### 1. Tesseract Not Found
**Error**: `TesseractNotFoundError`
**Solution**: Install Tesseract OCR and ensure it's in your system PATH

#### 2. CUDA/GPU Issues
**Error**: CUDA-related errors
**Solution**: Install CPU-only versions:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### 3. Memory Issues
**Error**: Out of memory errors
**Solution**: 
- Close other applications
- Use smaller models (e.g., `whisper-tiny` instead of `whisper-base`)
- Increase virtual memory (Windows)

#### 4. Import Errors
**Error**: Module not found
**Solution**: 
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

### Model Download Issues

If model downloads fail:

1. **Check Internet Connection**: Ensure stable internet connection
2. **Use VPN**: Some models may be blocked in certain regions
3. **Manual Download**: Download models manually and place in `models/` directory
4. **Alternative Models**: Use smaller models for faster download

## Running the Application

### Start GutachtenAssist
```bash
python main.py
```

The application will open in your default web browser at `http://localhost:8501`

### First Run
1. **Upload Documents**: Start by uploading existing Gutachten (.doc/.docx) to learn templates
2. **Process Images**: Upload medical document images for OCR processing
3. **Transcribe Audio**: Upload audio files (.flac) for speech recognition
4. **Generate Gutachten**: Create expert opinions based on learned patterns

## Offline Operation

Once models are downloaded, GutachtenAssist operates completely offline:

- ✅ **Document Learning**: Analyzes existing Gutachten
- ✅ **Image OCR**: Processes medical documents
- ✅ **Speech Recognition**: Transcribes audio files
- ✅ **Text Generation**: Creates formatted Gutachten
- ✅ **Template Management**: Stores and updates learned patterns

## Performance Optimization

### For Better Performance:
1. **Use SSD**: Store models on SSD for faster loading
2. **Increase RAM**: More RAM allows larger models
3. **GPU Acceleration**: Install CUDA for GPU acceleration (optional)
4. **Batch Processing**: Process multiple files together

### For Limited Resources:
1. **Use Smaller Models**: `whisper-tiny` instead of `whisper-base`
2. **Reduce Image Size**: Limit image resolution
3. **Close Other Apps**: Free up system resources

## Support

If you encounter issues:

1. **Check Logs**: Look in `logs/gutachten_assist.log`
2. **Run Tests**: `python test_installation.py`
3. **Update Dependencies**: `pip install --upgrade -r requirements.txt`
4. **Report Issues**: Create an issue on GitHub

## License

This project is licensed under the MIT License. See LICENSE file for details. 