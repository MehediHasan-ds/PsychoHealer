# api/endpoints/psycho.py
from fastapi import APIRouter, HTTPException
from api.models.psycho_schema import PsychologyRequest, PsychologyResponse, ChatHistoryRequest
from services.psycho_services import PsychologyService
from services.chat_services import memory_service

router = APIRouter()
psychology_service = PsychologyService()

@router.post("/psychology/chat", response_model=PsychologyResponse)
async def psychology_chat(request: PsychologyRequest):
    """Main endpoint for psychology chatbot with automatic model selection"""
    try:
        # Check if query is psychology-related (basic filter)
        psychology_keywords = [
            'anxiety', 'depression', 'stress', 'mental', 'psychological', 'therapy', 
            'counseling', 'emotion', 'feeling', 'mood', 'behavior', 'trauma', 'fear',
            'panic', 'phobia', 'addiction', 'relationship', 'family', 'grief', 'loss',
            'self-esteem', 'confidence', 'anger', 'communication', 'mindfulness', 'help',
            'support', 'problem', 'issue', 'concern', 'struggle', 'difficult', 'hard'
        ]
        
        query_lower = request.query.lower()
        is_psychology_related = any(keyword in query_lower for keyword in psychology_keywords)
        
        if not is_psychology_related and len(request.query.split()) > 3:
            # For longer queries, add a filter response
            filter_response = """
I'm PsychoHealer, a specialized psychology assistant. I only provide support for psychological and mental health concerns.

If you're experiencing psychological distress, anxiety, depression, relationship issues, stress, or any mental health challenges, I'm here to help with structured guidance and therapeutic approaches.

Please share your psychological concern, and I'll provide you with a comprehensive analysis and step-by-step treatment plan.

**If this is a mental health emergency, please contact:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911
"""
            return PsychologyResponse(
                response=filter_response,
                youtube_videos=[],
                model_used="filter",
                model_selection_reason="Non-psychology query filtered",
                user_id=request.user_id
            )
        
        result = psychology_service.get_psychology_response(
            request.query, 
            request.user_id
        )
        
        return PsychologyResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/psychology/history")
async def get_chat_history(request: ChatHistoryRequest):
    """Get user's chat history"""
    try:
        history = memory_service.get_conversation_history(request.user_id, request.limit)
        return {"history": history, "user_id": request.user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/psychology/status")
async def get_system_status():
    """Get system status and available models"""
    from core.config import Config
    config = Config()
    return {
        "status": "active", 
        "available_models": list(config.MODELS.keys()), 
        "default_model": config.DEFAULT_MODEL,
        "auto_selection": True
    }
