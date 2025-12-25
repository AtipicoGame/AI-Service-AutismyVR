from flask import Blueprint, request, jsonify
from src.services import ChatService

api_bp = Blueprint('api', __name__)
chat_service = ChatService()

@api_bp.route('/chat', methods=['POST'])
def chat():
    """
    Send a message to the AI and get a response.
    ---
    tags:
      - Chat
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - prompt
          properties:
            prompt:
              type: string
              description: The user message
            session_id:
              type: integer
              description: Optional session ID to continue conversation
    responses:
      200:
        description: AI Response
        schema:
          type: object
          properties:
            response:
              type: string
            session_id:
              type: integer
            interaction_id:
              type: integer
      500:
        description: Internal Server Error
    """
    data = request.get_json()
    prompt = data.get('prompt')
    session_id = data.get('session_id')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
        
    try:
        result = chat_service.process_message(prompt, session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/history/<int:session_id>', methods=['GET'])
def history(session_id):
    """
    Get chat history for a session.
    ---
    tags:
      - Chat
    parameters:
      - in: path
        name: session_id
        type: integer
        required: true
    responses:
      200:
        description: History of interactions
      500:
        description: Internal Server Error
    """
    try:
        history = chat_service.get_history(session_id)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
