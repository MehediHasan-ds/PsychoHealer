# IT Chat/Agent Webapp

A FastAPI-based RAG chatbot for Psycho people to help them heal with support for multiple LLMs (OpenAI, Grok, LLaMA, DeepSeek).

## Features



## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file with your API keys:

```bash
OPENAI_API_KEY=your_openai_key_here
GROK_API_KEY=your_grok_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

### 3. Directory Structure

Ensure your directory structure matches:

```
PsychoHealer/
├── api/
│   ├── endpoints/
│   │   ├── __init__.py
│   │   ├── chatbot.py
│   │   └── psycho.py
│   └── models/
│       ├── __init__.py
│       ├── chatbot_schema.py
│       └── psycho_schema.py
├── core/
│   ├── __init__.py
│   ├── agents.py
│   ├── config.py
│   └── tasks.py
├── services/
│   ├── __init__.py
│   ├── chat_services.py
│   └── psycho_services.py
├── __init__.py
└── main.py
```

### 4. Run the Application

```bash
python main.py
```

Or using uvicorn:

```bash
uvicorn main:app --reload
```

## API Usage

### Chat Endpoint

**POST** `/api/chat`

```json

```

**Response:**
```json

```

### psycho Endpoints



## Testing Multiple LLMs

### Change Model Configuration

Edit `app/core/config.py`:


```python
class Settings:
    CURRENT_MODEL = "deepseek"  # Change to: "grok", "llama", "deepseek"
```
and `.env`:
```python
  CURRENT_MODEL = "deepseek"
  OPENAI_API_KEY = "you-openai-key"
  GROQ_API_KEY = "your-groq-api-key"
```

### Test Sequence

1. Set `CURRENT_MODEL = "openai"` → Test with OpenAI
2. Set `CURRENT_MODEL = "deepseek"` → Test with DeepSeek
3. Set `CURRENT_MODEL = "llama"` → Test with LLaMA (requires local setup

## Architecture

### Unified Task-Based Agents


### Memory Optimization

- On-demand embedding generation
- Disk-based FAISS storage
- Streaming JSON parsing with ijson
- No persistent memory loading

## Swagger Documentation

Access interactive API docs at: `http://localhost:8000/docs`

## Production Deployment

1. Set environment variables for API keys
2. Configure rate limiting and authentication
3. Use production ASGI server (e.g., Gunicorn + Uvicorn)
4. Set up monitoring and logging

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure environment variables are set
2. **FAISS Indices**: Indices are created automatically on first query
3. **Role Not Found**: Check available roles with `/api/roles`
4. **Memory Issues**: Embeddings are generated on-demand to minimize memory

### Logs

Check console output for:
- API call errors
- Validation failures

## Example Queries

