# AutismyVR AI Service

This repository provides AI services for the AutismyVR platform, including a Flask REST API and a Streamlit Debug UI, both integrated with a PostgreSQL database and LLM models.

## Architecture

- **API**: Flask REST API with Swagger documentation (`/apidocs`).
- **UI**: Streamlit interface for chat and debugging.
- **Database**: PostgreSQL for storing chat sessions and interactions.
- **Services**: Shared logic in `src/` for consistent behavior across API and UI.
- **Models**: Abstraction layer for LLM (Ollama) and other AI models.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12 (for local development)

### Running with Docker (Recommended)

To start the entire stack (Postgres, API, UI):

```bash
docker-compose up -d --build
```

- **API Swagger**: http://localhost:5000/apidocs
- **Streamlit UI**: http://localhost:8501

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

The API is documented using Swagger. Once running, access it at `/apidocs`.

**Authentication**: All API endpoints require Firebase Authentication in staging and production environments. Include the Firebase ID token in the `Authorization` header as `Bearer <token>`. See [Firebase Setup Guide](docs/FIREBASE_SETUP.md) for configuration details.

**Development Mode**: When `ENV_LEVEL=dev` (default), Firebase authentication is bypassed for testing purposes. In this mode, all requests are automatically authenticated with a mock user (`dev-user`). This allows testing the API without Firebase credentials. **Note**: Authentication bypass is only available in development. Staging (`ENV_LEVEL=stag`) and production (`ENV_LEVEL=prod`) environments require valid Firebase tokens.

## Testing

The project includes Integration and BDD tests.
- **Integration**: `tests/integration/`
- **BDD**: `tests/bdd/` checking features in `tests/bdd/features/`

CI/CD is configured via GitHub Actions.