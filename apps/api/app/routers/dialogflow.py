"""Dialogflow CX webhook handlers for conversation fulfillment."""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class DialogflowResponse:
    """Helper class to build Dialogflow CX webhook responses."""

    @staticmethod
    def create_text_response(text: str) -> Dict[str, Any]:
        """Create a simple text response."""
        return {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [text]
                        }
                    }
                ]
            }
        }

    @staticmethod
    def create_response_with_params(
        text: str,
        session_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a response with session parameters."""
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [text]
                        }
                    }
                ]
            }
        }

        if session_params:
            response["session_info"] = {
                "parameters": session_params
            }

        return response


@router.post("/")
async def dialogflow_webhook(request: Request) -> Dict[str, Any]:
    """
    Handle Dialogflow CX webhook requests.

    This endpoint is called by Dialogflow when a webhook is triggered
    during the conversation flow (e.g., to check availability, book appointments).
    """
    try:
        payload = await request.json()

        # Extract key information from the webhook request
        session_info = payload.get("sessionInfo", {})
        tag = payload.get("fulfillmentInfo", {}).get("tag", "")
        intent_name = payload.get("intentInfo", {}).get("displayName", "")
        parameters = session_info.get("parameters", {})

        logger.info(f"Dialogflow webhook called - Tag: {tag}, Intent: {intent_name}")
        logger.debug(f"Parameters: {parameters}")

        # Route to appropriate handler based on webhook tag
        if tag == "check_availability":
            return await check_availability(parameters)
        elif tag == "book_appointment":
            return await book_appointment(parameters)
        elif tag == "cancel_appointment":
            return await cancel_appointment(parameters)
        elif tag == "get_services":
            return await get_services(parameters)
        else:
            logger.warning(f"Unhandled webhook tag: {tag}")
            return DialogflowResponse.create_text_response(
                "I can help you with that. Let me connect you with our team."
            )

    except Exception as e:
        logger.error(f"Error processing Dialogflow webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def check_availability(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check appointment availability in Phorest.

    Expected params:
    - date: requested appointment date
    - time: requested appointment time (optional)
    - service: requested service type
    """
    date = params.get("date")
    time = params.get("time")
    service = params.get("service")

    logger.info(f"Checking availability for {service} on {date} at {time}")

    # TODO: Integrate with Phorest API to check actual availability
    # For now, return a mock response

    available_times = ["10:00 AM", "2:00 PM", "4:30 PM"]

    return DialogflowResponse.create_response_with_params(
        f"I have availability on {date} at {', '.join(available_times)}. Which time works best for you?",
        session_params={
            "available_times": available_times,
            "requested_date": date
        }
    )


async def book_appointment(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Book an appointment in Phorest.

    Expected params:
    - date: appointment date
    - time: appointment time
    - service: service type
    - customer_name: customer name
    - customer_phone: customer phone number
    """
    date = params.get("date")
    time = params.get("time")
    service = params.get("service")
    customer_name = params.get("customer_name")
    customer_phone = params.get("customer_phone")

    logger.info(f"Booking appointment: {customer_name} - {service} on {date} at {time}")

    # TODO: Integrate with Phorest API to create actual appointment
    # For now, return a mock confirmation

    confirmation_number = "APT-12345"

    return DialogflowResponse.create_response_with_params(
        f"Perfect! I've booked your {service} appointment for {date} at {time}. "
        f"Your confirmation number is {confirmation_number}. "
        f"We'll send a reminder to {customer_phone}.",
        session_params={
            "confirmation_number": confirmation_number,
            "booking_confirmed": True
        }
    )


async def cancel_appointment(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cancel an appointment in Phorest.

    Expected params:
    - confirmation_number: appointment confirmation number
    - customer_phone: customer phone for verification
    """
    confirmation_number = params.get("confirmation_number")
    customer_phone = params.get("customer_phone")

    logger.info(f"Cancelling appointment: {confirmation_number}")

    # TODO: Integrate with Phorest API to cancel appointment

    return DialogflowResponse.create_text_response(
        f"I've cancelled your appointment {confirmation_number}. "
        "Is there anything else I can help you with?"
    )


async def get_services(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get list of available services from Phorest.
    """
    logger.info("Fetching available services")

    # TODO: Integrate with Phorest API to get actual services
    # For now, return mock services

    services = [
        "Haircut",
        "Hair Coloring",
        "Manicure",
        "Pedicure",
        "Facial",
        "Massage"
    ]

    return DialogflowResponse.create_response_with_params(
        f"We offer the following services: {', '.join(services)}. "
        "Which service are you interested in?",
        session_params={
            "available_services": services
        }
    )


@router.get("/health")
async def dialogflow_health():
    """Health check for Dialogflow integration."""
    return {"status": "healthy", "service": "dialogflow_webhooks"}
