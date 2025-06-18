# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Model configurations
    MODELS = {
        "llama": "llama-3.3-70b-versatile",
        "deepseek": "deepseek-r1-distill-llama-70b",
        "mistral": "mistral-saba-24b",
        "openai": "gpt-3.5-turbo"
    }
    
    DEFAULT_MODEL = "llama"
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7