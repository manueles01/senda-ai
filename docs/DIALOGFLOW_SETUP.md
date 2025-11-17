# Dialogflow CX Setup Guide for salon-voice-system

## Prerequisites
- Google Cloud project: `salon-voice-system` ✓ (you already have this!)
- Billing enabled on the project
- Owner or Editor permissions

## Step 1: Enable Required APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project: **salon-voice-system**
3. Navigate to **APIs & Services > Library**
4. Search for and enable these APIs:
   - **Dialogflow API**
   - **Cloud Text-to-Speech API**
   - **Cloud Speech-to-Text API**
   - **Generative AI API** (for Gemini)

Or use the command line:

```bash
# Set your project
gcloud config set project salon-voice-system

# Enable APIs
gcloud services enable dialogflow.googleapis.com
gcloud services enable texttospeech.googleapis.com
gcloud services enable speech.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

## Step 2: Create Service Account & Download Credentials

1. Go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Name: `senda-ai-service`
4. Click **Create and Continue**
5. Grant these roles:
   - **Dialogflow API Client**
   - **Dialogflow API Admin**
   - Click **Continue**, then **Done**

6. Click on the service account you just created
7. Go to **Keys** tab
8. Click **Add Key > Create New Key**
9. Choose **JSON**
10. Save the downloaded file as `service-account-key.json` in your project root

```bash
# Move the downloaded key to your project
mv ~/Downloads/salon-voice-system-*.json ~/senda-ai/service-account-key.json
```

## Step 3: Create Dialogflow CX Agent (EASY WAY)

1. Go to [Dialogflow CX Console](https://dialogflow.cloud.google.com/cx/projects)
2. Select project: **salon-voice-system**
3. Click **Create Agent**
4. Fill in:
   - **Display Name**: `Senda AI Receptionist`
   - **Location**: `us-central1`
   - **Default Time Zone**: `America/New_York` (or your timezone)
   - **Default Language**: `en - English`
5. Click **Create**

**IMPORTANT**: After creation, look at the URL. It will be:
```
https://dialogflow.cloud.google.com/cx/projects/salon-voice-system/locations/us-central1/agents/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

Copy that UUID (the XXXXXXXX part) - that's your **AGENT_ID**.

## Step 4: Configure Agent Voice Settings

1. In your agent, click **Agent Settings** (gear icon at top)
2. Go to **Speech and IVR** tab:
   - **Enable speech adaptation**: ON
   - **Speech model**: `phone_call`
   - **No-speech timeout**: `5s`
   - **Endpointer sensitivity**: `50`

3. Go to **Text to Speech** tab:
   - **Voice**: `en-US-Neural2-F` (female, natural)
   - **Speaking rate**: `1.0`
   - **Pitch**: `0`
   - **Effects profile**: Check `telephony-class-application`

4. Click **Save**

## Step 5: Build Your First Simple Flow

Let's start simple to test everything works:

### Edit the Start Flow

1. Click **Build** in left sidebar
2. You'll see **Default Start Flow**
3. Click on the **Start** page
4. In **Entry fulfillment** section:
   - Click **Add dialogue option > Agent says**
   - Type: "Thank you for calling Senda Salon! I'm your AI assistant. I can help you book appointments, check our hours, or answer questions about our services. How can I help you today?"

5. Click **Save**

### Add a Simple Intent & Response

1. Click **Manage > Intents**
2. Click **Create**
3. Create intent: `hours_inquiry`
   - Training phrases:
     - "What are your hours"
     - "When are you open"
     - "What time do you close"
   - Click **Save**

4. Go back to **Build > Default Start Flow**
5. On the **Start** page, scroll to **Routes**
6. Click **Add route**:
   - **Intent**: Select `hours_inquiry`
   - **Fulfillment**: Agent says "We're open Monday through Friday from 9 AM to 8 PM, Saturday from 9 AM to 6 PM, and Sunday from 10 AM to 5 PM. Would you like to book an appointment?"
   - Click **Save route**

## Step 6: Test in Dialogflow Simulator

1. Click **Test Agent** button (right sidebar with play icon)
2. Type: "Hi"
   - Should respond with your greeting
3. Type: "What are your hours"
   - Should respond with hours
4. Great! It's working!

## Step 7: Get a Test Phone Number (Optional but FUN!)

