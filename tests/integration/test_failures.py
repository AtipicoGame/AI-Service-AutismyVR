import pytest
from unittest.mock import patch, MagicMock
from api.app import create_app
from src.services import ChatService
from api.routes import chat_service

@pytest.fixture
def client_fail():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_history_error(client_fail):
    with patch('src.services.ChatService.get_history', side_effect=Exception("History Error")):
        response = client_fail.get('/history/1')
        assert response.status_code == 500
        assert "History Error" in response.get_json()['error']

def test_service_db_rollback():
    # Test that rollback happens on error
    service = ChatService()
    
    # We need to mock SessionLocal to return a session that raises on commit
    mock_session = MagicMock()
    mock_session.commit.side_effect = Exception("Commit Fail")
    
    with patch('src.services.SessionLocal', return_value=mock_session):
        # Allow query to work for creating session (or just ignore finding session)
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Determine behavior of ollama
        with patch.object(service.ollama_client, 'request', return_value={"content": "OK", "total_duration": 1}):
            with pytest.raises(Exception) as exc:
                service.process_message("Hi")
            assert "Commit Fail" in str(exc.value)
            mock_session.rollback.assert_called()

def test_app_db_init_failure():
    with patch('src.db.Base.metadata.create_all', side_effect=Exception("DB Init Fail")):
        # Should check it prints error but doesn't crash create_app
        try:
            app = create_app()
            assert app is not None
        except Exception:
            pytest.fail("create_app crashed on db failure")

def test_llm_returns_none(client_fail):
    # Test when LLM returns None
    with patch('src.services.ChatService.process_message') as mock_process:
        # Actually we want to test the service logic, so we shouldn't mock process_message
        pass

    service = ChatService()
    # Mock DB session to avoid real DB interaction and just check logic
    with patch('src.services.SessionLocal') as MockSession:
        session = MockSession.return_value
        session.query.return_value.filter.return_value.first.return_value = MagicMock(id=1)
        
        with patch.object(service.ollama_client, 'request', return_value=None):
            result = service.process_message("Hi", session_id=1)
            # It should return "Error generating response"
            assert result['response'] == "Error generating response"
