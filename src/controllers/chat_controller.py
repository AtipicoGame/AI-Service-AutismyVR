from flask import Blueprint, request, jsonify, g
from src.services.chat_service import ChatService
from src.auth import require_firebase_auth
import os

chat_bp = Blueprint('chat', __name__)
chat_service = ChatService()

@chat_bp.route('/chat', methods=['POST'])
@require_firebase_auth
def create_chat():
    """
    Create a new text chat session.
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
              description: The first message
    responses:
      201:
        description: Chat session created
        schema:
          type: object
          properties:
            session_uuid:
              type: string
            title:
              type: string
            response:
              type: string
            interaction_id:
              type: integer
      400:
        description: Bad Request
      401:
        description: Unauthorized
      500:
        description: Internal Server Error
    """
    data = request.get_json()
    prompt = data.get('prompt')
    firebase_uid = g.firebase_uid
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        result = chat_service.create_text_session(prompt, firebase_uid)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/chat/<uuid:session_uuid>', methods=['POST'])
@require_firebase_auth
def send_message(session_uuid):
    """
    Send a message to an existing chat session.
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
      - in: path
        name: session_uuid
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        schema:
          type: object
          required:
            - prompt
          properties:
            prompt:
              type: string
    responses:
      200:
        description: Message sent successfully
      400:
        description: Bad Request
      401:
        description: Unauthorized
      404:
        description: Session not found
      500:
        description: Internal Server Error
    """
    data = request.get_json()
    prompt = data.get('prompt')
    firebase_uid = g.firebase_uid
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    try:
        result = chat_service.send_text_message(str(session_uuid), prompt, firebase_uid)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/history', methods=['GET'])
@require_firebase_auth
def list_sessions():
    """
    List all chat sessions for the authenticated user.
    In dev: returns all interactions. In stag/prod: returns session list only.
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    responses:
      200:
        description: List of sessions or interactions
    """
    firebase_uid = g.firebase_uid
    env_level = os.getenv('ENV_LEVEL', 'dev').lower()
    
    try:
        if env_level == 'dev':
            result = chat_service.get_all_interactions(firebase_uid)
        else:
            result = chat_service.get_user_sessions(firebase_uid)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/history/<uuid:session_uuid>', methods=['GET'])
@require_firebase_auth
def get_session_history(session_uuid):
    """
    Get full history of a specific session.
    ---
    tags:
      - Chat
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_uuid
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Session history
    """
    firebase_uid = g.firebase_uid
    
    try:
        result = chat_service.get_session_history(str(session_uuid), firebase_uid)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

