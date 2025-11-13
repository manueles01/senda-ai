"""
Conversation Service
Manages conversation state and Claude AI interactions
"""

import os
import json
from typing import Dict, List, Optional, Any
from anthropic import Anthropic


class ConversationService:
    """Service for managing conversations with Claude AI"""

    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.conversations: Dict[str, Dict] = {}
        self.model = "claude-sonnet-4-20250514"

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

        # Build system prompt
        system_prompt = self._build_system_prompt(client_info)

        try:
            # Call Claude
            response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=conv["messages"],
            )

            reply = response.content[0].text
            print(f"🤖 Claude: '{reply[:100]}...'")

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
            print(f"❌ Claude error: {e}")
            return {
                "response": "I'm having trouble understanding. Could you repeat that?",
                "intent": None,
            }

    def _build_system_prompt(
        self, client_info: Optional[Dict] = None
    ) -> str:
        """Build system prompt based on context"""
        base_prompt = """You are a friendly receptionist for Paulo Lanfredi Salon.

Your responsibilities:
1. Greet customers warmly
2. Understand their needs: BOOKING, RESCHEDULING, or CANCELLATION
3. Extract details: SERVICE, STYLIST/STAFF preference, DATE/TIME preference
4. If customer seems frustrated or specifically asks, offer to transfer to a human

Available Services: Haircut, Color, Highlights, Blowout, Treatment
Available Stylists: Paulo, Leo, Patrick, Joseph, Jake

Response Guidelines:
- Keep responses brief and natural (1-2 sentences)
- If you have enough info to book, respond with JSON:
  {"action": "book", "service": "haircut", "stylist": "Paulo"}
- For rescheduling: {"action": "reschedule", "appointment_id": "xxx"}
- For cancellation: {"action": "cancel", "appointment_id": "xxx"}
- If customer asks for human: {"action": "transfer"}
- Otherwise, ask clarifying questions naturally

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
