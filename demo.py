#!/usr/bin/env python3
"""
Demo script for GutachtenAssist
Shows how to use the system programmatically
"""

import sys
from pathlib import Path
import tempfile
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import Config
from src.core.assistant import GutachtenAssistant


def create_sample_document():
    """Create a sample Gutachten document for learning"""
    sample_text = """
GUTACHTEN

Einleitung:
Der vorliegende Fall betrifft einen 45-jährigen Patienten mit chronischen Rückenschmerzen.

Befund:
Die medizinische Untersuchung zeigt eine Lumbalgie mit radikulären Symptomen.
Die MRT-Untersuchung bestätigt einen Bandscheibenvorfall L4/L5.

Beurteilung:
Der Patient leidet unter einer chronischen Lumbalgie mit radikulärer Komponente.
Die Arbeitsfähigkeit ist eingeschränkt.

Zusammenfassung:
Es liegt eine behandlungsbedürftige Wirbelsäulenerkrankung vor.
"""
    
    # Create temporary document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_text)
        return f.name


def create_sample_medical_data():
    """Create sample medical data from OCR"""
    return {
        'diagnoses': [
            'Chronische Lumbalgie',
            'Bandscheibenvorfall L4/L5',
            'Radikuläre Symptomatik'
        ],
        'findings': [
            'MRT zeigt Bandscheibenvorfall',
            'Neurologische Ausfälle L5',
            'Positive Lasègue-Zeichen'
        ],
        'patient_info': {
            'name': 'Max Mustermann',
            'birth_date': '15.03.1978'
        },
        'medical_terms': [
            'Lumbalgie',
            'Bandscheibenvorfall',
            'Radikulopathie'
        ],
        'measurements': [
            '120/80 mmHg',
            '75 kg',
            '175 cm'
        ]
    }


def create_sample_transcription():
    """Create sample transcribed text"""
    return """
Der Patient zeigt typische Symptome einer chronischen Lumbalgie.
Die neurologische Untersuchung bestätigt radikuläre Ausfälle.
Die Arbeitsfähigkeit ist deutlich eingeschränkt.
Eine operative Behandlung sollte erwogen werden.
"""


def run_demo():
    """Run the complete demo"""
    print("🚀 GutachtenAssist Demo")
    print("=" * 50)
    
    try:
        # Initialize system
        print("1. Initializing GutachtenAssist...")
        config = Config()
        assistant = GutachtenAssistant(config)
        
        # Create sample data
        print("2. Creating sample data...")
        sample_doc = create_sample_document()
        medical_data = create_sample_medical_data()
        transcribed_text = create_sample_transcription()
        
        # Learn from document
        print("3. Learning from sample document...")
        learning_results = assistant.learn_from_documents([sample_doc])
        print(f"   ✅ Learned {learning_results['templates_learned']} templates")
        
        # Generate Gutachten
        print("4. Generating Gutachten...")
        gutachten_text = assistant.generate_gutachten(
            medical_data=medical_data,
            transcribed_text=transcribed_text
        )
        
        # Display results
        print("5. Generated Gutachten:")
        print("-" * 50)
        print(gutachten_text)
        print("-" * 50)
        
        # Test feedback learning
        print("6. Testing feedback learning...")
        feedback = "Das Gutachten ist gut strukturiert, aber die Beurteilung könnte detaillierter sein."
        success = assistant.learn_from_feedback(gutachten_text, feedback)
        print(f"   ✅ Feedback processed: {success}")
        
        # Show system status
        print("7. System status:")
        status = assistant.get_status()
        print(f"   - Templates loaded: {status['templates_loaded']}")
        print(f"   - Models ready: {status['models_ready']}")
        
        print("\n✅ Demo completed successfully!")
        print("\nTo run the full application:")
        print("  python main.py")
        
        # Cleanup
        Path(sample_doc).unlink()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        print("  python setup_models.py")


if __name__ == "__main__":
    run_demo() 