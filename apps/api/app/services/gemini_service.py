"""Gemini AI service for enhanced conversation responses."""

import google.generativeai as genai
from typing import Dict, Any, List, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_PROJECT_ID)  # Note: You may need a separate Gemini API key


class GeminiService:
    """Service for leveraging Gemini AI for enhanced conversation capabilities."""

    def __init__(self):
        """Initialize Gemini service with configured model."""
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

        # System instruction for the salon receptionist context
        self.system_context = """You are a helpful AI receptionist for Senda Salon,
a premium salon and spa. Your role is to:
- Greet customers warmly and professionally
- Help them book appointments for services like haircuts, coloring, manicures, pedicures, facials, and massages
- Answer questions about services, pricing, and availability
- Handle appointment modifications and cancellations
- Provide information about business hours
- Be conversational, friendly, and efficient

Keep responses concise and natural for phone conversations. Always confirm important details
like dates, times, and services to avoid mistakes."""

    async def enhance_response(
        self,
        user_input: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an enhanced response using Gemini.

        This can be used to generate better Dialogflow responses or handle
        complex queries that need advanced reasoning.

        Args:
            user_input: The user's message
            conversation_history: Previous messages in the conversation
            context: Additional context (e.g., available appointments, user info)

        Returns:
            Enhanced response text
        """
        try:
            # Build the prompt
            prompt_parts = [self.system_context, "\n\n"]

            # Add conversation history if available
            if conversation_history:
                prompt_parts.append("Conversation history:\n")
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    prompt_parts.append(f"{role}: {content}\n")
                prompt_parts.append("\n")

            # Add context if available
            if context:
                prompt_parts.append(f"Context: {context}\n\n")

            # Add current user input
            prompt_parts.append(f"User: {user_input}\n\n")
            prompt_parts.append("Assistant:")

            full_prompt = "".join(prompt_parts)

            # Generate response
            response = self.model.generate_content(full_prompt)

            logger.info(f"Generated Gemini response for input: {user_input[:50]}...")

            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            # Return a fallback response
            return "I apologize, but I'm having trouble processing that. Could you please repeat?"

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of user input.

        Helps detect if customer is frustrated, happy, urgent, etc.

        Args:
            text: User's message

        Returns:
            Dictionary with sentiment analysis
        """
        try:
            prompt = f"""Analyze the sentiment and emotion of this customer message:
"{text}"

Provide:
1. Overall sentiment (positive, neutral, negative)
2. Emotion (happy, neutral, frustrated, angry, urgent)
3. Confidence score (0-1)
4. Suggested response tone (warm, professional, apologetic, enthusiastic)

Format as JSON."""

            response = self.model.generate_content(prompt)

            # Parse response (simplified - in production, use structured output)
            result = {
                "text": text,
                "sentiment": "neutral",  # Parse from response
                "emotion": "neutral",
                "confidence": 0.8,
                "suggested_tone": "professional",
                "raw_analysis": response.text
            }

            logger.info(f"Sentiment analysis: {result['sentiment']}")

            return result

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "text": text,
                "sentiment": "neutral",
                "emotion": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }

    async def extract_booking_details(self, text: str) -> Dict[str, Any]:
        """
        Extract booking details from natural language.

        Uses Gemini to parse complex booking requests.

        Args:
            text: User's booking request

        Returns:
            Extracted booking details
        """
        try:
            prompt = f"""Extract booking details from this request:
"{text}"

Extract:
- service: type of service (haircut, coloring, manicure, pedicure, facial, massage, etc.)
- date: requested date (in ISO format if possible, or natural description)
- time: preferred time
- duration: expected duration if mentioned
- special_requests: any special requirements

Format as JSON. If information is not mentioned, use null."""

            response = self.model.generate_content(prompt)

            # Parse response (simplified - in production, use structured output)
            logger.info(f"Extracted booking details from: {text}")
            logger.debug(f"Gemini response: {response.text}")

            # Return structured data (simplified)
            return {
                "raw_response": response.text,
                "extracted": True
            }

        except Exception as e:
            logger.error(f"Error extracting booking details: {str(e)}")
            return {
                "extracted": False,
                "error": str(e)
            }

    async def suggest_alternative_times(
        self,
        requested_time: str,
        available_times: List[str],
        customer_preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a natural response suggesting alternative appointment times.

        Args:
            requested_time: Time customer originally requested
            available_times: List of available alternative times
            customer_preferences: Any known preferences

        Returns:
            Natural language response with alternatives
        """
        try:
            prompt = f"""You are a salon receptionist. A customer requested an appointment at {requested_time},
but that time is not available.

Available times are: {', '.join(available_times)}

Generate a warm, professional response offering the alternatives. Keep it concise for phone conversation.
{f'Customer preferences: {customer_preferences}' if customer_preferences else ''}"""

            response = self.model.generate_content(prompt)

            return response.text.strip()

        except Exception as e:
            logger.error(f"Error suggesting alternatives: {str(e)}")
            # Fallback response
            return f"I'm sorry, {requested_time} is not available. We have openings at {', '.join(available_times[:3])}. Would any of these work for you?"

    async def handle_complex_query(
        self,
        query: str,
        knowledge_base: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Handle complex queries that Dialogflow might not handle well.

        Args:
            query: User's complex question
            knowledge_base: Optional knowledge base (hours, pricing, policies)

        Returns:
            Response to the query
        """
        try:
            kb_text = ""
            if knowledge_base:
                kb_text = f"\n\nSalon information:\n{knowledge_base}"

            prompt = f"""{self.system_context}{kb_text}

Customer question: {query}

Provide a helpful, concise answer suitable for a phone conversation."""

            response = self.model.generate_content(prompt)

            logger.info(f"Handled complex query: {query[:50]}...")

            return response.text.strip()

        except Exception as e:
            logger.error(f"Error handling complex query: {str(e)}")
            return "Let me connect you with someone who can better assist you with that question."

    async def generate_follow_up_questions(
        self,
        conversation_context: Dict[str, Any]
    ) -> List[str]:
        """
        Generate relevant follow-up questions to gather more information.

        Args:
            conversation_context: Current conversation state

        Returns:
            List of suggested follow-up questions
        """
        try:
            prompt = f"""Based on this conversation context:
{conversation_context}

What are the most relevant follow-up questions to ask the customer to complete their booking?
Provide 2-3 specific questions."""

            response = self.model.generate_content(prompt)

            # Parse questions (simplified)
            questions = response.text.strip().split("\n")
            questions = [q.strip("- ").strip() for q in questions if q.strip()]

            return questions[:3]

        except Exception as e:
            logger.error(f"Error generating follow-up questions: {str(e)}")
            return []

    async def summarize_call(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a summary of the call for record-keeping.

        Args:
            conversation_history: Full conversation

        Returns:
            Call summary
        """
        try:
            conversation_text = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in conversation_history
            ])

            prompt = f"""Summarize this salon call in 2-3 sentences for internal records:

{conversation_text}

Include: purpose of call, outcome, any bookings made or actions taken."""

            response = self.model.generate_content(prompt)

            return response.text.strip()

        except Exception as e:
            logger.error(f"Error summarizing call: {str(e)}")
            return "Call summary unavailable"
