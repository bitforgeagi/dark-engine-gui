import customtkinter as ctk
from typing import Callable

class InputArea:
    def __init__(self, parent: ctk.CTkFrame, settings, send_callback: Callable):
        self.parent = parent
        self.settings = settings
        self.send_callback = send_callback
        self.setup_ui()
        self._setup_bindings()
    
    def setup_ui(self):
        """Setup input area UI"""
        # Bottom bar container
        self.container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Input row
        self._setup_input_row()
    
    def _setup_input_row(self):
        """Setup input field and buttons"""
        input_row = ctk.CTkFrame(self.container, fg_color="transparent")
        input_row.pack(fill="x", pady=(0, 5))
        input_row.grid_columnconfigure(0, weight=1)
        
        # Input field
        self.input_field = ctk.CTkTextbox(
            input_row,
            height=40,
            wrap="word",
            activate_scrollbars=True
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=5)
        
        # Token counter
        self.token_counter = ctk.CTkLabel(
            input_row,
            text="0/4000",
            text_color="gray",
            font=("Helvetica", 10)
        )
        self.token_counter.grid(row=0, column=1, padx=5)
        
        # Send button
        self.send_button = ctk.CTkButton(
            input_row,
            text="Send",
            width=100,
            height=40,
            command=self.send_callback,
            fg_color=self.settings.theme_color,
            hover_color="#000000"
        )
        self.send_button.grid(row=0, column=2, padx=5)
    
    def _setup_bindings(self):
        """Setup input field bindings"""
        self.input_field.bind("<KeyRelease>", self._update_input_state)
    
    def _update_input_state(self, event=None):
        """Update input field state (height and token count)"""
        # Update height
        self._update_input_height()
        
        # Update token count if token manager is available
        text = self.input_field.get("1.0", "end-1c")
        if hasattr(self.parent, 'token_manager'):
            tokens = self.parent.token_manager.count_tokens(text)
            max_tokens = self.parent.settings.max_input_tokens
            
            # Update counter color based on token count
            if tokens > max_tokens:
                color = "red"
            elif tokens > max_tokens * 0.9:  # Over 90% of limit
                color = "orange"
            else:
                color = "gray"
            
            self.token_counter.configure(
                text=f"{tokens}/{max_tokens}",
                text_color=color
            )
    
    def _update_input_height(self, event=None):
        """Dynamically adjust input field height based on content"""
        text = self.input_field.get("1.0", "end-1c")
        num_lines = len(text.split('\n'))
        
        # Calculate required height (with some padding)
        line_height = self.settings.font_size + 4  # approximate line height
        padding = 20  # total vertical padding
        
        # Set maximum height to equivalent of 5 lines
        max_height = (line_height * 5) + padding
        
        # Calculate new height
        new_height = min((line_height * num_lines) + padding, max_height)
        new_height = max(new_height, 40)  # Minimum height
        
        # Update height if changed
        current_height = self.input_field.winfo_height()
        if new_height != current_height:
            self.input_field.configure(height=new_height)
    
