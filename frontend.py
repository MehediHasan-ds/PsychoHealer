# frontend.py
import streamlit as st
import requests
import json
import uuid
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PsychoHealer - AI Psychology Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .response-container {
        background: #f8f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .video-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
        margin: 0.5rem 0;
    }
    .crisis-warning {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .model-info {
        background: #e8f4f8;
        padding: 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #0c5460;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
st.markdown("""
<div class="main-header">
    <h1>PsychoHealer</h1>
    <p>AI-Powered Psychology Assistant with Intelligent Model Selection</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("System Information")
    
    # User ID display
    st.info(f"**User ID:** `{st.session_state.user_id[:8]}...`")
    
    # System status
    try:
        status_response = requests.get(f"{API_BASE_URL}/psychology/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            st.success("System Online")
            st.write(f"**Auto Model Selection:** {status_data.get('auto_selection', 'Enabled')}")
            st.write(f"**Available Models:** {', '.join(status_data.get('available_models', []))}")
        else:
            st.error("System Offline")
    except:
        st.error("Unable to connect to backend")
    
    # Session management
    st.header("Session Management")
    if st.button("New Session"):
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()
    
    if st.button("View History"):
        try:
            history_response = requests.post(
                f"{API_BASE_URL}/psychology/history",
                json={"user_id": st.session_state.user_id, "limit": 5}
            )
            if history_response.status_code == 200:
                history_data = history_response.json()
                st.write("**Recent Sessions:**")
                for i, session in enumerate(history_data.get("history", [])[-3:], 1):
                    with st.expander(f"Session {i}"):
                        st.write(f"**Query:** {session.get('user_message', '')[:100]}...")
                        st.write(f"**Time:** {session.get('timestamp', '')}")
        except:
            st.error("Could not load history")

# Crisis Resources Warning
st.markdown("""
<div class="crisis-warning">
    <h4>Crisis Resources</h4>
    <p><strong>National Suicide Prevention Lifeline:</strong> 988</p>
    <p><strong>Crisis Text Line:</strong> Text HOME to 741741</p>
    <p><strong>Emergency:</strong> 911</p>
</div>
""", unsafe_allow_html=True)

# Main interface
st.header("Share Your Psychological Concerns")

# Information about the service
with st.expander("How PsychoHealer Works"):
    st.write("""
    **PsychoHealer** is an AI-powered psychology assistant that provides structured mental health support:
    
    - **Specialized Focus**: Only handles psychology and mental health topics
    - **Intelligent Model Selection**: Automatically chooses the best AI model based on your query type
    - **Structured Analysis**: Provides severity assessment and step-by-step treatment plans
    - **Therapeutic Videos**: Recommends relevant YouTube videos for each treatment phase
    - **Session Memory**: Remembers your progress across multiple conversations
    - **Safety First**: Includes crisis detection and professional referral protocols
    
    **Query Types & Model Selection:**
    - Crisis situations → Most reliable model (Llama)
    - Complex conditions → Advanced analysis model (DeepSeek)
    - Relationship issues → Social dynamics model (Mistral)
    - General anxiety/depression → Rotating selection for variety
    """)

# Chat input
user_input = st.text_area(
    "Describe your psychological concern, feelings, or mental health challenge:",
    height=150,
    placeholder="Share what you're experiencing... For example: 'I've been feeling anxious about work lately and it's affecting my sleep' or 'I'm having trouble communicating with my partner and we keep arguing'"
)

# Submit button
if st.button("🔍 Get Psychology Support", type="primary"):
    if user_input.strip():
        with st.spinner("Analyzing your concern and selecting optimal AI model..."):
            try:
                # Make API request
                response = requests.post(
                    f"{API_BASE_URL}/psychology/chat",
                    json={
                        "query": user_input,
                        "user_id": st.session_state.user_id
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "query": user_input,
                        "response": data,
                    })
                    
                    # Display model selection info
                    st.markdown(f"""
                    <div class="model-info">
                        <strong>AI Model Selected:</strong> {data.get('model_used', 'Unknown').upper()}<br>
                        <strong>Selection Reason:</strong> {data.get('model_selection_reason', 'Automatic selection')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display response
                    st.markdown(f"""
                    <div class="response-container">
                        <h3>Your Psychology Support Plan</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Main response
                    st.markdown(data["response"])
                    
                    # YouTube videos
                    if data.get("youtube_videos"):
                        st.subheader("Recommended Therapeutic Videos")
                        
                        # Display videos in columns
                        cols = st.columns(2)
                        for i, video in enumerate(data["youtube_videos"]):
                            with cols[i % 2]:
                                st.markdown(f"""
                                <div class="video-card">
                                    <h4>{video.get('title', 'No title')}</h4>
                                    <p><strong>Channel:</strong> {video.get('channel', 'Unknown')}</p>
                                    <a href="{video.get('url', '#')}" target="_blank">
                                        <button style="background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                                             Watch Video
                                        </button>
                                    </a>
                                </div>
                                """, unsafe_allow_html=True)
                    
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
                st.info("Please make sure the backend server is running on http://localhost:8000")
    else:
        st.warning("Please enter your psychological concern to get support.")

# Display chat history
if st.session_state.chat_history:
    st.header("Current Session History")
    
    for i, chat in enumerate(reversed(st.session_state.chat_history[-3:]), 1):
        with st.expander(f"Conversation {len(st.session_state.chat_history) - i + 1} - {chat['timestamp']}"):
            st.write(f"**Your Query:** {chat['query']}")
            st.write(f"**Model Used:** {chat['response'].get('model_used', 'Unknown').upper()}")
            st.write("**Response:**")
            st.write(chat['response']['response'][:500] + "..." if len(chat['response']['response']) > 500 else chat['response']['response'])

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>PsychoHealer</strong> - AI-Powered Psychology Assistant</p>
    <p>Remember: This is AI-generated support. For serious mental health concerns, please consult a licensed professional.</p>
</div>
""", unsafe_allow_html=True)