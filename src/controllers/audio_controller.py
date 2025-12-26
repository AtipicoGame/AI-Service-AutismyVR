from flask import Blueprint, request, jsonify, g
from src.services.audio_service import AudioService
from src.auth import require_firebase_auth
import os

audio_bp = Blueprint('audio', __name__)
audio_service = AudioService()

@audio_bp.route('/audio2audio', methods=['POST'])
@require_firebase_auth
def create_audio_chat():
    """
    Create a new audio chat session.
    Receives audio file, transcribes, generates title, creates session.
    ---
    tags:
      - Audio
    security:
      - Bearer: []
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
      - in: formData
        name: audio
        type: file
        required: true
        description: Audio file (WAV, MP3, etc.)
      - in: query
        name: liveportrait
        type: boolean
        description: Enable LivePortrait generation
    responses:
      201:
        description: Audio chat session created
        schema:
          type: object
          properties:
            session_uuid:
              type: string
            title:
              type: string
            response_audio_url:
              type: string
            response_text:
              type: string
            liveportrait:
              type: object
      400:
        description: Bad Request
      401:
        description: Unauthorized
      500:
        description: Internal Server Error
    """
    firebase_uid = g.firebase_uid
    liveportrait = request.args.get('liveportrait', '').lower() == 'true'
    
    if 'audio' not in request.files:
        return jsonify({"error": "Audio file is required"}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No audio file selected"}), 400
    
    try:
        result = audio_service.create_audio_session(
            audio_file, 
            firebase_uid, 
            liveportrait=liveportrait
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@audio_bp.route('/audio2audio/<uuid:session_uuid>', methods=['POST'])
@require_firebase_auth
def send_audio_message(session_uuid):
    """
    Send audio to an existing audio chat session.
    ---
    tags:
      - Audio
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
      - in: formData
        name: audio
        type: file
        required: true
      - in: query
        name: liveportrait
        type: boolean
        description: Enable LivePortrait generation
    responses:
      200:
        description: Audio message processed
      400:
        description: Bad Request
      401:
        description: Unauthorized
      404:
        description: Session not found
      500:
        description: Internal Server Error
    """
    firebase_uid = g.firebase_uid
    liveportrait = request.args.get('liveportrait', '').lower() == 'true'
    
    if 'audio' not in request.files:
        return jsonify({"error": "Audio file is required"}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No audio file selected"}), 400
    
    try:
        result = audio_service.send_audio_message(
            str(session_uuid),
            audio_file,
            firebase_uid,
            liveportrait=liveportrait
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

