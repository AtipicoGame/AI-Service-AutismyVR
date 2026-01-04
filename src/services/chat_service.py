from src.clients.ollama_client import OllamaClient
from src.clients.rails_client import RailsClient
from src.services.title_service import TitleService
import os

class ChatService:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.title_service = TitleService()
        self.rails_client = RailsClient()
    
    def create_text_session(self, prompt: str, firebase_uid: str):
        title = self.title_service.generate_title(prompt)
        
        session = self.rails_client.create_chat_session(
            firebase_uid=firebase_uid,
            title=title,
            mode="text"
        )
        
        llm_response = self.ollama_client.request(prompt)
        content = llm_response.get("content", "Error generating response") if llm_response else "Error generating response"
        
        interaction = self.rails_client.create_interaction(
            session_uuid=session["session_uuid"],
            firebase_uid=firebase_uid,
            prompt=prompt,
            response=content,
            model_used=self.ollama_client.llm_model
        )
        
        return {
            "session_uuid": session["session_uuid"],
            "title": title,
            "response": content,
            "interaction_id": interaction["id"]
        }
    
    def send_text_message(self, session_uuid: str, prompt: str, firebase_uid: str):
        session = self.rails_client.get_chat_session(session_uuid, firebase_uid)
        
        if not session:
            raise ValueError("Session not found or access denied")
        
        history = self._build_history(session_uuid, firebase_uid)
        
        llm_response = self.ollama_client.request(prompt)
        content = llm_response.get("content", "Error generating response") if llm_response else "Error generating response"
        
        interaction = self.rails_client.create_interaction(
            session_uuid=session_uuid,
            firebase_uid=firebase_uid,
            prompt=prompt,
            response=content,
            model_used=self.ollama_client.llm_model
        )
        
        return {
            "session_uuid": session_uuid,
            "response": content,
            "interaction_id": interaction["id"]
        }
    
    def get_session_history(self, session_uuid: str, firebase_uid: str):
        interactions = self.rails_client.get_interactions(session_uuid, firebase_uid)
        
        return [
            {
                "prompt": i["prompt"],
                "response": i["response"],
                "created_at": i["created_at"],
                "model_used": i.get("model_used")
            } for i in interactions
        ]
    
    def get_user_sessions(self, firebase_uid: str):
        sessions = self.rails_client.list_chat_sessions(firebase_uid)
        
        return [
            {
                "session_uuid": s["session_uuid"],
                "title": s["title"],
                "mode": s["mode"],
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
                "interaction_count": s["interaction_count"]
            } for s in sessions
        ]
    
    def get_all_interactions(self, firebase_uid: str):
        sessions = self.rails_client.list_chat_sessions(firebase_uid)
        
        interactions = []
        for session in sessions:
            session_interactions = self.rails_client.get_interactions(session["session_uuid"], firebase_uid)
            for interaction in session_interactions:
                interactions.append({
                    "session_uuid": session["session_uuid"],
                    "session_title": session["title"],
                    "prompt": interaction["prompt"],
                    "response": interaction["response"],
                    "created_at": interaction["created_at"],
                    "model_used": interaction.get("model_used")
                })
        
        return sorted(interactions, key=lambda x: x['created_at'], reverse=True)
    
    def _build_history(self, session_uuid: str, firebase_uid: str):
        interactions = self.rails_client.get_interactions(session_uuid, firebase_uid)
        
        history = []
        for interaction in interactions:
            history.append({"role": "user", "content": interaction["prompt"]})
            history.append({"role": "assistant", "content": interaction["response"]})
        return history

