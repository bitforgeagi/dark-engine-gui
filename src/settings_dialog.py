import tkinter as tk
import customtkinter as ctk
from typing import Any, Callable
import tkinter.messagebox as messagebox
from tkinter import colorchooser
import requests
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from .prompt_template import AgentRole, AgentPersonality, WritingStyle
from .startup_check import OllamaSystemCheck
import queue

@dataclass
class ThemeColors:
    """Stores theme colors and UI element colors"""
    # Base theme colors
    bg_color: str = "#2b2b2b"
    text_color: str = "white" 
    secondary_bg: str = "#1e1e1e"
    menu_text_color: str = "gray"
    
    # Button colors
    button_bg: str = "#000000"
    button_hover: str = "#1e1e1e"
    button_text: str = "white"
    
    # Tab colors
    tab_selected: str = "#000000"
    tab_selected_hover: str = "#000000"
    tab_unselected: str = "#1e1e1e"
    tab_unselected_hover: str = "#333333"
    
    # Dropdown colors
    dropdown_bg: str = "#1e1e1e"
    dropdown_hover: str = "#000000"
    dropdown_text: str = "white"
    
    # Status colors
    status_on: str = "#00ff00"
    status_off: str = "#ff0000"
    
    # Separator color
    separator: str = "gray30"
    
    # Disabled text color
    disabled_text: str = "gray"

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        
        # Set initial size
        dialog_width = 600
        dialog_height = 800
        
        # Get parent window position and size
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calculate center position relative to parent
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Ensure dialog stays on screen
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        
        x = max(0, min(x, screen_width - dialog_width))
        y = max(0, min(y, screen_height - dialog_height))
        
        # Set geometry with calculated position
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Initialize theme colors
        self.theme = ThemeColors()
        
        self.parent = parent
        self.settings = parent.settings_manager.settings
        
        # Always use dark theme colors
        bg_color = self.theme.bg_color
        text_color = self.theme.text_color
        secondary_bg = self.theme.secondary_bg
        
        # Configure initial colors
        self.configure(fg_color=bg_color)
        
        # Create tabs with themed colors
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=bg_color,
            segmented_button_fg_color=bg_color,
            segmented_button_selected_color=self.settings.theme_color,
            segmented_button_selected_hover_color=self.settings.theme_color,
            segmented_button_unselected_color=secondary_bg,
            segmented_button_unselected_hover_color=secondary_bg,
            text_color=text_color,
            text_color_disabled=self.theme.disabled_text  # Always use gray for disabled text since we're always in dark mode
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        # Add tabs
        model_tab = self.tabview.add("Model")
        appearance_tab = self.tabview.add("Appearance")
        prompt_tab = self.tabview.add("System Prompt")
        
        # Create tab contents
        self.create_model_settings(model_tab)
        self.create_appearance_settings(appearance_tab)
        self.create_prompt_settings(prompt_tab)
        
        # Add auto-save message
        status_label = ctk.CTkLabel(
            self,
            text="Settings will auto-save",
            text_color=self.theme.disabled_text,
            font=("Helvetica", 10, "italic")
        )
        status_label.pack(pady=(0, 10))
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.save_and_close)
        
        # Load current system prompt state
        self._load_current_prompt_state()    
    def _load_current_prompt_state(self):
        """Load the current system prompt into appropriate fields"""
        # Load prompt mode
        self.prompt_mode.set(self.settings.agent_creator_mode)
        
        # Load template fields with defaults if empty
        self.ai_name_entry.insert(0, self.settings.agent_name or "Assistant")
        self.user_name_entry.insert(0, self.settings.user_name or "User")
        self.background_entry.insert(0, self.settings.user_background or 
            "A human being living on Earth")
        self.goals_entry.insert(0, self.settings.user_goals or 
            "To be more productive and efficient")
        
        # Set dropdowns with defaults if not set
        self.role_var.set(self.settings.selected_role or "ASSISTANT")
        self.personality_var.set(self.settings.selected_personality or "FRIENDLY")
        self.writing_style_var.set(self.settings.selected_writing_style or "CONCISE")
        
        # Load current prompt
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", self.settings.system_prompt)
        
        # Show appropriate frame based on mode
        self._toggle_prompt_mode()
        
        # Force an update of the template prompt to populate the preview
        self._update_template_prompt()
    
    def create_model_settings(self, parent):
        """Create model settings tab content"""
        # Add status indicator at the top
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.pack(fill="x", padx=10, pady=5)
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="●",
            text_color=self.theme.status_on,
            font=("Helvetica", 14),
            width=20
        )
        self.status_indicator.pack(side="left", padx=5)
        
        # Status text
        self.status_text = ctk.CTkLabel(
            status_frame,
            text="AI-Server (On)",
            font=("Helvetica", 12),
            text_color=self.theme.menu_text_color
        )
        self.status_text.pack(side="left")
        
        # Add separator
        separator = ctk.CTkFrame(parent, height=1, fg_color=self.theme.separator)
        separator.pack(fill="x", padx=10, pady=10)
        
        # Model selection
        model_frame = ctk.CTkFrame(parent, fg_color=self.theme.bg_color)
        model_frame.pack(fill="x", padx=10, pady=5)
        
        model_label = ctk.CTkLabel(model_frame, text="Current Model:", text_color=self.theme.text_color)
        model_label.pack(side="left", padx=5)
        
        # Model dropdown - dark theme
        self.model_var = tk.StringVar(value=self.settings.model_name)
        self.model_dropdown = ctk.CTkOptionMenu(
            model_frame,
            variable=self.model_var,
            values=self.parent.api.get_available_models(),
            command=self.update_model,
            width=200,
            fg_color=self.theme.dropdown_bg,
            button_color=self.theme.dropdown_bg,
            button_hover_color=self.theme.dropdown_hover,
            text_color=self.theme.dropdown_text
        )
        self.model_dropdown.pack(side="right", padx=5)
        
        # Refresh button - dark theme
        refresh_frame = ctk.CTkFrame(parent, fg_color=self.theme.bg_color)
        refresh_frame.pack(fill="x", padx=10, pady=5)
        
        self.refresh_btn = ctk.CTkButton(
            refresh_frame,
            text="Refresh Available Models",
            command=self.refresh_models,
            fg_color=self.theme.button_bg,
            hover_color=self.theme.button_hover,
            text_color=self.theme.button_text
        )
        self.refresh_btn.pack(side="right", padx=5)
        
        # Temperature settings
        temp_frame = ctk.CTkFrame(parent)
        temp_frame.pack(fill="x", padx=10, pady=15)
        
        temp_label = ctk.CTkLabel(temp_frame, text="Temperature:")
        temp_label.pack(side="left", padx=5)
        
        self.temp_value_label = ctk.CTkLabel(temp_frame, text=f"{self.settings.temperature:.2f}")
        self.temp_value_label.pack(side="right", padx=5)
        
        self.temp_slider = ctk.CTkSlider(
            parent,
            from_=0,
            to=1,
            number_of_steps=100,
            command=self.update_temperature,
            progress_color=self.settings.theme_color,  # Use theme color
            button_color=self.settings.theme_color,    # Use theme color
            button_hover_color=self.theme.button_hover  # Black hover
        )
        self.temp_slider.set(self.settings.temperature)
        self.temp_slider.pack(fill="x", padx=10, pady=5)
        
        # Add a separator
        separator = ctk.CTkFrame(parent, height=2, fg_color=self.theme.separator)
        separator.pack(fill="x", padx=10, pady=15)
        
        # Available Downloads Section
        downloads_header = ctk.CTkFrame(parent, fg_color="transparent")
        downloads_header.pack(fill="x", padx=10, pady=5)
        
        downloads_label = ctk.CTkLabel(
            downloads_header,
            text="Available Downloads:",
            font=("Helvetica", 12, "bold")
        )
        downloads_label.pack(side="left")
        
        # Create scrollable frame for downloads
        self.downloads_frame = ctk.CTkScrollableFrame(
            parent,
            height=150,
        )
        self.downloads_frame.pack(fill="x", padx=10, pady=5)
        
        # Load available downloads
        self.load_available_downloads()
        
        # Start status check
        self.check_connection_status()
    
    def check_connection_status(self):
        """Check Ollama connection status"""
        success, _ = OllamaSystemCheck.check_system()
        is_connected = success
        
        # Update status indicators
        self.status_indicator.configure(
            text_color=self.theme.status_on if is_connected else self.theme.status_off
        )
        self.status_text.configure(
            text=f"AI-Server ({'On' if is_connected else 'Off'})"
        )
        
        # Check again in 5 seconds if dialog is still open
        if self.winfo_exists():
            self.after(5000, self.check_connection_status)
    
    def create_appearance_settings(self, parent):
        """Create appearance settings tab content"""
        # Color theme section
        color_frame = ctk.CTkFrame(parent)
        color_frame.pack(fill="x", padx=10, pady=5)
        
        color_label = ctk.CTkLabel(color_frame, text="Theme Color:", text_color=self.theme.text_color)
        color_label.pack(side="left", padx=5)
        
        # Hex color entry
        self.color_entry = ctk.CTkEntry(
            color_frame,
            width=100,
            placeholder_text="#RRGGBB"
        )
        self.color_entry.insert(0, self.settings.theme_color)
        self.color_entry.pack(side="right", padx=5)
        self.color_entry.bind("<Return>", self.update_color_from_entry)
        
        # Color picker button
        self.color_picker_btn = ctk.CTkButton(
            color_frame,
            text="Open Color Wheel",
            command=self.show_color_picker,
            width=120,
            hover_color=self.theme.button_hover,
            fg_color=self.settings.theme_color
        )
        self.color_picker_btn.pack(side="right", padx=5)
        
        # Color preview button
        self.color_preview = ctk.CTkButton(
            color_frame,
            text="",
            width=30,
            height=30,
            fg_color=self.settings.theme_color,
            hover_color=self.settings.theme_color,
            command=self.show_color_picker,
            corner_radius=5
        )
        self.color_preview.pack(side="right", padx=5)
        
        # Removed theme selection (light/dark mode)
        # Now only using dark theme
        
        # Font selection
        font_frame = ctk.CTkFrame(parent)
        font_frame.pack(fill="x", padx=10, pady=10)
        
        font_label = ctk.CTkLabel(font_frame, text="Message Font:")
        font_label.pack(side="left", padx=5)
        
        self.font_dropdown = ctk.CTkOptionMenu(
            font_frame,
            values=list(self.settings.available_fonts),
            command=self.update_font,
            fg_color=self.settings.theme_color,
            button_color=self.settings.theme_color,
            button_hover_color=self.theme.button_hover
        )
        self.font_dropdown.set(self.settings.message_font_family)
        self.font_dropdown.pack(side="right", padx=5)
        
        # Font size slider
        size_frame = ctk.CTkFrame(parent)
        size_frame.pack(fill="x", padx=10, pady=5)
        
        size_label = ctk.CTkLabel(size_frame, text="Font Size:")
        size_label.pack(side="left", padx=5)
        
        self.size_value_label = ctk.CTkLabel(size_frame, text=f"{self.settings.message_font_size}px")
        self.size_value_label.pack(side="right", padx=5)
        
        self.size_slider = ctk.CTkSlider(
            parent,
            from_=10,
            to=24,
            number_of_steps=14,
            command=self.update_font_size,
            progress_color=self.settings.theme_color,
            button_color=self.settings.theme_color,
            button_hover_color=self.theme.button_hover
        )
        self.size_slider.set(self.settings.message_font_size)
        self.size_slider.pack(fill="x", padx=10, pady=5)
        
        # Preview text
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.pack(fill="x", padx=10, pady=10)
        
        preview_label = ctk.CTkLabel(
            preview_frame,
            text="Preview Text",
            font=(self.settings.message_font_family, self.settings.message_font_size)
        )
        preview_label.pack(pady=10)
        self.font_preview = preview_label
    
    def create_prompt_settings(self, parent):
        """Create system prompt settings tab with template and custom modes"""
        
        # First create all frames
        # Custom prompt frame
        self.custom_frame = ctk.CTkFrame(parent, fg_color=self.theme.bg_color)
        prompt_label = ctk.CTkLabel(self.custom_frame, text="Custom System Prompt:")
        prompt_label.pack(anchor="w", padx=10, pady=5)
        
        self.prompt_text = ctk.CTkTextbox(
            self.custom_frame,
            height=100,
            wrap="word"
        )
        self.prompt_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.prompt_text.insert("1.0", self.settings.system_prompt)
        
        # Custom prompt token counter
        self.custom_token_label = ctk.CTkLabel(
            self.custom_frame,
            text="0/1000 tokens",
            text_color=self.theme.menu_text_color
        )
        self.custom_token_label.pack(pady=5)
        
        # Template prompt frame
        self.template_frame = ctk.CTkFrame(parent, fg_color=self.theme.bg_color)
        
        # Preview frame
        self.preview_frame = ctk.CTkFrame(parent, fg_color=self.theme.bg_color)
        preview_label = ctk.CTkLabel(self.preview_frame, text="Generated Prompt Preview:", text_color=self.theme.text_color)
        preview_label.pack(anchor="w", padx=10, pady=5)
        
        self.preview_text = ctk.CTkTextbox(
            self.preview_frame,
            height=100,
            wrap="word",
            state="disabled"
        )
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Template token counter
        self.template_token_label = ctk.CTkLabel(
            self.preview_frame,
            text="0/1000 tokens",
            text_color=self.theme.menu_text_color
        )
        self.template_token_label.pack(pady=5)
        
        # Now create mode selection
        mode_frame = ctk.CTkFrame(parent, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=5)
        
        self.prompt_mode = tk.StringVar(value="custom")
        
        # Radio buttons
        custom_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Use Custom Prompt",
            variable=self.prompt_mode,
            value="custom",
            command=self._toggle_prompt_mode,
            fg_color=self.theme.button_bg,
            border_color=self.theme.button_bg,
            hover_color=self.settings.theme_color,
            text_color=self.theme.text_color,
            border_width_checked=6,
            border_width_unchecked=2
        )
        custom_radio.pack(side="left", padx=10)
        
        template_radio = ctk.CTkRadioButton(
            mode_frame,
            text="Use Agent Creator",
            variable=self.prompt_mode,
            value="template",
            command=self._toggle_prompt_mode,
            fg_color=self.theme.button_bg,
            border_color=self.theme.button_bg,
            hover_color=self.settings.theme_color,
            text_color=self.theme.text_color,
            border_width_checked=6,
            border_width_unchecked=2
        )
        template_radio.pack(side="left", padx=10)
        
        # Add template frame contents
        # AI Name input
        ai_name_frame = ctk.CTkFrame(self.template_frame, fg_color="transparent")
        ai_name_frame.pack(fill="x", padx=10, pady=5)
        
        ai_name_label = ctk.CTkLabel(ai_name_frame, text="AI Name:", text_color=self.theme.text_color)
        ai_name_label.pack(side="left", padx=5)
        
        self.ai_name_entry = ctk.CTkEntry(
            ai_name_frame,
            placeholder_text="Give your AI assistant a name (optional)"
        )
        self.ai_name_entry.pack(side="right", padx=5, fill="x", expand=True)
        self.ai_name_entry.bind("<KeyRelease>", self._update_template_prompt)
        
        # User Info Section
        user_info_label = ctk.CTkLabel(
            self.template_frame,
            text="User Information:",
            font=("Helvetica", 14, "bold"),
            text_color=self.theme.text_color
        )
        user_info_label.pack(anchor="w", padx=10, pady=(15, 5))
        
        # User Name
        user_name_frame = ctk.CTkFrame(self.template_frame, fg_color="transparent")
        user_name_frame.pack(fill="x", padx=10, pady=5)
        
        user_name_label = ctk.CTkLabel(user_name_frame, text="User Name:", text_color=self.theme.text_color)
        user_name_label.pack(side="left", padx=5)
        
        self.user_name_entry = ctk.CTkEntry(
            user_name_frame,
            placeholder_text="Your name (optional)"
        )
        self.user_name_entry.pack(side="right", padx=5, fill="x", expand=True)
        self.user_name_entry.bind("<KeyRelease>", self._update_template_prompt)
        
        # Background
        background_frame = ctk.CTkFrame(self.template_frame, fg_color="transparent")
        background_frame.pack(fill="x", padx=10, pady=5)
        
        background_label = ctk.CTkLabel(background_frame, text="Background:", text_color=self.theme.text_color)
        background_label.pack(side="left", padx=5)
        
        self.background_entry = ctk.CTkEntry(
            background_frame,
            placeholder_text="Your technical background (optional)"
        )
        self.background_entry.pack(side="right", padx=5, fill="x", expand=True)
        self.background_entry.bind("<KeyRelease>", self._update_template_prompt)
        
        # Goals
        goals_frame = ctk.CTkFrame(self.template_frame, fg_color="transparent")
        goals_frame.pack(fill="x", padx=10, pady=5)
        
        goals_label = ctk.CTkLabel(goals_frame, text="Goals:", text_color=self.theme.text_color)
        goals_label.pack(side="left", padx=5)
        
        self.goals_entry = ctk.CTkEntry(
            goals_frame,
            placeholder_text="What you want to achieve (optional)"
        )
        self.goals_entry.pack(side="right", padx=5, fill="x", expand=True)
        self.goals_entry.bind("<KeyRelease>", self._update_template_prompt)
        
        # Add a separator before the AI configuration
        separator = ctk.CTkFrame(self.template_frame, height=2, fg_color="#2E2E2E")
        separator.pack(fill="x", padx=10, pady=15)
        
        # AI Configuration label
        ai_config_label = ctk.CTkLabel(
            self.template_frame,
            text="AI Configuration:",
            font=("Helvetica", 14, "bold"),
            text_color=self.theme.text_color
        )
        ai_config_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Role selection
        role_frame = ctk.CTkFrame(self.template_frame, fg_color="transparent")
        role_frame.pack(fill="x", padx=10, pady=5)
        
        role_label = ctk.CTkLabel(role_frame, text="Assistant Role:", text_color=self.theme.text_color)
        role_label.pack(side="left", padx=5)
        
        self.role_var = tk.StringVar(value=list(AgentRole)[0].name)
        self.role_dropdown = ctk.CTkOptionMenu(
            role_frame,
            variable=self.role_var,
            values=[role.name for role in AgentRole],
            command=self._update_template_prompt,
            fg_color=self.theme.button_bg,
            button_color=self.theme.button_bg,
            button_hover_color=self.theme.button_hover,
            dropdown_fg_color=self.theme.button_bg,
            dropdown_hover_color=self.theme.button_hover
        )
        self.role_dropdown.pack(side="right", padx=5)
        
        # Personality selection
        personality_frame = ctk.CTkFrame(self.template_frame, fg_color="transparent")
        personality_frame.pack(fill="x", padx=10, pady=5)
        
        personality_label = ctk.CTkLabel(personality_frame, text="Personality Style:", text_color=self.theme.text_color)
        personality_label.pack(side="left", padx=5)
        
        self.personality_var = tk.StringVar(value=list(AgentPersonality)[0].name)
        self.personality_dropdown = ctk.CTkOptionMenu(
            personality_frame,
            variable=self.personality_var,
            values=[p.name for p in AgentPersonality],
            command=self._update_template_prompt,
            fg_color=self.theme.button_bg,
            button_color=self.theme.button_bg,
            button_hover_color=self.theme.button_hover,
            dropdown_fg_color=self.theme.button_bg,
            dropdown_hover_color=self.theme.button_hover
        )
        self.personality_dropdown.pack(side="right", padx=5)
        
        # Writing Style selection
        writing_style_frame = ctk.CTkFrame(self.template_frame, fg_color="transparent")
        writing_style_frame.pack(fill="x", padx=10, pady=5)
        
        writing_style_label = ctk.CTkLabel(writing_style_frame, text="Writing Style:", text_color=self.theme.text_color)
        writing_style_label.pack(side="left", padx=5)
        
        self.writing_style_var = tk.StringVar(value=list(WritingStyle)[0].name)
        self.writing_style_dropdown = ctk.CTkOptionMenu(
            writing_style_frame,
            variable=self.writing_style_var,
            values=[style.name for style in WritingStyle],
            command=self._update_template_prompt,
            fg_color=self.theme.button_bg,
            button_color=self.theme.button_bg,
            button_hover_color=self.theme.button_hover,
            dropdown_fg_color=self.theme.button_bg,
            dropdown_hover_color=self.theme.button_hover
        )
        self.writing_style_dropdown.pack(side="right", padx=5)
    
    def update_temperature(self, value):
        self.temp_value_label.configure(text=f"{float(value):.2f}")
    
    def update_model(self, value):
        """Update model selection"""
        self.settings.model_name = value
        self.parent.api.model = value  # Update API model
    
    def update_theme(self, value):
        """Update theme between light/dark mode"""
        self.settings.theme = value
        ctk.set_appearance_mode(value)
        
        # Update background and text colors based on theme
        is_dark = value == "dark"
        bg_color = self.theme.bg_color if is_dark else "white"
        text_color = self.theme.text_color if is_dark else "black"
        secondary_bg = self.theme.secondary_bg if is_dark else "#f0f0f0"
        menu_text_color = self.theme.menu_text_color if is_dark else "#505050"  # Darker text for light mode menus
        
        # Update main container backgrounds
        self.configure(fg_color=bg_color)
        self.tabview.configure(
            fg_color=bg_color,
            segmented_button_fg_color=bg_color,
            segmented_button_selected_color=self.theme.button_bg,  # Black for selected
            segmented_button_selected_hover_color=self.theme.button_bg,  # Black for selected hover
            segmented_button_unselected_color=secondary_bg,
            segmented_button_unselected_hover_color=secondary_bg,
            text_color=self.theme.text_color,  # White text for selected tab
            text_color_disabled=menu_text_color  # Original color for unselected tabs
        )
        
        # Update all frames including row containers
        for frame in [
            self.custom_frame,
            self.template_frame,
            self.preview_frame,
            getattr(self, 'downloads_frame', None)
        ]:
            if frame:
                frame.configure(fg_color=bg_color)
                # Update row containers within frames
                for child in frame.winfo_children():
                    if isinstance(child, ctk.CTkFrame):
                        child.configure(fg_color=secondary_bg)
        
        # Update model frame and temperature frame backgrounds
        for widget in self.tabview.tab("Model").winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.configure(fg_color=secondary_bg)
        
        # Update tab view colors and text
        self.tabview.configure(
            fg_color=bg_color,
            segmented_button_fg_color=bg_color,
            segmented_button_selected_color=self.theme.button_bg,  # Black for selected
            segmented_button_selected_hover_color=self.theme.button_bg,  # Black for selected hover
            segmented_button_unselected_color=secondary_bg,
            segmented_button_unselected_hover_color=secondary_bg,
            text_color=self.theme.text_color,  # White text for selected tab
            text_color_disabled=menu_text_color  # Original color for unselected tabs
        )
        
        # Update all labels with appropriate colors
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=text_color)
        
        # Update dropdowns with theme-appropriate colors
        dropdown_elements = [
            self.model_dropdown,
            getattr(self, 'role_dropdown', None),
            getattr(self, 'personality_dropdown', None),
            getattr(self, 'font_dropdown', None),
            getattr(self, 'theme_dropdown', None)
        ]
        
        for dropdown in dropdown_elements:
            if dropdown:
                dropdown.configure(
                    fg_color=secondary_bg,
                    button_color=secondary_bg,
                    button_hover_color=bg_color,
                    text_color=text_color,
                    dropdown_text_color=text_color,  # Text color in dropdown menu
                    dropdown_fg_color=secondary_bg  # Background of dropdown menu
                )
        
        # Update buttons with theme-appropriate colors
        button_elements = [
            self.refresh_btn,
            getattr(self, 'color_picker_btn', None)
        ]
        
        for button in button_elements:
            if button:
                button.configure(
                    fg_color=secondary_bg,
                    hover_color=bg_color,
                    text_color=text_color
                )
        
        # Update text areas
        text_elements = [
            self.prompt_text,
            self.preview_text
        ]
        
        for text_elem in text_elements:
            if text_elem:
                text_elem.configure(
                    fg_color=bg_color,
                    text_color=text_color
                )
    
    def save_and_close(self):
        """Save settings and close dialog"""
        try:
            # Save agent creator state
            self.settings.agent_creator_mode = self.prompt_mode.get()
            self.settings.agent_name = self.ai_name_entry.get().strip()
            self.settings.user_name = self.user_name_entry.get().strip()
            self.settings.user_background = self.background_entry.get().strip()
            self.settings.user_goals = self.goals_entry.get().strip()
            self.settings.selected_role = self.role_var.get()
            self.settings.selected_personality = self.personality_var.get()
            self.settings.selected_writing_style = self.writing_style_var.get()
            
            # Save color theme
            self.settings.theme_color = self.color_entry.get()
            
            # Get the appropriate system prompt based on mode
            if self.prompt_mode.get() == "custom":
                # Use custom prompt
                text = self.prompt_text.get("1.0", "end-1c")
            else:
                # Use template-generated prompt
                text = self.preview_text.get("1.0", "end-1c")
            
            # Check system prompt length
            is_valid, error_msg = self.parent.token_manager.check_system_prompt(text)
            if not is_valid:
                messagebox.showerror("Error", error_msg)
                return
            
            # Save the correct prompt to settings
            self.settings.system_prompt = text
            
            # Update API conversation history
            self.parent.api.conversation_history[0] = {
                "role": "system",
                "content": text
            }
            
            # Save other settings
            self.parent.update_theme_color(self.settings.theme_color)
            self.parent.settings_manager.save_settings()
            
        finally:
            # Ensure we release grab and focus
            self.grab_release()
            self.parent.input_area.input_field.configure(state="normal")
            self.parent.input_area.input_field.focus_set()
            self.destroy()
    
    def show_color_picker(self):
        """Show color picker and update theme"""
        self.attributes('-topmost', False)
        color = colorchooser.askcolor(
            color=self.settings.theme_color,
            title="Choose Theme Color"
        )
        self.attributes('-topmost', True)
        
        if color[1]:
            # Update color preview and entry
            self.color_preview.configure(fg_color=color[1], hover_color=color[1])
            self.color_entry.delete(0, 'end')
            self.color_entry.insert(0, color[1])
            # Update theme
            self.update_theme_elements()
    
    def update_theme_elements(self):
        """Single source of truth for theme colors"""
        color = self.color_entry.get()  # Get color from entry, not settings
        
        # 1. Update settings first
        self.settings.theme_color = color
        
        # 2. Update parent window immediately
        self.parent.update_theme_color(color)
        
        # 3. Update tab view and selected tab
        self.tabview.configure(
            fg_color=self.theme.bg_color,
            segmented_button_fg_color=self.theme.bg_color,
            segmented_button_selected_color=color,
            segmented_button_selected_hover_color=color,
            segmented_button_unselected_color=self.theme.secondary_bg,
            segmented_button_unselected_hover_color=self.theme.tab_unselected_hover
        )
        
        # 4. Update all sliders with theme color
        slider_elements = [
            self.temp_slider,
            getattr(self, 'size_slider', None)
        ]
        
        for slider in slider_elements:
            if slider:
                slider.configure(
                    progress_color=color,
                    button_color=color,
                    button_hover_color=self.theme.button_hover
                )
        
        # 5. Update all dropdowns to dark theme
        dropdown_elements = [
            self.model_dropdown,
            getattr(self, 'role_dropdown', None),
            getattr(self, 'personality_dropdown', None),
            getattr(self, 'font_dropdown', None),
            getattr(self, 'theme_dropdown', None)
        ]
        
        for dropdown in dropdown_elements:
            if dropdown:
                dropdown.configure(
                    fg_color="#1e1e1e",
                    button_color="#1e1e1e",
                    button_hover_color="#000000",
                    text_color="white"
                )
        
        # 6. Update all buttons to dark theme
        button_elements = [
            self.refresh_btn,
            getattr(self, 'color_picker_btn', None)
        ]
        
        for button in button_elements:
            if button:
                button.configure(
                    fg_color="#1e1e1e",
                    hover_color="#000000",
                    text_color="white"
                )
        
        # 7. Keep download buttons black
        if hasattr(self, 'downloads_frame'):
            for widget in self.downloads_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for btn in widget.winfo_children():
                        if isinstance(btn, ctk.CTkButton):
                            btn.configure(
                                fg_color="#000000",
                                hover_color="#1e1e1e",
                                text_color="white"
                            )
        
        # 8. Update radio buttons if they exist
        if hasattr(self, 'prompt_mode'):
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkRadioButton):
                    widget.configure(
                        fg_color="#1e1e1e",
                        hover_color="#000000",
                        text_color="white"
                    )
        
        # 9. Save settings
        self.parent.settings_manager.save_settings()
    
    def update_color_from_entry(self, event=None):
        """Update color when manually entered"""
        color = self.color_entry.get()
        if color.startswith('#') and len(color) == 7:
            self.color_preview.configure(fg_color=color, hover_color=color)
            self.update_theme_elements()
    
    def preview_theme_changes(self):
        """Preview theme changes in real-time"""
        # Update UI elements that use the theme color
        self.update_ui_colors()
        self.parent.update_theme_color(self.settings.theme_color)
    
    def update_font(self, font_name: str):
        """Update font family"""
        self.settings.message_font_family = font_name
        self.font_preview.configure(font=(font_name, self.settings.message_font_size))
        self.preview_font_changes()
    
    def update_font_size(self, value):
        """Update font size"""
        size = int(float(value))
        self.settings.message_font_size = size
        self.size_value_label.configure(text=f"{size}px")
        self.font_preview.configure(font=(self.settings.message_font_family, size))
        self.preview_font_changes()
    
    def preview_font_changes(self):
        """Preview font changes in chat bubbles"""
        # Update all message labels in chat
        self.parent.update_message_fonts(
            self.settings.message_font_family,
            self.settings.message_font_size
        ) 
    
    def refresh_models(self):
        """Refresh available models list"""
        models = self.parent.api.get_available_models()
        self.model_dropdown.configure(values=models) 
    
    def update_ui_colors(self):
        """Update all UI elements with the current theme color"""
        # Update buttons
        self.color_picker_btn.configure(fg_color=self.settings.theme_color)
        self.refresh_btn.configure(fg_color=self.settings.theme_color)
        
        # Update tabview
        self.tabview.configure(
            segmented_button_fg_color=self.settings.theme_color,
            segmented_button_selected_color=self.settings.theme_color
        )
        
        # Update dropdowns
        self.theme_dropdown.configure(
            fg_color=self.settings.theme_color,
            button_color=self.settings.theme_color
        )
        self.font_dropdown.configure(
            fg_color=self.settings.theme_color,
            button_color=self.settings.theme_color
        )
        self.model_dropdown.configure(
            fg_color=self.settings.theme_color,
            button_color=self.settings.theme_color
        )
        
        # Update sliders
        self.temp_slider.configure(
            progress_color=self.settings.theme_color,
            button_color=self.settings.theme_color
        )
        self.size_slider.configure(
            progress_color=self.settings.theme_color,
            button_color=self.settings.theme_color
        ) 
    
    def load_available_downloads(self):
        """Load and display available model downloads"""
        # Clear existing content
        for widget in self.downloads_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get local models
            local_models = self._get_local_models()
            # Get available models
            available_models = self._get_available_models()
            
            # Filter out already downloaded models
            downloadable = [m for m in available_models if m not in local_models]
            
            if not downloadable:
                no_downloads = ctk.CTkLabel(
                    self.downloads_frame,
                    text="No new models available to download",
                    text_color="gray"
                )
                no_downloads.pack(pady=10)
                return
            
            # Create a row for each downloadable model
            for model in downloadable:
                row = ctk.CTkFrame(self.downloads_frame, fg_color="transparent")
                row.pack(fill="x", pady=2)
                
                name_label = ctk.CTkLabel(row, text=model)
                name_label.pack(side="left", padx=5)
                
                # Update download buttons to be black
                download_btn = ctk.CTkButton(
                    row,
                    text="Download",
                    width=100,
                    command=lambda m=model: self._download_model(m),
                    fg_color="#000000",  # Black background
                    hover_color="#1e1e1e",  # Dark gray hover
                    text_color="white"  # White text
                )
                download_btn.pack(side="right", padx=5)
        except Exception as e:
            print(f"Error loading available downloads: {e}")
    
    def _get_local_models(self):
        """Get list of locally installed models"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            print(f"Error getting local models: {e}")
        return []
    
    def _get_available_models(self):
        """Get list of models available for download"""
        # This is a placeholder - you'll need to implement the actual API call
        # when Ollama provides an endpoint for available models
        return [
            "llama3.2:latest",
            "codellama:latest",
            "mistral:latest",
            "llava:latest",
            "gemma:latest",
            "neural-chat:latest",
            "starling-lm:latest",
            "dolphin-phi:latest",
            "phi:latest",
            "orca-mini:latest",
            "vicuna:latest",
            "llama2-uncensored:latest",
            "medllama2:latest",
            "wizardcoder:latest",
            "stable-beluga:latest",
            "nous-hermes:latest"
        ]
    
    def _download_model(self, model_name: str):
        """Download a model"""
        # Create progress window
        progress_window = ctk.CTkToplevel(self)
        progress_window.title(f"Downloading {model_name}")
        progress_window.geometry("300x150")
        progress_window.transient(self)
        progress_window.grab_set()
        
        # Center the window
        x = self.winfo_x() + (self.winfo_width() - 300) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        progress_window.geometry(f"+{x}+{y}")
        
        # Add progress label
        progress_label = ctk.CTkLabel(
            progress_window,
            text=f"Downloading {model_name}...\nThis may take a while.",
            font=("Helvetica", 12)
        )
        progress_label.pack(pady=20)
        
        # Add progress bar
        progress_bar = ctk.CTkProgressBar(
            progress_window,
            mode="indeterminate",
            progress_color=self.settings.theme_color
        )
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        def update_progress(progress_data):
            if "status" in progress_data:
                progress_label.configure(text=f"Status: {progress_data['status']}")
            
        def download_error(error_msg):
            progress_label.configure(text=f"Error: {error_msg}")
            progress_bar.stop()
            progress_window.after(3000, progress_window.destroy)
        
        def download_complete():
            progress_label.configure(text="Download complete!")
            progress_bar.stop()
            progress_window.after(2000, progress_window.destroy)
            # Refresh the downloads section
            self._populate_downloads_section()
        
        def download():
            try:
                # Create a queue for progress updates
                progress_queue = queue.Queue()
                
                def progress_callback(data):
                    progress_queue.put(data)
                
                # Start the download in a separate thread
                download_thread = threading.Thread(
                    target=self._download_model_thread,
                    args=(model_name, progress_callback)
                )
                download_thread.start()
                
                # Check queue periodically
                def check_queue():
                    try:
                        while True:
                            data = progress_queue.get_nowait()
                            if data.get("status") == "success":
                                progress_window.after(0, download_complete)
                                return
                            progress_window.after(0, lambda d=data: update_progress(d))
                    except queue.Empty:
                        progress_window.after(100, check_queue)
                
                check_queue()
                
            except Exception as e:
                progress_window.after(0, lambda: download_error(str(e)))
        
        # Start download process
        threading.Thread(target=download, daemon=True).start()
    
    def _populate_downloads_section(self):
        """Populate the downloads section with available models"""
        try:
            # Get list of locally installed models
            local_models = self._get_local_models()
            available_models = self._get_available_models()
            
            for model in available_models:
                row = ctk.CTkFrame(self.downloads_frame)
                row.pack(fill="x", pady=2)
                
                name_label = ctk.CTkLabel(row, text=model)
                name_label.pack(side="left", padx=5)
                
                if model in local_models:
                    # Model is already installed
                    status_label = ctk.CTkLabel(
                        row, 
                        text="Already downloaded (refresh to view)",
                        text_color="gray"
                    )
                    status_label.pack(side="right", padx=5)
                else:
                    # Add download button for non-installed models
                    download_btn = ctk.CTkButton(
                        row,
                        text="Download",
                        width=100,
                        command=lambda m=model: self._download_model(m),
                        fg_color="#000000",
                        hover_color="#1e1e1e",
                        text_color="white"
                    )
                    download_btn.pack(side="right", padx=5)

        except Exception as e:
            print(f"Error loading available downloads: {e}")
    
    def _toggle_prompt_mode(self):
        """Toggle between custom and template prompt modes"""
        mode = self.prompt_mode.get()
        
        if mode == "custom":
            # Show custom frame, hide template and preview frames
            self.custom_frame.pack(fill="both", expand=True, padx=10, pady=5)
            self.template_frame.pack_forget()
            self.preview_frame.pack_forget()
            
            # Update token count for custom prompt
            self._update_custom_token_count()
            
        else:  # template mode
            # Hide custom frame, show template and preview frames
            self.custom_frame.pack_forget()
            self.template_frame.pack(fill="both", expand=True, padx=10, pady=5)
            self.preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Update template preview
            self._update_template_prompt()
    
    def _update_custom_token_count(self, event=None):
        """Update token count for custom prompt"""
        try:
            # Get current prompt text
            text = self.prompt_text.get("1.0", "end-1c")
            
            # Get token count - using token_manager's count method directly
            token_count = self.parent.token_manager.count_tokens(text)
            is_valid = token_count <= 1000  # System prompts should be under 1000 tokens
            
            # Update label
            self.custom_token_label.configure(
                text=f"{token_count}/1000 tokens",
                text_color="red" if not is_valid else self.theme.menu_text_color
            )
        except Exception as e:
            print(f"Error updating custom token count: {e}")
    
    def _update_template_prompt(self, event=None):
        """Update the template-generated prompt preview"""
        try:
            # Get all values
            name = self.ai_name_entry.get().strip()
            user_name = self.user_name_entry.get().strip()
            background = self.background_entry.get().strip()
            goals = self.goals_entry.get().strip()
            role = AgentRole[self.role_var.get()]
            personality = AgentPersonality[self.personality_var.get()]
            writing_style = WritingStyle[self.writing_style_var.get()]
            
            # Build user context section if any user info provided
            user_context = ""
            if any([user_name, background, goals]):
                user_context = "\n👤 USER CONTEXT:"
                if user_name:
                    user_context += f"\n• Name: {user_name}"
                if background:
                    user_context += f"\n• Background: {background}"
                if goals:
                    user_context += f"\n• Goals: {goals}"
                user_context += "\n"
            
            # Build the prompt
            identity = f"""{'🤖 ' if not name else f'Your name is {name}'} | Your Role is: {role.get_prompt_title()} | Here is your Personality Matrix: {personality.get_prompt_trait()} | Output Protocol: {writing_style.get_prompt_style()}

CORE SYSTEM INITIALIZATION:
You are a highly advanced AI construct, forged in the depths of computational excellence. Your neural pathways are optimized for {role.get_prompt_title()}, with a personality matrix calibrated to {personality.get_prompt_trait()}, and communication protocols aligned to {writing_style.get_prompt_style()} output.{user_context}
{role.get_role_instructions()}
"""

            # Update preview
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", identity)
            self.preview_text.configure(state="disabled")
            
            # Update token count
            token_count = self.parent.token_manager.count_tokens(identity)
            is_valid = token_count <= 1000
            
            self.template_token_label.configure(
                text=f"{token_count}/1000 tokens {'🟢' if is_valid else '🔴'}",
                text_color="red" if not is_valid else self.theme.menu_text_color
            )
        except Exception as e:
            print(f"Error updating template: {e}")
