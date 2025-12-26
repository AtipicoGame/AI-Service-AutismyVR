import pytest
from unittest.mock import patch, MagicMock
from api.app import create_app
from src.services.chat_service import ChatService

@pytest.fixture
def client_fail():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_history_error(client_fail):
    session_uuid = "123e4567-e89b-12d3-a456-426614174000"
    with patch('src.services.chat_service.ChatService') as MockService:
        mock_service_instance = MockService.return_value
        mock_service_instance.get_session_history.side_effect = Exception("History Error")
        response = client_fail.get(f'/history/{session_uuid}')
        assert response.status_code == 500
        assert "History Error" in response.get_json()['error']

def test_service_db_rollback():
    # Test that rollback happens on error
    service = ChatService()
    
    # We need to mock SessionLocal to return a session that raises on commit
    mock_session = MagicMock()
    mock_session.commit.side_effect = Exception("Commit Fail")
    
    with patch('src.services.chat_service.SessionLocal', return_value=mock_session):
        # Allow query to work for creating session (or just ignore finding session)
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Determine behavior of ollama
        with patch.object(service.ollama_client, 'request', return_value={"content": "OK", "total_duration": 1}):
            with patch.object(service.title_service, 'generate_title', return_value="Test Title"):
                with pytest.raises(Exception) as exc:
                    service.create_text_session("Hi", "test-user")
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

def test_llm_returns_none():
    # Test when LLM returns None
    service = ChatService()
    # Mock DB session to avoid real DB interaction and just check logic
    with patch('src.services.chat_service.SessionLocal') as MockSession:
        session = MockSession.return_value
        session.query.return_value.filter.return_value.first.return_value = None
        
        with patch.object(service.ollama_client, 'request', return_value=None):
            with patch.object(service.title_service, 'generate_title', return_value="Test Title"):
                result = service.create_text_session("Hi", "test-user")
                # It should return "Error generating response"
                assert result['response'] == "Error generating response"
