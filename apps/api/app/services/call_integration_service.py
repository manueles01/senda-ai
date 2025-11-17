"""Integration service for connecting Telnyx calls with Dialogflow CX."""

import asyncio
import logging
from typing import Dict, Any, Optional
from app.services.telnyx_service import TelnyxService
from app.services.dialogflow_service import DialogflowService
from app.config import settings

logger = logging.getLogger(__name__)


class CallIntegrationService:
    """Service for integrating Telnyx telephony with Dialogflow CX conversations."""

    def __init__(self):
        """Initialize integration service with Telnyx and Dialogflow clients."""
        self.telnyx = TelnyxService()
        self.dialogflow = DialogflowService()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def handle_incoming_call(
        self,
        call_control_id: str,
        from_number: str,
        to_number: str
    ) -> Dict[str, Any]:
        """
        Handle a new incoming call by answering and initiating Dialogflow session.

        Args:
            call_control_id: Telnyx call control ID
            from_number: Caller's phone number
            to_number: Dialed number

        Returns:
            Session information
        """
        try:
            # Create a unique session ID for this call
            session_id = f"call-{call_control_id}"

            # Store session information
            self.active_sessions[call_control_id] = {
                "session_id": session_id,
                "from_number": from_number,
                "to_number": to_number,
                "status": "active"
            }

            logger.info(f"Created Dialogflow session {session_id} for call {call_control_id}")

            # Answer the call
            await self.telnyx.answer_call(call_control_id)

            # Play initial greeting using TTS
            # In production, this would be replaced with Dialogflow's greeting
            greeting = (
                "Thank you for calling Senda Salon! "
                "I'm your AI assistant. How can I help you today?"
            )

            await self.telnyx.speak_text(call_control_id, greeting)

            return {
                "status": "success",
                "session_id": session_id,
                "call_control_id": call_control_id
            }

        except Exception as e:
            logger.error(f"Error handling incoming call: {str(e)}")
            # Try to hangup call if there's an error
            try:
                await self.telnyx.hangup_call(call_control_id)
            except:
                pass
            raise

    async def process_audio_stream(
        self,
        call_control_id: str,
        audio_data: bytes
    ) -> Optional[Dict[str, Any]]:
        """
        Process audio from call through Dialogflow.

        This would be called when receiving audio chunks from Telnyx.

        Args:
            call_control_id: Telnyx call control ID
            audio_data: Audio bytes from the call

        Returns:
            Dialogflow response if available
        """
        try:
            session_info = self.active_sessions.get(call_control_id)
            if not session_info:
                logger.warning(f"No session found for call {call_control_id}")
                return None

            session_id = session_info["session_id"]

            # Send audio to Dialogflow
            result = await self.dialogflow.detect_intent_audio(
                session_id=session_id,
                audio_data=audio_data,
                sample_rate_hertz=8000  # Telnyx uses 8kHz for MULAW
            )

            # If Dialogflow returned a response, play it back on the call
            if result.get("messages"):
                response_text = " ".join(result["messages"])
                await self.telnyx.speak_text(call_control_id, response_text)

            return result

        except Exception as e:
            logger.error(f"Error processing audio stream: {str(e)}")
            return None

    async def handle_dtmf_input(
        self,
        call_control_id: str,
        digit: str
    ) -> Optional[Dict[str, Any]]:
        """
        Handle DTMF (keypad) input from the caller.

        Args:
            call_control_id: Telnyx call control ID
            digit: DTMF digit pressed

        Returns:
            Dialogflow response if available
        """
        try:
            session_info = self.active_sessions.get(call_control_id)
            if not session_info:
                logger.warning(f"No session found for call {call_control_id}")
                return None

            session_id = session_info["session_id"]

            # Convert DTMF to text intent
            # For example, 1 = "yes", 2 = "no", etc.
            dtmf_map = {
                "1": "yes",
                "2": "no",
                "0": "speak to representative"
            }

            text_input = dtmf_map.get(digit, digit)

            # Send to Dialogflow
            result = await self.dialogflow.detect_intent(
                session_id=session_id,
                text=text_input
            )

            # Play response
            if result.get("messages"):
                response_text = " ".join(result["messages"])
                await self.telnyx.speak_text(call_control_id, response_text)

            return result

        except Exception as e:
            logger.error(f"Error handling DTMF input: {str(e)}")
            return None

    async def end_call_session(self, call_control_id: str) -> None:
        """
        Clean up session when call ends.

        Args:
            call_control_id: Telnyx call control ID
        """
        try:
            if call_control_id in self.active_sessions:
                session_info = self.active_sessions[call_control_id]
                logger.info(f"Ending session {session_info['session_id']} for call {call_control_id}")

                # Remove from active sessions
                del self.active_sessions[call_control_id]

                # Here you could save call logs, analytics, etc.

        except Exception as e:
            logger.error(f"Error ending call session: {str(e)}")

    async def transfer_to_human(
        self,
        call_control_id: str,
        transfer_number: str
    ) -> Dict[str, Any]:
        """
        Transfer call to a human representative.

        Args:
            call_control_id: Telnyx call control ID
            transfer_number: Phone number to transfer to

        Returns:
            Transfer result
        """
        try:
            # Play transfer message
            await self.telnyx.speak_text(
                call_control_id,
                "Please hold while I transfer you to a representative."
            )

            # Transfer the call
            result = await self.telnyx.transfer_call(
                call_control_id,
                transfer_number
            )

            # End our session since call is being transferred
            await self.end_call_session(call_control_id)

            return result

        except Exception as e:
            logger.error(f"Error transferring call: {str(e)}")
            raise

    def get_session_info(self, call_control_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information for a call.

        Args:
            call_control_id: Telnyx call control ID

        Returns:
            Session information if exists
        """
        return self.active_sessions.get(call_control_id)

    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active sessions.

        Returns:
            Dictionary of active sessions
        """
        return self.active_sessions.copy()
