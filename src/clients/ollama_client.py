import ollama
import os

class OllamaClient:
    def __init__(self, model: str = None):
        self.llm_model = model or os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

    def request(self, prompt: str, system_prompt: str = None):
        try:
            messages = []
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            response = ollama.chat(
                model=self.llm_model,
                messages=messages
            )

            return {
                "content": response['message']['content'],
                "total_duration": response.get('total_duration', 0)
            }
        except Exception as e:
            print(f"Ollama error occurred: {e}")
            return None
    
    def request_with_prompt(self, prompt: str, system_prompt: str):
        return self.request(prompt, system_prompt)

