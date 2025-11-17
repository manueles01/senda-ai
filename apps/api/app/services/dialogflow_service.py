"""Dialogflow CX service for managing conversation sessions."""

from google.cloud import dialogflowcx_v3 as dialogflow
from google.api_core.exceptions import GoogleAPIError
from typing import Dict, Any, Optional, List
import logging
import uuid
from app.config import settings

logger = logging.getLogger(__name__)


class DialogflowService:
    """Service for managing Dialogflow CX conversations."""

    def __init__(self):
        """Initialize Dialogflow CX session client."""
        self.project_id = settings.GOOGLE_PROJECT_ID
        self.location = settings.DIALOGFLOW_LOCATION
        self.agent_id = settings.DIALOGFLOW_AGENT_ID

        # Initialize clients
        self.session_client = dialogflow.SessionsClient(
            client_options={
                "api_endpoint": f"{self.location}-dialogflow.googleapis.com"
            }
        )
        self.agents_client = dialogflow.AgentsClient(
            client_options={
                "api_endpoint": f"{self.location}-dialogflow.googleapis.com"
            }
        )

    def create_session_path(self, session_id: Optional[str] = None) -> str:
        """
        Create a session path for Dialogflow CX.

        Args:
            session_id: Optional session ID. If not provided, generates a new UUID.

        Returns:
            Full session path string
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        return self.session_client.session_path(
            project=self.project_id,
            location=self.location,
            agent=self.agent_id,
            session=session_id
        )

    async def detect_intent(
        self,
        session_id: str,
        text: str,
        language_code: str = "en"
    ) -> Dict[str, Any]:
        """
        Send text input to Dialogflow CX and get response.

        Args:
            session_id: Unique session identifier
            text: User's text input
            language_code: Language code (default: en)

        Returns:
            Dictionary containing response messages and parameters
        """
        try:
            session_path = self.create_session_path(session_id)

            # Prepare text input
            text_input = dialogflow.TextInput(text=text)
            query_input = dialogflow.QueryInput(
                text=text_input,
                language_code=language_code
            )

            # Make the API request
            request = dialogflow.DetectIntentRequest(
                session=session_path,
                query_input=query_input
            )

            response = self.session_client.detect_intent(request=request)

            # Extract response messages
            messages = []
            for message in response.query_result.response_messages:
                if message.text:
                    messages.extend(message.text.text)

            result = {
                "messages": messages,
                "intent": response.query_result.intent.display_name if response.query_result.intent else None,
                "parameters": dict(response.query_result.parameters) if response.query_result.parameters else {},
                "confidence": response.query_result.intent_detection_confidence,
                "session_id": session_id
            }

            logger.info(f"Detected intent: {result['intent']} with confidence {result['confidence']}")

            return result

        except GoogleAPIError as e:
            logger.error(f"Dialogflow API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            raise

    async def detect_intent_audio(
        self,
        session_id: str,
        audio_data: bytes,
        sample_rate_hertz: int = 8000,
        language_code: str = "en"
    ) -> Dict[str, Any]:
        """
        Send audio input to Dialogflow CX and get response.

        Args:
            session_id: Unique session identifier
            audio_data: Audio bytes
            sample_rate_hertz: Sample rate of the audio
            language_code: Language code (default: en)

        Returns:
            Dictionary containing response messages and parameters
        """
        try:
            session_path = self.create_session_path(session_id)

            # Configure audio input
            audio_config = dialogflow.InputAudioConfig(
                audio_encoding=dialogflow.AudioEncoding.AUDIO_ENCODING_MULAW,
                sample_rate_hertz=sample_rate_hertz,
                language_code=language_code
            )

            audio_input = dialogflow.AudioInput(
                config=audio_config,
                audio=audio_data
            )

            query_input = dialogflow.QueryInput(
                audio=audio_input,
                language_code=language_code
            )

            # Make the API request
            request = dialogflow.DetectIntentRequest(
                session=session_path,
                query_input=query_input
            )

            response = self.session_client.detect_intent(request=request)

            # Extract response messages
            messages = []
            for message in response.query_result.response_messages:
                if message.text:
                    messages.extend(message.text.text)

            result = {
                "messages": messages,
                "intent": response.query_result.intent.display_name if response.query_result.intent else None,
                "parameters": dict(response.query_result.parameters) if response.query_result.parameters else {},
                "confidence": response.query_result.intent_detection_confidence,
                "session_id": session_id,
                "output_audio": response.output_audio if response.output_audio else None
            }

            logger.info(f"Detected intent from audio: {result['intent']}")

            return result

        except GoogleAPIError as e:
            logger.error(f"Dialogflow API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error detecting intent from audio: {str(e)}")
            raise

    async def streaming_detect_intent(
        self,
        session_id: str,
        audio_generator,
        sample_rate_hertz: int = 8000,
        language_code: str = "en"
    ):
        """
        Stream audio to Dialogflow CX for real-time conversation.

        This is used for phone calls where audio is continuously streamed.

        Args:
            session_id: Unique session identifier
            audio_generator: Generator that yields audio chunks
            sample_rate_hertz: Sample rate of the audio
            language_code: Language code (default: en)

        Yields:
            Response objects from Dialogflow
        """
        try:
            session_path = self.create_session_path(session_id)

            def request_generator():
                """Generate streaming requests."""
                # First request contains session and audio config
                audio_config = dialogflow.InputAudioConfig(
                    audio_encoding=dialogflow.AudioEncoding.AUDIO_ENCODING_MULAW,
                    sample_rate_hertz=sample_rate_hertz,
                    language_code=language_code,
                    single_utterance=False  # Don't stop after first utterance
                )

                query_input = dialogflow.QueryInput(
                    audio=dialogflow.AudioInput(config=audio_config),
                    language_code=language_code
                )

                yield dialogflow.StreamingDetectIntentRequest(
                    session=session_path,
                    query_input=query_input
                )

                # Subsequent requests contain audio data
                for audio_chunk in audio_generator:
                    yield dialogflow.StreamingDetectIntentRequest(
                        input_audio=audio_chunk
                    )

            # Make streaming API call
            responses = self.session_client.streaming_detect_intent(
                requests=request_generator()
            )

            for response in responses:
                logger.debug(f"Streaming response: {response}")
                yield response

        except GoogleAPIError as e:
            logger.error(f"Dialogflow streaming API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in streaming detect intent: {str(e)}")
            raise

    async def fulfill_webhook(
        self,
        webhook_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process webhook fulfillment request from Dialogflow.

        This is called when Dialogflow needs to execute custom logic.

        Args:
            webhook_request: Webhook request payload from Dialogflow

        Returns:
            Webhook response with fulfillment messages
        """
        try:
            tag = webhook_request.get("fulfillmentInfo", {}).get("tag")
            parameters = webhook_request.get("sessionInfo", {}).get("parameters", {})

            logger.info(f"Processing webhook tag: {tag}")

            # This method is a placeholder - actual fulfillment logic
            # is handled in the dialogflow router
            return {
                "fulfillment_response": {
                    "messages": [
                        {
                            "text": {
                                "text": ["Processing your request..."]
                            }
                        }
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            raise
