"""
Template manager for storing and managing learned Gutachten templates
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.logger import get_logger


class TemplateManager:
    """
    Manages learned templates and patterns
    """
    
    def __init__(self, config):
        """Initialize template manager"""
        self.config = config
        self.logger = get_logger("TemplateManager")
        
        self.templates = []
        self.templates_file = self.config.templates_dir / "templates.json"
        self.patterns_file = self.config.templates_dir / "patterns.pkl"
        
        # Create templates directory if it doesn't exist
        self.config.templates_dir.mkdir(exist_ok=True)
    
    def load_templates(self) -> bool:
        """Load existing templates from disk"""
        try:
            if self.templates_file.exists():
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
                self.logger.info(f"Loaded {len(self.templates)} templates")
                return True
            else:
                self.logger.info("No existing templates found")
                return False
        except Exception as e:
            self.logger.error(f"Error loading templates: {e}")
            return False
    
    def save_templates(self) -> bool:
        """Save templates to disk"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Saved {len(self.templates)} templates")
            return True
        except Exception as e:
            self.logger.error(f"Error saving templates: {e}")
            return False
    
    def add_template(self, template_data: Dict[str, Any]) -> bool:
        """Add a new template"""
        try:
            # Add metadata
            template_data['created_at'] = datetime.now().isoformat()
            template_data['template_id'] = f"template_{len(self.templates) + 1}"
            
            # Validate template
            if self._validate_template(template_data):
                self.templates.append(template_data)
                self.logger.info(f"Added template: {template_data['template_id']}")
                return True
            else:
                self.logger.warning("Template validation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adding template: {e}")
            return False
    
    def get_best_template(self, medical_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get the best matching template for given medical data"""
        if not self.templates:
            return None
        
        best_template = None
        best_score = 0.0
        
        for template in self.templates:
            score = self._calculate_template_score(template, medical_data)
            if score > best_score and score >= self.config.min_template_confidence:
                best_score = score
                best_template = template
        
        if best_template:
            self.logger.info(f"Selected template {best_template['template_id']} with score {best_score:.2f}")
        
        return best_template
    
    def update_from_feedback(self, gutachten_text: str, user_feedback: str) -> bool:
        """Update templates based on user feedback"""
        try:
            # Create feedback entry
            feedback_entry = {
                'timestamp': datetime.now().isoformat(),
                'gutachten_text': gutachten_text,
                'user_feedback': user_feedback,
                'feedback_type': self._classify_feedback(user_feedback)
            }
            
            # Find most recent template and update it
            if self.templates:
                latest_template = self.templates[-1]
                if 'feedback' not in latest_template:
                    latest_template['feedback'] = []
                latest_template['feedback'].append(feedback_entry)
                
                # Update template based on feedback
                self._apply_feedback_to_template(latest_template, feedback_entry)
                
                self.logger.info("Template updated based on user feedback")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating template from feedback: {e}")
            return False
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored templates"""
        if not self.templates:
            return {'total_templates': 0}
        
        stats = {
            'total_templates': len(self.templates),
            'avg_sections_per_template': 0,
            'common_patterns': {},
            'recent_templates': []
        }
        
        # Calculate average sections
        total_sections = sum(len(t.get('structure', {}).get('sections', {})) 
                           for t in self.templates)
        stats['avg_sections_per_template'] = total_sections / len(self.templates)
        
        # Find common patterns
        pattern_counts = {}
        for template in self.templates:
            for pattern in template.get('patterns', []):
                pattern_type = pattern.get('type', 'unknown')
                pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        
        stats['common_patterns'] = pattern_counts
        
        # Get recent templates
        stats['recent_templates'] = [
            {
                'id': t.get('template_id', 'unknown'),
                'created_at': t.get('created_at', 'unknown'),
                'sections': len(t.get('structure', {}).get('sections', {}))
            }
            for t in self.templates[-5:]  # Last 5 templates
        ]
        
        return stats
    
    def _validate_template(self, template_data: Dict[str, Any]) -> bool:
        """Validate template data structure"""
        required_fields = ['structure', 'patterns', 'formatting']
        
        for field in required_fields:
            if field not in template_data:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Check if structure has sections
        if not template_data['structure'].get('sections'):
            self.logger.warning("Template has no sections")
            return False
        
        return True
    
    def _calculate_template_score(self, template: Dict[str, Any], medical_data: Dict[str, Any]) -> float:
        """Calculate how well a template matches the medical data"""
        score = 0.0
        
        # Check if template has relevant medical patterns
        template_patterns = template.get('patterns', [])
        medical_terms = medical_data.get('medical_terms', [])
        
        # Count matching medical terms
        matches = 0
        for pattern in template_patterns:
            if pattern.get('type') == 'medical_terminology':
                for term in medical_terms:
                    if any(keyword in term.lower() for keyword in ['diagnose', 'befund', 'untersuchung']):
                        matches += 1
        
        # Normalize score
        if template_patterns:
            score += min(matches / len(template_patterns), 1.0)
        
        # Bonus for having similar structure
        if medical_data.get('diagnoses') and template.get('structure', {}).get('sections'):
            score += 0.3
        
        return min(score, 1.0)
    
    def _classify_feedback(self, feedback: str) -> str:
        """Classify user feedback type"""
        feedback_lower = feedback.lower()
        
        if any(word in feedback_lower for word in ['gut', 'gut gemacht', 'perfekt']):
            return 'positive'
        elif any(word in feedback_lower for word in ['schlecht', 'falsch', 'korrigieren']):
            return 'negative'
        elif any(word in feedback_lower for word in ['ändern', 'modifizieren', 'anpassen']):
            return 'modification'
        else:
            return 'neutral'
    
    def _apply_feedback_to_template(self, template: Dict[str, Any], feedback_entry: Dict[str, Any]):
        """Apply user feedback to improve template"""
        feedback_type = feedback_entry.get('feedback_type', 'neutral')
        
        if feedback_type == 'positive':
            # Increase confidence for this template
            template['confidence'] = template.get('confidence', 0.5) + 0.1
        elif feedback_type == 'negative':
            # Decrease confidence
            template['confidence'] = max(template.get('confidence', 0.5) - 0.1, 0.0)
        elif feedback_type == 'modification':
            # Extract modification suggestions
            feedback_text = feedback_entry.get('user_feedback', '')
            # Here you could implement more sophisticated feedback processing
            self.logger.info(f"Modification feedback received: {feedback_text}")
    
    def cleanup_old_templates(self) -> int:
        """Remove old templates to stay within limits"""
        if len(self.templates) <= self.config.max_templates_to_keep:
            return 0
        
        templates_to_remove = len(self.templates) - self.config.max_templates_to_keep
        self.templates = self.templates[-self.config.max_templates_to_keep:]
        
        self.logger.info(f"Removed {templates_to_remove} old templates")
        return templates_to_remove 