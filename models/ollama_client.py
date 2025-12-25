# Ollama Client Connector
import ollama


class OllamaClient:
    # Ollama Model
    llm_model = "llama3.2"

    def request(self, prompt):
        try:
            # Generate the response
            response = ollama.chat(
                model=self.llm_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )

            return {"content": response['message']['content'], "total_duration": response['total_duration']}
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
