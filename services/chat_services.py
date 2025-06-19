# services/chat_services.py
import json
from datetime import datetime
from typing import Dict, List, Optional

class ChatMemoryService:
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
        self.user_profiles: Dict[str, Dict] = {}
    
    def add_message(self, user_id: str, message: str, response: str, session_data: Optional[Dict] = None):
        """Add a conversation message to memory"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
            self.user_profiles[user_id] = {
                "first_session": datetime.now().isoformat(),
                "total_sessions": 0,
                "current_issues": [],
                "progress_notes": []
            }
        
        self.conversations[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "bot_response": response,
            "session_data": session_data or {}
        })
        
        self.user_profiles[user_id]["total_sessions"] += 1
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        if user_id not in self.conversations:
            return []
        return self.conversations[user_id][-limit:]
    
    def get_context_summary(self, user_id: str) -> str:
        """Generate context summary for the AI"""
        if user_id not in self.conversations:
            return "New user - no previous history."
        
        history = self.conversations[user_id]
        profile = self.user_profiles[user_id]
        
        context = f"""
        PATIENT CONTEXT:
        - Total sessions: {profile['total_sessions']}
        - First session: {profile['first_session']}
        - Current issues: {', '.join(profile.get('current_issues', ['None documented']))}

        RECENT CONVERSATION SUMMARY:
        """
                
        # Add last 3 conversations
        recent = history[-3:] if len(history) >= 3 else history
        for i, conv in enumerate(recent, 1):
            context += f"\nSession {i}: User discussed - {conv['user_message'][:100]}..."
        
        return context
    
    def update_user_profile(self, user_id: str, issues: List[str], notes: List[str]):
        """Update user profile with current issues and progress notes"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id]["current_issues"] = issues
            self.user_profiles[user_id]["progress_notes"].extend(notes)

# Initialize global memory service
memory_service = ChatMemoryService()