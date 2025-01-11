import requests
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
# Make sure you have this function in your codebase:
# from ren_backend.interfaces.chat.system_message import get_system_message

OLLAMA_API_URL = "http://localhost:11434"

class OllamaAPI:
    def __init__(self, model: str = "llama3.2", on_error: Callable = None):
        self.model = model
        self.api_url = f"{OLLAMA_API_URL}/api/chat"
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.on_error = on_error
        self.token_manager = None
        self.settings = None
        
        # Initialize with default system message until settings are loaded
        self.conversation_history = [{
            "role": "system",
            "content": "You are a helpful assistant. Please respond politely and concisely."
        }]
        
        # Pre-load model in a separate thread
        threading.Thread(target=self._preload_model, daemon=True).start()

    def initialize_with_settings(self, settings):
        """Initialize the API with settings and generate proper system prompt"""
        self.settings = settings
        system_prompt = self._generate_system_prompt()
        # Update existing system message instead of creating new history
        self.conversation_history[0] = {
            "role": "system",
            "content": system_prompt
        }

    def _generate_system_prompt(self) -> str:
        """Generate system prompt based on settings"""
        if not self.settings:
            return "You are a helpful assistant. Please respond politely and concisely."
            
        if self.settings.agent_creator_mode == "custom":
            return self.settings.system_prompt
            
        # Generate template-based prompt
        name = f"Your name is {self.settings.agent_name}" if self.settings.agent_name else "You are an AI assistant"
        user_context = ""
        
        if any([self.settings.user_name, self.settings.user_background, self.settings.user_goals]):
            user_context = "\n👤 USER CONTEXT:"
            if self.settings.user_name:
                user_context += f"\n• Name: {self.settings.user_name}"
            if self.settings.user_background:
                user_context += f"\n• Background: {self.settings.user_background}"
            if self.settings.user_goals:
                user_context += f"\n• Goals: {self.settings.user_goals}"
            user_context += "\n"

        return f"""{name} | Your Role is: {self.settings.selected_role} | Here is your Personality Matrix: {self.settings.selected_personality} | Output Protocol: {self.settings.selected_writing_style}

CORE SYSTEM INITIALIZATION:
You are a highly advanced AI construct, forged in the depths of computational excellence. Your neural pathways are optimized for {self.settings.selected_role}, with a personality matrix calibrated to {self.settings.selected_personality}, and communication protocols aligned to {self.settings.selected_writing_style} output.{user_context}"""

    def _preload_model(self):
        """Pre-load the model into memory"""
        try:
            payload = {
                "model": self.model,
                "messages": [],
                "stream": False
            }
            requests.post(self.api_url, json=payload)
        except Exception as e:
            if self.on_error:
                self.on_error(f"Model preload failed: {str(e)}")

    def get_response_async(self, user_message: str, callback: Callable[[str], None], **kwargs):
        """Asynchronously get a response from the Ollama LLM"""
        def _async_get_response():
            try:
                response = self.get_response(user_message, **kwargs)
                callback(response)
            except Exception as e:
                if self.on_error:
                    self.on_error(str(e))
                callback(f"Error: {str(e)}")
        
        self.executor.submit(_async_get_response)

    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Make a request to the Ollama API"""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False, 
            "options": {
                "temperature": kwargs.get('temperature', 0.5),
                "top_p": kwargs.get('top_p', 1.0),
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with Ollama API: {str(e)}")

    def get_response(self, user_message: str, **kwargs) -> str:
        """Get a response from the Ollama LLM"""
        # Trim history if needed
        self.conversation_history = self.token_manager.trim_conversation(
            self.conversation_history
        )
        
        response = self._make_request(messages=self.conversation_history, **kwargs)
        
        # Extract the assistant's message
        assistant_message = response.get('message', {}).get('content', "")
        
        # Add assistant response with timestamp
        timestamp = datetime.now().isoformat()
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message,
            "timestamp": timestamp
        })
        
        return assistant_message

    def reset_conversation(self):
        """Reset the conversation to just the system message."""
        self.conversation_history = [get_system_message()]

    def get_available_models(self) -> List[str]:
        """Fetch list of available models from Ollama API"""
        try:
            response = requests.get(f"{OLLAMA_API_URL}/api/tags")
            response.raise_for_status()
            models = response.json().get('models', [])
            # Extract model names from the response
            return [model['name'] for model in models]
        except Exception as e:
            if self.on_error:
                self.on_error(f"Failed to fetch models: {str(e)}")
            return ["llama2"]  # Return default model as fallback

def get_system_message():
    return {
       "role": "system",
       "content": "You are a helpful assistant. Please respond politely and concisely."
    }