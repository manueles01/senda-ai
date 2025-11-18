# Senda AI - Dialogflow CX Agent

This directory contains the Dialogflow CX agent configuration and documentation for the Senda AI conversational interface.

## Agent Overview

The Senda AI agent is designed to handle:
- **Appointment Booking**: Schedule services with Phorest
- **Availability Checking**: Check available time slots
- **Business Information**: Hours, services, pricing
- **Appointment Management**: Cancel or reschedule appointments
- **General Inquiries**: Answer common questions

## Agent Structure

### Flows

1. **Default Start Flow**
   - Welcome message
   - Initial intent classification
   - Routes to specific flows

2. **Booking Flow**
   - Collect service type
   - Collect preferred date/time
   - Check availability (webhook to Phorest)
   - Confirm booking
   - Create appointment (webhook to Phorest)

3. **Information Flow**
   - Business hours
   - Services offered
   - Pricing information
   - Location/directions

4. **Manage Appointment Flow**
   - Lookup appointment (webhook)
   - Cancel appointment (webhook)
   - Reschedule appointment (webhook)

### Intents

#### Booking Intents
- `book.appointment` - User wants to book an appointment
- `check.availability` - User wants to check available times
- `select.service` - User selects a specific service

#### Information Intents
- `get.business.hours` - User asks about business hours
- `get.services` - User asks about available services
- `get.pricing` - User asks about pricing
- `get.location` - User asks about location/directions

#### Management Intents
- `cancel.appointment` - User wants to cancel
- `reschedule.appointment` - User wants to reschedule
- `lookup.appointment` - User wants to check their appointment

### Entities

- **@service**: Types of services offered (haircut, color, styling, etc.)
- **@sys.date**: Appointment dates
- **@sys.time**: Appointment times
- **@sys.phone-number**: Customer phone numbers
- **@sys.email**: Customer emails
- **@appointment-id**: Appointment reference numbers

### Parameters

Session parameters stored across the conversation:
- `customer_phone`: Customer's phone number
- `customer_email`: Customer's email address
- `customer_name`: Customer's name
- `selected_service`: Service they want to book
- `selected_date`: Preferred date
- `selected_time`: Preferred time
- `appointment_id`: ID of created/managed appointment

## Webhook Configuration

The agent uses webhooks to integrate with backend services:

**Webhook URL**: `https://your-domain.com/dialogflow/webhook`

**Webhook Secret**: Set in environment variable `DIALOGFLOW_WEBHOOK_SECRET`

### Webhook Handlers

The following intents trigger webhook calls:

1. **book.appointment**
   - Creates appointment in Phorest
   - Returns confirmation details

2. **check.availability**
   - Queries Phorest for available slots
   - Returns list of available times

3. **cancel.appointment**
   - Cancels appointment in Phorest
   - Sends confirmation

4. **lookup.appointment**
   - Retrieves appointment details from Phorest
   - Returns appointment information

## Telephony Integration

The agent integrates with Telnyx for voice calls:

1. **Inbound Calls**: Telnyx forwards calls to Dialogflow
2. **Outbound Calls**: Agent can initiate calls for confirmations/reminders
3. **DTMF Support**: Handle phone menu inputs
4. **Call Recording**: Optional call recording for quality assurance

### Telnyx Configuration

1. Set up SIP connection in Telnyx
2. Configure Dialogflow CX telephony integration
3. Set webhook URL for call events
4. Configure call forwarding rules

## Setup Instructions

### 1. Create Dialogflow CX Agent

1. Go to [Dialogflow CX Console](https://dialogflow.cloud.google.com/cx)
2. Create a new agent:
   - **Name**: Senda AI
   - **Location**: us-central1 (or your preferred region)
   - **Time Zone**: Your business timezone
   - **Default Language**: English

3. Note the Agent ID from the settings page

### 2. Configure Environment Variables

Add to your `.env` file:

```env
DIALOGFLOW_PROJECT_ID=your-gcp-project-id
DIALOGFLOW_LOCATION=us-central1
DIALOGFLOW_AGENT_ID=your-agent-id
DIALOGFLOW_WEBHOOK_SECRET=your-secret-token
```

### 3. Create Flows

Follow the flow structure outlined above to create each flow in the Dialogflow CX console.

### 4. Create Intents

Create intents with training phrases for each intent listed above.

### 5. Set Up Webhooks

1. In Dialogflow CX, go to **Manage** > **Webhooks**
2. Create webhook:
   - **Display Name**: Senda API
   - **Webhook URL**: `https://your-domain.com/dialogflow/webhook`
   - **Authentication**: Add `X-Webhook-Secret` header with your secret
   - **Timeout**: 30 seconds

3. Enable webhook for relevant intents

### 6. Configure Telephony

1. In Dialogflow CX, go to **Manage** > **Integrations**
2. Enable **Dialogflow CX Phone Gateway** or **Telnyx**
3. Configure phone number routing
4. Set up call forwarding from Telnyx

### 7. Test the Agent

1. Use the built-in simulator in Dialogflow CX console
2. Test with sample phrases:
   - "I'd like to book an appointment"
   - "What are your hours?"
   - "Check my appointment"

3. Test telephony integration by calling your Telnyx number

## Agent Export/Import

To export the agent configuration:
```bash
# Using gcloud CLI
gcloud dialogflow-cx agents export \
  --agent=projects/PROJECT_ID/locations/LOCATION/agents/AGENT_ID \
  --output-file=agent-export.json
```

To import:
```bash
gcloud dialogflow-cx agents import \
  --agent=projects/PROJECT_ID/locations/LOCATION/agents/AGENT_ID \
  --source-file=agent-export.json
```

## Monitoring and Debugging

- **Dialogflow CX Console**: View conversation logs and analytics
- **Google Cloud Logging**: View webhook logs
- **API Logs**: Check FastAPI logs for webhook processing

## Best Practices

1. **Keep conversations natural**: Use varied training phrases
2. **Handle errors gracefully**: Provide fallback responses
3. **Test thoroughly**: Test all conversation paths
4. **Monitor performance**: Track success rates and common failures
5. **Update regularly**: Add new training phrases based on real conversations

## Resources

- [Dialogflow CX Documentation](https://cloud.google.com/dialogflow/cx/docs)
- [Webhook Reference](https://cloud.google.com/dialogflow/cx/docs/reference/rest/v3/Webhook)
- [Telephony Integration](https://cloud.google.com/dialogflow/cx/docs/concept/integration/phone-gateway)
- [Best Practices](https://cloud.google.com/dialogflow/cx/docs/concept/best-practices)
