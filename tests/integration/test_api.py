import pytest
import json
from unittest.mock import MagicMock, patch
from api.app import create_app
from src.db import Base, engine, SessionLocal
from src.models import ChatSession

@pytest.fixture
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

from api.routes import chat_service

@pytest.fixture
def mock_ollama():
    with patch.object(chat_service.ollama_client, 'request') as mock_request:
        mock_request.return_value = {"content": "Test Response", "total_duration": 1.0}
        yield mock_request

def test_chat_endpoint_new_session(test_client, mock_ollama):
    response = test_client.post('/chat', json={"prompt": "Hello"})
    assert response.status_code == 200
    data = response.get_json()
    assert data['response'] == "Test Response"
    assert 'session_id' in data
    assert 'interaction_id' in data

def test_chat_endpoint_continue_session(test_client, mock_ollama):
    # First call
    r1 = test_client.post('/chat', json={"prompt": "Hello"})
    session_id = r1.get_json()['session_id']
    
    # Second call
    r2 = test_client.post('/chat', json={"prompt": "Again", "session_id": session_id})
    assert r2.status_code == 200
    assert r2.get_json()['session_id'] == session_id

def test_history_endpoint(test_client, mock_ollama):
    # Create conversation
    r1 = test_client.post('/chat', json={"prompt": "Msg 1"})
    session_id = r1.get_json()['session_id']
    
    r2 = test_client.get(f'/history/{session_id}')
    assert r2.status_code == 200
    history = r2.get_json()
    assert len(history) == 1
    assert history[0]['prompt'] == "Msg 1"
    assert history[0]['response'] == "Test Response"

def test_chat_missing_prompt(test_client):
    response = test_client.post('/chat', json={})
    assert response.status_code == 400

def test_invalid_session(test_client, mock_ollama):
    # Pass non-existent session, should create new one or handle gracefully
    # Service implementation creates new if not found, let's verify that behavior or if it errors out
    # My implementation: if not session: session = ChatSession()
    response = test_client.post('/chat', json={"prompt": "Hi", "session_id": 99999})
    assert response.status_code == 200
    # It creates a new session, so ID won't match 99999
    assert response.get_json()['session_id'] != 99999

def test_service_error_handling(test_client):
    with patch('src.services.ChatService.process_message', side_effect=Exception("DB Error")):
        response = test_client.post('/chat', json={"prompt": "Fail"})
        assert response.status_code == 500
        assert "DB Error" in response.get_json()['error']
