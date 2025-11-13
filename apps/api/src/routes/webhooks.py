"""
Webhook Routes
Handles incoming webhooks from Telnyx and other services
"""

from fastapi import APIRouter, Request
from src.services.telnyx import telnyx_service
from src.services.phorest import phorest_service
from src.services.conversation import conversation_service

router = APIRouter()


@router.post("/webhook/call")
async def handle_call_webhook(request: Request):
    """
    Handle Telnyx call webhooks
    Manages the complete call flow from initiation to completion
    """
    data = await request.json()

    event_type = data.get("data", {}).get("event_type")
    payload = data.get("data", {}).get("payload", {})
    call_control_id = payload.get("call_control_id")

    print(f"\n📞 Event: {event_type}")

    # CALL INITIATED - Customer calls in
    if event_type == "call.initiated":
        caller = payload.get("from")
        print(f"📞 Call from: {caller}")

        # Initialize conversation
        conversation_service.create_conversation(call_control_id, caller)

        # Check if customer exists in Phorest
        client = await phorest_service.find_client_by_phone(caller)
        if client:
            print(f"✅ Found client: {client.get('firstName', '')} {client.get('lastName', '')}")
            conversation_service.set_client_info(call_control_id, client)
        else:
            print(f"🆕 New caller: {caller}")

        # Answer the call
        await telnyx_service.answer_call(call_control_id)

    # CALL ANSWERED - Ready to greet
    elif event_type == "call.answered":
        print("🎤 Speaking greeting...")

        # Get conversation to check if returning customer
        conv = conversation_service.get_conversation(call_control_id)
        client_info = conv.get("client_info") if conv else None

        if client_info:
            greeting = f"Hello {client_info.get('firstName', '')}! Thank you for calling Paulo Lanfredi Salon. How can I help you today?"
        else:
            greeting = "Hello! Thank you for calling Paulo Lanfredi Salon. How can I help you today?"

        await telnyx_service.speak(call_control_id, greeting)

    # GREETING FINISHED - Start listening
    elif event_type == "call.speak.ended":
        print("👂 Starting transcription...")
        await telnyx_service.start_transcription(call_control_id)

    # GOT TRANSCRIPTION - Process customer speech
    elif event_type == "call.transcription":
        transcription_data = payload.get("transcription_data", {})
        transcript = transcription_data.get("transcript", "").strip()
        is_final = transcription_data.get("is_final", False)

        # Only process final transcriptions
        if not is_final or not transcript or len(transcript) < 3:
            return {"status": "ok"}

        print(f"\n{'='*70}")
        print(f"👤 CUSTOMER: '{transcript}'")
        print(f"{'='*70}")

        # Get conversation context
        conv = conversation_service.get_conversation(call_control_id)
        client_info = conv.get("client_info") if conv else None

        # Process with Claude
        result = await conversation_service.process_message(
            call_control_id, transcript, client_info
        )

        response_text = result["response"]
        intent = result["intent"]

        # Handle specific intents
        if intent:
            action = intent.get("action")

            # BOOKING REQUEST
            if action == "book":
                service = intent.get("service", "haircut")
                stylist = intent.get("stylist", "")

                print(f"🎯 BOOKING: {service} with {stylist}")

                # Check availability
                availability = await phorest_service.check_availability(
                    service, stylist
                )

                if availability["slots"]:
                    # Found available slots
                    times = ", ".join([s["time"] for s in availability["slots"]])
                    response_text = f"Great! I found {availability['service']} appointments with {availability['staff']}. Available: {times}. Which works best for you?"

                    # Store availability in context for confirmation
                    conversation_service.set_context(
                        call_control_id, "availability", availability
                    )
                    print(f"✅ SLOTS: {times}")
                else:
                    response_text = "I'm sorry, I don't see any availability this week for that service. Would you like to try a different time or stylist?"
                    print("❌ No slots available")

            # TRANSFER TO HUMAN
            elif action == "transfer":
                print("📞 Transfer requested")
                conversation_service.request_transfer(call_control_id)

                # Get handoff summary
                summary = conversation_service.get_handoff_summary(
                    call_control_id
                )
                print(f"\n📋 HANDOFF SUMMARY:\n{summary}\n")

                response_text = "Of course! Let me connect you with someone who can help. Please hold for a moment."

                # TODO: Implement actual transfer
                # await telnyx_service.transfer_call(call_control_id, "+1234567890")

            # CANCELLATION
            elif action == "cancel":
                # TODO: Implement cancellation flow
                response_text = "I can help you cancel your appointment. Let me look that up for you."

            # RESCHEDULING
            elif action == "reschedule":
                # TODO: Implement rescheduling flow
                response_text = "I can help you reschedule. Let me check your current appointment."

        # Speak the response
        await telnyx_service.speak(call_control_id, response_text)
        print(f"🗣️  Response: '{response_text[:80]}...'")

    # CALL ENDED - Cleanup
    elif event_type == "call.hangup":
        print("📴 Call ended")

        # Get final conversation state
        final_conv = conversation_service.end_conversation(call_control_id)

        if final_conv:
            # Log for analytics/training
            if final_conv.get("transfer_requested"):
                print("📋 Call was transferred to human")

            print(f"💬 Total messages: {len(final_conv.get('messages', []))}")

    return {"status": "ok"}


@router.get("/webhook/health")
async def webhook_health():
    """Health check for webhooks"""
    return {"status": "healthy", "service": "webhooks"}
