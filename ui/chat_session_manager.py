import time
from src.services import ChatService

# Helper class to manage chat session and response generation
class ChatSessionManager:
    def __init__(self):
        self.chat_service = ChatService()
        self.session_id = None

    def response_generator(self, prompt):
        start_time = time.time()

        # Process message via Service (saves to DB and gets response)
        # Note: This is synchronous wait for LLM
        result = self.chat_service.process_message(prompt, self.session_id)
        
        full_response = result["response"]
        self.session_id = result["session_id"]
        
        # Simulate typing effect by yielding chunks of the response
        chunk_size = 5
        for i in range(0, len(full_response), chunk_size):
            yield full_response[i:i + chunk_size]
            time.sleep(0.01) # Faster simulation

        # Calculate total time taken (this is just python processing time + wait, actual LLM time was inside service)
        total_time_elapsed = time.time() - start_time
        yield f"\n\n---\n⏱️ Total Process Time: {total_time_elapsed:.2f} seconds\n"
