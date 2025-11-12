# Senda API

FastAPI orchestrator that integrates:

- **Telnyx**: Telephony services
- **Phorest**: Salon management system
- **Gemini**: AI/ML capabilities

## Development

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Run

```bash
uvicorn src.main:app --reload
```

### Test

```bash
pytest
```

### Lint & Format

```bash
black src tests
ruff check src tests
mypy src
```

## Environment Variables

See `.env.example` for required configuration.
