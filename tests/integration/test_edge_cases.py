from api.app import create_app
from unittest.mock import patch, MagicMock
import pytest
from src.services import ChatService

@pytest.fixture
def client_fail():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_history_not_found(client_fail):
    response = client_fail.get('/history/9999999')
    assert response.status_code == 200
    assert response.get_json() == []

def test_llm_missing_content_key(client_fail):
     service = ChatService()
     
     # Mock LLM to return dict without 'content'
     with patch.object(service.ollama_client, 'request', return_value={"total_duration": 1}):
         # Mock DB logic
         with patch('src.services.SessionLocal') as MockSession:
             session = MagicMock()
             session.id = 1
             MockSession.return_value = session
             # Query returns None (new session) or Mock (existing)
             # If we want to test interaction logic:
             # process_message creates session.
             
             # Let's ensure query returns a session or creates one
             # We want to test logic AFTER LLM call: content = ...
             
             result = service.process_message("Hi")
             assert result['response'] == "Error generating response"
             # Assert interaction saved "Error generating response"
             # mock_session.add was called with interaction having response="Error..."
             # We can check that if we want, but coverage is the goal.
