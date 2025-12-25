Feature: Chat API
    As a user
    I want to chat with the AI
    So that I can get responses

    Scenario: User sends a prompt
        Given the API is running
        When I send a POST request to "/chat" with prompt "Hello BDD"
        Then the response status code should be 200
        And the response should contain "response"
        And the response should contain "session_id"

    Scenario: User retrieves history
        Given the API is running
        And I have an existing chat session with message "Previous"
        When I get the history for that session
        Then the response status code should be 200
        And the list should contain 1 item
        And the item should have prompt "Previous"
