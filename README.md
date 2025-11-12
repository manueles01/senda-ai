# Senda – Conversational AI Platform

> Guiding businesses along the path to automation and intelligent service.

## Monorepo Structure

```
senda-ai/
├── apps/
│   ├── api/              # FastAPI orchestrator (Python)
│   ├── web/              # Next.js site and ops console (TypeScript)
│   └── agent/            # Dialogflow CX agent definitions
├── packages/
│   ├── shared-types/     # Shared TypeScript types
│   ├── ui/               # Shared React components
│   └── clients/          # API clients (Phorest, Telnyx, Gemini)
└── docs/
    ├── architecture/     # System architecture docs
    └── brand/            # Brand guidelines

```

## Tech Stack

- **Monorepo**: pnpm workspaces + Turborepo
- **Backend**: Python 3.11+, FastAPI
- **Frontend**: TypeScript, Next.js 14, React 18, Tailwind CSS
- **AI/ML**: Dialogflow CX, Google Gemini
- **Integrations**: Telnyx (telephony), Phorest (salon management)
- **Tooling**: ESLint, Prettier, TypeScript, Black, Ruff

## Getting Started

### Prerequisites

- Node.js 18+ and pnpm 8+
- Python 3.11+
- Google Cloud Platform account

### Installation

```bash
# Install Node dependencies
pnpm install

# Set up Python environment for API
cd apps/api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Development

```bash
# Run all apps in development mode
pnpm dev

# Run specific app
pnpm --filter @senda/web dev
pnpm --filter @senda/api dev

# Run API separately
cd apps/api
source .venv/bin/activate
uvicorn src.main:app --reload
```

### Building

```bash
# Build all apps
pnpm build

# Build specific app
pnpm --filter @senda/web build
```

### Testing

```bash
# Run all tests
pnpm test

# Test API
cd apps/api
pytest
```

### Linting & Formatting

```bash
# Lint and format all code
pnpm lint
pnpm format

# Python linting (in apps/api)
black src tests
ruff check src tests
mypy src
```

## Environment Variables

Each app has its own `.env.example` file:
- `apps/api/.env.example` - API configuration
- `apps/web/.env.local.example` - Web app configuration (create this file)

## Documentation

See [docs/](./docs/) for architecture and brand guidelines.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run `pnpm lint` and `pnpm format`
4. Submit a pull request

## License

Proprietary - All rights reserved
