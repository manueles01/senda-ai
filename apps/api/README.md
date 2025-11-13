# Senda API

FastAPI orchestrator that powers Senda's conversational AI voice assistant.

## Features

- **Voice Call Handling** - Telnyx integration for incoming calls
- **Customer Recognition** - Automatic lookup in Phorest database
- **AI Conversations** - Claude-powered natural language understanding
- **Appointment Management** - Book, reschedule, and cancel appointments
- **Smart Handoff** - Transfer to human with conversation context

## Architecture

```
src/
├── main.py              # FastAPI app and routes
├── services/
│   ├── phorest.py       # Phorest salon management integration
│   ├── telnyx.py        # Telnyx telephony service
│   └── conversation.py  # Claude AI conversation management
├── routes/
│   └── webhooks.py      # Telnyx webhook handlers
└── models/
    └── schemas.py       # Pydantic data models
```

## Setup

### 1. Create virtual environment

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install -e ".[dev]"  # For development tools
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

Required credentials:

- Phorest API credentials (username, password, business ID, branch ID)
- Telnyx API key and phone number
- Anthropic API key for Claude

### 4. Run the API

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000

## Testing

### Test endpoints

```bash
# Check API health
curl http://localhost:8000/health

# Check status and active calls
curl http://localhost:8000/status
```

### Test with Telnyx

1. **Expose local server** (use ngrok or similar):

   ```bash
   ngrok http 8000
   ```

2. **Configure Telnyx webhook**:
   - Go to Telnyx dashboard
   - Set webhook URL to: `https://your-ngrok-url.ngrok.io/webhook/call`
   - Enable call events

3. **Make a test call** to your Telnyx number

## Call Flow

1. **Customer calls** → Telnyx webhook triggers
2. **System answers** and checks if customer exists in Phorest
3. **Greets customer** (personalized if returning client)
4. **Starts transcription** and listens
5. **Claude processes** intent (booking, rescheduling, cancellation)
6. **Checks Phorest** availability and offers time slots
7. **Confirms booking** or transfers to human if requested

## Development

### Run tests

```bash
pytest
```

### Format code

```bash
black src tests
ruff check src tests
```

### Type checking

```bash
mypy src
```

## API Endpoints

- `GET /` - API info and active call count
- `GET /health` - Health check
- `GET /status` - Detailed status with active conversations
- `POST /webhook/call` - Telnyx call webhook
- `GET /webhook/health` - Webhook health check

## Monitoring

View active calls and conversation state:

```bash
curl http://localhost:8000/status
```

Check logs for detailed call flow and Claude responses.
