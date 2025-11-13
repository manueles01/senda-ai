"""
Telnyx API Service
Handles all interactions with Telnyx telephony platform
"""

import httpx
import os
from typing import Optional


class TelnyxService:
    """Service for interacting with Telnyx API"""

    def __init__(self):
        self.api_key = os.getenv("TELNYX_API_KEY")
        self.phone_number = os.getenv("TELNYX_PHONE_NUMBER")
        self.base_url = "https://api.telnyx.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def answer_call(self, call_control_id: str) -> bool:
        """Answer an incoming call"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/calls/{call_control_id}/actions/answer"

            try:
                response = await client.post(url, headers=self.headers, json={})
                response.raise_for_status()
                print(f"✅ Call answered: {call_control_id}")
                return True
            except Exception as e:
                print(f"❌ Error answering call: {e}")
                return False

    async def speak(
        self,
        call_control_id: str,
        text: str,
        voice: str = "female",
        language: str = "en-US",
    ) -> bool:
        """
        Speak text on a call using text-to-speech

        Args:
            call_control_id: Call control ID
            text: Text to speak
            voice: Voice type (male/female)
            language: Language code

        Returns:
            True if successful, False otherwise
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/calls/{call_control_id}/actions/speak"

            payload = {"payload": text, "voice": voice, "language": language}

            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                print(f"🗣️  Speaking: '{text[:80]}...'")
                return True
            except Exception as e:
                print(f"❌ Error speaking: {e}")
                return False

    async def start_transcription(
        self, call_control_id: str, language: str = "en"
    ) -> bool:
        """
        Start transcribing audio from a call

        Args:
            call_control_id: Call control ID
            language: Language code for transcription

        Returns:
            True if successful, False otherwise
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = (
                f"{self.base_url}/calls/{call_control_id}/actions/transcription_start"
            )

            payload = {"transcription_engine": "B", "language": language}

            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                print(f"👂 Transcription started: {call_control_id}")
                return True
            except Exception as e:
                print(f"❌ Error starting transcription: {e}")
                return False

    async def stop_transcription(self, call_control_id: str) -> bool:
        """Stop transcription on a call"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = (
                f"{self.base_url}/calls/{call_control_id}/actions/transcription_stop"
            )

            try:
                response = await client.post(url, headers=self.headers, json={})
                response.raise_for_status()
                print(f"🛑 Transcription stopped: {call_control_id}")
                return True
            except Exception as e:
                print(f"❌ Error stopping transcription: {e}")
                return False

    async def transfer_call(
        self, call_control_id: str, to_number: str
    ) -> bool:
        """
        Transfer call to a human agent

        Args:
            call_control_id: Call control ID
            to_number: Phone number to transfer to

        Returns:
            True if successful, False otherwise
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/calls/{call_control_id}/actions/transfer"

            payload = {"to": to_number}

            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                print(f"📞 Call transferred to: {to_number}")
                return True
            except Exception as e:
                print(f"❌ Error transferring call: {e}")
                return False

    async def hangup_call(self, call_control_id: str) -> bool:
        """Hang up a call"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/calls/{call_control_id}/actions/hangup"

            try:
                response = await client.post(url, headers=self.headers, json={})
                response.raise_for_status()
                print(f"📴 Call hung up: {call_control_id}")
                return True
            except Exception as e:
                print(f"❌ Error hanging up: {e}")
                return False

    async def send_sms(
        self, to_number: str, message: str, from_number: Optional[str] = None
    ) -> bool:
        """
        Send an SMS message

        Args:
            to_number: Recipient phone number
            message: SMS message text
            from_number: Sender phone number (uses default if not provided)

        Returns:
            True if successful, False otherwise
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/messages"

            payload = {
                "from": from_number or self.phone_number,
                "to": to_number,
                "text": message,
            }

            try:
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                print(f"📱 SMS sent to: {to_number}")
                return True
            except Exception as e:
                print(f"❌ Error sending SMS: {e}")
                return False


# Create singleton instance
telnyx_service = TelnyxService()
