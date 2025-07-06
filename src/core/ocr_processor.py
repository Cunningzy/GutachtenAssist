"""
OCR processor for medical document image recognition
"""

import cv2
import numpy as np
from PIL import Image
import pytesseract
import easyocr
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..utils.logger import get_logger


class OCRProcessor:
    """
    Handles OCR processing for medical document images
    """
    
    def __init__(self, config):
        """Initialize OCR processor"""
        self.config = config
        self.logger = get_logger("OCRProcessor")
        
        # Initialize EasyOCR reader
        try:
            self.reader = easyocr.Reader(['de', 'en'], gpu=False)
            self.logger.info("EasyOCR initialized successfully")
        except Exception as e:
            self.logger.warning(f"EasyOCR initialization failed: {e}")
            self.reader = None
        
        # Medical document keywords for better recognition
        self.medical_keywords = [
            "Diagnose", "Befund", "Anamnese", "Untersuchung",
            "Patient", "Patientin", "Arzt", "Ärztin",
            "Krankenhaus", "Klinik", "Labor", "Röntgen",
            "Blut", "Urin", "EKG", "CT", "MRT"
        ]
    
    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from medical document image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        self.logger.info(f"Processing image: {image_path}")
        
        try:
            # Load and preprocess image
            image = self._load_image(image_path)
            processed_image = self._preprocess_image(image)
            
            # Extract text using multiple methods
            tesseract_text = self._extract_with_tesseract(processed_image)
            easyocr_text = self._extract_with_easyocr(image_path) if self.reader else ""
            
            # Combine and clean results
            combined_text = self._combine_results(tesseract_text, easyocr_text)
            cleaned_text = self._clean_text(combined_text)
            
            # Structure the extracted information
            structured_info = self._structure_medical_info(cleaned_text)
            
            return {
                'raw_text': combined_text,
                'cleaned_text': cleaned_text,
                'structured_info': structured_info,
                'confidence': self._calculate_confidence(tesseract_text, easyocr_text),
                'metadata': {
                    'image_path': image_path,
                    'image_size': image.shape if hasattr(image, 'shape') else None,
                    'processing_methods': ['tesseract'] + (['easyocr'] if self.reader else [])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error processing image {image_path}: {e}")
            return {
                'error': str(e),
                'raw_text': '',
                'cleaned_text': '',
                'structured_info': {},
                'confidence': 0.0
            }
    
    def _load_image(self, image_path: str) -> np.ndarray:
        """Load image from path"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        return image
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _extract_with_tesseract(self, image: np.ndarray) -> str:
        """Extract text using Tesseract OCR"""
        try:
            # Configure Tesseract for German medical documents
            custom_config = r'--oem 3 --psm 6 -l deu+eng'
            text = pytesseract.image_to_string(image, config=custom_config)
            return text
        except Exception as e:
            self.logger.warning(f"Tesseract extraction failed: {e}")
            return ""
    
    def _extract_with_easyocr(self, image_path: str) -> str:
        """Extract text using EasyOCR"""
        try:
            results = self.reader.readtext(image_path)
            text_parts = [result[1] for result in results]
            return " ".join(text_parts)
        except Exception as e:
            self.logger.warning(f"EasyOCR extraction failed: {e}")
            return ""
    
    def _combine_results(self, tesseract_text: str, easyocr_text: str) -> str:
        """Combine results from multiple OCR methods"""
        if not tesseract_text and not easyocr_text:
            return ""
        
        if not tesseract_text:
            return easyocr_text
        elif not easyocr_text:
            return tesseract_text
        
        # Simple combination - prefer longer text
        if len(tesseract_text) > len(easyocr_text):
            return tesseract_text
        else:
            return easyocr_text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = " ".join(text.split())
        
        # Remove common OCR artifacts
        artifacts = ["|", "]", "[", "}", "{", "\\", "/"]
        for artifact in artifacts:
            cleaned = cleaned.replace(artifact, "")
        
        # Fix common OCR mistakes
        replacements = {
            "0": "O",  # Common OCR mistake
            "1": "I",  # Common OCR mistake
            "5": "S",  # Common OCR mistake
        }
        
        for wrong, correct in replacements.items():
            cleaned = cleaned.replace(wrong, correct)
        
        return cleaned
    
    def _structure_medical_info(self, text: str) -> Dict[str, Any]:
        """Structure extracted medical information"""
        structured = {
            'diagnoses': [],
            'findings': [],
            'patient_info': {},
            'medical_terms': [],
            'dates': [],
            'measurements': []
        }
        
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Extract diagnoses
            if any(keyword in line_lower for keyword in ["diagnose", "diagnosis"]):
                structured['diagnoses'].append(line.strip())
            
            # Extract findings
            if any(keyword in line_lower for keyword in ["befund", "finding", "ergebnis"]):
                structured['findings'].append(line.strip())
            
            # Extract patient information
            if any(keyword in line_lower for keyword in ["patient", "name", "geboren", "geb"]):
                structured['patient_info'][line.split(':')[0].strip()] = line.split(':')[1].strip() if ':' in line else line.strip()
            
            # Extract medical terms
            for keyword in self.medical_keywords:
                if keyword.lower() in line_lower:
                    structured['medical_terms'].append(line.strip())
                    break
        
        return structured
    
    def _calculate_confidence(self, tesseract_text: str, easyocr_text: str) -> float:
        """Calculate confidence score for OCR results"""
        if not tesseract_text and not easyocr_text:
            return 0.0
        
        # Simple confidence based on text length and medical keyword presence
        combined_text = tesseract_text + " " + easyocr_text
        text_length = len(combined_text)
        
        # Count medical keywords
        keyword_count = sum(1 for keyword in self.medical_keywords 
                          if keyword.lower() in combined_text.lower())
        
        # Calculate confidence (0-1)
        length_score = min(text_length / 1000, 1.0)  # Normalize by expected length
        keyword_score = min(keyword_count / 5, 1.0)  # Normalize by expected keywords
        
        return (length_score + keyword_score) / 2
    
    def is_ready(self) -> bool:
        """Check if OCR processor is ready"""
        try:
            # Test Tesseract availability
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False 