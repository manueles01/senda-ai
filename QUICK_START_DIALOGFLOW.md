# Quick Start: Getting Dialogflow CX Working

Your Dialogflow CX integration is now ready! Here's how to get it working:

## What Was Built

✓ **Dialogflow webhook endpoint** at `/dialogflow/webhook`
✓ **Intent handlers** for booking, availability, business hours, and cancellations
✓ **Configuration** for Dialogflow CX settings
✓ **Complete documentation** for setup

## Quick Start Steps

### 1. Update Your .env File

Add these new variables to your `.env` file:

```env
# Telnyx
TELNYX_PHONE_NUMBER=+16815080516

# Dialogflow CX
DIALOGFLOW_PROJECT_ID=your-google-project-id
DIALOGFLOW_LOCATION=us-central1
DIALOGFLOW_AGENT_ID=your-agent-id-here
DIALOGFLOW_WEBHOOK_SECRET=generate-a-random-secret
```

To generate a webhook secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Create Dialogflow CX Agent

1. Go to [https://dialogflow.cloud.google.com/cx](https://dialogflow.cloud.google.com/cx)
2. Click **Create Agent**
3. Name it "Senda AI Assistant"
4. Choose location: `us-central1`
5. Copy the Agent ID from settings

### 3. Set Up Webhook URL

**For local testing:**
```bash
# Terminal 1: Start your API
cd apps/api
uvicorn app.main:app --port 8000

# Terminal 2: Start ngrok
ngrok http 8000
```

Copy the ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`)

Your webhook URL is: `https://abc123.ngrok.io/dialogflow/webhook`

### 4. Configure Webhook in Dialogflow

1. In Dialogflow CX Console, go to **Manage** > **Webhooks**
2. Click **+ Create**
3. Fill in:
   - Display Name: `Senda API Webhook`
   - URL: `https://your-ngrok-url/dialogflow/webhook`
   - Add header: `X-Webhook-Secret` = your secret from .env

### 5. Create Your First Intent

1. Go to **Manage** > **Intents**
2. Click **+ Create**
3. Display Name: `book.appointment`
4. Add training phrases:
   - "I'd like to book an appointment"
   - "Schedule a haircut"
   - "Book me in"

5. Enable webhook for this intent
6. Select your webhook: `Senda API Webhook`

### 6. Test It!

**Test in Dialogflow Console:**
1. Click **Test Agent** (top right)
2. Type: "I'd like to book an appointment"
3. Should trigger your webhook

**Check your API logs:**
```
INFO: Received Dialogflow webhook request: {...}
```

**Test the webhook directly:**
```bash
curl -X POST https://your-ngrok-url/dialogflow/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-secret" \
  -d '{
    "intentInfo": {"displayName": "book.appointment"},
    "sessionInfo": {"parameters": {}},
    "text": "I want to book an appointment"
  }'
```

## Available Endpoints

After setup, your API will have:

- `GET /` - Root endpoint
- `GET /health` - API health check
- `GET /dialogflow/health` - Dialogflow webhook health check
- `POST /dialogflow/webhook` - Main Dialogflow webhook
- `GET /docs` - Interactive API documentation

## Current Intent Handlers

Your webhook already handles these intents:

1. **book.appointment** - Books appointments (placeholder, needs Phorest integration)
2. **check.availability** - Checks available slots
3. **get.business.hours** - Returns business hours
4. **cancel.appointment** - Cancels appointments
5. **default** - Fallback handler

## Next Steps

1. **Follow the complete guide**: See [DIALOGFLOW_SETUP.md](./DIALOGFLOW_SETUP.md)
2. **Build out intents**: Add more intents and training phrases
3. **Add Phorest integration**: Connect real booking system
4. **Set up telephony**: Connect Telnyx for voice calls
5. **Add AI responses**: Integrate Claude or Gemini for intelligent responses

## Testing Checklist

- [ ] .env file updated with Dialogflow settings
- [ ] Dialogflow CX agent created
- [ ] Webhook configured in Dialogflow
- [ ] At least one intent created and webhook-enabled
- [ ] Tested in Dialogflow console
- [ ] Webhook receiving requests (check API logs)
- [ ] Responses returning correctly

## Troubleshooting

**Webhook not being called?**
- Check webhook is enabled on the intent
- Verify webhook URL is accessible (test with curl)
- Check authentication header matches

**Getting 401 errors?**
- Verify `X-Webhook-Secret` header matches your `.env` value
- Check no extra spaces in environment variable

**Agent not responding?**
- Check training phrases match user input
- Verify intent is enabled
- Check API logs for errors

## Resources

- **Detailed Setup**: [DIALOGFLOW_SETUP.md](./DIALOGFLOW_SETUP.md)
- **Agent Architecture**: [apps/agent/README.md](./apps/agent/README.md)
- **API Docs**: http://localhost:8000/docs (when server is running)
- **Dialogflow CX Docs**: https://cloud.google.com/dialogflow/cx/docs

Need help? Check the logs or review the detailed setup guide!
