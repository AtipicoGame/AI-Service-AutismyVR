import time
from src.services.chat_service import ChatService

class ChatSessionManager:
    def __init__(self):
        self.chat_service = ChatService()
        self.session_uuid = None

    def response_generator(self, prompt):
        start_time = time.time()

        firebase_uid = 'dev-user'
        
        if self.session_uuid:
            result = self.chat_service.send_text_message(self.session_uuid, prompt, firebase_uid)
        else:
            result = self.chat_service.create_text_session(prompt, firebase_uid)
            self.session_uuid = result["session_uuid"]
        
        full_response = result["response"]
        
        chunk_size = 5
        for i in range(0, len(full_response), chunk_size):
            yield full_response[i:i + chunk_size]
            time.sleep(0.01)

        total_time_elapsed = time.time() - start_time
        yield f"\n\n---\n⏱️ Total Process Time: {total_time_elapsed:.2f} seconds\n"
