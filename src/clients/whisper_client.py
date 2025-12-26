import requests
import os

class WhisperClient:
    def __init__(self):
        self.api_url = os.getenv('WHISPER_API_URL', 'http://localhost:8000')
    
    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text using Whisper API.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            with open(audio_file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f'{self.api_url}/transcribe',
                    files=files,
                    timeout=60
                )
                response.raise_for_status()
                return response.json().get('text', '')
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            raise

