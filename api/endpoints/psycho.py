# api/endpoints/psycho.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from api.models.psycho_schema import PsychologyRequest, PsychologyResponse, ChatHistoryRequest
from services.psycho_services import PsychologyService
from services.chat_services import memory_service
import asyncio

router = APIRouter()

# Initialize service once
psychology_service = PsychologyService()

@router.post("/psychology/chat", response_model=PsychologyResponse)
async def psychology_chat(request: PsychologyRequest):
    """Optimized psychology chat endpoint with async processing"""
    try:
        # Use the async method for better performance
        result = await psychology_service.get_psychology_response_async(
            query=request.query,
            user_id=request.user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/psychology/history")
async def get_chat_history(request: ChatHistoryRequest):
    """Get chat history - async for consistency"""
    try:
        loop = asyncio.get_event_loop()
        limit = request.limit if request.limit is not None else 10
        history = await loop.run_in_executor(
            None,
            memory_service.get_conversation_history,
            request.user_id,
            limit
        )
        return {"history": history, "user_id": request.user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@router.get("/psychology/status")
async def get_system_status():
    """Fast system status check"""
    available_models = []
    
    if psychology_service.groq_client:
        available_models.extend(["llama", "deepseek"])
    if psychology_service.openai_client:
        available_models.append("openai")
    
    return {
        "status": "online",
        "available_models": available_models,
        "auto_selection": "enabled",
        "response_optimization": "active"
    }

