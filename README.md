# Senda – Conversational AI Platform

> Guiding businesses along the path to automation and intelligent service.

An AI-powered salon receptionist that handles phone calls, books appointments, and provides customer service using Dialogflow CX, Telnyx telephony, and Google Gemini AI.

## Features

- **🤖 AI Phone Receptionist**: Automated call handling with natural conversation
- **📅 Appointment Booking**: Integration with Phorest salon management system
- **🧠 Smart Responses**: Gemini AI for enhanced, context-aware responses
- **☁️ Google Cloud**: Built on Dialogflow CX for robust conversation management
- **📞 Production Phone Numbers**: Telnyx integration for real phone numbers
- **🔄 Real-time Processing**: Streaming audio processing for natural conversations

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Telnyx    │────▶│  FastAPI     │────▶│ Dialogflow  │
│  (Phone)    │     │  (Webhooks)  │     │  CX (NLU)   │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │   Gemini AI  │     │   Phorest   │
                    │  (Enhanced)  │     │  (Booking)  │
                    └──────────────┘     └─────────────┘
```

## Project Structure

```
senda-ai/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   └── app/
│   │       ├── main.py         # Main application
│   │       ├── config.py       # Configuration
│   │       ├── routers/        # API routes
│   │       │   ├── telnyx.py   # Telnyx webhooks
│   │       │   └── dialogflow.py # Dialogflow webhooks
│   │       └── services/       # Business logic
│   │           ├── telnyx_service.py      # Telnyx API client
│   │           ├── dialogflow_service.py  # Dialogflow CX client
│   │           ├── gemini_service.py      # Gemini AI client
│   │           ├── phorest_service.py     # Phorest API client
│   │           └── call_integration_service.py # Call orchestration
│   ├── agent/                  # Dialogflow CX agent definitions
│   │   ├── agent-config.json   # Agent configuration
│   │   ├── intents.json        # Intent definitions
│   │   ├── entities.json       # Custom entities
│   │   └── flows/              # Conversation flows
│   └── web/                    # (Future) Next.js frontend
├── packages/                   # (Future) Shared packages
├── .env                        # Environment configuration
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Docker compose setup
└── setup.sh                    # Setup script
```

## Quick Start

### Prerequisites

- Python 3.9+
- Google Cloud account with Dialogflow CX enabled
- Telnyx account with phone number
- Phorest salon management account (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd senda-ai
   ```

2. **Run setup script**
   ```bash
   ./setup.sh
   ```

3. **Configure environment**
   ```bash
   # Edit .env with your credentials
   vim .env
   ```

4. **Set up Google Cloud credentials**
   - Download service account key from Google Cloud Console
   - Save as `service-account-key.json`
   - Grant Dialogflow CX permissions

5. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

6. **Run the API server**
   ```bash
   uvicorn apps.api.app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Configuration

### Environment Variables

Create a `.env` file with the following:

```env
# Google Cloud
GOOGLE_PROJECT_ID=your-google-project-id
FIREBASE_PROJECT_ID=your-firebase-project-id
GEMINI_MODEL=gemini-1.5-pro

# Dialogflow CX
DIALOGFLOW_AGENT_ID=your-agent-id
DIALOGFLOW_LOCATION=us-central1

# Telnyx
TELEPHONY_TELNYX_API_KEY=your-telnyx-api-key
TELNYX_PUBLIC_KEY=your-telnyx-public-key

# Phorest
PHOREST_BRANCH_ID=your-branch-id
PHOREST_CLIENT_ID=your-client-id
PHOREST_CLIENT_SECRET=your-client-secret
```

### Dialogflow CX Setup

1. Go to [Dialogflow CX Console](https://dialogflow.cloud.google.com/cx)
2. Create a new agent or use existing
3. Import agent definitions from `apps/agent/`
4. Configure webhook URL to point to your API: `https://your-domain.com/webhooks/dialogflow`
5. Test using the built-in simulator

### Telnyx Setup

1. Sign up at [Telnyx](https://telnyx.com)
2. Purchase a phone number
3. Configure webhook URL: `https://your-domain.com/webhooks/telnyx`
4. Enable call control application
5. Copy API key to `.env`

## API Endpoints

### Health Check
```
GET /health
```

### Telnyx Webhooks
```
POST /webhooks/telnyx
```
Receives call events from Telnyx (call.initiated, call.answered, call.hangup)

### Dialogflow Webhooks
```
POST /webhooks/dialogflow
```
Handles fulfillment requests from Dialogflow CX

## Development

### Running Tests
```bash
pytest
```

### Code Style
```bash
# Format code
black apps/

# Lint
flake8 apps/
```

### Adding New Intents

1. Add intent definition to `apps/agent/intents.json`
2. Update flows in `apps/agent/flows/`
3. Implement webhook handler in `apps/api/app/routers/dialogflow.py`
4. Deploy to Dialogflow CX

## Deployment

### Google Cloud Run

```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/senda-ai

# Deploy
gcloud run deploy senda-ai \
  --image gcr.io/PROJECT_ID/senda-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Railway / Render / Fly.io

Use the provided `Dockerfile` for deployment to these platforms.

## Troubleshooting

### Call not connecting
- Check Telnyx webhook URL is correct and publicly accessible
- Verify Telnyx API key in `.env`
- Check API logs for errors

### Dialogflow not responding
- Verify agent ID and location in `.env`
- Check Google Cloud credentials are valid
- Ensure webhook URL is accessible from Google Cloud

### Phorest integration failing
- Verify Phorest credentials
- Check branch ID is correct
- Review API logs for specific errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: See `apps/agent/README.md` for Dialogflow details

---

Built with ❤️ by Senda AI
