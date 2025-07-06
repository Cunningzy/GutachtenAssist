"""
Chat interface for GutachtenAssist using Streamlit
"""

import streamlit as st
import os
from pathlib import Path
from typing import List, Dict, Any
import tempfile

from ..utils.logger import get_logger


class ChatInterface:
    """
    Main chat interface for GutachtenAssist
    """
    
    def __init__(self, assistant):
        """Initialize chat interface"""
        self.assistant = assistant
        self.logger = get_logger("ChatInterface")
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'current_gutachten' not in st.session_state:
            st.session_state.current_gutachten = None
    
    def run(self):
        """Run the chat interface"""
        # Page header
        st.title("📋 GutachtenAssist")
        st.markdown("**Offline Expert Opinion Writing Assistant**")
        
        # Sidebar for file uploads and settings
        self._render_sidebar()
        
        # Main chat area
        self._render_chat_area()
        
        # File processing area
        self._render_file_processing()
        
        # Status area
        self._render_status()
    
    def _render_sidebar(self):
        """Render sidebar with file uploads and settings"""
        with st.sidebar:
            st.header("📁 Datei-Upload")
            
            # Document learning upload
            st.subheader("Gutachten zum Lernen")
            uploaded_docs = st.file_uploader(
                "Laden Sie .doc/.docx Dateien hoch",
                type=['doc', 'docx'],
                accept_multiple_files=True,
                key="doc_uploader"
            )
            
            if uploaded_docs:
                if st.button("Templates lernen", key="learn_templates"):
                    self._process_document_learning(uploaded_docs)
            
            # Image upload for OCR
            st.subheader("Medizinische Dokumente")
            uploaded_images = st.file_uploader(
                "Laden Sie Bilder hoch",
                type=['jpg', 'jpeg', 'png', 'tiff', 'bmp'],
                accept_multiple_files=True,
                key="image_uploader"
            )
            
            if uploaded_images:
                if st.button("Text extrahieren", key="extract_text"):
                    self._process_image_ocr(uploaded_images)
            
            # Audio upload for transcription
            st.subheader("Audio-Transkription")
            uploaded_audio = st.file_uploader(
                "Laden Sie Audio-Dateien hoch",
                type=['flac', 'wav', 'mp3'],
                key="audio_uploader"
            )
            
            if uploaded_audio:
                if st.button("Audio transkribieren", key="transcribe_audio"):
                    self._process_audio_transcription(uploaded_audio)
            
            # Settings
            st.header("⚙️ Einstellungen")
            st.info("Alle Funktionen arbeiten offline")
            
            # Status information
            status = self.assistant.get_status()
            st.subheader("System-Status")
            st.write(f"Templates geladen: {status['templates_loaded']}")
            st.write(f"Modelle bereit: {'✅' if status['models_ready'] else '❌'}")
    
    def _render_chat_area(self):
        """Render main chat area"""
        st.header("💬 Chat mit GutachtenAssist")
        
        # Chat input
        user_input = st.text_input(
            "Ihre Nachricht:",
            placeholder="Fragen Sie mich nach dem Gutachten oder geben Sie Anweisungen...",
            key="user_input"
        )
        
        # Send button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Senden", key="send_button"):
                if user_input:
                    self._process_user_message(user_input)
        
        # Chat history
        st.subheader("Chat-Verlauf")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Generate Gutachten button
        if st.session_state.uploaded_files:
            if st.button("Gutachten generieren", key="generate_gutachten"):
                self._generate_gutachten()
    
    def _render_file_processing(self):
        """Render file processing results"""
        if st.session_state.uploaded_files:
            st.header("📄 Verarbeitete Dateien")
            
            for file_info in st.session_state.uploaded_files:
                with st.expander(f"📄 {file_info['name']} ({file_info['type']})"):
                    if file_info['type'] == 'image':
                        st.write("**Extrahierter Text:**")
                        st.text(file_info.get('extracted_text', 'Kein Text gefunden'))
                        
                        if file_info.get('structured_info'):
                            st.write("**Strukturierte Informationen:**")
                            st.json(file_info['structured_info'])
                    
                    elif file_info['type'] == 'audio':
                        st.write("**Transkription:**")
                        st.text(file_info.get('transcription', 'Keine Transkription verfügbar'))
                    
                    elif file_info['type'] == 'document':
                        st.write("**Gelernte Template-Informationen:**")
                        st.json(file_info.get('template_data', {}))
    
    def _render_status(self):
        """Render system status"""
        if st.session_state.current_gutachten:
            st.header("📋 Generiertes Gutachten")
            
            # Display the generated Gutachten
            st.text_area(
                "Gutachten-Text:",
                value=st.session_state.current_gutachten,
                height=400,
                key="gutachten_display"
            )
            
            # Feedback section
            st.subheader("Feedback")
            feedback = st.text_area(
                "Geben Sie Feedback zum generierten Gutachten:",
                placeholder="Was war gut? Was sollte verbessert werden?",
                key="feedback_input"
            )
            
            if st.button("Feedback senden", key="send_feedback"):
                if feedback:
                    self._process_feedback(feedback)
    
    def _process_user_message(self, message: str):
        """Process user message and generate response"""
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": message
        })
        
        # Generate response based on message content
        response = self._generate_response(message)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Rerun to update chat display
        st.rerun()
    
    def _generate_response(self, message: str) -> str:
        """Generate response to user message"""
        message_lower = message.lower()
        
        if "hallo" in message_lower or "hello" in message_lower:
            return "Hallo! Ich bin Ihr GutachtenAssist. Ich kann Ihnen bei der Erstellung von Gutachten helfen. Laden Sie Dokumente hoch oder stellen Sie mir Fragen!"
        
        elif "status" in message_lower:
            status = self.assistant.get_status()
            return f"System-Status:\n- Templates geladen: {status['templates_loaded']}\n- Modelle bereit: {'Ja' if status['models_ready'] else 'Nein'}"
        
        elif "hilfe" in message_lower or "help" in message_lower:
            return """Ich kann Ihnen bei folgenden Aufgaben helfen:
1. **Dokumente lernen**: Laden Sie .doc/.docx Dateien hoch, damit ich Templates lerne
2. **Bilder verarbeiten**: Laden Sie medizinische Dokumente hoch für OCR
3. **Audio transkribieren**: Laden Sie Audio-Dateien hoch für Transkription
4. **Gutachten generieren**: Ich erstelle ein vollständiges Gutachten aus allen Daten"""
        
        elif "generieren" in message_lower or "erstellen" in message_lower:
            if st.session_state.uploaded_files:
                return "Ich kann ein Gutachten generieren. Klicken Sie auf 'Gutachten generieren' oder laden Sie zuerst Dateien hoch."
            else:
                return "Bitte laden Sie zuerst Dateien hoch (Dokumente, Bilder oder Audio), bevor ich ein Gutachten generieren kann."
        
        else:
            return "Ich verstehe Ihre Nachricht. Bitte laden Sie Dateien hoch oder fragen Sie mich nach dem Status oder der Hilfe."
    
    def _process_document_learning(self, uploaded_files):
        """Process document learning"""
        with st.spinner("Lerne Templates aus Dokumenten..."):
            # Save uploaded files temporarily
            temp_files = []
            for uploaded_file in uploaded_files:
                temp_path = self._save_uploaded_file(uploaded_file)
                temp_files.append(temp_path)
            
            # Learn from documents
            results = self.assistant.learn_from_documents(temp_files)
            
            # Add to uploaded files list
            for uploaded_file in uploaded_files:
                st.session_state.uploaded_files.append({
                    'name': uploaded_file.name,
                    'type': 'document',
                    'template_data': results
                })
            
            # Clean up temp files
            for temp_file in temp_files:
                os.unlink(temp_file)
            
            st.success(f"✅ {results['templates_learned']} Templates gelernt!")
    
    def _process_image_ocr(self, uploaded_files):
        """Process image OCR"""
        with st.spinner("Verarbeite Bilder..."):
            for uploaded_file in uploaded_files:
                # Save uploaded file temporarily
                temp_path = self._save_uploaded_file(uploaded_file)
                
                # Process image
                results = self.assistant.process_images([temp_path])
                
                # Add to uploaded files list
                st.session_state.uploaded_files.append({
                    'name': uploaded_file.name,
                    'type': 'image',
                    'extracted_text': results.get('text_extracted', {}).get(temp_path, ''),
                    'structured_info': results.get('descriptions', {}).get(temp_path, {})
                })
                
                # Clean up temp file
                os.unlink(temp_path)
            
            st.success(f"✅ {len(uploaded_files)} Bilder verarbeitet!")
    
    def _process_audio_transcription(self, uploaded_file):
        """Process audio transcription"""
        with st.spinner("Transkribiere Audio..."):
            # Save uploaded file temporarily
            temp_path = self._save_uploaded_file(uploaded_file)
            
            # Transcribe audio
            results = self.assistant.transcribe_audio(temp_path)
            
            # Add to uploaded files list
            st.session_state.uploaded_files.append({
                'name': uploaded_file.name,
                'type': 'audio',
                'transcription': results.get('formatted_text', ''),
                'raw_transcription': results.get('raw_transcription', '')
            })
            
            # Clean up temp file
            os.unlink(temp_path)
            
            if results.get('success'):
                st.success("✅ Audio erfolgreich transkribiert!")
            else:
                st.error(f"❌ Fehler bei der Transkription: {results.get('error', 'Unbekannter Fehler')}")
    
    def _generate_gutachten(self):
        """Generate complete Gutachten"""
        with st.spinner("Generiere Gutachten..."):
            # Collect all medical data
            medical_data = {}
            transcribed_text = None
            
            for file_info in st.session_state.uploaded_files:
                if file_info['type'] == 'image':
                    # Merge structured info
                    if file_info.get('structured_info'):
                        for key, value in file_info['structured_info'].items():
                            if key not in medical_data:
                                medical_data[key] = []
                            if isinstance(value, list):
                                medical_data[key].extend(value)
                            else:
                                medical_data[key].append(value)
                
                elif file_info['type'] == 'audio':
                    # Use transcribed text
                    transcribed_text = file_info.get('transcription', '')
            
            # Generate Gutachten
            gutachten_text = self.assistant.generate_gutachten(
                medical_data=medical_data,
                transcribed_text=transcribed_text
            )
            
            # Store in session state
            st.session_state.current_gutachten = gutachten_text
            
            st.success("✅ Gutachten erfolgreich generiert!")
    
    def _process_feedback(self, feedback: str):
        """Process user feedback"""
        if st.session_state.current_gutachten:
            success = self.assistant.learn_from_feedback(
                st.session_state.current_gutachten,
                feedback
            )
            
            if success:
                st.success("✅ Feedback erfolgreich verarbeitet! Das System lernt aus Ihrem Feedback.")
            else:
                st.error("❌ Fehler beim Verarbeiten des Feedbacks.")
    
    def _save_uploaded_file(self, uploaded_file) -> str:
        """Save uploaded file to temporary location"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name 