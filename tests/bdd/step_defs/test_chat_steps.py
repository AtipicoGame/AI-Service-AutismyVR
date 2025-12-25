import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from api.app import create_app
from src.db import Base, engine, SessionLocal
from unittest.mock import patch

scenarios('../features/chat.feature')

from api.routes import chat_service

@pytest.fixture
def client_bdd():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with patch.object(chat_service.ollama_client, 'request') as mock_request:
            mock_request.return_value = {"content": "BDD Response", "total_duration": 1.0}
            yield client

@given('the API is running')
def api_running(client_bdd):
    pass

@given('I have an existing chat session with message "Previous"', target_fixture="session_id")
def existing_session(client_bdd):
    response = client_bdd.post('/chat', json={"prompt": "Previous"})
    return response.get_json()['session_id']

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
