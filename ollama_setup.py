import os
import ollama
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("enge_ai.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EngE-AI")

# Load environment variables
load_dotenv()

class OllamaManager:
    """Manager for Ollama LLM interactions"""

    def __init__(self, model_name="llama3.2"):
        """
        Initialize the Ollama manager with the specified model.

        Args:
            model_name (str): Name of the Ollama model to use
        """
        self.model_name = model_name
        self.api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        self.is_available = self._check_model_availability()

        if not self.is_available:
            logger.info(f"Model {model_name} not found. Pulling from Ollama library...")
            self._pull_model()

    def _check_model_availability(self):
        """Check if the specified model is available locally"""
        try:
            models = ollama.list()
            for model in models.get('models', []):
                if model.get('name') == self.model_name:
                    logger.info(f"Model {self.model_name} is available locally")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking model availability: {str(e)}")
            return False

    def _pull_model(self):
        """Pull the model from Ollama repository"""
        try:
            logger.info(f"Pulling model {self.model_name}...")
            ollama.pull(self.model_name)
            self.is_available = True
            logger.info(f"Model {self.model_name} successfully pulled")
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
            self.is_available = False

    def generate_response(self, prompt, system_prompt=None, temperature=0.7, max_tokens=1024):
        """
        Generate a response using the Ollama model

        Args:
            prompt (str): The user prompt
            system_prompt (str, optional): System instructions for the model
            temperature (float): Controls randomness (0.0-1.0)
            max_tokens (int): Maximum number of tokens to generate

        Returns:
            str: Generated response text
        """
        if not self.is_available:
            return "Model is not available. Please check logs for details."

        try:
            params = {
                "model": self.model_name,
                "prompt": prompt,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            if system_prompt:
                params["system"] = system_prompt

            response = ollama.generate(**params)
            return response.get('response', "No response generated")

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Error generating response: {str(e)}"

    def chat(self, messages, temperature=0.7, max_tokens=1024):
        """
        Multi-turn conversation with the model

        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            temperature (float): Controls randomness (0.0-1.0)
            max_tokens (int): Maximum number of tokens to generate

        Returns:
            str: Generated response text
        """
        if not self.is_available:
            return "Model is not available. Please check logs for details."

        try:
            params = {
                "model": self.model_name,
                "messages": messages,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            response = ollama.chat(**params)
            return response.get('message', {}).get('content', "No response generated")

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"Error in chat: {str(e)}"

    def list_available_models(self):
        """List all available models"""
        try:
            models = ollama.list()
            return [model.get('name') for model in models.get('models', [])]
        except Exception as e:
            logger.error(f"Error listing available models: {str(e)}")
            return []

    def set_model(self, model_name):
        """Set the model to the specified model_name"""
        self.model_name = model_name
        self.is_available = self._check_model_availability()
        if not self.is_available:
            self._pull_model()

if __name__ == "__main__":
    # Simple test of the OllamaManager
    manager = OllamaManager()
    if manager.is_available:
        test_prompt = "Explain what critical thinking means in engineering education."
        response = manager.generate_response(test_prompt)
        print(f"Test response: {response}")
    else:
        print("Model is not available. Please check logs for details.")
