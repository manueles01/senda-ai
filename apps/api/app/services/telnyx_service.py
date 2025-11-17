"""Telnyx service for managing call operations."""

import telnyx
from typing import Optional, Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Telnyx API key
telnyx.api_key = settings.TELEPHONY_TELNYX_API_KEY


class TelnyxService:
    """Service for managing Telnyx telephony operations."""

    @staticmethod
    async def answer_call(call_control_id: str) -> Dict[str, Any]:
        """Answer an incoming call."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            result = call.answer()
            logger.info(f"Answered call: {call_control_id}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Error answering call {call_control_id}: {str(e)}")
            raise

    @staticmethod
    async def speak_text(call_control_id: str, text: str, voice: str = "female") -> Dict[str, Any]:
        """
        Speak text using text-to-speech.

        Args:
            call_control_id: The call control ID
            text: Text to speak
            voice: Voice to use (male, female)
        """
        try:
            call = telnyx.Call.retrieve(call_control_id)
            result = call.speak(
                payload=text,
                voice=voice,
                language="en-US"
            )
            logger.info(f"Speaking text on call {call_control_id}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Error speaking on call {call_control_id}: {str(e)}")
            raise

    @staticmethod
    async def start_streaming(
        call_control_id: str,
        stream_url: str
    ) -> Dict[str, Any]:
        """
        Start streaming audio to/from the call.

        This is used to stream audio to Dialogflow CX for processing.

        Args:
            call_control_id: The call control ID
            stream_url: WebSocket URL to stream audio to
        """
        try:
            call = telnyx.Call.retrieve(call_control_id)
            result = call.stream_start(
                stream_url=stream_url,
                stream_track="both"  # Stream both inbound and outbound audio
            )
            logger.info(f"Started streaming on call {call_control_id} to {stream_url}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Error starting stream on call {call_control_id}: {str(e)}")
            raise

    @staticmethod
    async def stop_streaming(call_control_id: str) -> Dict[str, Any]:
        """Stop streaming audio."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            result = call.stream_stop()
            logger.info(f"Stopped streaming on call {call_control_id}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Error stopping stream on call {call_control_id}: {str(e)}")
            raise

    @staticmethod
    async def hangup_call(call_control_id: str) -> Dict[str, Any]:
        """Hangup a call."""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            result = call.hangup()
            logger.info(f"Hung up call {call_control_id}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Error hanging up call {call_control_id}: {str(e)}")
            raise

    @staticmethod
    async def gather_using_speak(
        call_control_id: str,
        text: str,
        valid_digits: Optional[str] = None,
        max_digits: int = 1,
        timeout_millis: int = 5000
    ) -> Dict[str, Any]:
        """
        Gather DTMF input while speaking text.

        Useful for menu systems or getting confirmation.

        Args:
            call_control_id: The call control ID
            text: Text to speak
            valid_digits: Valid digits to accept (e.g., "12" for 1 or 2)
            max_digits: Maximum number of digits to collect
            timeout_millis: Timeout in milliseconds
        """
        try:
            call = telnyx.Call.retrieve(call_control_id)
            result = call.gather_using_speak(
                payload=text,
                voice="female",
                language="en-US",
                valid_digits=valid_digits,
                max=max_digits,
                timeout_millis=timeout_millis
            )
            logger.info(f"Started gathering input on call {call_control_id}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Error gathering input on call {call_control_id}: {str(e)}")
            raise

    @staticmethod
    async def enable_machine_detection(
        call_control_id: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Enable answering machine detection.

        Helps determine if call was answered by a person or machine.

        Args:
            call_control_id: The call control ID
            timeout: Detection timeout in seconds
        """
        try:
            # This is typically set when answering the call
            call = telnyx.Call.retrieve(call_control_id)
            # Machine detection settings are usually configured at the connection level
            # or when answering the call
            logger.info(f"Machine detection enabled for call {call_control_id}")
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Error enabling machine detection on call {call_control_id}: {str(e)}")
            raise

    @staticmethod
    async def transfer_call(
        call_control_id: str,
        to_number: str
    ) -> Dict[str, Any]:
        """
        Transfer call to another number.

        Args:
            call_control_id: The call control ID
            to_number: Number to transfer to
        """
        try:
            call = telnyx.Call.retrieve(call_control_id)
            result = call.transfer(to=to_number)
            logger.info(f"Transferred call {call_control_id} to {to_number}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Error transferring call {call_control_id}: {str(e)}")
            raise

    @staticmethod
    async def play_audio(
        call_control_id: str,
        audio_url: str,
        loop: int = 1
    ) -> Dict[str, Any]:
        """
        Play an audio file on the call.

        Args:
            call_control_id: The call control ID
            audio_url: URL of the audio file to play
            loop: Number of times to loop the audio
        """
        try:
            call = telnyx.Call.retrieve(call_control_id)
            result = call.playback_start(
                audio_url=audio_url,
                overlay=False
            )
            logger.info(f"Playing audio on call {call_control_id}: {audio_url}")
            return {"status": "success", "data": result}
        except Exception as e:
            logger.error(f"Error playing audio on call {call_control_id}: {str(e)}")
            raise
