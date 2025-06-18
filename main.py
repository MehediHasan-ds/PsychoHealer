# main.py
from fastapi import FastAPI
from api.endpoints import psycho
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PsychoHealer API",
    description="AI-powered Psychology Assistant API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(psycho.router, prefix="/api/v1", tags=["Psychology"])

@app.get("/")
async def root():
    return {
        "message": "PsychoHealer API is running",
        "version": "1.0.0",
        "description": "AI-powered Psychology Assistant"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "PsychoHealer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
