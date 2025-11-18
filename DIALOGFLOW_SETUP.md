# Dialogflow CX Setup Guide for Senda AI

This guide will walk you through setting up Dialogflow CX to work with your Senda AI FastAPI application.

## Prerequisites

- ✓ Google Cloud Platform account
- ✓ FastAPI application running (completed in previous steps)
- ✓ Telnyx account with phone number
- ✓ Public URL for webhooks (use ngrok for local development)

## Step 1: Set Up Google Cloud Project

### 1.1 Create or Select Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing:
   - Project Name: `Senda AI`
   - Note your Project ID (e.g., `senda-ai-12345`)

### 1.2 Enable Required APIs

```bash
# Enable Dialogflow CX API
gcloud services enable dialogflow.googleapis.com

# Enable other required APIs
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable iam.googleapis.com
```

Or enable via Cloud Console:
1. Go to **APIs & Services** > **Library**
2. Search for "Dialogflow CX API"
3. Click **Enable**

### 1.3 Set Up Service Account (for API access)

```bash
# Create service account
gcloud iam service-accounts create senda-dialogflow \
    --display-name="Senda Dialogflow Service Account"

# Grant Dialogflow API Client role
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:senda-dialogflow@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/dialogflow.client"

# Create and download key
gcloud iam service-accounts keys create ~/senda-dialogflow-key.json \
    --iam-account=senda-dialogflow@PROJECT_ID.iam.gserviceaccount.com
```

## Step 2: Create Dialogflow CX Agent

### 2.1 Create Agent via Console

