# Senda AI - Virtual Voice Assistant for Salons

## Project Overview

**Senda** is a conversational AI platform that allows salon owners to set up virtual voice assistants (like "Bruna") to handle phone calls for appointment booking, rescheduling, cancellations, and customer inquiries.

### Core Goals

1. **Answer incoming calls** to the salon's phone number
2. **Understand customer intent** (book, reschedule, cancel, ask questions)
3. **Check availability** in real-time from Phorest salon management system
4. **Book appointments** directly into Phorest
5. **Transfer to human** when needed or requested
6. **Provide natural conversation** using Claude AI

---

## Architecture

### Monorepo Structure (pnpm + Turborepo)

```
senda-ai/
├── apps/
│   ├── api/          # FastAPI backend (Python) - Core orchestrator
│   ├── web/          # Next.js 14 frontend - User dashboard
│   └── agent/        # Dialogflow CX (future migration from Telnyx AI)
├── packages/
│   ├── shared-types/ # TypeScript type definitions
│   ├── ui/           # Shared React components
│   └── clients/      # API client libraries
└── docs/             # Documentation
```

### Tech Stack

**Backend (apps/api):**
- FastAPI (Python 3.11+)
- Async/await for concurrent API calls
- Services architecture (Phorest, Telnyx, Conversation/Claude)

**Frontend (apps/web):**
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Firebase Authentication

**AI/Telephony:**
- **Telnyx** - Phone number, call handling, transcription, text-to-speech
- **Anthropic Claude** - Conversation understanding and responses
- **Phorest API** - Salon management (appointments, clients, services, staff)

**Future:**
- Google Cloud Run (deployment)
- Dialogflow CX (cost-effective replacement for Telnyx AI)
- Gemini 2.5 (future Claude alternative)

---

## Phorest API Integration

### Key Information

**Base URL:** `https://api-gateway-us.phorest.com/third-party-api-server`
**Authentication:** Basic Auth with `global/` prefix
**Business ID:** `6Sg8C_kl47YIHlStGcv-_Q`
**Branch ID:** `mfxegqrFVfJXm_G75LlO8w`

### Critical Authentication Format

```python
# CORRECT format (required by Phorest):
auth = base64.b64encode(f"global/{username}:{password}".encode())

# WRONG (will fail with 401):
auth = base64.b64encode(f"{username}:{password}".encode())
```

### Core Endpoints

#### 1. **Client Management**

```
GET /api/business/{businessId}/client?mobile={phone}&size=50&page=0
POST /api/business/{businessId}/client
PUT /api/business/{businessId}/client/{clientId}
```

**Note:** Client endpoints do NOT include `/branch/{branchId}` in the path.

#### 2. **Services Catalog**

```
GET /api/business/{businessId}/branch/{branchId}/service?size=500
```

Returns all services with IDs, durations, and attributes.

#### 3. **Staff**

```
GET /api/business/{businessId}/branch/{branchId}/staff
GET /api/business/{businessId}/branch/{branchId}/staff/worktimetable?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD
```

#### 4. **Availability Check** (CRITICAL)

```
POST /api/business/{businessId}/branch/{branchId}/appointments/availability
```

**Request Body:**
```json
{
  "startTime": "2025-11-15T00:00:00Z",
  "endTime": "2025-12-06T00:00:00Z",
  "clientServiceSelections": [
    {
      "serviceSelections": [{ "serviceId": "xyz123" }],
      "staffId": "abc456"  // Optional
    }
  ]
}
```

**Response:**
```json
{
  "data": [
    {
      "clientSchedules": [
        {
          "serviceSchedules": [
            {
              "startTime": "2025-11-15T14:30:00Z",
              "endTime": "2025-11-15T15:00:00Z"
            }
          ]
        }
      ]
    }
  ]
}
```

**Key Notes:**
- Times are in UTC (must convert to salon timezone for display)
- Staff must be qualified for the service
- Minimum notice windows and buffers affect availability
- If `staffId` is omitted, returns slots for any qualified staff

#### 5. **Create Appointment**

```
POST /api/business/{businessId}/branch/{branchId}/appointment
```

**Request Body:**
```json
{
  "clientId": "client123",
  "startTime": "2025-11-15T14:30:00Z",
  "services": [
    {
      "serviceId": "xyz123",
      "staffId": "abc456"
    }
  ]
}
```

