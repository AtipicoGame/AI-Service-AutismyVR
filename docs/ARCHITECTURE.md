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

## Design Decisions

### 1. Communication Protocol: HTTP REST over gRPC
**Decision**: Use standard HTTP POST requests for chat interaction.
**Context**: Real-time voice interaction often implies gRPC streaming.
**Rationale**:
- **Simplicity**: HTTP is stateless and widely supported.
- **Server Effort**: Avoids managing persistent socket connections for thousands of potential users.
- **Latency Strategy**: We accept the minor latency cost of "waiting for silence" (Post-Speech) in exchange for significant architectural simplicity. The Client is responsible for VAD (Voice Activity Detection).

### 2. Implementation: Custom Python (Pure Ollama Client) vs n8n Agents
**Decision**: Build a custom service using Flask and a **direct Ollama Client** (`src/models/ollama_client.py`).
**Context**: 
- **n8n Agents**: Provide high-level "drag and drop" agent nodes (LangChain based) that handle memory and tools automatically.
- **Pure Client**: Manual handling of the prompt + context window loop.
**Rationale**:
- **Control vs Magic**: n8n Agent nodes abstract away the "Context Window" and memory management. For a VR avatar, we eventually need fine-grained control over exactly *what* the specifically user said (AudioSTT) and *how* the prompt is constructed to maintain the "Character".
- **Performance**: A direct Python function call to an LLM API is faster (~10ms overhead) than an n8n workflow execution engine (~100ms+ overhead).
- **Testing**: We need rigorous BDD and Integration testing (100% coverage). Testing a specific "Prompt Template" is trivial in Python unit tests but difficult inside a compiled n8n workflow.
- **Code Reuse**: The same `OllamaClient` logic is imported directly by our Streamlit Debug UI, ensuring 1:1 parity between development and production.
