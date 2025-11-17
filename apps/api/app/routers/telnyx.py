"""Telnyx webhook handlers for telephony events."""

from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging
from app.services.call_integration_service import CallIntegrationService

logger = logging.getLogger(__name__)
router = APIRouter()
integration_service = CallIntegrationService()


@router.post("/")
async def telnyx_webhook(request: Request) -> Dict[str, Any]:
    """
    Handle incoming Telnyx webhooks for call events.

    Telnyx will send webhooks for events like:
    - call.initiated
    - call.answered
    - call.hangup
    - call.machine.detection.ended
    """
    try:
        payload = await request.json()
        event_type = payload.get("data", {}).get("event_type")

        logger.info(f"Received Telnyx event: {event_type}")
        logger.debug(f"Payload: {payload}")

        # Route to appropriate handler based on event type
        if event_type == "call.initiated":
            return await handle_call_initiated(payload)
        elif event_type == "call.answered":
            return await handle_call_answered(payload)
        elif event_type == "call.hangup":
            return await handle_call_hangup(payload)
        elif event_type == "call.machine.detection.ended":
            return await handle_machine_detection(payload)
        else:
            logger.warning(f"Unhandled event type: {event_type}")
            return {"status": "received"}

    except Exception as e:
        logger.error(f"Error processing Telnyx webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_call_initiated(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle when a call is first initiated."""
    call_control_id = payload.get("data", {}).get("payload", {}).get("call_control_id")
    from_number = payload.get("data", {}).get("payload", {}).get("from")
    to_number = payload.get("data", {}).get("payload", {}).get("to")

    logger.info(f"Call initiated from {from_number} to {to_number}")

    try:
        # Answer the call and initiate Dialogflow session
        result = await integration_service.handle_incoming_call(
            call_control_id=call_control_id,
            from_number=from_number,
            to_number=to_number
        )

        logger.info(f"Successfully answered call {call_control_id} and created Dialogflow session")

        return result
    except Exception as e:
        logger.error(f"Failed to handle incoming call {call_control_id}: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


async def handle_call_answered(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle when a call is answered."""
    call_control_id = payload.get("data", {}).get("payload", {}).get("call_control_id")

    logger.info(f"Call answered: {call_control_id}")

    # Start the Dialogflow conversation
    # This is where we'd initiate the Dialogflow CX session

    return {"status": "call_answered"}


async def handle_call_hangup(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle when a call ends."""
    call_control_id = payload.get("data", {}).get("payload", {}).get("call_control_id")
    hangup_cause = payload.get("data", {}).get("payload", {}).get("hangup_cause")

    logger.info(f"Call ended: {call_control_id}, cause: {hangup_cause}")

    # Clean up Dialogflow session and save call logs
    await integration_service.end_call_session(call_control_id)

    return {"status": "call_ended", "hangup_cause": hangup_cause}


async def handle_machine_detection(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle answering machine detection result."""
    result = payload.get("data", {}).get("payload", {}).get("result")

    logger.info(f"Machine detection result: {result}")

    # Adjust behavior if voicemail detected

    return {"status": "machine_detection_processed"}


@router.get("/health")
async def telnyx_health():
    """Health check for Telnyx integration."""
    return {"status": "healthy", "service": "telnyx_webhooks"}
