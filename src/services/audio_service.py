from src.clients.whisper_client import WhisperClient
from src.clients.tts_client import TTSClient
from src.clients.liveportrait_client import LivePortraitClient
from src.clients.ollama_client import OllamaClient
from src.clients.rails_client import RailsClient
from src.services.title_service import TitleService
import tempfile
import os

class AudioService:
    def __init__(self):
        self.whisper = WhisperClient()
        self.tts = TTSClient()
        self.liveportrait = LivePortraitClient()
        self.ollama = OllamaClient(model='gemma2:1b')
        self.title_service = TitleService()
        self.rails_client = RailsClient()
    
    def create_audio_session(self, audio_file, firebase_uid: str, liveportrait: bool = False):
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                audio_file.save(tmp.name)
                tmp_path = tmp.name
            
            transcribed_text = self.whisper.transcribe(tmp_path)
            
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
            title = self.title_service.generate_title(transcribed_text)
            
            session = self.rails_client.create_chat_session(
                firebase_uid=firebase_uid,
                title=title,
                mode="audio"
            )
            
            prompt_file = 'prompts/Conversational/AutismyVR-Gemma3:1b.txt'
            system_prompt = ""
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
            
            response_text = self.ollama.request_with_prompt(transcribed_text, system_prompt)
            content = response_text.get("content", "Error generating response") if response_text else "Error generating response"
            
            audio_response = self.tts.synthesize(content)
            audio_url = self._save_audio(audio_response, session["session_uuid"])
            
            liveportrait_data = None
            if liveportrait or self.liveportrait.enabled:
                liveportrait_data = self.liveportrait.generate(content, audio_url=audio_url)
            
            self.rails_client.create_interaction(
                session_uuid=session["session_uuid"],
                firebase_uid=firebase_uid,
                prompt=transcribed_text,
                response=content,
                audio_response_url=audio_url,
                liveportrait_data=str(liveportrait_data) if liveportrait_data else None,
                model_used='gemma2:1b'
            )
            
            return {
                'session_uuid': session["session_uuid"],
                'title': title,
                'response_audio_url': audio_url,
                'response_text': content,
                'liveportrait': liveportrait_data
            }
        except Exception as e:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e
    
    def send_audio_message(self, session_uuid: str, audio_file, firebase_uid: str, liveportrait: bool = False):
        tmp_path = None
        try:
            session = self.rails_client.get_chat_session(session_uuid, firebase_uid)
            
            if not session:
                raise ValueError("Session not found or access denied")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                audio_file.save(tmp.name)
                tmp_path = tmp.name
            
            transcribed_text = self.whisper.transcribe(tmp_path)
            
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
            prompt_file = 'prompts/Conversational/AutismyVR-Gemma3:1b.txt'
            system_prompt = ""
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
            
            history = self._build_history(session_uuid, firebase_uid)
            
            response_text = self.ollama.request_with_prompt(transcribed_text, system_prompt)
            content = response_text.get("content", "Error generating response") if response_text else "Error generating response"
            
            audio_response = self.tts.synthesize(content)
            audio_url = self._save_audio(audio_response, session_uuid)
            
            liveportrait_data = None
            if liveportrait or self.liveportrait.enabled:
                liveportrait_data = self.liveportrait.generate(content, audio_url=audio_url)
            
            self.rails_client.create_interaction(
                session_uuid=session_uuid,
                firebase_uid=firebase_uid,
                prompt=transcribed_text,
                response=content,
                audio_response_url=audio_url,
                liveportrait_data=str(liveportrait_data) if liveportrait_data else None,
                model_used='gemma2:1b'
            )
            
            return {
                'session_uuid': session_uuid,
                'response_audio_url': audio_url,
                'response_text': content,
                'liveportrait': liveportrait_data
            }
        except Exception as e:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e
    
    def _save_audio(self, audio_data: bytes, session_uuid: str) -> str:
        """
        Save audio file and return URL.
        For now, returns a placeholder URL. In production, save to S3/storage.
        
        Args:
            audio_data: Audio bytes
            session_uuid: Session UUID
            
        Returns:
            Audio URL
        """
        audio_dir = 'audio_responses'
        os.makedirs(audio_dir, exist_ok=True)
        
        audio_path = os.path.join(audio_dir, f'{session_uuid}.wav')
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        return f'/audio/{session_uuid}.wav'
    
    def _build_history(self, session_uuid: str, firebase_uid: str):
        interactions = self.rails_client.get_interactions(session_uuid, firebase_uid)
        
        history = []
        for interaction in interactions:
            history.append({"role": "user", "content": interaction["prompt"]})
            history.append({"role": "assistant", "content": interaction["response"]})
        return history

