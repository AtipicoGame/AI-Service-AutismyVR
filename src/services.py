from src.db import SessionLocal
from src.models import ChatSession, Interaction
from models.ollama_client import OllamaClient

class ChatService:
    def __init__(self):
        self.ollama_client = OllamaClient()

    def process_message(self, prompt: str, session_id: int = None):
        """
        Process a user prompt:
        1. Get or create session
        2. Call LLM
        3. Save interaction
        4. Return response
        """
        db = SessionLocal()
        try:
            if session_id:
                session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
                if not session:
                    # Fallback or error? For now create new if not found, or maybe just create new
                    session = ChatSession()
                    db.add(session)
                    db.commit()
            else:
                session = ChatSession()
                db.add(session)
                db.commit()
                # Refresh to get ID?
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

    def get_history(self, session_id: int):
        db = SessionLocal()
        try:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
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
