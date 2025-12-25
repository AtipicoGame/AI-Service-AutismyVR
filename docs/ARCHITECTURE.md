# Architecture

## Overview

The AutismyVR AI Service is designed as a modular system exposing AI capabilities through a REST API and typically consumed by VR clients. It also includes a Streamlit UI for debugging and demonstrations.

## Components

### 1. Database (PostgreSQL)
Stores persistent data including:
- **ChatSession**: Represents a conversation thread.
- **Interaction**: Stores individual User Prompt -> AI Response pairs.

### 2. Core Service Layer (`src/`)
Contains shared business logic.
- `src.db`: Database connection and session management.
- `src.models`: ORM definitions.
- `src.services.ChatService`: Manages the flow of interaction, including:
  - Validating input
  - Handling history
  - Invoking LLM clients
  - Persisting data to DB

### 3. API Layer (`api/`)
Flask-based REST API for external consumers.
- **Framework**: Flask
- **Documentation**: Swagger (Flasgger)
- **Endpoints**:
  - `POST /chat`: Main interaction point.
  - `GET /history/{id}`: Retrieval of past contexts.

### 4. UI Layer (`ui/`)
Streamlit application for developer testing.
- Directly imports `src.services` to ensure logic parity with API.
- Simulates real-time typing for better UX (though backend is synchronous request/response).

### 5. Infrastructure
- **Docker Compose**: Orchestrates API, DB, and UI.
- **Ollama**: External (host) or containerized LLM provider.

## Data Flow

1. **User Request** (API or UI) -> `ChatService`
2. `ChatService` -> **Database** (Fetch/Create Session)
3. `ChatService` -> **OllamaClient** (Generate Response)
4. `ChatService` -> **Database** (Save Interaction)
5. `ChatService` -> **Response** (Return structure)

## Deployment

The system is containerized for easy deployment via `docker-compose`. 
CI/CD integration via GitHub Actions ensures tests pass on every commit.
