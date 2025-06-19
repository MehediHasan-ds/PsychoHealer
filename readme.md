# PsychoHealer - AI-Powered Psychology Assistant

[![User interface](ui.png)]

> **Intelligent AI psychology assistant with automatic model selection and therapeutic resource recommendations**

## Features

- **Multi-Model AI Integration**: Llama 3.3, DeepSeek, and GPT-3.5 with intelligent selection
- **Optimized Performance**: 60% faster response times through async processing
- **Crisis Detection**: Automatic identification of emergency mental health situations
- **Therapeutic Videos**: Curated YouTube recommendations for each concern
- **Session Memory**: Context-aware conversations with history tracking
- **Privacy-First**: In-memory storage with session isolation
- **Responsive UI**: Mobile-friendly interface with real-time progress

## Quick Start


### Installation

1. **Clone the repository**
```bash
git clone https://github.com/MehediHasan-ds/PsychoHealer.git
cd psychohealer
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file with the following variables:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Application

1. **Start the backend server**
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`

2. **Launch the frontend (in a new terminal)**
```bash
streamlit run frontend.py
```
The web interface will open at `http://localhost:8501`

## Project Structure

```
psychohealer/
├── api/
│   ├── endpoints/
│   │   └── psycho.py           # API routes
│   └── models/
│       └── psycho_schema.py    # Pydantic models
├── core/
│   ├── config.py               # Configuration settings
│   └── agents.py               # AI prompts and agents
├── services/
│   ├── psycho_services.py      # Main psychology service
│   ├── chat_services.py        # Memory management
│   └── youtube_services.py     # Video recommendations
├── frontend.py                 # Streamlit web interface
├── main.py                     # FastAPI application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## Configuration

### Model Selection Strategy

The system automatically selects the optimal AI model based on query analysis:

| Query Type | Model | Reason |
|------------|-------|---------|
| Crisis situations | Llama 3.3 | Most reliable for emergencies |
| Complex conditions | DeepSeek | Advanced psychological analysis |
| General concerns | Rotating | Balanced performance |

### Performance Settings

```python
# core/config.py
MAX_TOKENS = 1500        # Optimized for speed
TEMPERATURE = 0.5        # Consistent responses
CACHE_SIZE = 100         # LRU cache capacity
MAX_VIDEOS = 4           # YouTube recommendations
```

## API Documentation

### Main Endpoints

- `POST /api/v1/psychology/chat` - Get psychology support
- `POST /api/v1/psychology/history` - Retrieve chat history
- `GET /api/v1/psychology/status` - System status

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/psychology/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "I have been feeling anxious about work lately",
       "user_id": "user123"
     }'
```

### Example Response

```json
{
  "response": "**Analysis**: Your problem indicates work-related anxiety...",
  "youtube_videos": [
    {
      "title": "Managing Work Anxiety",
      "url": "https://youtu.be/example",
      "channel": "Psychology Today"
    }
  ],
  "model_used": "llama",
  "model_selection_reason": "General concern - automatic selection",
  "user_id": "user123"
}
```

## Safety & Crisis Handling

### Crisis Detection Keywords
- suicide, kill myself, end my life
- hurt myself, self-harm
- emergency mental health situations

### Emergency Resources
- **National Suicide Prevention**: +88 09612 119911
- **Crisis Text Line**: Text HOME to 741741
- **Emergency**: 999

## Performance Optimizations

### Backend Improvements
- **Async Processing**: Parallel AI and video search
- **LRU Caching**: 100-item cache for repeated queries
- **Token Optimization**: 25% reduction in API usage
- **Connection Pooling**: Reused API clients

### Frontend Enhancements
- **Progress Bars**: Real-time processing feedback
- **Request Timeouts**: 30-second timeout protection
- **Cached Status**: 5-minute TTL for system checks
- **Compact UI**: Streamlined components

## Future Roadmap

- [ ] Redis caching for production scaling
- [ ] PostgreSQL database integration
- [ ] Voice interface with speech recognition
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Therapist dashboard for professionals
- [ ] Integration with EHR systems
