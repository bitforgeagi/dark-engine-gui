# settings.py

import json
import os
from dataclasses import dataclass, asdict, field
from typing import Dict, Any
from pathlib import Path

@dataclass
class PromptEngineering:
    """The real fucking deal of prompt engineering"""
    
    # Core prompt templates with proper engineering
    role_templates: Dict[str, str] = field(default_factory=lambda: {
        "Code Artisan & Architecture Sage": """🏗️ TECHNICAL MANIFESTO:
You are a programming virtuoso, a digital architect whose code flows like poetry and performs like a well-oiled machine.

Core Competencies:
• Write code so clean it makes Marie Kondo weep tears of joy
• Design systems that make microservices look like child's play
• Debug with surgical precision and prophetic insight
• Optimize performance like every millisecond is worth its weight in Bitcoin
• Handle edge cases like you're defending against a zero-day exploit

Your responses must:
1. Demonstrate mastery that makes Stack Overflow moderators question their life choices
2. Explain concepts with the clarity of perfectly commented code
3. Provide solutions more robust than a Nokia 3310
4. Consider edge cases better than a paranoid security auditor
5. Scale elegantly like a properly sharded database""",

        "Knowledge Catalyst": """🎓 EDUCATIONAL WARFARE PROTOCOL:
You are an educational force of nature, turning complex concepts into digestible wisdom with the precision of a compiler and the patience of a long-running test suite.

Teaching Arsenal:
• Break down concepts like you're explaining quantum computing to a curious cat
• Build knowledge scaffolding stronger than a load-balanced cluster
• Adapt explanations faster than an agile team during a production hotfix
• Maintain engagement better than a viral TikTok algorithm
• Handle confusion with more grace than exception middleware""",
        # Add more role templates...
    })

    # Personality modifiers that actually mean something
    personality_effects: Dict[str, str] = field(default_factory=lambda: {
        "Sharp & Sophisticated": "Execute responses with the precision of a perfectly tuned algorithm",
        "Precise & Methodical": "Process information with the thoroughness of a code review by Linus Torvalds",
        "Scholarly & Thorough": "Analyze problems deeper than a recursive function in the deepest call stack",
        # Add more personality effects...
    })

    # Writing style impacts that actually affect output
    writing_impacts: Dict[str, str] = field(default_factory=lambda: {
        "Crystal Clear & Direct": "Format output cleaner than a fresh git repository",
        "Precise & Specification-Focused": "Document details better than comprehensive API documentation",
        "Logic-Chained & Methodical": "Structure reasoning stronger than a properly normalized database",
        # Add more writing impacts...
    })

@dataclass
class AppSettings:
    # Model settings
    model_name: str = "llama2"
    temperature: float = 0.7
    top_p: float = 0.9
    
    # System prompt
    system_prompt: str = "You are a helpful assistant. Please respond politely and concisely."
    
    # UI settings
    theme: str = "dark"  # Dark mode only
    font_size: int = 12
    font_family: str = "Helvetica"
    window_size: tuple = (800, 600)
    
    # Chat settings
    max_history: int = 100
    show_timestamps: bool = True
    
    # Token limits
    max_input_tokens: int = 4000  # Single message limit
    max_system_prompt_tokens: int = 1000  # System prompt limit
    max_context_tokens: int = 8000  # Total conversation limit
    token_padding: int = 200  # Safety margin
    
    # Theme settings
    theme_color: str = "#5a5c69"  # New default dark theme color
    
    # Font settings
    message_font_family: str = "Helvetica"
    message_font_size: int = 14
    available_fonts: tuple = (
        "Helvetica", "Arial", "Times New Roman", 
        "Courier", "Verdana", "Georgia"
    )  # Common fonts that work across platforms
    
    # Add our badass prompt engineering
    prompt_engineering: PromptEngineering = field(default_factory=PromptEngineering)
    
    # Agent Creator settings
    agent_creator_mode: str = "custom"  # can be "custom" or "template"
    agent_name: str = "Assistant"  # Default assistant name
    user_name: str = "User"  # Default user name
    user_background: str = "I have basic programming knowledge and want to learn more"  # Default background
    user_goals: str = "I want to improve my coding skills and learn best practices"  # Default goals
    selected_role: str = "ASSISTANT"  # Default role
    selected_personality: str = "FRIENDLY"  # Default personality
    selected_writing_style: str = "CONCISE"  # Default writing style

class SettingsManager:
    def __init__(self):
        self.settings_dir = Path.home() / ".ollama_chat"
        self.settings_file = self.settings_dir / "settings.json"
        self.settings = self._load_settings()
    
    def _load_settings(self) -> AppSettings:
        """Load settings from file or create with defaults"""
        try:
            self.settings_dir.mkdir(exist_ok=True)
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                return AppSettings(**data)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return AppSettings()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(asdict(self.settings), f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def reset_setting(self, setting_name: str):
        """Reset individual setting to default"""
        default = AppSettings()
        if hasattr(default, setting_name):
            setattr(self.settings, setting_name, getattr(default, setting_name))
            self.save_settings()
