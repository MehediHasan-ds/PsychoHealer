# services/youtube_services.py
from googleapiclient.discovery import build
import aiohttp
import asyncio
from functools import lru_cache
from core.config import Config
from typing import List, Dict

# Cache for YouTube API client
_youtube_client = None

def get_youtube_client():
    """Singleton YouTube client to avoid repeated initialization"""
    global _youtube_client
    if _youtube_client is None:
        config = Config()
        if config.YOUTUBE_API_KEY:
            _youtube_client = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY, cache_discovery=False)
    return _youtube_client

@lru_cache(maxsize=100)
def get_youtube_recommendations(search_query: str, max_results: int = 4) -> List[Dict]:
    """Cached YouTube video recommendations - reduced results for speed"""
    client = get_youtube_client()
    
    if not client:
        return []
    
    try:
        search_response = client.search().list(
            q=search_query,
            part='snippet',
            type='video',
            maxResults=max_results,  # Reduced from 5 to 4
            relevanceLanguage='en',
            safeSearch='strict',
            order='relevance',
            fields='items(id/videoId,snippet(title,description,channelTitle))'  # Only get needed fields
        ).execute()

        recommendations = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            description = item['snippet']['description'][:100] + "..." if len(item['snippet']['description']) > 100 else item['snippet']['description']
            
            recommendations.append({
                'title': title,
                'video_id': video_id,
                'url': f"https://youtu.be/{video_id}",
                'description': description,
                'channel': item['snippet']['channelTitle']
            })
        
        return recommendations
        
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return []

async def get_youtube_recommendations_async(search_query: str, max_results: int = 4) -> List[Dict]:
    """Async wrapper for YouTube recommendations"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_youtube_recommendations, search_query, max_results)

