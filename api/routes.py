from flask import Blueprint
from src.controllers.chat_controller import chat_bp
from src.controllers.audio_controller import audio_bp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(chat_bp)
api_bp.register_blueprint(audio_bp)