1. Go to [Dialogflow CX Console](https://dialogflow.cloud.google.com/cx)
2. Click **Create Agent**
3. Configure agent:
   - **Display Name**: `Senda AI Assistant`
   - **Location**: `us-central1` (or your preferred region)
   - **Default Time Zone**: Your business timezone
   - **Default Language**: `English - en`

4. Click **Create**

### 2.2 Note Agent Information

After creation, go to **Agent Settings**:
- Copy the **Agent ID** (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
- Note the **Project ID**
- Note the **Location**

### 2.3 Update Environment Variables

Add to your `.env` file:

```env
# Dialogflow CX Configuration
DIALOGFLOW_PROJECT_ID=your-project-id
DIALOGFLOW_LOCATION=us-central1
DIALOGFLOW_AGENT_ID=your-agent-id-here
DIALOGFLOW_WEBHOOK_SECRET=your-random-secret-token-here
```

Generate a secure webhook secret:
```bash
# Linux/Mac
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 3: Configure Webhook URL

### 3.1 For Local Development (Using ngrok)

```bash
# Install ngrok if not already installed
# Download from https://ngrok.com/download

# Start your FastAPI server
cd apps/api
uvicorn app.main:app --port 8000

# In another terminal, start ngrok
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

Your webhook URL will be: `https://abc123.ngrok.io/dialogflow/webhook`

### 3.2 For Production

Deploy your FastAPI application to:
- **Google Cloud Run**
- **Google App Engine**
- **AWS/Azure/Other Cloud Provider**
- **Your own server with HTTPS**

Your webhook URL will be: `https://your-domain.com/dialogflow/webhook`

### 3.3 Test Webhook Endpoint

```bash
# Test that your webhook is accessible
curl https://your-webhook-url/dialogflow/health

# Should return:
# {"status":"healthy","service":"dialogflow-webhook","configured":true}
```

## Step 4: Create Intents and Flows

### 4.1 Create Booking Intent

1. In Dialogflow CX Console, go to **Manage** > **Intents**
2. Click **+ Create**
3. Configure:
   - **Display Name**: `book.appointment`
   - **Training Phrases**: Add phrases like:
     - "I'd like to book an appointment"
     - "Schedule a haircut"
     - "Book me in for tomorrow"
     - "I need to make an appointment"
     - "Can I book a service?"

4. Click **Save**

### 4.2 Create Entities

1. Go to **Manage** > **Entity Types**
2. Create custom entity for services:
   - **Display Name**: `service`
   - **Entities**:
     - `haircut`: haircut, cut, trim
     - `coloring`: color, coloring, dye, highlights
     - `styling`: styling, style, blowout
     - `treatment`: treatment, deep conditioning

### 4.3 Create Booking Flow

1. Go to **Build** > **Flows**
2. Click **+ Create**
3. **Display Name**: `Booking Flow`
4. Add pages for conversation steps:
   - Collect Service
   - Collect Date
   - Collect Time
   - Confirm Details
   - Complete Booking

For each page:
- Add **Parameters** to collect (service, date, time)
- Add **Entry Fulfillment** (what agent says)
- Add **Routes** (how to move to next page)
- Enable **Webhook** where needed

## Step 5: Set Up Webhook Integration

### 5.1 Create Webhook

1. Go to **Manage** > **Webhooks**
2. Click **+ Create**
3. Configure:
   - **Display Name**: `Senda API Webhook`
   - **Webhook URL**: `https://your-domain.com/dialogflow/webhook`
   - **Timeout**: `30` seconds

4. Add authentication header:
   - **Header Name**: `X-Webhook-Secret`
   - **Header Value**: Your secret from `.env`

5. Click **Save**

### 5.2 Enable Webhook for Intents

For each intent that needs backend processing:

1. Go to the intent (e.g., `book.appointment`)
2. Scroll to **Webhook** section
3. Select your webhook: `Senda API Webhook`
4. Choose when to call:
   - **Webhook**: Call webhook
   - **Tag**: `book-appointment` (for identifying in code)

## Step 6: Integrate with Telnyx

### 6.1 Configure Telnyx Integration

1. In Dialogflow CX, go to **Manage** > **Integrations**
2. Look for **Telephony** options
3. Choose integration method:
   - **Dialogflow CX Phone Gateway** (Google's built-in)
   - **Custom SIP Integration** (for Telnyx)

### 6.2 For Dialogflow Phone Gateway

1. Enable **Dialogflow CX Phone Gateway**
2. Copy the **Phone Number** or **SIP URI**
3. In Telnyx:
   - Go to your phone number settings
   - Set **Call Forwarding** to Dialogflow's SIP URI
   - Or use **SIP Connection** to route calls

### 6.3 For Direct Telnyx Integration

Create a webhook in Telnyx to forward calls to your API:

1. In Telnyx, create **Call Control Application**
2. Set **Webhook URL**: `https://your-domain.com/telnyx/call-webhook`
3. In your FastAPI app, create Telnyx webhook handler that:
   - Answers call
   - Starts Dialogflow session
   - Streams audio to/from Dialogflow
   - Handles DTMF inputs

(This requires additional code - see advanced integration docs)

## Step 7: Test Your Agent

### 7.1 Test in Dialogflow Console

1. Go to **Test Agent** (top right)
2. Try conversations:
   ```
   User: "I'd like to book an appointment"
   Agent: "I can help you with that. What service would you like?"
   User: "A haircut"
   Agent: "Great! What date works for you?"
   ```

3. Check that webhook is being called:
   - Look for webhook indicators in test console
   - Check your API logs for incoming requests

### 7.2 Test API Logs

In your terminal running uvicorn, you should see:
```
INFO: Received Dialogflow webhook request: {...}
```

### 7.3 Test via Phone

1. Call your Telnyx phone number
2. Speak to the agent
3. Test full conversation flow

## Step 8: Monitor and Debug

### 8.1 View Logs in Dialogflow

1. Go to **Analyze** > **Logs**
2. View conversation transcripts
3. Check for errors or unhandled intents

### 8.2 View Logs in Google Cloud

```bash
# View Dialogflow logs
gcloud logging read "resource.type=dialogflow_agent" --limit 50

# View webhook logs (if running on Cloud Run)
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### 8.3 Debug Webhook Issues

Common issues:
- **401 Unauthorized**: Check webhook secret matches
- **Timeout**: Webhook took too long (> 30s)
- **500 Error**: Check API logs for exceptions

Test webhook locally:
```bash
curl -X POST https://your-webhook-url/dialogflow/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-secret" \
  -d '{
    "intentInfo": {"displayName": "book.appointment"},
    "sessionInfo": {"parameters": {}},
    "text": "I want to book an appointment"
  }'
```

## Next Steps

1. ✓ Implement Phorest integration for real booking
2. ✓ Add Claude AI for intelligent responses
3. ✓ Set up appointment reminders via Telnyx SMS
4. ✓ Add analytics and reporting
5. ✓ Deploy to production

## Resources

- [Dialogflow CX Docs](https://cloud.google.com/dialogflow/cx/docs)
- [Webhook Guide](https://cloud.google.com/dialogflow/cx/docs/concept/webhook)
- [Telephony Integration](https://cloud.google.com/dialogflow/cx/docs/concept/integration/phone-gateway)
- [Telnyx Docs](https://developers.telnyx.com/)
- [Senda AI Agent README](./apps/agent/README.md)

## Troubleshooting

### Webhook Not Being Called

1. Check webhook is enabled on intent
2. Verify webhook URL is accessible (test with curl)
3. Check authentication header is correct
4. Look for errors in Dialogflow logs

### Authentication Errors

1. Verify `X-Webhook-Secret` header matches `.env` value
2. Check no extra spaces in environment variable
3. Test webhook endpoint with correct header

### Agent Not Responding Correctly

1. Check training phrases cover user inputs
2. Verify entities are being extracted
3. Check parameter mapping
4. Review conversation flow logic

## Support

For issues with:
- **Dialogflow**: [Dialogflow Support](https://cloud.google.com/dialogflow/docs/support)
- **Senda AI**: Check application logs and GitHub issues
- **Telnyx**: [Telnyx Support](https://telnyx.com/support)
