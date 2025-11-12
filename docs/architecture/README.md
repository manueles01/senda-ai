# Architecture

System architecture documentation for Senda platform.

## System Overview

Senda is a conversational AI platform that integrates:

- **Telephony** (Telnyx)
- **Business Systems** (Phorest)
- **AI/ML** (Google Gemini)
- **Conversational AI** (Dialogflow CX)

## Components

### Apps

- **API** (`apps/api`): FastAPI orchestrator that coordinates between services
- **Web** (`apps/web`): Next.js frontend for public site and operations console
- **Agent** (`apps/agent`): Dialogflow CX agent definitions

### Packages

- **shared-types**: TypeScript type definitions
- **ui**: Reusable UI components
- **clients**: API client libraries

## Data Flow

```
User → Telnyx → Dialogflow CX → FastAPI → Phorest/Gemini
                                       ↓
                                   Web Console
```

## Technology Stack

- **Backend**: Python, FastAPI
- **Frontend**: TypeScript, Next.js, React, Tailwind CSS
- **AI**: Dialogflow CX, Google Gemini
- **Telephony**: Telnyx
- **Business**: Phorest API
- **Infrastructure**: Google Cloud Platform
