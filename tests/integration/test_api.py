import pytest
import json
from unittest.mock import MagicMock, patch
from api.app import create_app
from src.db import Base, engine, SessionLocal
from src.models.chat_models import ChatSession
from src.services.chat_service import ChatService

@pytest.fixture
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_ollama():
    """Mock Ollama client for tests."""
    pass

def test_chat_endpoint_new_session(test_client, mock_ollama):
    with patch('src.services.chat_service.ChatService') as MockService:
        mock_service_instance = MagicMock()
        MockService.return_value = mock_service_instance
        mock_service_instance.create_text_session.return_value = {
            "session_uuid": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Test Title",
            "response": "Test Response",
            "interaction_id": 1
        }
        with patch('src.controllers.chat_controller.chat_service', mock_service_instance):
            response = test_client.post('/chat', json={"prompt": "Hello"})
            assert response.status_code == 201
            data = response.get_json()
            assert data['response'] == "Test Response"
            assert 'session_uuid' in data
            assert 'interaction_id' in data

def test_chat_endpoint_continue_session(test_client, mock_ollama):
    session_uuid = "123e4567-e89b-12d3-a456-426614174000"
    with patch('src.services.chat_service.ChatService') as MockService:
        mock_service_instance = MagicMock()
        MockService.return_value = mock_service_instance
        mock_service_instance.create_text_session.return_value = {
            "session_uuid": session_uuid,
            "title": "Test Title",
            "response": "Test Response 1",
            "interaction_id": 1
        }
        with patch('src.controllers.chat_controller.chat_service', mock_service_instance):
            r1 = test_client.post('/chat', json={"prompt": "Hello"})
            assert r1.status_code == 201
            
            mock_service_instance.send_text_message.return_value = {
                "session_uuid": session_uuid,
                "response": "Test Response 2",
                "interaction_id": 2
            }
            r2 = test_client.post(f'/chat/{session_uuid}', json={"prompt": "Again"})
            assert r2.status_code == 200
            assert r2.get_json()['session_uuid'] == session_uuid

def test_history_endpoint(test_client, mock_ollama):
    session_uuid = "123e4567-e89b-12d3-a456-426614174000"
    with patch('src.services.chat_service.ChatService') as MockService:
        mock_service_instance = MagicMock()
        MockService.return_value = mock_service_instance
        mock_service_instance.get_session_history.return_value = [
            {
                "prompt": "Msg 1",
                "response": "Test Response",
                "created_at": "2024-01-01T00:00:00",
                "model_used": "llama3.2"
            }
        ]
        with patch('src.controllers.chat_controller.chat_service', mock_service_instance):
            r2 = test_client.get(f'/history/{session_uuid}')
            assert r2.status_code == 200
            history = r2.get_json()
            assert len(history) == 1
            assert history[0]['prompt'] == "Msg 1"
            assert history[0]['response'] == "Test Response"

def test_chat_missing_prompt(test_client):
    response = test_client.post('/chat', json={})
    assert response.status_code == 400

def test_invalid_session(test_client, mock_ollama):
    invalid_uuid = "00000000-0000-0000-0000-000000000000"
    with patch('src.services.chat_service.ChatService') as MockService:
        mock_service_instance = MagicMock()
        MockService.return_value = mock_service_instance
        mock_service_instance.send_text_message.side_effect = ValueError("Session not found or access denied")
        with patch('src.controllers.chat_controller.chat_service', mock_service_instance):
            response = test_client.post(f'/chat/{invalid_uuid}', json={"prompt": "Hi"})
            assert response.status_code == 404

def test_service_error_handling(test_client):
    with patch('src.services.chat_service.ChatService') as MockService:
        mock_service_instance = MagicMock()
        MockService.return_value = mock_service_instance
        mock_service_instance.create_text_session.side_effect = Exception("DB Error")
        with patch('src.controllers.chat_controller.chat_service', mock_service_instance):
            response = test_client.post('/chat', json={"prompt": "Fail"})
            assert response.status_code == 500
            assert "DB Error" in response.get_json()['error']
