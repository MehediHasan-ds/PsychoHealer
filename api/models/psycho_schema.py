# api/models/psycho_schema.py
from pydantic import BaseModel
from typing import List, Dict, Optional

class PsychologyRequest(BaseModel):
    query: str
    user_id: str

class PsychologyResponse(BaseModel):
    response: str
    youtube_videos: List[Dict]
    model_used: str
    model_selection_reason: str
    user_id: str

class ChatHistoryRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 10
