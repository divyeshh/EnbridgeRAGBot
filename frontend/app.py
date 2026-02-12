"""
Streamlit Frontend for RAG Chatbot
"""
import streamlit as st
import requests
import os
from pathlib import Path

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Enbridge Bot",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.title("🛡️ Enbridge Bot")
    
    # System status
    try:
        response = requests.get(f"{API_URL}/status")
        if response.status_code == 200:
            status = response.json()
            st.success(f"✅ System Online")
            # Keep chunk count internal for admin visibility but simplified
            st.caption(f"Knowledge density: {status['document_count']} units")
        else:
            st.error("❌ API not responding")
    except:
        st.error("❌ Cannot connect to API")
        st.stop()
    
    st.divider()
    
    # Clear all (Simplified)
    if st.button("🗑️ Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# Main chat interface
st.title("Enbridge Bot")
st.caption("I've read your documents and I'm ready to help.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "question": prompt,
                        "chat_history": st.session_state.chat_history
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["answer"]
                    
                    st.markdown(answer)
                    
                    # Update chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })
                    st.session_state.chat_history.append({"role": "human", "content": prompt})
                    st.session_state.chat_history.append({"role": "ai", "content": answer})
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"❌ Error: {error_detail}")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
st.caption("Powered by Advanced RAG Pipeline | 100% Free")
