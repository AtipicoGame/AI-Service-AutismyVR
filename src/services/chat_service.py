from src.db import SessionLocal
from src.models.chat_models import ChatSession, Interaction, ChatMode
from src.clients.ollama_client import OllamaClient
from src.services.title_service import TitleService
import uuid
import os

class ChatService:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.title_service = TitleService()
    
    def create_text_session(self, prompt: str, firebase_uid: str):
        """
        Create a new text chat session with first message.
        
        Args:
            prompt: First message text
            firebase_uid: Firebase user ID
            
        Returns:
            dict with session_uuid, response, and interaction_id
        """
        db = SessionLocal()
        try:
            title = self.title_service.generate_title(prompt)
            
            session = ChatSession(
                session_uuid=uuid.uuid4(),
                firebase_uid=firebase_uid,
                title=title,
                mode=ChatMode.TEXT
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
            llm_response = self.ollama_client.request(prompt)
            content = llm_response.get("content", "Error generating response") if llm_response else "Error generating response"
            
            interaction = Interaction(
                session_id=session.id,
                prompt=prompt,
                response=content,
                model_used=self.ollama_client.llm_model
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            
            return {
                "session_uuid": str(session.session_uuid),
                "title": title,
                "response": content,
                "interaction_id": interaction.id
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def send_text_message(self, session_uuid: str, prompt: str, firebase_uid: str):
        """
        Send a message to an existing text chat session.
        
        Args:
            session_uuid: Session UUID
            prompt: Message text
            firebase_uid: Firebase user ID
            
        Returns:
            dict with response and interaction_id
        """
        db = SessionLocal()
        try:
            session = db.query(ChatSession).filter(
                ChatSession.session_uuid == session_uuid,
                ChatSession.firebase_uid == firebase_uid,
                ChatSession.mode == ChatMode.TEXT
            ).first()
            
            if not session:
                raise ValueError("Session not found or access denied")
            
            history = self._build_history(session)
            
            llm_response = self.ollama_client.request(prompt)
            content = llm_response.get("content", "Error generating response") if llm_response else "Error generating response"
            
            interaction = Interaction(
                session_id=session.id,
                prompt=prompt,
                response=content,
                model_used=self.ollama_client.llm_model
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            
            return {
                "session_uuid": str(session.session_uuid),
                "response": content,
                "interaction_id": interaction.id
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_session_history(self, session_uuid: str, firebase_uid: str):
        """
        Get full history of a specific session.
        
        Args:
            session_uuid: Session UUID
            firebase_uid: Firebase user ID
            
        Returns:
            List of interactions
        """
        db = SessionLocal()
        try:
            session = db.query(ChatSession).filter(
                ChatSession.session_uuid == session_uuid,
                ChatSession.firebase_uid == firebase_uid
            ).first()
            
            if not session:
                return []
            
            return [
                {
                    "prompt": i.prompt,
                    "response": i.response,
                    "created_at": i.created_at.isoformat(),
                    "model_used": i.model_used
                } for i in session.interactions
            ]
        finally:
            db.close()
    
    def get_user_sessions(self, firebase_uid: str):
        """
        Get all sessions for a user.
        
        Args:
            firebase_uid: Firebase user ID
            
        Returns:
            List of session summaries
        """
        db = SessionLocal()
        try:
            sessions = db.query(ChatSession).filter(
                ChatSession.firebase_uid == firebase_uid
            ).order_by(ChatSession.created_at.desc()).all()
            
            return [
                {
                    "session_uuid": str(s.session_uuid),
                    "title": s.title,
                    "mode": s.mode.value,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat(),
                    "interaction_count": len(s.interactions)
                } for s in sessions
            ]
        finally:
            db.close()
    
    def get_all_interactions(self, firebase_uid: str):
        """
        Get all interactions for a user (dev mode only).
        
        Args:
            firebase_uid: Firebase user ID
            
        Returns:
            List of all interactions across all sessions
        """
        db = SessionLocal()
        try:
            sessions = db.query(ChatSession).filter(
                ChatSession.firebase_uid == firebase_uid
            ).all()
            
            interactions = []
            for session in sessions:
                for interaction in session.interactions:
                    interactions.append({
                        "session_uuid": str(session.session_uuid),
                        "session_title": session.title,
                        "prompt": interaction.prompt,
                        "response": interaction.response,
                        "created_at": interaction.created_at.isoformat(),
                        "model_used": interaction.model_used
                    })
            
            return sorted(interactions, key=lambda x: x['created_at'], reverse=True)
        finally:
            db.close()
    
    def _build_history(self, session: ChatSession):
        """
        Build conversation history for context.
        
        Args:
            session: ChatSession object
            
        Returns:
            List of message dicts
        """
        history = []
        for interaction in session.interactions:
            history.append({"role": "user", "content": interaction.prompt})
            history.append({"role": "assistant", "content": interaction.response})
        return history

