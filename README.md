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

## API Documentation

The API is documented using Swagger. Once running, access it at `/apidocs`.

## Testing

The project includes Integration and BDD tests.
- **Integration**: `tests/integration/`
- **BDD**: `tests/bdd/` checking features in `tests/bdd/features/`

CI/CD is configured via GitHub Actions.