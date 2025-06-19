# frontend.py - Optimized version
import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import asyncio
import aiohttp

# Page configuration
st.set_page_config(
    page_title="PsychoHealer - AI Psychology Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlined CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .response-container {
        background: #f8f9ff;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .video-card {
        background: white;
        padding: 0.8rem;
        border-radius: 6px;
        border: 1px solid #e1e5e9;
        margin: 0.4rem 0;
    }
    .model-info {
        background: #e8f4f8;
        padding: 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        color: #0c5460;
        margin: 0.4rem 0;
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

# Cached functions for better performance
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_system_status():
    """Cached system status check"""
    try:
        response = requests.get(f"{API_BASE_URL}/psychology/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# Header
st.markdown("""
<div class="main-header">
    <h1>PsychoHealer</h1>
    <p>AI-Powered Psychology Assistant</p>
</div>
""", unsafe_allow_html=True)

# Streamlined sidebar
with st.sidebar:
    st.header("System Info")
    
    # User ID display
    st.info(f"**User:** `{st.session_state.user_id[:8]}...`")
    
    # System status (cached)
    status_data = get_system_status()
    if status_data:
        st.success("System Online")
        st.write(f"**Models:** {len(status_data.get('available_models', []))}")
    else:
        st.error("System Offline")
    
    # Quick session management
    if st.button("New Session"):
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()

# Main interface
st.header("Share Your Concerns")

# Optimized input
user_input = st.text_area(
    "Describe your psychological concern:",
    height=120,
    placeholder="Example: 'I've been feeling anxious about work and it's affecting my sleep...'"
)

# Submit with progress bar
if st.button("🔍 Get Support", type="primary"):
    if user_input.strip():
        # Show progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Selecting optimal AI model...")
            progress_bar.progress(20)
            
            status_text.text("Analyzing your concern...")
            progress_bar.progress(40)
            
            # Make API request with timeout
            response = requests.post(
                f"{API_BASE_URL}/psychology/chat",
                json={
                    "query": user_input,
                    "user_id": st.session_state.user_id
                },
                timeout=30  # 30 second timeout
            )
            
            progress_bar.progress(80)
            status_text.text("Preparing response...")
            
            if response.status_code == 200:
                data = response.json()
                
                progress_bar.progress(100)
                status_text.text("Complete!")
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "query": user_input,
                    "response": data,
                })
                
                # Display model info (compact)
                st.markdown(f"""
                <div class="model-info">
                    <strong>AI Model:</strong> {data.get('model_used', 'Unknown').upper()} | 
                    <strong>Reason:</strong> {data.get('model_selection_reason', 'Auto-selected')}
                </div>
                """, unsafe_allow_html=True)
                
                # Main response
                st.markdown(f"""
                <div class="response-container">
                    <h3>Your Psychology Support Plan</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Response content
                st.markdown(data["response"])
                
                # YouTube videos (compact display)
                if data.get("youtube_videos"):
                    st.subheader("Recommended Videos")
                    
                    cols = st.columns(2)
                    for i, video in enumerate(data["youtube_videos"][:4]):  # Limit to 4 videos
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div class="video-card">
                                <h4 style="font-size: 0.9rem; margin-bottom: 0.3rem;">{video.get('title', 'No title')[:60]}...</h4>
                                <p style="font-size: 0.8rem; margin-bottom: 0.5rem;"><strong>By:</strong> {video.get('channel', 'Unknown')}</p>
                                <a href="{video.get('url', '#')}" target="_blank">
                                    <button style="background: #667eea; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">
                                        ▶ Watch
                                    </button>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                
            else:
                st.error(f"Error: {response.status_code}")
                progress_bar.empty()
                status_text.empty()
                
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            progress_bar.empty()
            status_text.empty()
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            progress_bar.empty()
            status_text.empty()
    else:
        st.warning("Please enter your concern to get support.")

# Compact chat history
if st.session_state.chat_history:
    st.header("Recent History")
    
    for i, chat in enumerate(reversed(st.session_state.chat_history[-2:]), 1):  # Show only last 2
        with st.expander(f"Session {len(st.session_state.chat_history) - i + 1} - {chat['timestamp']}"):
            st.write(f"**Query:** {chat['query'][:100]}...")
            st.write(f"**Model:** {chat['response'].get('model_used', 'Unknown').upper()}")
            response_preview = chat['response']['response'][:300]
            st.write(f"**Response:** {response_preview}..." if len(chat['response']['response']) > 300 else response_preview)

# Compact crisis resources
st.markdown("""
<div style="background: #fff3cd; padding: 0.8rem; border-radius: 6px; border-left: 3px solid #ffc107; margin: 1rem 0;">
    <h4 style="margin-bottom: 0.5rem;"> Crisis Resources</h4>
    <p style="margin: 0.2rem 0;"><strong>National Suicide Prevention:</strong> +88 09612 119911</p>
    <p style="margin: 0.2rem 0;"><strong>Emergency:</strong> 999</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 0.5rem;">
    <p><strong>PsychoHealer</strong> - Optimized for Fast AI Psychology Support</p>
</div>
""", unsafe_allow_html=True)