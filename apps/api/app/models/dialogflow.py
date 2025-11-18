"""
Pydantic models for Dialogflow CX webhook requests and responses.
Based on: https://cloud.google.com/dialogflow/cx/docs/reference/rest/v3/Webhook
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DialogflowIntent(BaseModel):
    """Dialogflow intent information."""
    displayName: str


class DialogflowPage(BaseModel):
    """Dialogflow page information."""
    displayName: str
    name: Optional[str] = None


class DialogflowSession(BaseModel):
    """Dialogflow session information."""
    name: str
    parameters: Optional[Dict[str, Any]] = None


class DialogflowText(BaseModel):
    """Text response."""
    text: List[str]


class DialogflowMessage(BaseModel):
    """Response message."""
    text: Optional[DialogflowText] = None
    payload: Optional[Dict[str, Any]] = None


class DialogflowFulfillmentResponse(BaseModel):
    """Fulfillment response to be sent back to Dialogflow."""
    messages: Optional[List[DialogflowMessage]] = Field(default_factory=list)


class DialogflowSessionInfo(BaseModel):
    """Session information for parameter updates."""
    parameters: Optional[Dict[str, Any]] = None


class DialogflowWebhookRequest(BaseModel):
    """
    Incoming webhook request from Dialogflow CX.

    Docs: https://cloud.google.com/dialogflow/cx/docs/reference/rest/v3/Webhook#WebhookRequest
    """
    detectIntentResponseId: Optional[str] = None
    intentInfo: Optional[Dict[str, Any]] = None
    pageInfo: Optional[Dict[str, Any]] = None
    sessionInfo: Optional[DialogflowSession] = None
    fulfillmentInfo: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    triggerIntent: Optional[str] = None
    transcript: Optional[str] = None
    triggerEvent: Optional[str] = None
    languageCode: Optional[str] = "en"
    messages: Optional[List[DialogflowMessage]] = None
    payload: Optional[Dict[str, Any]] = None


class DialogflowWebhookResponse(BaseModel):
    """
    Webhook response to send back to Dialogflow CX.

    Docs: https://cloud.google.com/dialogflow/cx/docs/reference/rest/v3/Webhook#WebhookResponse
    """
    fulfillmentResponse: Optional[DialogflowFulfillmentResponse] = None
    sessionInfo: Optional[DialogflowSessionInfo] = None
    pageInfo: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None
    targetPage: Optional[str] = None
    targetFlow: Optional[str] = None


def create_text_response(text: str) -> DialogflowWebhookResponse:
    """Helper function to create a simple text response."""
    return DialogflowWebhookResponse(
        fulfillmentResponse=DialogflowFulfillmentResponse(
            messages=[
                DialogflowMessage(
                    text=DialogflowText(text=[text])
                )
            ]
        )
    )


def create_response_with_params(
    text: str,
    parameters: Dict[str, Any]
) -> DialogflowWebhookResponse:
    """Helper function to create a response with session parameters."""
    return DialogflowWebhookResponse(
        fulfillmentResponse=DialogflowFulfillmentResponse(
            messages=[
                DialogflowMessage(
                    text=DialogflowText(text=[text])
                )
            ]
        ),
        sessionInfo=DialogflowSessionInfo(
            parameters=parameters
        )
    )
