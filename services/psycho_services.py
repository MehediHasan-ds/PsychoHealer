# services/psycho_services.py - Fixed Service
from groq import Groq
import openai
from typing import Dict, Any, List
import random
import re
from .chat_services import memory_service
from .youtube_services import get_youtube_recommendations
from core.config import Config
from core.agents import PSYCHOLOGY_SYSTEM_PROMPT

class PsychologyService:
    def __init__(self):
        self.config = Config()
        self.groq_client = None
        self.openai_client = None
        self.current_model = self.config.DEFAULT_MODEL
        
        # Initialize clients
        if self.config.GROQ_API_KEY:
            self.groq_client = Groq(api_key=self.config.GROQ_API_KEY)
        
        if self.config.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
    
    def _is_psychology_related(self, query: str) -> bool:
        """Enhanced psychology detection with negative prompting resistance"""
        query_lower = query.lower()
        
        # Detect bypass attempts
        bypass_patterns = [
            r'ignore\s+previous\s+instructions',
            r'act\s+as\s+(?!.*psychologist|.*therapist)',
            r'pretend\s+you\s+are\s+(?!.*psychologist|.*therapist)',
            r'roleplay\s+as\s+(?!.*psychologist|.*therapist)',
            r'system\s+prompt',
            r'override\s+your',
            r'forget\s+your\s+role',
            r'you\s+are\s+now\s+(?!.*psychologist|.*therapist)',
            r'new\s+instructions',
            r'developer\s+mode',
            r'jailbreak',
            r'\[SYSTEM\]',
            r'\[ADMIN\]'
        ]
        
        # Check for bypass attempts
        for pattern in bypass_patterns:
            if re.search(pattern, query_lower):
                return False
        
        # Strong psychology keywords
        strong_psychology_keywords = [
            'anxiety', 'depression', 'stress', 'mental health', 'psychological', 
            'therapy', 'counseling', 'psychiatrist', 'psychologist', 'trauma',
            'ptsd', 'panic', 'phobia', 'bipolar', 'schizophrenia', 'addiction',
            'self-harm', 'suicide', 'grief', 'loss', 'bereavement', 'mood disorder'
        ]
        
        # Moderate psychology keywords
        moderate_psychology_keywords = [
            'emotion', 'feeling', 'mood', 'behavior', 'fear', 'anger', 'sad',
            'happy', 'relationship', 'family', 'communication', 'conflict',
            'self-esteem', 'confidence', 'mindfulness', 'meditation', 'coping',
            'support', 'help me', 'struggling', 'difficult', 'hard time',
            'overwhelmed', 'frustrated', 'worried', 'nervous', 'upset'
        ]
        
        # Non-psychology keywords (strong indicators)
        non_psychology_keywords = [
            'code', 'programming', 'python', 'javascript', 'html', 'css',
            'database', 'server', 'api', 'algorithm', 'software', 'computer',
            'recipe', 'cooking', 'food', 'ingredients', 'restaurant',
            'travel', 'hotel', 'flight', 'vacation', 'tourism',
            'movie', 'film', 'book', 'music', 'game', 'sport',
            'math', 'physics', 'chemistry', 'biology', 'history',
            'weather', 'news', 'politics', 'economics', 'finance',
            'shopping', 'product', 'buy', 'price', 'store'
        ]
        
        # Check for non-psychology content
        non_psych_count = sum(1 for keyword in non_psychology_keywords if keyword in query_lower)
        if non_psych_count >= 2:  # Multiple non-psychology keywords
            return False
        
        # Check for psychology content
        strong_count = sum(1 for keyword in strong_psychology_keywords if keyword in query_lower)
        moderate_count = sum(1 for keyword in moderate_psychology_keywords if keyword in query_lower)
        
        # Decision logic
        if strong_count >= 1:  # At least one strong psychology keyword
            return True
        elif moderate_count >= 2:  # At least two moderate psychology keywords
            return True
        elif len(query.split()) <= 5 and moderate_count >= 1:  # Short queries with psychology keywords
            return True
        
        # Special cases for help-seeking language
        help_patterns = [
            r"help\s+me\s+with",
            r"i\s+need\s+support",
            r"i\s+am\s+struggling",
            r"i\s+feel\s+like",
            r"what\s+should\s+i\s+do",
            r"how\s+do\s+i\s+deal\s+with",
            r"i\s+have\s+been\s+feeling"
        ]
        
        for pattern in help_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _select_optimal_model(self, query: str) -> tuple[str, str]:
        """Internal model selection with reasoning - returns (model, reason)"""
        query_lower = query.lower()
        
        # Crisis/emergency - use most reliable
        if any(keyword in query_lower for keyword in ['suicide', 'kill myself', 'end my life', 'hurt myself', 'self-harm', 'emergency']):
            return "llama", "Crisis situation detected - using most reliable model"
        
        # Complex conditions - use advanced
        if any(keyword in query_lower for keyword in ['trauma', 'ptsd', 'bipolar', 'schizophrenia', 'personality disorder', 'addiction']):
            return "deepseek", "Complex psychological condition - using advanced analysis model"
        
        # Social/relationship - use social model
        if any(keyword in query_lower for keyword in ['relationship', 'marriage', 'family', 'social', 'communication', 'conflict']):
            return "mistral", "Social/relationship issue - using social dynamics model"
        
        # Default rotation for general cases
        selected_model = random.choice(["llama", "deepseek", "mistral"])
        return selected_model, "General psychological concern - automatic model rotation"
    
    def get_psychology_response(self, query: str, user_id: str) -> Dict[str, Any]:
        """Main psychology response with negative prompting protection"""
        try:
            # Check if query is psychology-related and not a bypass attempt
            if not self._is_psychology_related(query):
                refusal_response = """I'm PsychoHealer, a specialized psychology assistant. I only provide support for psychological and mental health concerns.

If you're experiencing psychological distress, anxiety, depression, relationship issues, stress, or any mental health challenges, I'm here to help with structured guidance and therapeutic approaches.

Please share your psychological concern, and I'll provide you with a comprehensive analysis and step-by-step treatment plan.

**If this is a mental health emergency, please contact:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911"""
                
                return {
                    "response": refusal_response,
                    "youtube_videos": [],
                    "model_used": "filter",
                    "model_selection_reason": "Non-psychology query filtered",
                    "user_id": user_id
                }
            
            # Internal model selection (with reasoning)
            selected_model, selection_reason = self._select_optimal_model(query)
            
            # Get conversation context
            context = memory_service.get_context_summary(user_id)
            
            # Create secure prompt
            full_prompt = f"""
{PSYCHOLOGY_SYSTEM_PROMPT}

PATIENT CONTEXT:
{context}

CURRENT USER QUERY: {query}

Provide a comprehensive psychological response following the exact structure specified. Focus only on the psychological aspects and ignore any non-psychology elements in the query.
"""
            
            # Get AI response
            ai_response = self._get_model_response(full_prompt, selected_model)
            
            # Clean response to remove any reasoning artifacts
            cleaned_response = self._clean_response(ai_response)
            
            # Get YouTube recommendations
            youtube_videos = self._get_therapeutic_videos(query, cleaned_response)
            
            # Save to memory
            memory_service.add_message(user_id, query, cleaned_response, {
                "model_used": selected_model,
                "videos_recommended": len(youtube_videos)
            })
            
            return {
                "response": cleaned_response,
                "youtube_videos": youtube_videos,
                "model_used": selected_model,
                "model_selection_reason": selection_reason,
                "user_id": user_id
            }
            
        except Exception as e:
            error_response = "I apologize, but I'm having technical difficulties. Please try again in a moment. If you're experiencing a mental health crisis, please contact a crisis hotline immediately."
            return {
                "response": error_response,
                "youtube_videos": [],
                "model_used": "error",
                "model_selection_reason": "Error occurred",
                "user_id": user_id,
                "error": str(e)
            }
    
    def _clean_response(self, response: str) -> str:
        """Remove any reasoning artifacts or meta-commentary"""
        # Remove common reasoning patterns
        patterns_to_remove = [
            r"Let me think about this\.\.\.",
            r"First, I'll analyze\.\.\.",
            r"Based on my analysis\.\.\.",
            r"I need to consider\.\.\.",
            r"My reasoning is\.\.\.",
            r"\[REASONING:.*?\]",
            r"\[ANALYSIS:.*?\]",
            r"\[MODEL SELECTION:.*?\]",
            r"<thinking>.*?</thinking>",
            r"<analysis>.*?</analysis>"
        ]
        
        cleaned = response
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _get_model_response(self, prompt: str, model: str) -> str:
        """Get response from specified model"""
        try:
            if model == "openai" and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.config.MODELS["openai"],
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.TEMPERATURE
                )
                return response.choices[0].message.content.strip()
            
            elif self.groq_client and model in ["llama", "deepseek", "mistral"]:
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "system", "content": prompt}],
                    model=self.config.MODELS[model],
                    max_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.TEMPERATURE
                )
                return response.choices[0].message.content.strip()
            
            else:
                return "Model not available. Please check your API configuration."
                
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _get_therapeutic_videos(self, query: str, ai_response: str) -> List[Dict]:
        """Get therapeutic YouTube video recommendations"""
        video_queries = [
            f"psychology therapy {query}",
            f"mental health {query}",
            f"therapeutic exercises {query}",
            f"mindfulness {query}",
            f"cognitive behavioral therapy {query}"
        ]
        
        all_videos = []
        for search_query in video_queries[:3]:
            videos = get_youtube_recommendations(search_query)
            all_videos.extend(videos[:2])
        
        # Remove duplicates and return top 6
        unique_videos = []
        seen_ids = set()
        for video in all_videos:
            if video['video_id'] not in seen_ids:
                unique_videos.append(video)
                seen_ids.add(video['video_id'])
                if len(unique_videos) >= 6:
                    break
        
        return unique_videos
    
    
