"""
Conversation Service
Manages conversation state and AI interactions
"""

import os
import json
from typing import Dict, List, Optional, Any
import google.generativeai as genai


class ConversationService:
    """Service for managing conversations with Gemini AI"""

    def __init__(self):
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.conversations: Dict[str, Dict] = {}

    def create_conversation(
        self, call_control_id: str, caller_number: str
    ) -> None:
        """
        Initialize a new conversation

        Args:
            call_control_id: Unique call identifier
            caller_number: Customer's phone number
        """
        self.conversations[call_control_id] = {
            "messages": [],
            "caller": caller_number,
            "client_info": None,
            "intent": None,
            "context": {},
            "transfer_requested": False,
        }
        print(f"💬 New conversation: {call_control_id}")

    def add_message(
        self, call_control_id: str, role: str, content: str
    ) -> None:
        """Add a message to the conversation history"""
        if call_control_id not in self.conversations:
            return

        self.conversations[call_control_id]["messages"].append(
            {"role": role, "content": content}
        )

    def set_client_info(
        self, call_control_id: str, client_info: Dict[str, Any]
    ) -> None:
        """Store client information in conversation context"""
        if call_control_id in self.conversations:
            self.conversations[call_control_id]["client_info"] = client_info

    def set_context(
        self, call_control_id: str, key: str, value: Any
    ) -> None:
        """Store additional context data"""
        if call_control_id in self.conversations:
            self.conversations[call_control_id]["context"][key] = value

    def get_conversation(self, call_control_id: str) -> Optional[Dict]:
        """Get conversation data"""
        return self.conversations.get(call_control_id)

    def request_transfer(self, call_control_id: str) -> None:
        """Mark conversation for transfer to human"""
        if call_control_id in self.conversations:
            self.conversations[call_control_id]["transfer_requested"] = True

    def end_conversation(self, call_control_id: str) -> Optional[Dict]:
        """
        Remove conversation and return final state for logging

        Returns:
            Final conversation state including handoff summary if transfer was requested
        """
        return self.conversations.pop(call_control_id, None)

    async def process_message(
        self,
        call_control_id: str,
        transcript: str,
        client_info: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Process customer message and generate response

        Args:
            call_control_id: Call identifier
            transcript: Customer's spoken words
            client_info: Optional client information from Phorest

        Returns:
            Dictionary with response and extracted intent
        """
        conv = self.conversations.get(call_control_id)
        if not conv:
            return {
                "response": "I'm sorry, I lost track of our conversation.",
                "intent": None,
            }

        # Add customer message
        self.add_message(call_control_id, "user", transcript)

        # Build system prompt with real staff data
        system_prompt = await self._build_system_prompt(client_info)

        try:
            # Build conversation history for Gemini
            gemini_messages = []
            for msg in conv["messages"]:
                role = "user" if msg["role"] == "user" else "model"
                gemini_messages.append({
                    "role": role,
                    "parts": [msg["content"]]
                })

            # Start chat with Gemini
            chat = self.model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])

            # Send the system prompt + latest user message
            prompt = f"{system_prompt}\n\nUser: {transcript}"
            response = chat.send_message(prompt)

            reply = response.text
            print(f"🤖 Gemini: '{reply[:100]}...'")

            # Add assistant response
            self.add_message(call_control_id, "assistant", reply)

            # Parse intent if present
            intent = self._parse_intent(reply)
            if intent:
                conv["intent"] = intent

            # Check for transfer request
            if "transfer" in reply.lower() or "speak with someone" in reply.lower():
                self.request_transfer(call_control_id)

            return {"response": reply, "intent": intent}

        except Exception as e:
            print(f"❌ Gemini error: {e}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()}")
            return {
                "response": "I'm having trouble understanding. Could you repeat that?",
                "intent": None,
            }

    async def _build_system_prompt(
        self, client_info: Optional[Dict] = None
    ) -> str:
        """Build system prompt based on context and real Phorest data"""

        # Fetch real staff from Phorest
        from src.services.phorest import phorest_service
        try:
            staff_list = await phorest_service.get_staff()
            staff_names = [s.get("firstName", "") for s in staff_list if s.get("firstName")]
            staff_str = ", ".join(staff_names) if staff_names else "Paulo, Leo, Patrick, Joseph, Jake"
            print(f"📋 Using real staff list: {staff_str}")
        except Exception as e:
            print(f"⚠️  Could not fetch staff list: {e}")
            staff_str = "Paulo, Leo, Patrick, Joseph, Jake"  # Fallback

        base_prompt = f"""You are a friendly receptionist for Paulo Lanfredi Salon.

Your responsibilities:
1. Greet customers warmly
2. Understand their needs: BOOKING, RESCHEDULING, or CANCELLATION
3. Extract details: SERVICE, STYLIST/STAFF preference, DATE/TIME preference
4. If customer seems frustrated or specifically asks, offer to transfer to a human

Available Services: Haircut, Color, Highlights, Blowout, Treatment, Beard Trim, Shave
Available Stylists: {staff_str}

IMPORTANT RULES:
- Only suggest stylists from the list above. Never make up stylist names.
- DO NOT ask about location or which salon/barbershop. We have one location with all services.
- DO NOT mention "cave" or "salon" - just book the appointment.
- If they ask for a service like "beard trim" or "shave", that's fine - just book it as a service.

Response Guidelines:
- Keep responses brief and natural (1-2 sentences)
- If you have enough info to book, respond with JSON:
  {{"action": "book", "service": "haircut", "stylist": "Paulo"}}
- For rescheduling: {{"action": "reschedule", "appointment_id": "xxx"}}
- For cancellation: {{"action": "cancel", "appointment_id": "xxx"}}
- If customer asks for human: {{"action": "transfer"}}
- Otherwise, ask clarifying questions naturally (but NEVER about location)

"""

        if client_info:
            name = client_info.get("firstName", "")
            base_prompt += f"\nNote: This is {name}, a returning customer.\n"

        return base_prompt

    def _parse_intent(self, reply: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured intent from Claude's response

        Returns:
            Parsed intent dictionary or None
        """
        if '"action"' not in reply:
            return None

        try:
            # Find JSON in response
            json_start = reply.find("{")
            json_end = reply.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                intent = json.loads(reply[json_start:json_end])
                return intent
        except json.JSONDecodeError:
            pass

        return None

    def get_handoff_summary(self, call_control_id: str) -> str:
        """
        Generate a summary for human handoff

        Returns:
            Summary text with conversation context
        """
        conv = self.conversations.get(call_control_id)
        if not conv:
            return "No conversation history available."

        summary_parts = []

        # Caller info
        summary_parts.append(f"Caller: {conv.get('caller', 'Unknown')}")

        # Client info
        if conv.get("client_info"):
            client = conv["client_info"]
            summary_parts.append(
                f"Customer: {client.get('firstName', '')} {client.get('lastName', '')}"
            )

        # Intent
        if conv.get("intent"):
            intent = conv["intent"]
            action = intent.get("action", "unknown")
            summary_parts.append(f"Intent: {action.upper()}")

            if "service" in intent:
                summary_parts.append(f"Service: {intent['service']}")
            if "stylist" in intent:
                summary_parts.append(f"Stylist: {intent['stylist']}")

        # Recent messages
        recent = conv["messages"][-4:] if len(conv["messages"]) > 0 else []
        if recent:
            summary_parts.append("\nRecent conversation:")
            for msg in recent:
                role = "Customer" if msg["role"] == "user" else "Assistant"
                summary_parts.append(f"{role}: {msg['content'][:100]}")

        return "\n".join(summary_parts)


# Create singleton instance
conversation_service = ConversationService()
