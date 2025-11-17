"""
Senda API - FastAPI orchestrator
Integrates Telnyx, Phorest, and Gemini
"""

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.webhooks import router as webhook_router
from src.services.conversation import conversation_service

app = FastAPI(
    title="Senda API",
    description="Conversational AI Platform API",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook_router, tags=["webhooks"])


@app.get("/")
async def root() -> dict:
    """Root endpoint"""
    active_calls = len(conversation_service.conversations)
    return {
        "message": "Senda API - Conversational AI Platform",
        "active_calls": active_calls,
        "status": "online",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/status")
async def status() -> dict:
    """Get API status and active conversations"""
    return {
        "status": "online",
        "active_calls": len(conversation_service.conversations),
        "conversations": list(conversation_service.conversations.keys()),
    }
