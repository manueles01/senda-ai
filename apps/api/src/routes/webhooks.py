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
    print(f"📞 Call Control ID: {call_control_id}")

    # ASSISTANT INITIALIZATION or CALL INITIATED - Customer calls in
    if event_type in ["assistant.initialization", "call.initiated"]:
        caller = payload.get("from") or payload.get("caller_number")
        print(f"\n{'='*70}")
        print(f"📞 INCOMING CALL")
        print(f"{'='*70}")
        print(f"📞 Call from: {caller}")
        print(f"📞 Event type: {event_type}")
        print(f"📞 Call control ID: {call_control_id}")
        print(f"📞 Full payload keys: {list(payload.keys())}")
        print(f"📞 Full payload: {payload}")

        # Initialize conversation
        conversation_service.create_conversation(call_control_id, caller)

        # Check if customer exists in Phorest (IMMEDIATELY!)
        print(f"\n{'='*70}")
        print(f"🔍 CLIENT LOOKUP STARTING")
        print(f"{'='*70}")
        print(f"🔍 Looking up client by phone: {caller}")

        client = await phorest_service.find_client_by_phone(caller)

        print(f"\n{'='*70}")
        print(f"🔍 CLIENT LOOKUP RESULT")
        print(f"{'='*70}")
        if client:
            print(f"✅ CLIENT FOUND!")
            print(f"   Name: {client.get('firstName', '')} {client.get('lastName', '')}")
            print(f"   Client ID: {client.get('clientId', 'N/A')}")
            print(f"   Mobile: {client.get('mobile', 'N/A')}")
            print(f"   Email: {client.get('email', 'N/A')}")
            conversation_service.set_client_info(call_control_id, client)
        else:
            print(f"❌ NO CLIENT FOUND")
            print(f"   Phone number searched: {caller}")
            print(f"   This is a new caller (not in Phorest system)")
        print(f"{'='*70}\n")

        # Answer the call if needed
        if event_type == "call.initiated":
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
        booking_state = conv.get("context", {}).get("booking_state") if conv else None
        availability = conv.get("context", {}).get("availability") if conv else None

        # Check if we're waiting for slot confirmation
        if booking_state == "awaiting_slot_confirmation" and availability:
            print(f"🎯 Customer is confirming slot choice...")

            # Simple slot selection logic - look for keywords
            transcript_lower = transcript.lower()
            selected_slot = None

            if "first" in transcript_lower or "1" in transcript:
                selected_slot = availability["slots"][0] if availability["slots"] else None
            elif "second" in transcript_lower or "2" in transcript:
                selected_slot = availability["slots"][1] if len(availability["slots"]) > 1 else None
            elif "third" in transcript_lower or "3" in transcript:
                selected_slot = availability["slots"][2] if len(availability["slots"]) > 2 else None
            elif any(word in transcript_lower for word in ["yes", "sure", "ok", "that works", "perfect", "great"]):
                # They're confirming - assume first slot
                selected_slot = availability["slots"][0] if availability["slots"] else None

            if selected_slot:
                print(f"✅ Slot selected: {selected_slot['time']}")

                # Check if we have client info
                if not client_info:
                    response_text = "I need to create a profile for you first. Can I have your first and last name?"
                    conversation_service.set_context(call_control_id, "booking_state", "awaiting_client_name")
                    conversation_service.set_context(call_control_id, "selected_slot", selected_slot)
                else:
                    # Book the appointment!
                    print(f"🎯 Booking appointment for {client_info.get('firstName')} {client_info.get('lastName')}")
                    appointment = await phorest_service.create_appointment(
                        client_info["clientId"],
                        availability["service_id"],
                        availability["staff_id"],
                        selected_slot["raw"]
                    )

                    if appointment:
                        response_text = f"Perfect! I've booked your {availability['service']} appointment with {availability['staff']} on {selected_slot['time']}. See you then!"
                        print(f"✅ Appointment booked successfully!")
                    else:
                        response_text = "I'm sorry, I had trouble completing that booking. Let me transfer you to someone who can help."
                        print(f"❌ Appointment booking failed")

                    # Clear booking state
                    conversation_service.set_context(call_control_id, "booking_state", None)
                    conversation_service.set_context(call_control_id, "availability", None)

                # Speak the response and skip AI processing
                await telnyx_service.speak(call_control_id, response_text)
                print(f"🗣️  Response: '{response_text[:80]}...'")
                return {"status": "ok"}

        # Process with AI
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

                print(f"\n{'='*70}")
                print(f"🎯 BOOKING REQUEST DETECTED")
                print(f"{'='*70}")
                print(f"   Service: {service}")
                print(f"   Stylist: {stylist}")
                print(f"   Client info: {client_info.get('firstName') if client_info else 'None'}")

                # Send an immediate acknowledgment to keep the call alive
                await telnyx_service.speak(call_control_id, "Let me check availability for you, just one moment please.")
                print(f"🗣️  Sent acknowledgment to keep call alive")

                # Check availability
                print(f"🔍 Starting availability check...")
                availability = await phorest_service.check_availability(
                    service, stylist
                )
                print(f"✅ Availability check completed")
                print(f"   Result: {availability}")

                # Check if staff was not found
                if availability.get("error") and "not found" in availability.get("error", "").lower():
                    available_staff = availability.get("available_staff", [])
                    staff_list = ", ".join(available_staff) if available_staff else "our team"
                    response_text = f"I'm sorry, I don't have a stylist named {stylist}. Our available stylists are: {staff_list}. Would you like to book with one of them?"
                    print(f"❌ Staff '{stylist}' not found")
                elif availability["slots"]:
                    # Found available slots
                    times = ", ".join([s["time"] for s in availability["slots"]])
                    response_text = f"Great! I found {availability['service']} appointments with {availability['staff']}. Available: {times}. Which works best for you?"

                    # Store availability in context for confirmation
                    conversation_service.set_context(
                        call_control_id, "availability", availability
                    )
                    conversation_service.set_context(
                        call_control_id, "booking_state", "awaiting_slot_confirmation"
                    )
                    print(f"✅ SLOTS: {times}")
                    print(f"📌 Booking state set to: awaiting_slot_confirmation")
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
