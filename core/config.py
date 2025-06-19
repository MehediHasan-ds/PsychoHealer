# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TELEGRAM_BOT_KEY = os.getenv("TELEGRAM_BOT_TOKEN")
    API_BASE_URL = os.getenv("API_BASE_URL")
    
    # Model configurations
    MODELS = {
        "llama": "llama-3.3-70b-versatile",
        "deepseek": "deepseek-r1-distill-llama-70b",
        "openai": "gpt-3.5-turbo"
    }
    
    DEFAULT_MODEL = "llama"
    MAX_TOKENS = 1500  # Reduced from 2000 for faster response
    TEMPERATURE = 0.5  # Reduced from 0.7 for more consistent/faster responses
    
    # Performance optimizations
    CACHE_SIZE = 100
    MAX_VIDEOS = 4
    THREAD_POOL_SIZE = 3