1. In your agent, click **Integrations** (bottom of left sidebar)
2. Click **Dialogflow Phone Gateway**
3. Click **Manage**
4. Click **Create phone number**
5. Select a region and you'll get a FREE temporary number
6. Call it and test your agent!

Note: This number is free but expires in 7 days. Use Telnyx for production.

## Step 8: Update Your .env File

Now that everything is created, update your configuration:

```bash
cd ~/senda-ai
nano .env  # or vim, whatever you prefer
```

Update these values:

```env
# Application
DEBUG=true

# Google Cloud
GOOGLE_PROJECT_ID=salon-voice-system
FIREBASE_PROJECT_ID=salon-voice-system
GEMINI_MODEL=gemini-1.5-pro

# Dialogflow CX
DIALOGFLOW_AGENT_ID=YOUR_AGENT_UUID_FROM_STEP_3
DIALOGFLOW_LOCATION=us-central1

# Telnyx (your existing credentials)
TELEPHONY_TELNYX_API_KEY=your-telnyx-api-key
TELNYX_PUBLIC_KEY=your-telnyx-public-key

# Phorest (optional for now)
PHOREST_BRANCH_ID=
PHOREST_CLIENT_ID=
PHOREST_CLIENT_SECRET=
```

## Step 9: Set Up Local Environment

```bash
cd ~/senda-ai

# Make sure service account key is in place
ls -la service-account-key.json

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$PWD/service-account-key.json"

# Add to your shell profile so it persists
echo "export GOOGLE_APPLICATION_CREDENTIALS=\"$PWD/service-account-key.json\"" >> ~/.bashrc
source ~/.bashrc

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Start the API
uvicorn apps.api.app.main:app --reload --port 8000
```

## Step 10: Test the API Connection

Open another terminal and test:

```bash
# Health check
curl http://localhost:8000/health

# You should see:
# {
#   "status": "healthy",
#   "google_project": "salon-voice-system",
#   "dialogflow_configured": true,
#   "telnyx_configured": true
# }
```

## Step 11: Create More Complex Flows (When Ready)

Once the basics work, you can add the full appointment booking flow:

1. **Create "Appointment Booking" Flow**
2. **Add pages to collect**:
   - Service type
   - Date
   - Time
   - Customer name
   - Phone number
3. **Add webhook calls** to check availability and create bookings

See `apps/agent/flows/appointment-booking-flow.json` for the full structure.

## Step 12: Deploy to Production (When Ready)

### Option A: Deploy to Google Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/salon-voice-system/senda-ai --project salon-voice-system

# Deploy
gcloud run deploy senda-ai \
  --image gcr.io/salon-voice-system/senda-ai \
  --platform managed \
  --region us-central1 \
  --project salon-voice-system \
  --allow-unauthenticated
```

### Option B: Deploy to Railway/Render

Just connect your GitHub repo and they'll use the Dockerfile automatically.

## Step 13: Connect Telnyx to Your API

Once your API is deployed:

1. Get your public URL (e.g., `https://senda-ai-xyz.run.app`)
2. In Telnyx Portal:
   - Go to **Call Control Applications**
   - Create/edit application
   - Webhook URL: `https://senda-ai-xyz.run.app/webhooks/telnyx`
   - Assign your phone number

3. In Dialogflow:
   - Go to **Manage > Webhooks**
   - Create webhook
   - URL: `https://senda-ai-xyz.run.app/webhooks/dialogflow`

## Quick Troubleshooting

**Can't find my project?**
- Make sure you're logged into the right Google account
- Check billing is enabled

**APIs won't enable?**
- Enable billing on the project first

**Service account key not working?**
- Check the file path in GOOGLE_APPLICATION_CREDENTIALS
- Make sure the file is the JSON key (not P12)

**Agent not responding?**
- Check agent ID in .env matches the URL
- Verify GOOGLE_APPLICATION_CREDENTIALS is set
- Look at the Dialogflow logs in Cloud Console

## Next Steps After Setup

1. ✅ Test basic greeting and hours inquiry
2. Add appointment booking flow
3. Connect webhooks for availability checks
4. Integrate Phorest for real bookings
5. Add Gemini for smarter responses
6. Deploy to production
7. Connect Telnyx for your real phone number

Need help with any of these steps? Just ask!
