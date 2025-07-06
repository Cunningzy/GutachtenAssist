"""
Gutachten generator that creates final expert opinion documents
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.logger import get_logger


class GutachtenGenerator:
    """
    Generates complete Gutachten from processed data and templates
    """
    
    def __init__(self, config):
        """Initialize Gutachten generator"""
        self.config = config
        self.logger = get_logger("GutachtenGenerator")
        
        # Standard Gutachten sections
        self.sections = [
            "Einleitung",
            "Vorbemerkung", 
            "Auftrag",
            "Sachverhalt",
            "Befund",
            "Beurteilung",
            "Zusammenfassung"
        ]
    
    def generate(self, 
                 template: Dict[str, Any],
                 medical_data: Dict[str, Any],
                 transcribed_text: Optional[str] = None) -> str:
        """
        Generate complete Gutachten
        
        Args:
            template: Learned template
            medical_data: Structured medical information
            transcribed_text: Optional transcribed text from audio
            
        Returns:
            Complete Gutachten text
        """
        self.logger.info("Generating Gutachten")
        
        try:
            # Start with template structure
            gutachten_parts = []
            
            # Generate each section
            for section in self.sections:
                section_content = self._generate_section(
                    section, template, medical_data, transcribed_text
                )
                if section_content:
                    gutachten_parts.append(section_content)
            
            # Combine all sections
            complete_gutachten = "\n\n".join(gutachten_parts)
            
            # Add header and footer
            complete_gutachten = self._add_header_footer(complete_gutachten)
            
            self.logger.info(f"Generated Gutachten with {len(complete_gutachten)} characters")
            return complete_gutachten
            
        except Exception as e:
            self.logger.error(f"Error generating Gutachten: {e}")
            return f"Fehler bei der Generierung des Gutachtens: {str(e)}"
    
    def _generate_section(self, 
                         section_name: str,
                         template: Dict[str, Any],
                         medical_data: Dict[str, Any],
                         transcribed_text: Optional[str] = None) -> str:
        """Generate content for a specific section"""
        
        if section_name == "Einleitung":
            return self._generate_einleitung(medical_data, transcribed_text)
        elif section_name == "Befund":
            return self._generate_befund(medical_data)
        elif section_name == "Beurteilung":
            return self._generate_beurteilung(medical_data, transcribed_text)
        elif section_name == "Zusammenfassung":
            return self._generate_zusammenfassung(medical_data)
        else:
            return self._generate_generic_section(section_name, template, medical_data)
    
    def _generate_einleitung(self, medical_data: Dict[str, Any], transcribed_text: Optional[str] = None) -> str:
        """Generate Einleitung section"""
        content = "EINLEITUNG\n\n"
        
        # Add patient information if available
        patient_info = medical_data.get('patient_info', {})
        if patient_info:
            name = patient_info.get('name', 'der Patient')
            content += f"Der vorliegende Fall betrifft {name}.\n\n"
        
        # Add transcribed content if available
        if transcribed_text:
            # Extract relevant parts from transcription
            relevant_parts = self._extract_relevant_content(transcribed_text, "einleitung")
            if relevant_parts:
                content += f"{relevant_parts}\n\n"
        
        # Add medical context
        diagnoses = medical_data.get('diagnoses', [])
        if diagnoses:
            content += "Die vorliegenden medizinischen Unterlagen zeigen folgende Diagnosen:\n"
            for diagnosis in diagnoses[:3]:  # Limit to first 3
                content += f"- {diagnosis}\n"
            content += "\n"
        
        return content
    
    def _generate_befund(self, medical_data: Dict[str, Any]) -> str:
        """Generate Befund section"""
        content = "BEFUND\n\n"
        
        # Add findings from medical data
        findings = medical_data.get('findings', [])
        if findings:
            content += "Die medizinischen Befunde zeigen:\n"
            for finding in findings:
                content += f"- {finding}\n"
            content += "\n"
        
        # Add measurements if available
        measurements = medical_data.get('measurements', [])
        if measurements:
            content += "Messwerte:\n"
            for measurement in measurements:
                content += f"- {measurement}\n"
            content += "\n"
        
        # Add medical terms
        medical_terms = medical_data.get('medical_terms', [])
        if medical_terms:
            content += "Weitere medizinische Erkenntnisse:\n"
            for term in medical_terms[:5]:  # Limit to first 5
                content += f"- {term}\n"
            content += "\n"
        
        return content
    
    def _generate_beurteilung(self, medical_data: Dict[str, Any], transcribed_text: Optional[str] = None) -> str:
        """Generate Beurteilung section"""
        content = "BEURTEILUNG\n\n"
        
        # Add transcribed assessment if available
        if transcribed_text:
            assessment_parts = self._extract_relevant_content(transcribed_text, "beurteilung")
            if assessment_parts:
                content += f"{assessment_parts}\n\n"
        
        # Add structured assessment based on medical data
        diagnoses = medical_data.get('diagnoses', [])
        if diagnoses:
            content += "Basierend auf den vorliegenden Diagnosen:\n"
            for diagnosis in diagnoses:
                content += f"- {diagnosis}\n"
            content += "\n"
        
        # Add professional assessment
        content += "Die medizinische Beurteilung erfolgt unter Berücksichtigung der aktuellen medizinischen Standards und Leitlinien.\n\n"
        
        return content
    
    def _generate_zusammenfassung(self, medical_data: Dict[str, Any]) -> str:
        """Generate Zusammenfassung section"""
        content = "ZUSAMMENFASSUNG\n\n"
        
        # Summarize key findings
        diagnoses = medical_data.get('diagnoses', [])
        findings = medical_data.get('findings', [])
        
        if diagnoses or findings:
            content += "Zusammenfassend kann festgestellt werden:\n"
            
            if diagnoses:
                content += f"- Es liegen {len(diagnoses)} relevante Diagnosen vor.\n"
            
            if findings:
                content += f"- Es wurden {len(findings)} medizinische Befunde dokumentiert.\n"
            
            content += "\n"
        
        # Add final statement
        content += "Das vorliegende Gutachten basiert auf der sorgfältigen Auswertung aller verfügbaren medizinischen Unterlagen.\n\n"
        
        return content
    
    def _generate_generic_section(self, 
                                 section_name: str,
                                 template: Dict[str, Any],
                                 medical_data: Dict[str, Any]) -> str:
        """Generate generic section based on template"""
        content = f"{section_name.upper()}\n\n"
        
        # Try to get section content from template
        template_sections = template.get('structure', {}).get('sections', {})
        if section_name in template_sections:
            # Use template content as base
            template_content = template_sections[section_name]
            if template_content:
                content += " ".join(template_content[:3]) + "\n\n"  # Use first 3 lines
        
        # Add generic content
        content += f"Dieser Abschnitt behandelt die {section_name.lower()} des vorliegenden Falls.\n\n"
        
        return content
    
    def _extract_relevant_content(self, text: str, section_type: str) -> str:
        """Extract relevant content from transcribed text for specific section"""
        # Simple keyword-based extraction
        keywords = {
            "einleitung": ["einleitung", "vorliegend", "fall", "patient"],
            "beurteilung": ["beurteilung", "bewertung", "einschätzung", "meinung"]
        }
        
        if section_type not in keywords:
            return ""
        
        relevant_keywords = keywords[section_type]
        sentences = text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in relevant_keywords):
                relevant_sentences.append(sentence.strip())
        
        return ". ".join(relevant_sentences[:3])  # Limit to first 3 relevant sentences
    
    def _add_header_footer(self, content: str) -> str:
        """Add header and footer to Gutachten"""
        header = f"""
GUTACHTEN

Erstellt am: {datetime.now().strftime('%d.%m.%Y')}
Erstellt von: GutachtenAssist System

"""
        
        footer = f"""

---
Ende des Gutachtens
Erstellt mit GutachtenAssist
"""
        
        return header + content + footer 