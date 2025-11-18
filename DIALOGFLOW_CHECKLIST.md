# Dialogflow Setup Checklist

Follow these steps in order. Check off each item as you complete it.

## Prerequisites Checklist

- [ ] Google Cloud account created
- [ ] Telnyx account with phone number (+16815080516)
- [ ] FastAPI running locally (tested in previous steps)
- [ ] Git repository cloned and up to date

## Step 1: Update Your .env File

1. Open your `.env` file in the root directory
2. Add/update these values:

```env
# Telnyx (you already have this)
TELNYX_PHONE_NUMBER=+16815080516

# Dialogflow CX - UPDATE THESE
DIALOGFLOW_PROJECT_ID=
DIALOGFLOW_LOCATION=us-central1
DIALOGFLOW_AGENT_ID=
DIALOGFLOW_WEBHOOK_SECRET=
```

3. Generate a webhook secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

4. Copy the output and paste it as your `DIALOGFLOW_WEBHOOK_SECRET`

**Checklist:**
- [ ] .env file has TELNYX_PHONE_NUMBER
- [ ] Generated and added DIALOGFLOW_WEBHOOK_SECRET
- [ ] DIALOGFLOW_LOCATION set to us-central1

**Note:** You'll fill in DIALOGFLOW_PROJECT_ID and DIALOGFLOW_AGENT_ID in later steps.

---

## Step 2: Test Your API Locally

1. Make sure you pulled the latest code:
```bash
git pull origin claude/fix-pydantic-settings-0175i5qfAarSu8iN1k9eJdHA
```

2. Start your API server:
```bash
cd apps/api
uvicorn app.main:app --port 8000 --reload
```

3. In a NEW terminal, test the endpoints:
```bash
# Test root
curl http://localhost:8000/

# Test health
curl http://localhost:8000/health

# Test Dialogflow health
curl http://localhost:8000/dialogflow/health
```

**Expected responses:**
- Root: `{"message":"Welcome to Senda AI API","status":"running"}`
- Health: `{"status":"healthy","app_name":"Senda AI API"}`
- Dialogflow health: `{"status":"healthy","service":"dialogflow-webhook","configured":false}`

**Checklist:**
- [ ] API server running on port 8000
- [ ] All three endpoints responding successfully
- [ ] No errors in terminal

---

## Step 3: Set Up ngrok (For Testing)

ngrok creates a public HTTPS URL for your local server.

1. Download ngrok from https://ngrok.com/download (if not installed)

2. In a NEW terminal (keep API running), start ngrok:
```bash
ngrok http 8000
```

3. You'll see output like:
```
Forwarding  https://abc123xyz.ngrok.io -> http://localhost:8000
```

4. **COPY THE HTTPS URL** (e.g., `https://abc123xyz.ngrok.io`)

5. Test your ngrok URL:
```bash
curl https://YOUR-NGROK-URL/dialogflow/health
```

