"""Main FastAPI application for Senda AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import telnyx, dialogflow

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered salon receptionist with Dialogflow CX and Telnyx integration",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(telnyx.router, prefix="/webhooks/telnyx", tags=["telnyx"])
app.include_router(dialogflow.router, prefix="/webhooks/dialogflow", tags=["dialogflow"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "google_project": settings.GOOGLE_PROJECT_ID,
        "dialogflow_configured": bool(settings.DIALOGFLOW_AGENT_ID),
        "telnyx_configured": bool(settings.TELEPHONY_TELNYX_API_KEY),
    }
