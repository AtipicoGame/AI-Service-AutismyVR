# Project Wiki

## Development Guide

### Setting up Environment
We recommend using Docker for running the full stack, but for development:
1. Create a virtual environment `python -m venv venv`
2. Install requirements `pip install -r requirements.txt`
3. ensure a local postgres is running or use the docker one (`docker-compose up -d postgres`)

### database Migrations
Currently, the project uses `Base.metadata.create_all` which syncs models on startup. For production, setting up `alembic` is recommended.

### Adding New Models
To add a new AI model:
1. Create a client in `models/` (e.g. `openai_client.py`).
2. Update `ChatService` to allow selecting the model or switching logic.

### API Standards
- All endpoints must be documented with docstrings for Swagger.
- Use standard HTTP status codes.
- Responses should be JSON.

## Testing Strategy
- **Integration Tests**: Verify the API endpoints work (mocking the LLM).
- **BDD Tests**: Verify high-level user stories using Gherkin syntax.
- **Coverage**: Maintain 100% coverage on core logic.

## Common Issues
- **Ollama Connection**: Ensure Ollama is running (`ollama serve`). If running via Docker, ensure `OLLAMA_HOST` matches the host gateway.
- **DB Connection**: Check `DATABASE_URL` env var.
