"""
Unified Streamlit App for Cloud Deployment
Directly uses RAGChatbot without needing a separate FastAPI server.
"""
# --- SQLite Monkey Patch for Streamlit Cloud (MUST BE AT TOP) ---
import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass
# -------------------------------------------------------------

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to sys.path for internal imports
sys.path.append(os.getcwd())

from backend.rag_core import RAGChatbot

# Page config
st.set_page_config(
    page_title="Enbridge Assistant",
    page_icon="🤖",
    layout="wide"
)

# --- Custom CSS for Accessibility (Optimized Fonts & High Contrast) ---
st.markdown("""
<style>
    /* Global Font Size (Slightly reduced from 1.2rem) */
    html, body, [class*="st-"] {
        font-size: 1.1rem !important;
    }
    
    /* Chat Message Font Sizes (Better balance) */
    .stChatMessage p {
        font-size: 1.15rem !important;
        line-height: 1.5 !important;
    }
    
    /* Header Font Sizes */
    h1 { font-size: 2.2rem !important; }
    h2 { font-size: 1.8rem !important; }
    h3 { font-size: 1.4rem !important; }
    
    /* Sidebar Accessibility */
    .stSidebar [data-testid="stSidebarNav"] {
        font-size: 1.05rem !important;
    }
    
    /* Make buttons distinct but not oversized */
    .stButton button {
        height: 2.8em !important;
        font-size: 1.05rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chatbot" not in st.session_state:
    # 1. Get API Key from Secrets (Cloud) or Env (Local)
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        st.info("Please set the GROQ_API_KEY in Streamlit Secrets or .env file.")
        st.stop()
    
    # 2. Initialize the bot
    # Note: On Streamlit Cloud, we use In-Memory mode to avoid read-only DB errors.
    with st.spinner("🚀 Initializing AI Assistant..."):
        # Detect Streamlit Cloud
        is_cloud = os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud" or os.path.exists("/mount/src")
        
        # Use None for chroma_persist_dir to trigger In-Memory mode in the cloud
        persist_dir = None if is_cloud else "backend/chroma_db"
        
        chatbot = RAGChatbot(
            groq_api_key=api_key,
            chroma_persist_dir=persist_dir
        )
        
        # 3. Auto-sync documents on first run
        upload_dir = os.path.join(os.getcwd(), "backend", "uploaded_documents")
        if os.path.exists(upload_dir):
            chatbot.sync_folder(upload_dir)
            
        st.session_state.chatbot = chatbot

# Sidebar
with st.sidebar:
    st.title("🤖 Enbridge Bot")
    
    # System status
    count = st.session_state.chatbot.get_document_count()
    st.success(f"✅ System Ready")
    st.caption(f"Knowledge Base: {count} snippets active")
    
    st.divider()
    
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
st.title("🤖 Enbridge Assistant")

# --- Simple How-to Guide for Employees ---
with st.expander("👋 New here? Click for a simple guide", expanded=True):
    st.markdown("""
    **I am here to help you with your tech questions!**
    - ✏️ **Just type** your question in the box at the bottom (for example: *How do I set up my phone?*)
    - ⌨️ **Press Enter** on your keyboard to send it.
    - 👨‍💻 **I will give you a simple answer** to help you get started.
    - 🗑️ **Want to start over?** Click the "Reset Chat" button on the left.
    """)

st.caption("How can I help you today?")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about Enbridge or tech support..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Use the local chatbot instance directly
                result = st.session_state.chatbot.chat(
                    question=prompt,
                    chat_history=st.session_state.chat_history
                )
                
                answer = result["answer"]
                st.markdown(answer)
                
                # Update history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.chat_history.append({"role": "human", "content": prompt})
                st.session_state.chat_history.append({"role": "ai", "content": answer})
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
st.caption("Powered by Llama 3.1 & Enbridge Technical Data")
