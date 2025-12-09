from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, vision, tourism, culture

app = FastAPI(
    title="Deep-Shiva API",
    description="Backend API for Uttarakhand Tourism Chatbot",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(vision.router, prefix="/api/v1/vision", tags=["Vision"])
app.include_router(tourism.router, prefix="/api/v1/tourism", tags=["Tourism"])
app.include_router(culture.router, prefix="/api/v1/culture", tags=["Culture"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Deep-Shiva API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