#### 6. **Get Appointments**

```
GET /api/business/{businessId}/branch/{branchId}/appointment?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD&clientId={id}
```

#### 7. **Update Appointment (Reschedule)**

```
PUT /api/business/{businessId}/branch/{branchId}/appointment/{appointmentId}
```

**Note:** Must increment version (optimistic locking).

#### 8. **Cancel Appointment**

```
POST /api/business/{businessId}/branch/{branchId}/appointment/{appointmentId}/cancel
```

### Timezone Handling (CRITICAL)

**Phorest returns UTC times.** Must convert to salon's local timezone.

**Configuration:**
```bash
SALON_TIMEZONE=America/New_York  # Configurable via .env
```

**Implementation:**
```python
from zoneinfo import ZoneInfo

# Parse UTC from Phorest
dt_utc = datetime.fromisoformat(schedule["startTime"].replace("Z", "+00:00"))

# Convert to salon timezone
dt_local = dt_utc.astimezone(ZoneInfo(salon_timezone))

# Format for speech
formatted = dt_local.strftime("%A, %B %d") + ordinal_suffix + dt_local.strftime(" at %I:%M %p")
# Example: "Monday, November 18th at 2:30 PM"
```

---

## Telnyx Integration

**Phone Number:** `+16815080516`
**Webhook URL:** `https://YOUR-NGROK-URL.ngrok.io/webhook/call`

### Call Flow

1. **Incoming call** → Telnyx sends `assistant.initialization` event
2. **Answer call** → FastAPI responds with greeting
3. **Transcription** → User speaks, Telnyx sends `assistant.message` with transcript
4. **Claude processes** → Extract intent, generate response
5. **TTS response** → Speak back to caller
6. **Action** → Check availability, book appointment, transfer, etc.
7. **Hangup** → Clean up conversation state

### Telnyx AI Agent Instructions

Currently using Telnyx's built-in AI agent "Bruna" as the virtual assistant. Future plan: migrate to Dialogflow CX for cost savings.

---

## Critical Fixes Applied

### 1. Missing Environment Variable Loading

**Problem:** `.env` file was never loaded
**Impact:** All API calls failed (no credentials)
**Fix:** Added `load_dotenv()` to `apps/api/src/main.py:6-9`

```python
from dotenv import load_dotenv
load_dotenv()  # CRITICAL: Must be before service imports
```

### 2. Wrong Phorest Authentication

**Problem:** Missing `global/` prefix
**Impact:** 401 Unauthorized on all Phorest calls
**Fix:** Updated `apps/api/src/services/phorest.py:24`

```python
auth_string = base64.b64encode(f"global/{username}:{password}".encode())
```

### 3. Wrong API Path Structure

**Problem:** Missing `/third-party-api-server/` prefix
**Impact:** 404 Not Found on all Phorest calls
**Fix:** Updated all 8 endpoint URLs

```python
# Before: {host}/api/business/{id}/...
# After:  {host}/third-party-api-server/api/business/{id}/...
```

### 4. Wrong Client Endpoint

**Problem:** Client search included `/branch/{branchId}` in path
**Impact:** Client lookup failures
**Fix:** Removed branch ID from client endpoints

```python
# Before: /api/business/{id}/branch/{branchId}/client
# After:  /api/business/{id}/client
```

### 5. Wrong Gateway Region

**Problem:** Using EU gateway for US account
**Impact:** Authentication/routing errors
**Fix:** Changed to `https://api-gateway-us.phorest.com`

### 6. Datetime Formatting Issues

**Problem:** Said "date date and time" instead of actual dates
**Impact:** Confusing speech output
**Fix:** Proper UTC→local conversion + natural formatting

```python
# Before: "Monday at 2:30 PM" (no date!)
# After:  "Monday, November 18th at 2:30 PM"
```

---

## Environment Configuration

### Required `.env` Variables

