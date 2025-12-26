from api.app import create_app
from unittest.mock import patch, MagicMock
import pytest
from src.services.chat_service import ChatService

@pytest.fixture
def client_fail():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_history_not_found(client_fail):
    session_uuid = "00000000-0000-0000-0000-000000000000"
    with patch('src.services.chat_service.ChatService') as MockService:
        mock_service_instance = MockService.return_value
        mock_service_instance.get_session_history.return_value = []
        response = client_fail.get(f'/history/{session_uuid}')
        assert response.status_code == 200
        assert response.get_json() == []

def test_llm_missing_content_key():
     service = ChatService()
     
     # Mock LLM to return dict without 'content'
     with patch.object(service.ollama_client, 'request', return_value={"total_duration": 1}):
         with patch.object(service.title_service, 'generate_title', return_value="Test Title"):
             # Mock DB logic
             with patch('src.services.chat_service.SessionLocal') as MockSession:
                 session = MagicMock()
                 session.id = 1
                 session.session_uuid = "test-uuid"
                 MockSession.return_value = session
                 session.query.return_value.filter.return_value.first.return_value = None
                 
                 result = service.create_text_session("Hi", "test-user")
                 assert result['response'] == "Error generating response"
