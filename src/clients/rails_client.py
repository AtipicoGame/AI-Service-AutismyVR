import os
import requests
from typing import Dict, List, Optional

class RailsClient:
    def __init__(self):
        self.base_url = os.getenv("RAILS_API_URL", "http://localhost:3000")
        self.timeout = int(os.getenv("RAILS_API_TIMEOUT", "30"))
    
    def _headers(self, firebase_uid: str) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Firebase-UID": firebase_uid
        }
    
    def create_chat_session(self, firebase_uid: str, title: Optional[str] = None, mode: str = "text") -> Dict:
        url = f"{self.base_url}/apps/artificial_intelligence/api/v1/chat_sessions"
        data = {
            "title": title,
            "mode": mode
        }
        response = requests.post(
            url,
            json=data,
            headers=self._headers(firebase_uid),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_chat_session(self, session_uuid: str, firebase_uid: str) -> Dict:
        url = f"{self.base_url}/apps/artificial_intelligence/api/v1/chat_sessions/{session_uuid}"
        response = requests.get(
            url,
            headers=self._headers(firebase_uid),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def list_chat_sessions(self, firebase_uid: str) -> List[Dict]:
        url = f"{self.base_url}/apps/artificial_intelligence/api/v1/chat_sessions"
        response = requests.get(
            url,
            headers=self._headers(firebase_uid),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def create_interaction(self, session_uuid: str, firebase_uid: str, prompt: str, response: str, 
                          audio_response_url: Optional[str] = None, liveportrait_data: Optional[str] = None,
                          model_used: Optional[str] = None) -> Dict:
        url = f"{self.base_url}/apps/artificial_intelligence/api/v1/chat_sessions/{session_uuid}/interactions"
        data = {
            "prompt": prompt,
            "response": response,
            "audio_response_url": audio_response_url,
            "liveportrait_data": liveportrait_data,
            "model_used": model_used
        }
        response = requests.post(
            url,
            json=data,
            headers=self._headers(firebase_uid),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_interactions(self, session_uuid: str, firebase_uid: str) -> List[Dict]:
        url = f"{self.base_url}/apps/artificial_intelligence/api/v1/chat_sessions/{session_uuid}/interactions"
        response = requests.get(
            url,
            headers=self._headers(firebase_uid),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

