# AutismyVR AI Service

This repository provides AI services for the AutismyVR platform, including a Flask REST API and a Streamlit Debug UI, both integrated with a PostgreSQL database and LLM models.

## Architecture

- **API**: Flask REST API with Swagger documentation (`/apidocs`).
- **UI**: Streamlit interface for chat and debugging.
- **Database**: PostgreSQL for storing chat sessions and interactions.
- **Services**: Shared logic in `src/` for consistent behavior across API and UI.
- **Models**: Abstraction layer for LLM (Ollama) and other AI models.

## Project Structure

```
src/
├── models/              # SQLAlchemy database models
│   ├── __init__.py
│   └── chat_models.py
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── chat_service.py
│   ├── audio_service.py
│   └── title_service.py
├── clients/             # External service clients
│   ├── __init__.py
│   ├── ollama_client.py
│   ├── whisper_client.py
│   ├── tts_client.py
│   └── liveportrait_client.py
├── controllers/         # RESTful API controllers
│   ├── __init__.py
│   ├── chat_controller.py
│   └── audio_controller.py
├── auth.py              # Firebase authentication
└── db.py                # Database configuration

api/
├── routes.py            # Route registration
└── app.py               # Flask application factory
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12 (for local development)

### Running with Docker (Recommended)

To start the entire stack (Postgres, API, UI, Whisper, TTS, LivePortrait):

```bash
docker-compose up -d --build
```

Services:
- **API Swagger**: http://localhost:5000/apidocs
- **Streamlit UI**: http://localhost:8501
- **Whisper API**: http://localhost:8000
- **TTS API**: http://localhost:8001
- **LivePortrait API**: http://localhost:8002

**Note**: For Mac users, GPU services will run on CPU. For NVIDIA GPU support on Windows/Linux, ensure Docker Desktop has GPU support enabled.

### Local Development

1. **Install Dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Tests**:
   ```bash
   export PYTHONPATH=.
   pytest --cov=src --cov=api tests/
   ```

3. **Run API**:
   ```bash
   export PYTHONPATH=.
   python api/app.py
   ```

4. **Run Streamlit**:
   ```bash
   export PYTHONPATH=.
   streamlit run app.py
   ```

## Documentation

- [Architecture Diagram and Details](docs/ARCHITECTURE.md)
- [Project Wiki](docs/WIKI.md)
- [Firebase Authentication Setup](docs/FIREBASE_SETUP.md)

## Architectural Decisions

### HTTP vs gRPC
We chose **HTTP (REST)** over gRPC to minimize server complexity and resource usage. While gRPC offers lower latency for streaming, HTTP is stateless, easier to scale, and sufficient for the current "User Speaks -> Processing -> Response" flow where client-side VAD (Voice Activity Detection) handles the cutoff.

### Python Services vs n8n
We implemented a **Custom Python Service using direct Ollama Client integration** rather than n8n Agent nodes.
- **Why**: We require low-latency, granular control over the context window and chat history which "black box" agent nodes often abstract away.
- **Implementation**: We use a pure `OllamaClient` in `src/models` to interact directly with the LLM. This allows strict typing of input/output and simpler debugging integration with the rest of our application logic.
- **Benefit**: Easier testing (100% coverage), better performance, and ensures the "brain" of the VR avatar behaves exactly as defined without overhead from an orchestration platform.

## API Documentation

The API follows **RESTful design principles**, using clear resource-based endpoints and appropriate HTTP methods. All endpoints are documented using Swagger. Once running, access it at `/apidocs`.

### API Endpoints

**Text Chat:**
- `POST /chat` - Create a new text chat session
- `POST /chat/:session_uuid` - Send a message to an existing text session

**Audio Chat:**
- `POST /audio2audio` - Create a new audio chat session (receives audio file)
- `POST /audio2audio/:session_uuid` - Send audio to an existing audio session

**History:**
- `GET /history` - List all sessions (dev: all interactions, stag/prod: session list)
- `GET /history/:session_uuid` - Get full history of a specific session

### Authentication

All API endpoints require Firebase Authentication in staging and production environments. Include the Firebase ID token in the `Authorization` header as `Bearer <token>`. See [Firebase Setup Guide](docs/FIREBASE_SETUP.md) for configuration details.

**Development Mode**: When `ENV_LEVEL=dev` (default), Firebase authentication is bypassed for testing purposes. In this mode, all requests are automatically authenticated with a mock user (`dev-user`). This allows testing the API without Firebase credentials. **Note**: Authentication bypass is only available in development. Staging (`ENV_LEVEL=stag`) and production (`ENV_LEVEL=prod`) environments require valid Firebase tokens.

### LivePortrait Integration

LivePortrait can be enabled via:
- **Environment variable**: `LIVEPORTRAIT_ENABLED=true` (default: `false`)
- **Query parameter**: `?liveportrait=true` (overrides environment variable)

When enabled, audio responses include LivePortrait avatar animation data.

### GPU Support

The Docker Compose configuration supports GPU acceleration for AI services:
- **NVIDIA GPUs (Windows/Linux)**: Automatically uses GPU via Docker GPU runtime
- **Mac (Metal)**: Services run on CPU by default. For Metal acceleration, configure services to run directly on host or use Metal-compatible containers.

Services that use GPU:
- **Whisper**: Audio transcription
- **TTS (Piper)**: Text-to-speech synthesis
- **LivePortrait**: Avatar animation generation

## Testing

The project includes Integration and BDD tests.
- **Integration**: `tests/integration/`
- **BDD**: `tests/bdd/` checking features in `tests/bdd/features/`

CI/CD is configured via GitHub Actions.