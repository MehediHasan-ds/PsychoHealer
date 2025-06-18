# services/youtube_services.py (Updated)
from googleapiclient.discovery import build
from core.config import Config
from typing import List, Dict

def get_youtube_recommendations(search_query: str) -> List[Dict]:
    """Get YouTube video recommendations for therapeutic content"""
    config = Config()
    
    if not config.YOUTUBE_API_KEY:
        return []
    
    try:
        youtube = build('youtube', 'v3', developerKey=config.YOUTUBE_API_KEY)
        
        search_response = youtube.search().list(
            q=search_query,
            part='snippet',
            type='video',
            maxResults=5,
            relevanceLanguage='en',
            safeSearch='strict',  # Ensure safe content
            order='relevance'
        ).execute()

        recommendations = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            description = item['snippet']['description'][:200] + "..." if len(item['snippet']['description']) > 200 else item['snippet']['description']
            
            if len(video_id) == 11:
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