**Checklist:**
- [ ] ngrok installed and running
- [ ] HTTPS URL copied
- [ ] URL accessible from internet (curl test works)
- [ ] Keep ngrok running (don't close the terminal)

**Your webhook URL is:** `https://YOUR-NGROK-URL/dialogflow/webhook`

---

## Step 4: Create Google Cloud Project

1. Go to https://console.cloud.google.com/

2. Click "Select a project" → "New Project"
   - Project name: `Senda AI`
   - Click "Create"

3. **COPY THE PROJECT ID** (shown on the dashboard)
   - It looks like: `senda-ai-123456`

4. Update your `.env` file:
```env
DIALOGFLOW_PROJECT_ID=senda-ai-123456  # Your actual project ID
```

5. Enable Dialogflow CX API:
   - Go to https://console.cloud.google.com/apis/library
   - Search for "Dialogflow CX API"
   - Click it, then click "Enable"

**Checklist:**
- [ ] Google Cloud project created
- [ ] Project ID copied
- [ ] .env updated with DIALOGFLOW_PROJECT_ID
- [ ] Dialogflow CX API enabled

---

## Step 5: Create Dialogflow CX Agent

1. Go to https://dialogflow.cloud.google.com/cx

2. Make sure your project is selected (top bar)

3. Click "Create Agent"
   - Display name: `Senda AI Assistant`
   - Location: `us-central1`
   - Time zone: Your timezone
   - Default language: `English - en`
   - Click "Create"

4. After creation, go to **Agent Settings** (gear icon)

5. **COPY THE AGENT ID** from the URL or settings
   - URL looks like: `.../agents/YOUR-AGENT-ID`
   - The Agent ID is a UUID like: `12345678-1234-1234-1234-123456789abc`

6. Update your `.env` file:
```env
DIALOGFLOW_AGENT_ID=12345678-1234-1234-1234-123456789abc  # Your actual agent ID
```

**Checklist:**
- [ ] Dialogflow CX agent created
- [ ] Agent ID copied
- [ ] .env updated with DIALOGFLOW_AGENT_ID

---

## Step 6: Configure Webhook in Dialogflow

1. In Dialogflow CX Console, click **Manage** tab (left sidebar)

2. Click **Webhooks**

3. Click **+ Create**

4. Fill in:
   - Display name: `Senda API Webhook`
   - Webhook URL: `https://YOUR-NGROK-URL/dialogflow/webhook`
   - Timeout: `30` seconds

5. Add authentication header:
   - Click "+ Add header"
   - Header name: `X-Webhook-Secret`
   - Header value: (paste your DIALOGFLOW_WEBHOOK_SECRET from .env)

6. Click **Save**

7. Test the webhook:
```bash
# Replace with your values
curl -X POST https://YOUR-NGROK-URL/dialogflow/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR-SECRET-FROM-ENV" \
  -d '{
    "intentInfo": {"displayName": "test"},
    "sessionInfo": {"parameters": {}},
    "text": "test"
  }'
```

**Expected response:** JSON with fulfillment response

**Checklist:**
- [ ] Webhook created in Dialogflow
- [ ] Webhook URL set correctly
- [ ] Authentication header added
- [ ] Webhook test successful

---

## Step 7: Create Your First Intent

1. In Dialogflow CX, click **Build** tab

2. Click **Intents** (under Manage section)

3. Click **+ Create**

4. Fill in:
   - Display name: `book.appointment`

5. Add training phrases (click "+ Add training phrase"):
   - "I'd like to book an appointment"
   - "Schedule a haircut"
   - "Book me in for tomorrow"
   - "I need an appointment"
   - "Can I make a booking"

6. Scroll down to **Webhook** section
   - Enable: "Call webhook"
   - Select webhook: `Senda API Webhook`
   - Tag: `book-appointment`

7. Click **Save**

**Checklist:**
- [ ] Intent created: book.appointment
- [ ] Training phrases added (at least 5)
- [ ] Webhook enabled for this intent
- [ ] Intent saved

---

## Step 8: Test Everything!

### Test in Dialogflow Console:

1. Click **Test Agent** (top right corner)

2. Type: "I'd like to book an appointment"

3. The agent should respond with:
   > "I'll help you book a service appointment for  at . Let me check availability with Phorest."

4. Check your API terminal - you should see:
   ```
   INFO: Received Dialogflow webhook request: ...
   ```

**Checklist:**
- [ ] Test agent opens
- [ ] Agent responds to test message
- [ ] Webhook request appears in API logs
- [ ] No errors in API logs

### Test Other Intents:

Create more intents to test:

1. **get.business.hours** intent:
   - Training phrases: "What are your hours?", "When are you open?"
   - Enable webhook
   - Test: Should respond with business hours

**Checklist:**
- [ ] All created intents working
- [ ] Webhook being called for each intent
- [ ] Responses making sense

---

## Step 9: Monitor and Debug

### Check API Logs:
Watch your uvicorn terminal for:
```
INFO: Received Dialogflow webhook request: ...
```

### Check Dialogflow Logs:
1. In Dialogflow CX, go to **Analyze** → **Logs**
2. See all test conversations

### Common Issues:

**"Webhook timeout" error:**
- Check your API is running
- Check ngrok is running
- Verify webhook URL is correct

**"401 Unauthorized" error:**
- Check X-Webhook-Secret header matches .env value
- No extra spaces in environment variable

**"Agent not responding":**
- Check training phrases match your input
- Verify intent is enabled
- Check webhook is enabled on intent

**Checklist:**
- [ ] Can see webhook requests in API logs
- [ ] Can see conversations in Dialogflow logs
- [ ] No error messages

---

## Step 10: Next Steps

Now that basic webhook is working:

1. **Add more intents:**
   - check.availability
   - cancel.appointment
   - get.services

2. **Add flows:**
   - Create a booking flow with multiple pages
   - Collect service, date, time

3. **Integrate Phorest:**
   - Update webhook handlers to call Phorest API
   - Make real bookings

4. **Add AI responses:**
   - Integrate Claude or Gemini for intelligent responses

5. **Set up telephony:**
   - Connect Telnyx for voice calls
   - Test phone conversations

**Checklist:**
- [ ] Ready to add more intents
- [ ] Ready to integrate Phorest
- [ ] Ready to add AI responses

---

## Troubleshooting Guide

### API won't start:
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt

# Check for syntax errors
cd apps/api
python -m py_compile app/main.py
```

### ngrok issues:
```bash
# Check ngrok is installed
ngrok version

# Restart ngrok
# Kill existing ngrok process
# Start fresh: ngrok http 8000
```

### Dialogflow webhook not working:
```bash
# Test webhook directly
curl -X POST https://YOUR-NGROK-URL/dialogflow/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR-SECRET" \
  -d '{"intentInfo":{"displayName":"test"}}'

# Check API logs for error details
# Check Dialogflow logs under Analyze > Logs
```

---

## Summary

When everything is working, you should have:

✅ FastAPI server running on localhost:8000
✅ ngrok exposing API to internet
✅ Dialogflow CX agent created
✅ Webhook configured and working
✅ At least one intent (book.appointment) working
✅ Test agent responding correctly
✅ Webhook requests appearing in API logs

**Next:** Follow DIALOGFLOW_SETUP.md for advanced configuration!

---

## Quick Command Reference

```bash
# Start API
cd apps/api && uvicorn app.main:app --port 8000 --reload

# Start ngrok (in new terminal)
ngrok http 8000

# Test API health
curl http://localhost:8000/health

# Test Dialogflow health
curl http://localhost:8000/dialogflow/health

# Test webhook
curl -X POST https://YOUR-NGROK-URL/dialogflow/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR-SECRET" \
  -d '{"intentInfo":{"displayName":"book.appointment"}}'

# Generate webhook secret
python -c "import secrets; print(secrets.token_hex(32))"
```

---

**Need help?** Check the detailed guide: [DIALOGFLOW_SETUP.md](./DIALOGFLOW_SETUP.md)
