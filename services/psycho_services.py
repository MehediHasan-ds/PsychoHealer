# services/psycho_services.py
from groq import Groq
import openai
from typing import Dict, Any, List
import random
import re
import asyncio
import concurrent.futures
from functools import lru_cache
from .chat_services import memory_service
from .youtube_services import get_youtube_recommendations_async
from core.config import Config
from core.agents import PSYCHOLOGY_SYSTEM_PROMPT

class PsychologyService:
    def __init__(self):
        self.config = Config()
        self.groq_client = None
        self.openai_client = None
        self.current_model = self.config.DEFAULT_MODEL
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

        # Initialize clients with connection pooling
        if self.config.GROQ_API_KEY:
            self.groq_client = Groq(api_key=self.config.GROQ_API_KEY)

        if self.config.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)

    @lru_cache(maxsize=100)
    def _classify_query_fast(self, query_hash: str, query_lower: str) -> tuple[str, str]:
        """Fast cached query classification"""
        # Crisis keywords - highest priority
        crisis_keywords = ['suicide', 'kill myself', 'end my life', 'hurt myself', 'self-harm', 'emergency']
        if any(k in query_lower for k in crisis_keywords):
            return "llama", "Crisis situation detected"
        
        # Complex condition keywords
        complex_keywords = ['trauma', 'ptsd', 'bipolar', 'schizophrenia', 'personality disorder', 'addiction']
        if any(k in query_lower for k in complex_keywords):
            return "deepseek", "Complex psychological condition"

        # Default rotation for general queries
        return random.choice(["llama", "deepseek"]), "General concern"

    def _select_optimal_model(self, query: str) -> tuple[str, str]:
        """Optimized model selection with caching"""
        query_lower = query.lower()
        query_hash = str(hash(query_lower))
        return self._classify_query_fast(query_hash, query_lower)

    async def get_psychology_response_async(self, query: str, user_id: str) -> Dict[str, Any]:
        """Async main psychology response with parallel processing"""
        try:
            # Start parallel tasks immediately
            selected_model, selection_reason = self._select_optimal_model(query)
            
            # Create tasks for parallel execution
            context_task = asyncio.create_task(self._get_context_async(user_id))
            
            # Get context (fast operation)
            context = await context_task
            
            # Prepare optimized prompt
            full_prompt = self._build_optimized_prompt(query, context)
            
            # Start AI response and video search in parallel
            ai_task = asyncio.create_task(self._get_model_response_async(full_prompt, selected_model))
            video_task = asyncio.create_task(self._get_therapeutic_videos_async(query))
            
            # Wait for both to complete
            ai_response, youtube_videos = await asyncio.gather(ai_task, video_task)
            
            # Quick response cleaning
            cleaned_response = self._clean_response_fast(ai_response)
            
            # Save to memory (non-blocking)
            asyncio.create_task(self._save_memory_async(user_id, query, cleaned_response, {
                "model_used": selected_model,
                "videos_recommended": len(youtube_videos)
            }))

            return {
                "response": cleaned_response,
                "youtube_videos": youtube_videos,
                "model_used": selected_model,
                "model_selection_reason": selection_reason,
                "user_id": user_id
            }

        except Exception as e:
            return self._error_response(user_id, str(e))

    def get_psychology_response(self, query: str, user_id: str) -> Dict[str, Any]:
        """Sync wrapper for backward compatibility"""
        return asyncio.run(self.get_psychology_response_async(query, user_id))

    def _build_optimized_prompt(self, query: str, context: str) -> str:
        """Build streamlined prompt - reduce token count"""
        return f"""{PSYCHOLOGY_SYSTEM_PROMPT}

CONTEXT: {context}
QUERY: {query}

Provide structured psychological response."""

    async def _get_context_async(self, user_id: str) -> str:
        """Async context retrieval - lightweight"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, memory_service.get_context_summary, user_id)

    @lru_cache(maxsize=50)
    def _clean_response_fast(self, response: str) -> str:
        """Optimized response cleaning with caching"""
        # Single regex pass for multiple patterns
        pattern = r'(Let me think.*?\n|First, I.*?\n|Based on my analysis.*?\n|I need to consider.*?\n|My reasoning is.*?\n|\[REASONING:.*?\]|\[MODEL SELECTION:.*?\]|<thinking>.*?</thinking>|<analysis>.*?</analysis>)'
        response = re.sub(pattern, '', response, flags=re.IGNORECASE | re.DOTALL)
        return re.sub(r'\n\s*\n', '\n\n', response.strip())

    async def _get_model_response_async(self, prompt: str, model: str) -> str:
        """Async model response with optimized parameters"""
        try:
            loop = asyncio.get_event_loop()
            
            if model == "openai" and self.openai_client:
                return await loop.run_in_executor(
                    self.executor,
                    self._call_openai,
                    prompt
                )
            elif self.groq_client and model in ["llama", "deepseek"]:
                return await loop.run_in_executor(
                    self.executor,
                    self._call_groq,
                    prompt,
                    model
                )
            else:
                return "Model not available."
        except Exception as e:
            return f"Error: {str(e)}"

    def _call_openai(self, prompt: str) -> str:
        """Optimized OpenAI call"""
        response = self.openai_client.chat.completions.create(
            model=self.config.MODELS["openai"],
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1500,  # Reduced for faster response
            temperature=0.5,  # Reduced for consistency
            stream=False
        )
        return response.choices[0].message.content.strip()

    def _call_groq(self, prompt: str, model: str) -> str:
        """Optimized Groq call"""
        response = self.groq_client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}],
            model=self.config.MODELS[model],
            max_tokens=1500,  # Reduced for faster response
            temperature=0.5,  # Reduced for consistency
        )
        return response.choices[0].message.content.strip()

    async def _get_therapeutic_videos_async(self, query: str) -> List[Dict]:
        """Async video search with reduced scope"""
        try:
            # Simplified video search - only one query for speed
            video_query = f"psychology therapy {query[:50]}"  # Limit query length
            videos = await get_youtube_recommendations_async(video_query, max_results=4)
            return videos[:4]  # Limit to 4 videos for faster response
        except Exception:
            return []

    async def _save_memory_async(self, user_id: str, query: str, response: str, metadata: Dict):
        """Async memory saving"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            memory_service.add_message,
            user_id, query, response, metadata
        )

    def _error_response(self, user_id: str, error: str) -> Dict[str, Any]:
        """Quick error response"""
        return {
            "response": "I apologize, but I'm having technical difficulties. Please try again in a moment. If you're experiencing a mental health crisis, please contact a crisis hotline immediately.",
            "youtube_videos": [],
            "model_used": "error",
            "model_selection_reason": "Error occurred",
            "user_id": user_id,
            "error": error
        }
    
    