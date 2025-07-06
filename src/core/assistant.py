"""
Main GutachtenAssistant class that orchestrates all processing modules
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

from .document_learner import DocumentLearner
from .ocr_processor import OCRProcessor
from .speech_recognizer import SpeechRecognizer
from .template_manager import TemplateManager
from .text_processor import TextProcessor
from .gutachten_generator import GutachtenGenerator


class GutachtenAssistant:
    """
    Main assistant class that coordinates all processing modules
    """
    
    def __init__(self, config):
        """Initialize the assistant with all processing modules"""
        self.config = config
        self.logger = logger
        
        # Initialize processing modules
        self.document_learner = DocumentLearner(config)
        self.ocr_processor = OCRProcessor(config)
        self.speech_recognizer = SpeechRecognizer(config)
        self.template_manager = TemplateManager(config)
        self.text_processor = TextProcessor(config)
        self.gutachten_generator = GutachtenGenerator(config)
        
        # Load existing templates if available
        self.template_manager.load_templates()
        
        self.logger.info("GutachtenAssistant initialized successfully")
    
    def learn_from_documents(self, document_paths: List[str]) -> Dict[str, Any]:
        """
        Learn templates and patterns from existing Gutachten documents
        
        Args:
            document_paths: List of paths to .doc/.docx files
            
        Returns:
            Dictionary with learning results
        """
        self.logger.info(f"Learning from {len(document_paths)} documents")
        
        results = {
            'templates_learned': 0,
            'patterns_extracted': 0,
            'errors': []
        }
        
        for doc_path in document_paths:
            try:
                template_data = self.document_learner.learn_from_document(doc_path)
                self.template_manager.add_template(template_data)
                results['templates_learned'] += 1
                results['patterns_extracted'] += len(template_data.get('patterns', []))
            except Exception as e:
                self.logger.error(f"Error learning from {doc_path}: {e}")
                results['errors'].append(str(e))
        
        # Save updated templates
        self.template_manager.save_templates()
        
        return results
    
    def process_images(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Process medical document images using OCR
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            Dictionary with extracted text and structured information
        """
        self.logger.info(f"Processing {len(image_paths)} images")
        
        results = {
            'documents_processed': 0,
            'text_extracted': {},
            'diagnoses_found': [],
            'descriptions': {},
            'errors': []
        }
        
        for img_path in image_paths:
            try:
                # Extract text from image
                extracted_text = self.ocr_processor.extract_text(img_path)
                
                # Structure the information
                structured_info = self.text_processor.structure_medical_info(extracted_text)
                
                results['text_extracted'][img_path] = extracted_text
                results['diagnoses_found'].extend(structured_info.get('diagnoses', []))
                results['descriptions'][img_path] = structured_info.get('description', '')
                results['documents_processed'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing image {img_path}: {e}")
                results['errors'].append(str(e))
        
        return results
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file containing dictated Gutachten
        
        Args:
            audio_path: Path to audio file (.flac)
            
        Returns:
            Dictionary with transcription and corrections
        """
        self.logger.info(f"Transcribing audio: {audio_path}")
        
        try:
            # Transcribe audio
            raw_transcription = self.speech_recognizer.transcribe(audio_path)
            
            # Correct grammar and format
            corrected_text = self.text_processor.correct_grammar(raw_transcription)
            formatted_text = self.text_processor.format_gutachten_text(corrected_text)
            
            return {
                'raw_transcription': raw_transcription,
                'corrected_text': corrected_text,
                'formatted_text': formatted_text,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error transcribing audio {audio_path}: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_gutachten(self, 
                          medical_data: Dict[str, Any],
                          transcribed_text: Optional[str] = None) -> str:
        """
        Generate complete Gutachten from processed data
        
        Args:
            medical_data: Structured medical information from OCR
            transcribed_text: Optional transcribed text from audio
            
        Returns:
            Complete formatted Gutachten text
        """
        self.logger.info("Generating Gutachten")
        
        # Get best matching template
        template = self.template_manager.get_best_template(medical_data)
        
        # Generate Gutachten using template and data
        gutachten_text = self.gutachten_generator.generate(
            template=template,
            medical_data=medical_data,
            transcribed_text=transcribed_text
        )
        
        return gutachten_text
    
    def learn_from_feedback(self, gutachten_text: str, user_feedback: str) -> bool:
        """
        Learn from user feedback to improve templates
        
        Args:
            gutachten_text: Generated Gutachten text
            user_feedback: User feedback for improvement
            
        Returns:
            Success status
        """
        self.logger.info("Learning from user feedback")
        
        try:
            # Update template based on feedback
            self.template_manager.update_from_feedback(gutachten_text, user_feedback)
            
            # Save updated templates
            self.template_manager.save_templates()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error learning from feedback: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'templates_loaded': len(self.template_manager.templates),
            'models_ready': all([
                self.ocr_processor.is_ready(),
                self.speech_recognizer.is_ready(),
                self.text_processor.is_ready()
            ]),
            'last_activity': self.logger.info("Status requested")
        } 