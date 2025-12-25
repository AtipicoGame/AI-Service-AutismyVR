from flask import Blueprint, request, jsonify, g
from src.services import ChatService
from src.auth import require_firebase_auth

api_bp = Blueprint('api', __name__)
chat_service = ChatService()

@api_bp.route('/chat', methods=['POST'])
@require_firebase_auth
def chat():
    """
    Send a message to the AI and get a response.
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Firebase ID token as 'Bearer <token>'
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
      401:
        description: Unauthorized - Invalid or missing Firebase token
      400:
        description: Bad Request - Missing prompt
      500:
        description: Internal Server Error
    """
    data = request.get_json()
    prompt = data.get('prompt')
    session_id = data.get('session_id')
    firebase_uid = g.firebase_uid  # From @require_firebase_auth decorator
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
        
    try:
        result = chat_service.process_message(prompt, firebase_uid, session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/history/<int:session_id>', methods=['GET'])
@require_firebase_auth
def history(session_id):
    """
    Get chat history for a session.
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Firebase ID token as 'Bearer <token>'
      - in: path
        name: session_id
        type: integer
        required: true
    responses:
      200:
        description: History of interactions
        schema:
          type: array
          items:
            type: object
            properties:
              prompt:
                type: string
              response:
                type: string
              created_at:
                type: string
      401:
        description: Unauthorized - Invalid or missing Firebase token
      500:
        description: Internal Server Error
    """
    try:
        firebase_uid = g.firebase_uid  # From @require_firebase_auth decorator
        history = chat_service.get_history(session_id, firebase_uid)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/sessions', methods=['GET'])
@require_firebase_auth
def get_sessions():
    """
    Get all chat sessions for the authenticated user.
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Firebase ID token as 'Bearer <token>'
    responses:
      200:
        description: List of user's chat sessions
        schema:
          type: array
          items:
            type: object
            properties:
              session_id:
                type: integer
              created_at:
                type: string
              interaction_count:
                type: integer
      401:
        description: Unauthorized - Invalid or missing Firebase token
      500:
        description: Internal Server Error
    """
    try:
        firebase_uid = g.firebase_uid
        sessions = chat_service.get_user_sessions(firebase_uid)
        return jsonify(sessions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