```bash
# Phorest Salon Management
PHOREST_BASE_URL=https://api-gateway-us.phorest.com
PHOREST_USERNAME=your_username
PHOREST_PASSWORD=your_password
PHOREST_BUSINESS_ID=6Sg8C_kl47YIHlStGcv-_Q
PHOREST_BRANCH_ID=mfxegqrFVfJXm_G75LlO8w

# Salon Timezone (for UTC→local conversion)
SALON_TIMEZONE=America/New_York

# Telnyx Telephony
TELNYX_API_KEY=your_telnyx_api_key
TELNYX_PHONE_NUMBER=+16815080516

# Anthropic Claude AI
ANTHROPIC_API_KEY=your_anthropic_api_key

# Human Transfer (optional)
TRANSFER_PHONE_NUMBER=+1234567890
```

---

## Current Implementation Status

### ✅ Fully Working

- ✅ Answer incoming calls
- ✅ Speech transcription
- ✅ Claude AI conversation
- ✅ Customer lookup by phone number
- ✅ Personalized greetings for returning customers
- ✅ **Availability checking** - Finds available time slots from Phorest
- ✅ Proper timezone conversion (UTC→local)
- ✅ Natural date/time formatting in speech

### ⚠️ Partial Implementation

- ⚠️ **Booking** - Shows available slots but doesn't complete the booking
  - Missing: Customer confirmation of which slot they want
  - Missing: Actual call to `create_appointment()` to book in Phorest

### ❌ Not Implemented

- ❌ **Cancel appointments** - Placeholder only
- ❌ **Reschedule appointments** - Placeholder only
- ❌ **Transfer to human** - Code exists but not fully tested
- ❌ **Dashboard UI** - Frontend authentication works but no booking interface

---

## Agent Behavior Guide

### Staff-Service Mapping

**Primary approach:** Use availability endpoint with `staffId` to verify eligibility
- If slots returned → staff is qualified
- If no slots → staff not qualified or unavailable

**Secondary approach:** Combine staff list + services catalog
- Some staff have explicit skills/roles
- Map services to qualified staff

### Availability Strategy

**If user doesn't specify staff:**
1. Call availability without `staffId`
2. Present slots grouped by staff
3. Let customer choose or pick best fit (earliest, preferred staff, etc.)

**If user specifies staff:**
1. Call availability with `staffId`
2. If zero slots, check staff timetable and explain constraints
3. Offer alternative staff if customer is flexible

### Booking Flow

1. **Validate client** - Look up by phone or create new
2. **Check availability** - Get available slots for desired service/date/staff
3. **Confirm with customer** - "I have Monday at 2:30 PM with Paulo, does that work?"
4. **Create appointment** - Call Phorest API to book
5. **Confirm success** - "You're all set! See you Monday at 2:30."

### Reschedule Flow

1. **Find existing appointment** - Get appointments for client
2. **Confirm which one** - "I see you have a haircut on Monday, is that the one?"
3. **Get new availability** - Same service, new date/time
4. **Update appointment** - PUT with incremented version
5. **Confirm change** - "Changed to Tuesday at 3 PM."

### Cancel Flow

1. **Find appointment** - Get appointments for client
2. **Confirm cancellation** - Check policy, fees
3. **Cancel** - Call cancel endpoint
4. **Add note** - Reason for audit trail

### Q&A Support

Use available data to answer questions:
- "Who can do a balayage this Friday after 3pm?"
- "What's the earliest 60-minute haircut tomorrow?"
- "Does Paulo work Sundays?"
- "What services does Leo offer?"

---

## Known Issues & Constraints

### Phorest API Limitations

- **No webhooks** - Must poll for changes
- **Timezone sensitive** - All times must be in branch timezone or UTC
- **Staff qualification** - Staff must be enabled for online booking AND qualified for service
- **Minimum notice** - Can't book same-day slots if min notice window not met
- **Buffers** - Time buffers between appointments affect availability
- **Phone uniqueness** - Client phone numbers must be unique
- **Optimistic locking** - Must increment version on appointment updates

### Current Bugs/TODOs

- [ ] Complete booking confirmation flow
- [ ] Implement cancel/reschedule features
- [ ] Add error handling for race conditions (slot taken before booking)
- [ ] Make timezone configurable per salon
- [ ] Add support for multiple services in one appointment
- [ ] Handle appointment conflicts/overlaps
- [ ] Test transfer-to-human flow
- [ ] Add SMS confirmation (optional)
- [ ] Dashboard UI for salon owners

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm (`npm install -g pnpm`)

### Backend Setup

