import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from api.app import create_app
from src.db import Base, engine, SessionLocal
from unittest.mock import patch, MagicMock
from src.services.chat_service import ChatService

scenarios('../features/chat.feature')

@pytest.fixture
def client_bdd():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with patch('src.services.chat_service.ChatService') as MockService:
            mock_service_instance = MagicMock()
            MockService.return_value = mock_service_instance
            mock_service_instance.create_text_session.return_value = {
                "session_uuid": "bdd-session-uuid",
                "title": "BDD Title",
                "response": "BDD Response",
                "interaction_id": 1
            }
            mock_service_instance.send_text_message.return_value = {
                "session_uuid": "bdd-session-uuid",
                "response": "BDD Response",
                "interaction_id": 2
            }
            mock_service_instance.get_session_history.return_value = [
                {
                    "prompt": "Previous",
                    "response": "BDD Response",
                    "created_at": "2024-01-01T00:00:00",
                    "model_used": "llama3.2"
                }
            ]
            with patch('src.controllers.chat_controller.chat_service', mock_service_instance):
                yield client

@given('the API is running')
def api_running(client_bdd):
    pass

@given('I have an existing chat session with message "Previous"', target_fixture="session_id")
def existing_session(client_bdd):
    response = client_bdd.post('/chat', json={"prompt": "Previous"})
    return response.get_json()['session_uuid']

@when(parsers.parse('I send a POST request to "/chat" with prompt "{prompt}"'))
def send_chat(client_bdd, prompt):
    pytest.response = client_bdd.post('/chat', json={"prompt": prompt})

@when('I get the history for that session')
def get_history(client_bdd, session_id):
    pytest.response = client_bdd.get(f'/history/{session_id}')

@then(parsers.parse('the response status code should be {code:d}'))
def check_status(code):
    assert pytest.response.status_code == code

@then(parsers.parse('the response should contain "{field}"'))
def check_field(field):
    assert field in pytest.response.get_json()

@then(parsers.parse('the list should contain {count:d} item'))
def check_list_count(count):
    assert len(pytest.response.get_json()) == count

@then(parsers.parse('the item should have prompt "{prompt}"'))
def check_item_prompt(prompt):
    assert pytest.response.get_json()[0]['prompt'] == prompt
