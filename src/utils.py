# utils.py

import tiktoken

def format_timestamp(ts):
    """Example utility function: format a timestamp as a readable string."""
    return ts.strftime("%Y-%m-%d %H:%M:%S")

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Estimate token count for text using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback to rough estimation if tiktoken fails
        return len(text.split()) * 1.3

class TokenManager:
    def __init__(self, settings):
        self.settings = settings
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return count_tokens(text)
    
    def check_input_length(self, text: str) -> tuple[bool, str]:
        """Check if input text is within token limits"""
        tokens = count_tokens(text)
        if tokens > self.settings.max_input_tokens:
            return False, f"Message too long ({tokens} tokens). Maximum is {self.settings.max_input_tokens} tokens."
        return True, ""
    
    def check_system_prompt(self, text: str) -> tuple[bool, str]:
        """Check if system prompt is within limits"""
        tokens = count_tokens(text)
        if tokens > self.settings.max_system_prompt_tokens:
            return False, f"System prompt too long ({tokens} tokens). Maximum is {self.settings.max_system_prompt_tokens} tokens."
        return True, ""
    
    def estimate_conversation_tokens(self, messages: list) -> int:
        """Estimate total tokens in conversation"""
        return sum(count_tokens(msg["content"]) for msg in messages)
    
    def should_trim_history(self, messages: list) -> bool:
        """Check if conversation history needs trimming"""
        total_tokens = self.estimate_conversation_tokens(messages)
        return total_tokens > (self.settings.max_context_tokens - self.settings.token_padding)
    
    def trim_conversation(self, messages: list) -> list:
        """Trim conversation history to fit token limits while keeping system prompt"""
        if len(messages) <= 2:  # System prompt + current message
            return messages
            
        while self.should_trim_history(messages):
            # Remove oldest non-system messages
            for i in range(1, len(messages)):
                if messages[i]["role"] != "system":
                    messages.pop(i)
                    break
        
        return messages
