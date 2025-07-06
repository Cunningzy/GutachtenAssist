#!/usr/bin/env python3
"""
Simple Demo for GutachtenAssist
Works without heavy ML dependencies
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

def main():
    """Simple demo application"""
    
    st.set_page_config(
        page_title="GutachtenAssist Demo",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("📋 GutachtenAssist - Demo Version")
    st.markdown("**Offline Expert Opinion Writing Assistant**")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Datei-Upload (Demo)")
        
        # Document upload
        uploaded_docs = st.file_uploader(
            "Gutachten zum Lernen (.txt)",
            type=['txt'],
            accept_multiple_files=True
        )
        
        # Image upload
        uploaded_images = st.file_uploader(
            "Medizinische Dokumente (.txt)",
            type=['txt'],
            accept_multiple_files=True
        )
        
        # Audio upload
        uploaded_audio = st.file_uploader(
            "Audio-Transkription (.txt)",
            type=['txt']
        )
    
    # Main area
    st.header("💬 Chat mit GutachtenAssist")
    
    # Chat input
    user_input = st.text_input(
        "Ihre Nachricht:",
        placeholder="Fragen Sie mich nach dem Gutachten...",
        key="user_input"
    )
    
    if st.button("Senden"):
        if user_input:
            st.session_state.chat_history = st.session_state.get('chat_history', [])
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Generate response
            response = generate_response(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Display chat history
    if 'chat_history' in st.session_state:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Generate Gutachten button
    if st.button("Gutachten generieren (Demo)"):
        gutachten = generate_demo_gutachten()
        st.session_state.current_gutachten = gutachten
        
        st.success("✅ Gutachten generiert!")
        st.text_area("Generiertes Gutachten:", value=gutachten, height=400)
    
    # File processing results
    if uploaded_docs or uploaded_images or uploaded_audio:
        st.header("📄 Verarbeitete Dateien")
        
        for file in uploaded_docs or []:
            st.write(f"📄 {file.name} (Dokument)")
            st.text("Demo: Template gelernt")
        
        for file in uploaded_images or []:
            st.write(f"📄 {file.name} (Bild)")
            st.text("Demo: OCR Text extrahiert")
        
        if uploaded_audio:
            st.write(f"📄 {uploaded_audio.name} (Audio)")
            st.text("Demo: Audio transkribiert")

def generate_response(message: str) -> str:
    """Generate response to user message"""
    message_lower = message.lower()
    
    if "hallo" in message_lower:
        return "Hallo! Ich bin Ihr GutachtenAssist Demo. Ich kann Ihnen bei der Erstellung von Gutachten helfen!"
    
    elif "status" in message_lower:
        return "Demo-Status:\n- Templates: 0 (Demo-Modus)\n- Modelle: Demo-Modus aktiv"
    
    elif "hilfe" in message_lower:
        return """Ich kann Ihnen bei folgenden Aufgaben helfen:
1. **Dokumente lernen**: Laden Sie .txt Dateien hoch
2. **Bilder verarbeiten**: Laden Sie .txt Dateien hoch (Demo)
3. **Audio transkribieren**: Laden Sie .txt Dateien hoch (Demo)
4. **Gutachten generieren**: Ich erstelle ein Demo-Gutachten"""
    
    else:
        return "Ich verstehe Ihre Nachricht. Dies ist eine Demo-Version. Laden Sie Dateien hoch oder fragen Sie nach Hilfe."

def generate_demo_gutachten() -> str:
    """Generate a demo Gutachten"""
    return f"""
GUTACHTEN

Erstellt am: {datetime.now().strftime('%d.%m.%Y')}
Erstellt von: GutachtenAssist Demo System

EINLEITUNG

Der vorliegende Fall betrifft einen 45-jährigen Patienten mit chronischen Rückenschmerzen.
Die medizinische Vorgeschichte zeigt eine langjährige Beschwerdesymptomatik.

BEFUND

Die medizinische Untersuchung zeigt:
- Chronische Lumbalgie
- Radikuläre Symptomatik L5
- Positive Lasègue-Zeichen
- MRT: Bandscheibenvorfall L4/L5

BEURTEILUNG

Der Patient leidet unter einer chronischen Lumbalgie mit radikulärer Komponente.
Die Arbeitsfähigkeit ist deutlich eingeschränkt.
Eine operative Behandlung sollte erwogen werden.

ZUSAMMENFASSUNG

Es liegt eine behandlungsbedürftige Wirbelsäulenerkrankung vor.
Die Arbeitsfähigkeit ist eingeschränkt.

---
Ende des Gutachtens
Erstellt mit GutachtenAssist Demo
"""

if __name__ == "__main__":
    main() 