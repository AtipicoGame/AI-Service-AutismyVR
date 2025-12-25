from src.db import SessionLocal
from src.models import ChatSession, Interaction
from models.ollama_client import OllamaClient

class ChatService:
    def __init__(self):
        self.ollama_client = OllamaClient()

    def process_message(self, prompt: str, firebase_uid: str, session_id: int = None):
        """
        Process a user prompt:
        1. Get or create session (associated with firebase_uid)
        2. Call LLM
        3. Save interaction
        4. Return response
        
        Args:
            prompt: User message
            firebase_uid: Firebase user ID (from authenticated token)
            session_id: Optional session ID to continue conversation
        """
        db = SessionLocal()
        try:
            if session_id:
                # Verify session belongs to this user
                session = db.query(ChatSession).filter(
                    ChatSession.id == session_id,
                    ChatSession.firebase_uid == firebase_uid
                ).first()
                if not session:
                    # Session not found or doesn't belong to user - create new
                    session = ChatSession(firebase_uid=firebase_uid)
                    db.add(session)
                    db.commit()
                    db.refresh(session)
            else:
                session = ChatSession(firebase_uid=firebase_uid)
                db.add(session)
                db.commit()
                db.refresh(session)
            
            # Call LLM
            # Reuse existing client logic
            llm_response = self.ollama_client.request(prompt)
            content = llm_response.get("content", "Error generating response") if llm_response else "Error generating response"
            
            # Save Interaction
            interaction = Interaction(
                session_id=session.id,
                prompt=prompt,
                response=content,
                model_used=self.ollama_client.llm_model
            )
            db.add(interaction)
            db.commit()
            
            return {
                "session_id": session.id,
                "response": content,
                "interaction_id": interaction.id
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_history(self, session_id: int, firebase_uid: str):
        """
        Get chat history for a session, ensuring it belongs to the user.
        
        Args:
            session_id: Session ID
            firebase_uid: Firebase user ID (for authorization)
        """
        db = SessionLocal()
        try:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.firebase_uid == firebase_uid
            ).first()
            if not session:
                return []
            return [
                {
                    "prompt": i.prompt,
                    "response": i.response,
                    "created_at": i.created_at.isoformat()
                } for i in session.interactions
            ]
        finally:
            db.close()
    
    def get_user_sessions(self, firebase_uid: str):
        """
        Get all sessions for a user.
        
        Args:
            firebase_uid: Firebase user ID
        """
        db = SessionLocal()
        try:
            sessions = db.query(ChatSession).filter(
                ChatSession.firebase_uid == firebase_uid
            ).order_by(ChatSession.created_at.desc()).all()
            return [
                {
                    "session_id": s.id,
                    "created_at": s.created_at.isoformat(),
                    "interaction_count": len(s.interactions)
                } for s in sessions
            ]
        finally:
            db.close()
