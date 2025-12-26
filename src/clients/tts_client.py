import requests
import os

class TTSClient:
    def __init__(self):
        self.api_url = os.getenv('TTS_API_URL', 'http://localhost:8001')
    
    def synthesize(self, text: str, voice: str = 'default') -> bytes:
        """
        Synthesize text to speech audio.
        
        Args:
            text: Text to convert to speech
            voice: Voice model to use
            
        Returns:
            Audio data as bytes
        """
        try:
            response = requests.post(
                f'{self.api_url}/synthesize',
                json={'text': text, 'voice': voice},
                timeout=60
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"TTS synthesis error: {e}")
            raise

