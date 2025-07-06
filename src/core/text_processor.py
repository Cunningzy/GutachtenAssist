"""
Text processing module for grammar correction and formatting
"""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..utils.logger import get_logger


class TextProcessor:
    """
    Handles text processing, grammar correction, and formatting
    """
    
    def __init__(self, config):
        """Initialize text processor"""
        self.config = config
        self.logger = get_logger("TextProcessor")
        
        # German grammar rules and corrections
        self.grammar_rules = {
            'capitalization': [
                (r'\b(der|die|das|ein|eine|eines)\s+([a-z])', r'\1 \2'.upper()),
                (r'\b(patient|patientin|arzt|ärztin|diagnose|befund)\b', lambda m: str(m.group(1).title()))
            ],
            'punctuation': [
                (r'\s+([,.!?])', r'\1'),  # Remove spaces before punctuation
                (r'([,.!?])([A-Za-z])', r'\1 \2'),  # Add space after punctuation
            ],
            'medical_terms': [
                (r'\b(ekg|ct|mrt|blut|urin)\b', lambda m: str(m.group(1).upper())),
                (r'\b(herzinfarkt|diabetes|hypertension)\b', lambda m: str(m.group(1).title()))
            ]
        }
        
        # Common German medical abbreviations
        self.medical_abbreviations = {
            'EKG': 'Elektrokardiogramm',
            'CT': 'Computertomographie',
            'MRT': 'Magnetresonanztomographie',
            'Blut': 'Blutuntersuchung',
            'Urin': 'Urinuntersuchung'
        }
    
    def correct_grammar(self, text: str) -> str:
        """
        Correct grammar and formatting in German text
        
        Args:
            text: Input text to correct
            
        Returns:
            Corrected text
        """
        if not text:
            return ""
        
        self.logger.info(f"Correcting grammar for {len(text)} characters")
        
        corrected_text = text
        
        # Apply grammar rules
        for rule_type, rules in self.grammar_rules.items():
            for pattern, replacement in rules:
                if callable(replacement):
                    corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
                else:
                    corrected_text = re.sub(pattern, replacement, corrected_text)
        
        # Fix common OCR mistakes
        corrected_text = self._fix_ocr_mistakes(corrected_text)
        
        # Ensure proper sentence structure
        corrected_text = self._fix_sentence_structure(corrected_text)
        
        return corrected_text
    
    def format_gutachten_text(self, text: str) -> str:
        """
        Format text according to Gutachten standards
        
        Args:
            text: Raw text to format
            
        Returns:
            Formatted text
        """
        if not text:
            return ""
        
        self.logger.info("Formatting text for Gutachten")
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        formatted_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Format individual sentence
                formatted_sentence = self._format_sentence(sentence)
                formatted_sentences.append(formatted_sentence)
        
        # Join sentences with proper punctuation
        formatted_text = ". ".join(formatted_sentences) + "."
        
        # Add paragraph breaks for better readability
        formatted_text = self._add_paragraph_breaks(formatted_text)
        
        return formatted_text
    
    def structure_medical_info(self, text: str) -> Dict[str, Any]:
        """
        Structure medical information from text
        
        Args:
            text: Medical text to structure
            
        Returns:
            Structured medical information
        """
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
            if any(keyword in line_lower for keyword in ['diagnose', 'diagnosis']):
                diagnosis = self._extract_medical_entity(line, 'diagnose')
                if diagnosis:
                    structured['diagnoses'].append(diagnosis)
            
            # Extract findings
            if any(keyword in line_lower for keyword in ['befund', 'finding', 'ergebnis']):
                finding = self._extract_medical_entity(line, 'befund')
                if finding:
                    structured['findings'].append(finding)
            
            # Extract patient information
            if any(keyword in line_lower for keyword in ['patient', 'name', 'geboren', 'geb']):
                patient_info = self._extract_patient_info(line)
                if patient_info:
                    structured['patient_info'].update(patient_info)
            
            # Extract medical terms
            medical_terms = self._extract_medical_terms(line)
            structured['medical_terms'].extend(medical_terms)
            
            # Extract dates
            dates = self._extract_dates(line)
            structured['dates'].extend(dates)
            
            # Extract measurements
            measurements = self._extract_measurements(line)
            structured['measurements'].extend(measurements)
        
        return structured
    
    def _fix_ocr_mistakes(self, text: str) -> str:
        """Fix common OCR mistakes"""
        # Common OCR replacements
        replacements = {
            '0': 'O',  # Zero to O
            '1': 'I',  # One to I
            '5': 'S',  # Five to S
            '8': 'B',  # Eight to B
            '|': '',   # Remove vertical bars
            '[': '',   # Remove brackets
            ']': '',
        }
        
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def _fix_sentence_structure(self, text: str) -> str:
        """Fix sentence structure and capitalization"""
        # Ensure proper sentence capitalization
        sentences = re.split(r'[.!?]+', text)
        corrected_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                if sentence and sentence[0].islower():
                    sentence = sentence[0].upper() + sentence[1:]
                corrected_sentences.append(sentence)
        
        return ". ".join(corrected_sentences) + "."
    
    def _format_sentence(self, sentence: str) -> str:
        """Format individual sentence"""
        # Remove extra whitespace
        sentence = " ".join(sentence.split())
        
        # Ensure proper capitalization
        if sentence and sentence[0].islower():
            sentence = sentence[0].upper() + sentence[1:]
        
        # Fix common medical abbreviations
        for abbr, full in self.medical_abbreviations.items():
            sentence = re.sub(rf'\b{abbr}\b', full, sentence, flags=re.IGNORECASE)
        
        return sentence
    
    def _add_paragraph_breaks(self, text: str) -> str:
        """Add paragraph breaks for better readability"""
        # Add breaks after section headers
        section_keywords = ['Einleitung', 'Befund', 'Beurteilung', 'Zusammenfassung']
        
        for keyword in section_keywords:
            text = re.sub(rf'({keyword})', r'\n\n\1', text, flags=re.IGNORECASE)
        
        return text
    
    def _extract_medical_entity(self, line: str, entity_type: str) -> Optional[str]:
        """Extract medical entity from line"""
        # Simple extraction based on keywords
        if entity_type == 'diagnose':
            match = re.search(r'[Dd]iagnose[:\s]+([^.\n]+)', line)
        elif entity_type == 'befund':
            match = re.search(r'[Bb]efund[:\s]+([^.\n]+)', line)
        else:
            return None
        
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_patient_info(self, line: str) -> Dict[str, str]:
        """Extract patient information from line"""
        info = {}
        
        # Extract name
        name_match = re.search(r'[Nn]ame[:\s]+([^,\n]+)', line)
        if name_match:
            info['name'] = name_match.group(1).strip()
        
        # Extract birth date
        birth_match = re.search(r'[Gg]eboren[:\s]+([^,\n]+)', line)
        if birth_match:
            info['birth_date'] = birth_match.group(1).strip()
        
        return info
    
    def _extract_medical_terms(self, line: str) -> List[str]:
        """Extract medical terms from line"""
        terms = []
        
        # Common medical terms
        medical_keywords = [
            'Herzinfarkt', 'Diabetes', 'Hypertension', 'Arthritis',
            'Krebs', 'Tumor', 'Infektion', 'Entzündung'
        ]
        
        for term in medical_keywords:
            if term.lower() in line.lower():
                terms.append(term)
        
        return terms
    
    def _extract_dates(self, line: str) -> List[str]:
        """Extract dates from line"""
        # German date patterns
        date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{1,2}\.\d{1,2}\.\d{2}',   # DD.MM.YY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, line)
            dates.extend(matches)
        
        return dates
    
    def _extract_measurements(self, line: str) -> List[str]:
        """Extract measurements from line"""
        # Measurement patterns
        measurement_patterns = [
            r'\d+\.?\d*\s*(mmHg|mg/dl|mmol/l|kg|cm)',  # Blood pressure, lab values, etc.
        ]
        
        measurements = []
        for pattern in measurement_patterns:
            matches = re.findall(pattern, line)
            measurements.extend(matches)
        
        return measurements
    
    def is_ready(self) -> bool:
        """Check if text processor is ready"""
        return True  # No external dependencies 