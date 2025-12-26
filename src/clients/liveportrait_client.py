import requests
import os

class LivePortraitClient:
    def __init__(self):
        self.api_url = os.getenv('LIVEPORTRAIT_API_URL', 'http://localhost:8002')
        self.enabled = os.getenv('LIVEPORTRAIT_ENABLED', 'false').lower() == 'true'
    
    def generate(self, text: str, audio_url: str = None) -> dict:
        """
        Generate LivePortrait avatar animation.
        
        Args:
            text: Text to animate
            audio_url: Optional audio URL for lip-sync
            
        Returns:
            LivePortrait data or None if disabled
        """
        if not self.enabled:
            return None
        
        try:
            response = requests.post(
                f'{self.api_url}/generate',
                json={'text': text, 'audio_url': audio_url},
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"LivePortrait generation error: {e}")
            return None