```bash
cd apps/api

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Git Bash on Windows
# OR
source .venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt
pip install python-dotenv

# Configure environment
cp .env.example .env
# Edit .env with your actual credentials

# Run API
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd apps/web

# Install dependencies
pnpm install

# Configure Firebase
cp .env.local.example .env.local
# Edit .env.local with your Firebase config

# Run dev server
pnpm dev
```

### Testing with ngrok

```bash
# In a separate terminal
ngrok http 8000

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
# Update Telnyx webhook to: https://abc123.ngrok.io/webhook/call
```

---

## Troubleshooting

### Common Issues

**Problem: "ModuleNotFoundError: No module named 'anthropic'"**
**Solution:** Activate virtual environment and install dependencies

**Problem: 401 Unauthorized from Phorest**
**Solution:** Check `global/` prefix in auth and verify credentials

**Problem: 404 Not Found from Phorest**
**Solution:** Verify `/third-party-api-server/` in URL path

**Problem: "date date and time" in speech**
**Solution:** Pull latest code with timezone conversion fix

**Problem: No slots returned from availability**
**Solution:**
- Check staff qualification for service
- Verify min notice window
- Check staff/branch timetables
- Try different date/time range

**Problem: Call drops during availability check**
**Solution:**
- Check API timeout (default 30s)
- Verify Phorest credentials loaded
- Check uvicorn logs for errors

---

## Deployment (Future)

### Google Cloud Run

1. Build Docker container
2. Deploy to Cloud Run
3. Configure environment variables
4. Update Telnyx webhook to Cloud Run URL
5. Set up monitoring and logging

### Considerations

- **Cold starts** - Keep instances warm or accept latency
- **Secrets management** - Use Secret Manager
- **Scaling** - Auto-scale based on concurrent calls
- **Logging** - Structured logging for debugging
- **Monitoring** - Alert on errors, latency, failed bookings

---

## Future Enhancements

### Phase 1 (Next 2-3 days)
- [ ] Complete booking flow
- [ ] Add cancel/reschedule
- [ ] Production deployment to Cloud Run

### Phase 2 (Next 2 weeks)
- [ ] Multi-salon support
- [ ] Dashboard UI for managing settings
- [ ] SMS confirmations
- [ ] Email confirmations
- [ ] Analytics (call volume, bookings, transfers)

### Phase 3 (1 month)
- [ ] Migrate from Telnyx AI to Dialogflow CX
- [ ] Support for multiple services per appointment
- [ ] Customer preferences (favorite stylist, service history)
- [ ] Waitlist management
- [ ] Package/membership handling

### Phase 4 (Future)
- [ ] Multi-language support
- [ ] Integration with other salon systems (Square, Mindbody, etc.)
- [ ] WhatsApp/SMS bot (same backend)
- [ ] Advanced analytics and reporting

---

## Business Information

**Salon Name:** Paulo Lanfredi Salon
**Location:** 2nd floor (also The Cave Barber Shop on 1st floor)
**Phone:** +16815080516
**Services:** Haircut, Color, Highlights, Blowout, Treatment
**Staff:** Paulo, Leo, Patrick, Joseph, Jake

---

## Files & Documentation

### Key Files

- `apps/api/src/main.py` - FastAPI app entry point
- `apps/api/src/services/phorest.py` - Phorest API integration
- `apps/api/src/services/telnyx.py` - Telnyx telephony
- `apps/api/src/services/conversation.py` - Claude AI conversation
- `apps/api/src/routes/webhooks.py` - Call webhook handler

### Documentation

- `apps/api/CRITICAL_FIXES_FROM_POSTMAN.md` - Auth and endpoint fixes
- `apps/api/FIXES_APPLIED.md` - Environment loading fixes
- `apps/api/PHOREST_API_ANALYSIS.md` - API endpoint verification
- `apps/api/README.md` - Backend setup instructions

---

## Contact & Support

For questions or issues:
1. Check this claude.md first
2. Review documentation in `apps/api/` folder
3. Check Phorest API docs: https://developer.phorest.com
4. Check Telnyx docs: https://developers.telnyx.com

---

**Last Updated:** November 15, 2025
**Current Branch:** `claude/explore-codebase-011CV4qq9wNw8WciVzbJu8cD`
**Status:** ✅ Phorest integration working, ⚠️ Booking flow needs completion
