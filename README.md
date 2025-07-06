# GutachtenAssist

An offline expert opinion writing assistant that helps create German Gutachten (expert opinions) through machine learning, speech recognition, and document processing.

## Features

- **Document Learning**: Analyzes existing Gutachten to learn formatting, language, and style patterns
- **Image Recognition**: OCR for medical documents (discharge letters, reports, examination results)
- **Speech Recognition**: Transcribes dictated Gutachten with grammar correction
- **Template Generation**: Creates structured templates based on learned patterns
- **Offline Operation**: All features work without internet connection
- **Chat Interface**: Interactive bot for user communication

## Architecture

```
GutachtenAssist/
├── src/
│   ├── core/           # Core processing modules
│   ├── models/         # ML models and templates
│   ├── ui/            # Chat interface
│   ├── utils/         # Utility functions
│   └── data/          # Data storage
├── models/            # Pre-trained models
├── templates/         # Learned templates
└── docs/             # Documentation
```

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Download offline models:
```bash
python setup_models.py
```

3. Run the application:
```bash
python main.py
```

## Usage

1. **Learning Phase**: Upload existing Gutachten (.doc/.docx) to learn templates
2. **Document Processing**: Upload medical document images for OCR
3. **Speech Recognition**: Upload audio files (.flac) for transcription
4. **Generation**: Create new Gutachten based on learned patterns
5. **Chat Interface**: Interact with the system through natural language

## Technical Stack

- **Language Model**: Local LLM (Llama2 or similar)
- **OCR**: Tesseract for image text recognition
- **Speech Recognition**: Whisper for audio transcription
- **Document Processing**: python-docx for Word documents
- **UI**: Streamlit for chat interface
- **ML**: scikit-learn for pattern recognition

## Offline Capabilities

All components work offline:
- Local language model inference
- Offline OCR processing
- Local speech recognition
- Template-based text generation
- No external API dependencies 