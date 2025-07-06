"""
Configuration management for GutachtenAssist
"""

import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class for GutachtenAssist"""
    
    # Application paths
    base_dir: Path = Path(__file__).parent.parent.parent
    models_dir: Path = base_dir / "models"
    templates_dir: Path = base_dir / "templates"
    data_dir: Path = base_dir / "data"
    logs_dir: Path = base_dir / "logs"
    
    # Model settings
    language_model_name: str = "llama-2-7b-chat.gguf"
    ocr_language: str = "deu+eng"
    speech_model_name: str = "whisper-base"
    
    # Processing settings
    max_image_size: int = 4096
    supported_image_formats: tuple = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
    supported_audio_formats: tuple = ('.flac', '.wav', '.mp3')
    supported_document_formats: tuple = ('.doc', '.docx', '.pdf')
    
    # Template settings
    min_template_confidence: float = 0.7
    max_templates_to_keep: int = 50
    
    # Text processing
    max_text_length: int = 10000
    grammar_correction_enabled: bool = True
    
    def __post_init__(self):
        """Create necessary directories"""
        for directory in [self.models_dir, self.templates_dir, self.data_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
    
    def get_model_path(self, model_name: str) -> Path:
        """Get path to a specific model"""
        return self.models_dir / model_name
    
    def get_template_path(self, template_name: str) -> Path:
        """Get path to a specific template"""
        return self.templates_dir / f"{template_name}.json"
    
    def get_data_path(self, filename: str) -> Path:
        """Get path to data file"""
        return self.data_dir / filename
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'base_dir': str(self.base_dir),
            'models_dir': str(self.models_dir),
            'templates_dir': str(self.templates_dir),
            'data_dir': str(self.data_dir),
            'logs_dir': str(self.logs_dir),
            'language_model_name': self.language_model_name,
            'ocr_language': self.ocr_language,
            'speech_model_name': self.speech_model_name,
            'max_image_size': self.max_image_size,
            'supported_image_formats': self.supported_image_formats,
            'supported_audio_formats': self.supported_audio_formats,
            'supported_document_formats': self.supported_document_formats,
            'min_template_confidence': self.min_template_confidence,
            'max_templates_to_keep': self.max_templates_to_keep,
            'max_text_length': self.max_text_length,
            'grammar_correction_enabled': self.grammar_correction_enabled
        } 