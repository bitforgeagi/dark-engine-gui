import requests
from typing import Tuple, Optional
import webbrowser

class OllamaSystemCheck:
    OLLAMA_API = "http://localhost:11434/api"
    
    @classmethod
    def check_system(cls) -> Tuple[bool, str]:
        """Check if Ollama is running and has models available"""
        
        # Check if Ollama service is running
        try:
            response = requests.get(f"{cls.OLLAMA_API}/version", timeout=2)
            if response.status_code != 200:
                return False, "Ollama service is not responding correctly"
        except requests.exceptions.RequestException:
            return False, "Ollama service is not running"
            
        # Check for available models
        try:
            response = requests.get(f"{cls.OLLAMA_API}/tags")
            models = response.json().get('models', [])
            if not models:
                return False, "No models are installed"
        except:
            return False, "Could not check for installed models"
            
        return True, "System ready"
    
    @classmethod
    def open_ollama_website(cls):
        """Open Ollama website in default browser"""
        webbrowser.open("https://ollama.ai")
    
    @classmethod
    def pull_model(cls, model_name: str, progress_callback: Optional[callable] = None) -> bool:
        """Pull a model from Ollama library"""
        try:
            response = requests.post(
                f"{cls.OLLAMA_API}/pull",
                json={"model": model_name, "stream": True},
                stream=True
            )
            
            for line in response.iter_lines():
                if progress_callback and line:
                    progress_callback(line.decode())
                    
            return True
        except:
            return False 