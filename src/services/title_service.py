from src.clients.ollama_client import OllamaClient

class TitleService:
    def __init__(self):
        self.ollama = OllamaClient(model='gemma2:270m')
    
    def generate_title(self, first_message: str) -> str:
        """
        Generate a chat session title based on the first message.
        
        Args:
            first_message: The first message in the conversation
            
        Returns:
            Generated title (max 255 chars)
        """
        prompt = f"Generate a short, descriptive title (max 50 characters) for a conversation that starts with: '{first_message[:200]}'"
        
        response = self.ollama.request(prompt)
        if response and response.get('content'):
            title = response['content'].strip()
            title = title.replace('"', '').replace("'", '')
            if len(title) > 255:
                title = title[:252] + '...'
            return title[:255]
        
        return first_message[:50] + '...' if len(first_message) > 50 else first_message

