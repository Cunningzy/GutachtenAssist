"""
Speech recognition module for transcribing dictated Gutachten
"""

import whisper
import torch
import torchaudio
import librosa
from pathlib import Path
from typing import Dict, Any, Optional

from ..utils.logger import get_logger


class SpeechRecognizer:
    """
    Handles speech recognition for dictated Gutachten
    """
    
    def __init__(self, config):
        """Initialize speech recognizer"""
        self.config = config
        self.logger = get_logger("SpeechRecognizer")
        
        # Initialize Whisper model
        try:
            self.model = whisper.load_model(self.config.speech_model_name)
            self.logger.info(f"Whisper model '{self.config.speech_model_name}' loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
    
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file (.flac, .wav, .mp3)
            
        Returns:
            Transcribed text
        """
        self.logger.info(f"Transcribing audio: {audio_path}")
        
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Load and preprocess audio
            audio = self._load_audio(audio_path)
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio,
                language="de",  # German language
                task="transcribe",
                fp16=False  # Use CPU for offline operation
            )
            
            transcribed_text = result["text"]
            self.logger.info(f"Successfully transcribed {len(transcribed_text)} characters")
            
            return transcribed_text
            
        except Exception as e:
            self.logger.error(f"Error transcribing {audio_path}: {e}")
            raise
    
    def _load_audio(self, audio_path: str) -> str:
        """
        Load and preprocess audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Path to processed audio file
        """
        try:
            # Load audio with librosa
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Save as temporary WAV file for Whisper
            temp_path = Path(audio_path).with_suffix('.wav')
            librosa.output.write_wav(temp_path, audio, sr)
            
            return str(temp_path)
            
        except Exception as e:
            self.logger.error(f"Error loading audio {audio_path}: {e}")
            raise
    
    def transcribe_with_timestamps(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio with timestamp information
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription and timestamps
        """
        self.logger.info(f"Transcribing with timestamps: {audio_path}")
        
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        try:
            # Load audio
            audio = self._load_audio(audio_path)
            
            # Transcribe with word-level timestamps
            result = self.model.transcribe(
                audio,
                language="de",
                task="transcribe",
                fp16=False,
                word_timestamps=True
            )
            
            return {
                'text': result["text"],
                'segments': result.get("segments", []),
                'language': result.get("language", "de"),
                'duration': result.get("duration", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error transcribing with timestamps {audio_path}: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if speech recognizer is ready"""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {'status': 'not_loaded'}
        
        return {
            'status': 'loaded',
            'model_name': self.config.speech_model_name,
            'model_type': type(self.model).__name__
        } 