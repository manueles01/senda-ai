# Dialogflow CX Agent Build Guide - Senda AI

This guide shows you exactly what to build in the Dialogflow CX console for your salon appointment booking system.

## Overview

Good news! You already have complete agent configuration files in your repo:
- `apps/agent/agent-config.json` - Agent settings
- `apps/agent/intents.json` - All intent definitions with training phrases
- `apps/agent/entities.json` - Custom entities
- `apps/agent/flows/` - Conversation flow definitions

This guide will show you how to build it in the console step-by-step.

---

## Part 1: Create the Agent (5 minutes)

### Step 1: Go to Dialogflow CX Console

1. Open [https://dialogflow.cloud.google.com/cx](https://dialogflow.cloud.google.com/cx)
2. Select your Google Cloud project (or create one)
3. Click **"Create Agent"**

### Step 2: Configure Agent Settings

Fill in:
- **Display Name**: `Senda AI Receptionist`
- **Location**: `us-central1` (or your preferred region)
- **Time Zone**: `America/New_York` (or your timezone)
- **Default Language**: `English - en`

Click **Create**

### Step 3: Configure Advanced Settings

After creation, click the ⚙️ gear icon → **Agent Settings**:

**Speech and IVR Settings:**
- ✅ Enable **Speech Adaptation**
- **Endpointer Sensitivity**: `50` (medium sensitivity)
- **No Speech Timeout**: `5s`
- **Speech Model**: Select `phone_call` (optimized for telephony)
- ✅ Enable **DTMF** (keypad input)
  - **Max Digits**: `10`
  - **Finish Digit**: `#`

**Text-to-Speech:**
- **Voice**: `en-US-Neural2-F` (female neural voice)
- **Speaking Rate**: `1.0` (normal speed)
- **Effects Profile**: `telephony-class-application`

**Security:**
- **Retention**: `90 days`
- **Redaction**: Enable for PII data

Click **Save**

---

## Part 2: Create Custom Entities (10 minutes)

### Entity 1: @service

1. Go to **Manage** → **Entity Types**
2. Click **+ Create**
3. Fill in:
   - **Display Name**: `service`
   - **Enable fuzzy matching**: ✅
   - **Enable redaction**: ❌

4. Add entries (each with synonyms):

| **Entity Value** | **Synonyms** |
|------------------|--------------|
| `haircut` | haircut, cut, trim, hair cut |
| `coloring` | coloring, color, dye, highlights, lowlights, hair color |
| `manicure` | manicure, mani, nails, nail service |
| `pedicure` | pedicure, pedi, foot treatment |
| `facial` | facial, face treatment, skin care |
| `massage` | massage, body treatment |
| `styling` | styling, style, blow dry, blowout, updo |
| `treatment` | treatment, conditioning, hair treatment |

5. Click **Save**

### Entity 2: @time_preference

1. Click **+ Create**
2. Fill in:
   - **Display Name**: `time_preference`
   - **Enable fuzzy matching**: ✅

3. Add entries:

| **Entity Value** | **Synonyms** |
|------------------|--------------|
| `morning` | morning, am, early |
| `afternoon` | afternoon, midday, lunch time |
| `evening` | evening, night, pm, late |

4. Click **Save**

---

## Part 3: Create Intents (20 minutes)

You need to create these intents. I'll show you the most important ones:

### Intent 1: greeting

1. Go to **Manage** → **Intents**
2. Click **+ Create**
3. **Display Name**: `greeting`
4. Add **Training Phrases** (click "+ Add training phrase" for each):
   - hello
   - hi
   - hey
   - good morning
   - good afternoon
   - good evening
   - hi there
   - hey there

5. Click **Save**

### Intent 2: book_appointment

1. Click **+ Create**
2. **Display Name**: `book_appointment`
3. Add **Training Phrases**:
   - I need to book an appointment
   - I want to schedule an appointment
   - Can I book a haircut
   - I'd like to make an appointment
   - Schedule me for a service
   - I need a haircut
   - Book me in
   - I want to get my hair done
   - Can I get an appointment
   - I need an appointment

4. Click **Save**

### Intent 3: check_availability

1. Click **+ Create**
2. **Display Name**: `check_availability`
3. Add **Training Phrases**:
   - What times are available
   - Do you have any openings
   - Are you available on Monday
   - What's your availability
   - When can I come in
   - Do you have slots tomorrow
   - Check availability

4. Click **Save**

### Intent 4: cancel_appointment

1. Click **+ Create**
2. **Display Name**: `cancel_appointment`
3. Add **Training Phrases**:
   - I need to cancel my appointment
   - Cancel my booking
   - I can't make it
   - I need to cancel
   - Remove my appointment
   - I want to cancel

4. Click **Save**

### Intent 5: service_inquiry

1. Click **+ Create**
2. **Display Name**: `service_inquiry`
3. Add **Training Phrases**:
   - What services do you offer
   - What can you do
   - Tell me about your services
   - What treatments are available
   - Do you do haircuts
   - Do you offer coloring
   - What's on the menu

4. Click **Save**

### Intent 6: hours_inquiry

1. Click **+ Create**
2. **Display Name**: `hours_inquiry`
3. Add **Training Phrases**:
   - What are your hours
   - When are you open
   - What time do you close
   - Are you open on weekends
   - What's your schedule

4. Click **Save**

### Intent 7: pricing_inquiry

1. Click **+ Create**
2. **Display Name**: `pricing_inquiry`
3. Add **Training Phrases**:
   - How much does a haircut cost
   - What are your prices
   - How much for coloring
   - What's the price
   - How expensive is it
   - Cost of services

4. Click **Save**

### Intent 8: confirm_yes

1. Click **+ Create**
2. **Display Name**: `confirm_yes`
3. Add **Training Phrases**:
   - yes
   - yeah
   - yep
   - sure
   - that works
   - sounds good
   - perfect
   - correct

4. Click **Save**

### Intent 9: confirm_no

1. Click **+ Create**
2. **Display Name**: `confirm_no`
3. Add **Training Phrases**:
   - no
   - nope
   - not really
   - no thanks
   - that doesn't work

4. Click **Save**

---

## Part 4: Create the Appointment Booking Flow (30 minutes)

This is the main conversation flow for booking appointments.

### Step 1: Create the Flow

1. Go to **Build** → **Flows**
2. Click **+ Create**
3. **Display Name**: `Appointment Booking Flow`
4. **Description**: `Handles the appointment booking process`
5. Click **Save**

### Step 2: Create Flow Parameters

These are session-level variables that persist across the conversation:

1. In your new flow, click **Parameters** tab
2. Add these parameters:

| Parameter | Entity Type | Default Value |
|-----------|-------------|---------------|
| `service` | `@service` | - |
| `date` | `@sys.date` | - |
| `time` | `@sys.time` | - |
| `customer_name` | `@sys.person` | - |
| `customer_phone` | `@sys.phone-number` | - |
| `confirmation_number` | `@sys.any` | - |

### Step 3: Create Pages

Now create pages for each step of the booking process:

#### Page 1: Collect Service

1. In the flow, click **+ Add Page**
2. **Display Name**: `Collect Service`
3. Click on the page to edit it

4. **Entry fulfillment** (what agent says when entering this page):
   - Click **Entry fulfillment** → **Add dialogue option**
   - Add text: `What service would you like to book? We offer haircuts, coloring, manicures, pedicures, facials, and massages.`

5. **Parameters** (what to collect):
   - Click **+** under Parameters
   - **Display name**: `service`
   - **Entity type**: `@service`
   - **Required**: ✅
   - Click **Save**

6. **Route** (where to go next):
   - Click **Routes** → **+ Add route**
   - **Condition**: `$page.params.status = "FINAL"`
   - **Transition**: Select page → `Collect Date`
   - Click **Save**

#### Page 2: Collect Date

1. Click **+ Add Page**
2. **Display Name**: `Collect Date`

3. **Entry fulfillment**:
   - Add text: `Great! What date would you like to come in?`

4. **Parameters**:
   - **Display name**: `date`
   - **Entity type**: `@sys.date`
   - **Required**: ✅

5. **Route**:
   - **Condition**: `$page.params.status = "FINAL"`
   - **Transition**: → `Check Availability` (create this page next)

#### Page 3: Check Availability

1. Click **+ Add Page**
2. **Display Name**: `Check Availability`

3. **Entry fulfillment** with **WEBHOOK**:
   - Click **Entry fulfillment**
   - ✅ Enable **Webhook**
   - **Tag**: `check_availability` ⚠️ Important! This connects to your FastAPI webhook
   - Agent says (while webhook runs): `Let me check our availability for $session.params.date...`

4. **Parameters to send to webhook**:
   - `service`: `$session.params.service`
   - `date`: `$session.params.date`

5. **Route** (two options):
   - **Route 1** - If slots available:
     - **Condition**: `$session.params.available_times != null`
     - **Transition**: → `Collect Time`

   - **Route 2** - If no availability:
     - **Condition**: `$session.params.available_times = null`
     - **Fulfillment**: `I'm sorry, we don't have availability on that date. Would you like to try a different date?`
     - **Transition**: → `Collect Date`

#### Page 4: Collect Time

1. Click **+ Add Page**
2. **Display Name**: `Collect Time`

3. **Entry fulfillment**:
   - Add text: `I have the following times available: $session.params.available_times. Which time works best for you?`

4. **Parameters**:
   - **Display name**: `time`
   - **Entity type**: `@sys.time`
   - **Required**: ✅

5. **Route**:
   - **Condition**: `$page.params.status = "FINAL"`
   - **Transition**: → `Collect Customer Info`

#### Page 5: Collect Customer Info

1. Click **+ Add Page**
2. **Display Name**: `Collect Customer Info`

3. **Parameters** (collect both name and phone):
   - **Parameter 1**:
     - **Display name**: `customer_name`
     - **Entity type**: `@sys.person`
     - **Required**: ✅
     - **Prompt**: `May I have your name please?`

   - **Parameter 2**:
     - **Display name**: `customer_phone`
     - **Entity type**: `@sys.phone-number`
     - **Required**: ✅
     - **Prompt**: `And what's the best phone number to reach you?`

4. **Route**:
   - **Condition**: `$page.params.status = "FINAL"`
   - **Transition**: → `Confirm Booking`

#### Page 6: Confirm Booking

1. Click **+ Add Page**
2. **Display Name**: `Confirm Booking`

3. **Entry fulfillment**:
   - Add text: `Let me confirm: $session.params.service on $session.params.date at $session.params.time for $session.params.customer_name. Is that correct?`

4. **Routes** (two options):
   - **Route 1** - User confirms:
     - **Intent**: `confirm_yes`
     - **Transition**: → `Create Appointment`

   - **Route 2** - User declines:
     - **Intent**: `confirm_no`
     - **Fulfillment**: `No problem, let's start over.`
     - **Transition**: → `Collect Service`

#### Page 7: Create Appointment (WITH WEBHOOK)

1. Click **+ Add Page**
2. **Display Name**: `Create Appointment`

3. **Entry fulfillment** with **WEBHOOK**:
   - ✅ Enable **Webhook**
   - **Tag**: `book_appointment` ⚠️ Important!
   - Agent says: `Perfect! I'm booking your appointment now...`

4. **Parameters to send**:
   - `service`: `$session.params.service`
   - `date`: `$session.params.date`
   - `time`: `$session.params.time`
   - `customer_name`: `$session.params.customer_name`
   - `customer_phone`: `$session.params.customer_phone`

5. **Route** (after webhook completes):
   - **Condition**: `$session.params.booking_confirmed = true`
   - **Fulfillment**: `All set! Your $session.params.service is booked for $session.params.date at $session.params.time. Your confirmation number is $session.params.confirmation_number. We'll send you a reminder. Is there anything else I can help you with?`
   - **Transition**: → End Flow

---

## Part 5: Configure Default Start Flow (15 minutes)

### Step 1: Edit Default Start Flow

1. Go to **Build** → **Flows**
2. Click on **Default Start Flow**

### Step 2: Update Start Page

1. Click on **Start** page
2. **Entry fulfillment**:
   - Add text: `Thank you for calling Senda Salon! I'm your AI assistant. How can I help you today?`

### Step 3: Add Routes from Start

Add these routes to handle different user intents:

#### Route 1: Book Appointment

- **Intent requirement**: `book_appointment`
- **Transition target**: Flow → `Appointment Booking Flow`

#### Route 2: Check Availability

- **Intent requirement**: `check_availability`
- **Transition target**: Flow → `Appointment Booking Flow` → Page: `Collect Service`

#### Route 3: Service Inquiry (WITH WEBHOOK)

- **Intent requirement**: `service_inquiry`
- **Fulfillment**:
  - ✅ Enable **Webhook**
  - **Tag**: `get_services`
- **Transition**: Stay on Start page

#### Route 4: Hours Inquiry

- **Intent requirement**: `hours_inquiry`
- **Fulfillment**: `We're open Monday through Friday, 9 AM to 6 PM, and Saturday 10 AM to 4 PM. We're closed on Sundays. Would you like to book an appointment?`
- **Transition**: Stay on Start page

#### Route 5: Pricing Inquiry

- **Intent requirement**: `pricing_inquiry`
- **Fulfillment**: `Our prices vary by service. Haircuts start at $45, coloring from $80, and other services range from $30 to $150. Would you like to book something?`
- **Transition**: Stay on Start page

#### Route 6: Cancel Appointment (WITH WEBHOOK)

- **Intent requirement**: `cancel_appointment`
- **Fulfillment**:
  - ✅ Enable **Webhook**
  - **Tag**: `cancel_appointment`
  - Agent says: `I can help you cancel. May I have your phone number to look up your appointment?`

---

## Part 6: Set Up Webhook Integration (10 minutes)

### Step 1: Create Webhook

1. Go to **Manage** → **Webhooks**
2. Click **+ Create**
3. Fill in:
   - **Display Name**: `Senda API Webhook`
   - **Webhook URL**: Your API endpoint
     - Local (ngrok): `https://your-ngrok-url.ngrok.io/webhooks/dialogflow`
     - Production: `https://your-domain.com/webhooks/dialogflow`
   - **Timeout**: `10` seconds

4. **Authentication** (optional but recommended):
   - Add header: `X-Webhook-Secret`
   - Value: Your secret from `.env`

5. Click **Save**

### Step 2: Verify Webhook Tags Match Your Code

Make sure these tags in Dialogflow match your FastAPI handlers:

| Dialogflow Tag | FastAPI Handler Function | Purpose |
|----------------|-------------------------|---------|
| `check_availability` | `check_availability()` | Check available time slots |
| `book_appointment` | `book_appointment()` | Create booking in Phorest |
| `cancel_appointment` | `cancel_appointment()` | Cancel booking |
| `get_services` | `get_services()` | Get service list from Phorest |

**This is critical!** When Dialogflow sends a webhook request with tag `check_availability`, your FastAPI code looks for:

```python
if tag == "check_availability":
    return await check_availability(parameters)
```

---

## Part 7: Test Your Agent (15 minutes)

### Step 1: Test in Simulator

1. Click **Test Agent** (top right)
2. Try these conversations:

**Test 1: Full Booking Flow**
```
You: "I need to book a haircut"
Agent: "What service would you like to book?"
You: "haircut"
Agent: "Great! What date would you like to come in?"
You: "tomorrow"
Agent: "Let me check our availability..." [webhook call]
Agent: "I have the following times available: 10:00 AM, 2:00 PM, 4:30 PM"
You: "2pm"
Agent: "May I have your name please?"
You: "John Smith"
Agent: "And what's the best phone number?"
You: "555-123-4567"
Agent: "Let me confirm: haircut on [date] at 2:00 PM for John Smith. Correct?"
You: "yes"
Agent: "Perfect! Booking now..." [webhook call]
Agent: "All set! Your confirmation number is APT-12345..."
```

**Test 2: Check Hours**
```
You: "What are your hours?"
Agent: "We're open Monday through Friday, 9 AM to 6 PM..."
```

**Test 3: Service Inquiry**
```
You: "What services do you offer?"
Agent: [webhook call to get_services]
Agent: "We offer haircuts, coloring, manicures..."
```

### Step 2: Check Webhook Calls

While testing, check your FastAPI logs:
```bash
# You should see:
INFO: Received Dialogflow webhook - Tag: check_availability
INFO: Parameters: {'date': '2024-01-15', 'service': 'haircut'}
```

If you DON'T see webhook calls:
- ✅ Verify webhook is configured in Dialogflow
- ✅ Verify webhook URL is correct and accessible
- ✅ Check tags match exactly

---

## Part 8: Connect to Telnyx (5 minutes)

### Step 1: Enable Telephony Integration

1. In Dialogflow CX, go to **Manage** → **Integrations**
2. Look for **Telephony** section
3. You have two options:

**Option A: Use Dialogflow Phone Gateway** (Simpler)
- Enable **Dialogflow CX Phone Gateway**
- Get the phone number or SIP URI
- In Telnyx, forward calls to this SIP URI

**Option B: Direct Telnyx Integration** (More control)
- Your FastAPI already handles this!
- Telnyx webhooks go to: `/webhooks/telnyx`
- Your code connects Telnyx to Dialogflow

### Step 2: Test with Real Phone Call

1. Call your Telnyx number: `+16815080516`
2. You should hear: "Thank you for calling Senda Salon..."
3. Try booking an appointment via voice

---

## Webhook Response Format

Your FastAPI webhook must return this format:

```json
{
  "fulfillment_response": {
    "messages": [
      {
        "text": {
          "text": ["Response text here"]
        }
      }
    ]
  },
  "session_info": {
    "parameters": {
      "available_times": ["10:00 AM", "2:00 PM"],
      "confirmation_number": "APT-12345"
    }
  }
}
```

Your existing `DialogflowResponse` class already handles this!

---

## Common Issues & Solutions

### Issue 1: Webhook Not Being Called

**Symptoms**: Agent responds but webhook isn't triggered

**Solutions**:
- ✅ Verify webhook is **enabled** on the page/route
- ✅ Check webhook **tag** matches your code exactly
- ✅ Verify webhook URL is accessible (test with curl)
- ✅ Check Dialogflow logs: **Analyze** → **Logs**

### Issue 2: Parameters Not Passing

**Symptoms**: Webhook receives empty parameters

**Solutions**:
- ✅ Verify parameters are added to session with `$session.params.X`
- ✅ Check parameter names match exactly
- ✅ Use **Test Agent** → **Session Parameters** to debug

### Issue 3: Agent Gets Stuck

**Symptoms**: Conversation doesn't progress

**Solutions**:
- ✅ Check all routes have valid transitions
- ✅ Verify conditions are correct
- ✅ Add fallback routes with `true` condition

### Issue 4: Phone Call Quality Issues

**Symptoms**: Poor audio, delays

**Solutions**:
- ✅ Use `phone_call` speech model (see Part 1)
- ✅ Enable telephony audio effects
- ✅ Keep webhook responses under 5 seconds
- ✅ Use streaming for audio processing

---

## Next Steps

Once your agent is built:

1. ✅ Test thoroughly in simulator
2. ✅ Fix webhook handlers to call real Phorest API (see CODEBASE_ANALYSIS.md)
3. ✅ Test with phone calls
4. ✅ Add error handling
5. ✅ Monitor and improve based on real conversations

---

## Quick Reference: All Webhook Tags

Copy this for your reference:

| Tag | Description | Returns |
|-----|-------------|---------|
| `check_availability` | Check available appointment slots | `available_times` array |
| `book_appointment` | Create appointment in Phorest | `confirmation_number`, `booking_confirmed` |
| `cancel_appointment` | Cancel existing appointment | Confirmation message |
| `get_services` | Get list of services | Services array |

---

**Time Estimate**: 1.5 - 2 hours to build everything in Dialogflow CX console

**Questions?** Check the existing config files in `apps/agent/` for reference!
