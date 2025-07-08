"""
Configuration management for GutachtenAssist
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
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


@dataclass
class RedditConfig:
    """Reddit API configuration"""
    client_id: str
    client_secret: str
    user_agent: str
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass  
class TwitterConfig:
    """Twitter API configuration"""
    bearer_token: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None


@dataclass
class FacebookConfig:
    """Facebook API configuration"""
    access_token: str
    app_id: str
    app_secret: str


@dataclass
class ForumsConfig:
    """Forums scraping configuration"""
    urls: list
    request_delay: float = 1.0
    max_pages: int = 10


class SocialMediaConfig:
    """Configuration manager for social media data collection"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(exist_ok=True)
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = self._create_default_config()
            
        # Initialize platform configs
        self.reddit_enabled = config_data.get('reddit', {}).get('enabled', False)
        if self.reddit_enabled:
            reddit_config = config_data['reddit']
            self.reddit_config = RedditConfig(**reddit_config.get('credentials', {}))
            
        self.twitter_enabled = config_data.get('twitter', {}).get('enabled', False)
        if self.twitter_enabled:
            twitter_config = config_data['twitter']
            self.twitter_config = TwitterConfig(**twitter_config.get('credentials', {}))
            
        self.facebook_enabled = config_data.get('facebook', {}).get('enabled', False)
        if self.facebook_enabled:
            facebook_config = config_data['facebook']
            self.facebook_config = FacebookConfig(**facebook_config.get('credentials', {}))
            
        self.forums_enabled = config_data.get('forums', {}).get('enabled', False)
        if self.forums_enabled:
            forums_config = config_data['forums']
            self.forums_config = ForumsConfig(**forums_config.get('settings', {}))
            
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration file"""
        default_config = {
            "reddit": {
                "enabled": False,
                "credentials": {
                    "client_id": "your_reddit_client_id",
                    "client_secret": "your_reddit_client_secret",
                    "user_agent": "SocialMediaCollector/1.0"
                }
            },
            "twitter": {
                "enabled": False,
                "credentials": {
                    "bearer_token": "your_twitter_bearer_token"
                }
            },
            "facebook": {
                "enabled": False,
                "credentials": {
                    "access_token": "your_facebook_access_token",
                    "app_id": "your_facebook_app_id",
                    "app_secret": "your_facebook_app_secret"
                }
            },
            "forums": {
                "enabled": True,
                "settings": {
                    "urls": [
                        "https://www.reddit.com/r/all/new.json",
                        "https://news.ycombinator.com/newest"
                    ],
                    "request_delay": 1.0,
                    "max_pages": 5
                }
            }
        }
        
        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        return default_config 