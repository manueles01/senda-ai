"""
Dialogflow CX webhook endpoints.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.dialogflow import (
    DialogflowWebhookRequest,
    DialogflowWebhookResponse,
    create_text_response,
    create_response_with_params,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dialogflow", tags=["Dialogflow CX"])


async def verify_webhook_secret(x_webhook_secret: str = Header(None)) -> bool:
    """Verify the webhook secret if configured."""
    if settings.dialogflow_webhook_secret:
        if not x_webhook_secret or x_webhook_secret != settings.dialogflow_webhook_secret:
            raise HTTPException(status_code=401, detail="Invalid webhook secret")
    return True


@router.post("/webhook")
async def dialogflow_webhook(
    request: DialogflowWebhookRequest,
    verified: bool = None  # Dependency injection for verification
) -> DialogflowWebhookResponse:
    """
    Main webhook endpoint for Dialogflow CX.

    This endpoint receives webhook requests from Dialogflow CX and processes them
    based on the intent and parameters.
    """
    logger.info(f"Received Dialogflow webhook request: {request.dict()}")

    try:
        # Extract intent information
        intent_name = ""
        if request.intentInfo:
            intent_name = request.intentInfo.get("displayName", "")

        # Extract session parameters
        session_params = {}
        if request.sessionInfo and request.sessionInfo.parameters:
            session_params = request.sessionInfo.parameters

        # Route to appropriate handler based on intent
        if intent_name == "book.appointment":
            return await handle_book_appointment(request, session_params)
        elif intent_name == "check.availability":
            return await handle_check_availability(request, session_params)
        elif intent_name == "get.business.hours":
            return await handle_get_business_hours(request, session_params)
        elif intent_name == "cancel.appointment":
            return await handle_cancel_appointment(request, session_params)
        else:
            # Default handler for unrecognized intents
            return await handle_default(request, session_params)

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return create_text_response(
            "I'm sorry, I encountered an error processing your request. Please try again."
        )


async def handle_book_appointment(
    request: DialogflowWebhookRequest,
    session_params: Dict[str, Any]
) -> DialogflowWebhookResponse:
    """Handle appointment booking intent."""
    # TODO: Integrate with Phorest API to book appointment
    # For now, return a placeholder response

    service = session_params.get("service", "service")
    date = session_params.get("date", "")
    time = session_params.get("time", "")

    response_text = (
        f"I'll help you book a {service} appointment for {date} at {time}. "
        f"Let me check availability with Phorest."
    )

    return create_text_response(response_text)


async def handle_check_availability(
    request: DialogflowWebhookRequest,
    session_params: Dict[str, Any]
) -> DialogflowWebhookResponse:
    """Handle availability checking intent."""
    # TODO: Integrate with Phorest API to check availability

    date = session_params.get("date", "")

    response_text = (
        f"Let me check our availability for {date}. "
        f"I'll query our booking system."
    )

    return create_text_response(response_text)


async def handle_get_business_hours(
    request: DialogflowWebhookRequest,
    session_params: Dict[str, Any]
) -> DialogflowWebhookResponse:
    """Handle business hours inquiry."""
    # TODO: Get from Phorest or configuration

    response_text = (
        "Our business hours are Monday through Friday, 9 AM to 6 PM, "
        "and Saturday 10 AM to 4 PM. We're closed on Sundays."
    )

    return create_text_response(response_text)


async def handle_cancel_appointment(
    request: DialogflowWebhookRequest,
    session_params: Dict[str, Any]
) -> DialogflowWebhookResponse:
    """Handle appointment cancellation."""
    # TODO: Integrate with Phorest API to cancel appointment

    appointment_id = session_params.get("appointment_id", "")

    response_text = (
        "I'll help you cancel your appointment. "
        "Can you please confirm your phone number or email?"
    )

    return create_text_response(response_text)


async def handle_default(
    request: DialogflowWebhookRequest,
    session_params: Dict[str, Any]
) -> DialogflowWebhookResponse:
    """Default handler for unrecognized intents."""

    response_text = (
        "I can help you with booking appointments, checking availability, "
        "or answering questions about our services. What would you like to do?"
    )

    return create_text_response(response_text)


@router.get("/health")
async def dialogflow_health():
    """Health check endpoint for Dialogflow webhook."""
    return {
        "status": "healthy",
        "service": "dialogflow-webhook",
        "configured": bool(settings.dialogflow_agent_id)
    }
