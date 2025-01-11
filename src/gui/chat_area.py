import customtkinter as ctk
from typing import Dict
from datetime import datetime
import sys

class ChatArea:
    def __init__(self, parent: ctk.CTkFrame, settings):
        self.parent = parent
        self.settings = settings
        self.setup_ui()
    
    def setup_ui(self):
        """Setup chat area UI"""
        # Chat area container
        self.container = ctk.CTkFrame(self.parent)
        self.container.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        # Add header
        self._setup_header()
        
        # Chat frame (scrollable)
        self.chat_frame = self._create_chat_area()
        self.chat_frame.pack(fill="both", expand=True)
        
        # Add bottom fade effect
        self._setup_fade_effect()
    
    def _setup_header(self):
        """Setup chat header/banner"""
        self.header = ctk.CTkFrame(
            self.container,
            height=30,
            fg_color="#1a1a1a"
        )
        self.header.pack(fill="x", pady=(0, 5))
        
        # Add header text
        self.header_label = ctk.CTkLabel(
            self.header,
            text="Chat History",
            font=("Helvetica", 12),
            text_color="gray"
        )
        self.header_label.pack(side="left", padx=10)
    
    def _create_chat_area(self) -> ctk.CTkScrollableFrame:
        """Creates a scrollable chat area"""
        chat_frame = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            border_width=0,
            scrollbar_button_hover_color="#505050"  # Brighter hover color
        )
        
        # Get the parent canvas that CTkScrollableFrame creates
        parent_canvas = chat_frame._parent_canvas
        scrollbar = chat_frame._scrollbar
        
        # Configure scrollbar with proper colors and hover states
        scrollbar.configure(
            width=16,
            fg_color="#2b2b2b",         # Scrollbar track color
            button_color="#404040",      # Scrollbar thumb color
            button_hover_color="#4a4a4a" # Scrollbar thumb hover color
        )
        
        # Show scrollbar on hover
        def show_scrollbar(event):
            scrollbar.grid()  # Show the scrollbar
        
        def hide_scrollbar(event):
            if not scrollbar.winfo_ismapped():
                return
            # Get mouse position relative to the chat frame
            mouse_x = chat_frame.winfo_pointerx() - chat_frame.winfo_rootx()
            mouse_y = chat_frame.winfo_pointery() - chat_frame.winfo_rooty()
            
            # Check if mouse is outside the chat frame
            if not (0 <= mouse_x <= chat_frame.winfo_width() and 
                    0 <= mouse_y <= chat_frame.winfo_height()):
                scrollbar.grid_remove()  # Hide the scrollbar
        
        # Bind mouse enter/leave events
        chat_frame.bind('<Enter>', show_scrollbar)
        chat_frame.bind('<Leave>', hide_scrollbar)
        scrollbar.bind('<Enter>', show_scrollbar)
        scrollbar.bind('<Leave>', hide_scrollbar)
        
        # Initially hide scrollbar
        scrollbar.grid_remove()
        
        # Bind scroll events directly to the canvas based on platform
        if sys.platform.startswith("win") or sys.platform == "darwin":
            parent_canvas.bind("<MouseWheel>", self._on_mousewheel)
        else:  # Linux
            parent_canvas.bind("<Button-4>", self._on_mousewheel)
            parent_canvas.bind("<Button-5>", self._on_mousewheel)
        
        return chat_frame
    
    def _setup_fade_effect(self):
        """Setup bottom fade effect and progress bar"""
        self.bottom_fade = ctk.CTkFrame(
            self.container,
            height=8,
            fg_color="transparent",
            corner_radius=0
        )
        self.bottom_fade.place(relx=0, rely=1, relwidth=1, anchor="sw")
        
        # Create gradient effect using multiple thin frames
        base_color = self.container.cget("fg_color")[1]
        gradient_colors = self._create_gradient_colors(base_color, 5)
        
        for i, color in enumerate(gradient_colors):
            gradient_layer = ctk.CTkFrame(
                self.bottom_fade,
                height=4,
                fg_color=color,
                corner_radius=0
            )
            gradient_layer.place(relx=0, rely=i/5, relwidth=1)
        
        # Add progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.bottom_fade,
            mode="indeterminate",
            height=2,
            progress_color=self.settings.theme_color,
            fg_color="#1a1a1a"
        )
        self.progress_bar.place(relx=0.5, rely=0.5, relwidth=0.99, anchor="center")
        
        # Configure progress bar
        self.progress_bar.configure(indeterminate_speed=0.5)
        self.progress_bar.set(0)
        self.progress_bar.place_forget()
    
    def _create_gradient_colors(self, base_color: str, steps: int) -> list:
        """Create gradient colors for fade effect"""
        if isinstance(base_color, list):
            base_color = base_color[1] if len(base_color) > 1 else base_color[0]
        
        # Convert hex to RGB
        if base_color.startswith("#"):
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16)
            b = int(base_color[5:7], 16)
        else:
            r, g, b = 28, 28, 28  # Default dark theme color
        
        # Create gradient
        colors = []
        for i in range(steps):
            opacity = i / (steps - 1)
            bg_r, bg_g, bg_b = 28, 28, 28  # Dark theme background
            new_r = int(bg_r + (r - bg_r) * opacity)
            new_g = int(bg_g + (g - bg_g) * opacity)
            new_b = int(bg_b + (b - bg_b) * opacity)
            color = f"#{new_r:02x}{new_g:02x}{new_b:02x}"
            colors.append(color)
        
        return colors
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        parent_canvas = self.chat_frame._parent_canvas
        
        if event.num == 4:  # Linux scroll up
            parent_canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            parent_canvas.yview_scroll(1, "units")
        else:  # Windows/macOS
            direction = -1 if event.delta > 0 else 1
            parent_canvas.yview_scroll(direction, "units")
    
    def _append_to_chat(self, text: str, sender: str):
        """Add a message to the chat area"""
        # Get current timestamp
        timestamp = datetime.now().strftime("%I:%M %p")
        
        # Get custom names from settings
        ai_name = self.settings.agent_name if hasattr(self.settings, 'agent_name') else None
        user_name = self.settings.user_name if hasattr(self.settings, 'user_name') else None
        
        # Determine display name
        display_name = timestamp
        if sender == "user" and user_name:
            display_name = f"{user_name} • {timestamp}"
        elif sender == "assistant" and ai_name:
            display_name = f"{ai_name} • {timestamp}"
        elif sender == "user":
            display_name = f"User • {timestamp}"
        elif sender == "assistant":
            display_name = f"Assistant • {timestamp}"
        
        # Message container
        msg_container = ctk.CTkFrame(
            self.chat_frame,
            fg_color="transparent"
        )
        msg_container.pack(fill="x", pady=5, padx=10)
        
        # Inner container for timestamp and bubble
        inner_container = ctk.CTkFrame(
            msg_container,
            fg_color="transparent"
        )
        inner_container.pack(
            side="right" if sender == "user" else "left",
            anchor="e" if sender == "user" else "w"
        )
        
        # Add timestamp/name label
        time_label = ctk.CTkLabel(
            inner_container,
            text=display_name,
            text_color="gray",
            font=("Helvetica", 10)
        )
        time_label.pack(
            anchor="e" if sender == "user" else "w",
            padx=15,
            pady=(0, 2)
        )
        
        # Calculate maximum width
        max_width = min(self.container.winfo_width() * 0.7, 600)
        
        # Message bubble
        bubble = ctk.CTkFrame(
            inner_container,
            fg_color="#404040" if sender == "user" else self.settings.theme_color,
            corner_radius=15
        )
        bubble.pack(anchor="e" if sender == "user" else "w")
        
        # Handle code blocks
        if "```" in text:
            self._handle_code_blocks(text, bubble, max_width)
        else:
            self._create_text_message(text, bubble, max_width)
        
        # Configure bubble padding
        bubble_pad = (max_width * 0.25, 10) if sender == "user" else (10, max_width * 0.25)
        bubble.pack(side="right" if sender == "user" else "left", padx=bubble_pad)
        
        # Scroll to bottom
        self.chat_frame.after_idle(self._scroll_to_bottom)
    
    def _handle_code_blocks(self, text: str, bubble: ctk.CTkFrame, max_width: int):
        """Handle text with code blocks"""
        segments = text.split("```")
        for i, segment in enumerate(segments):
            if i % 2 == 0:  # Regular text
                if segment.strip():
                    self._create_text_message(segment.strip(), bubble, max_width)
            else:  # Code block
                self._create_code_block(segment.strip(), bubble)
    
    def _create_text_message(self, text: str, bubble: ctk.CTkFrame, max_width: int):
        """Create a regular text message"""
        # Create a container frame for the text
        container = ctk.CTkFrame(
            bubble,
            fg_color="transparent",
            width=max_width - 40
        )
        container.pack(padx=15, pady=10, fill="x")
        container.grid_columnconfigure(0, weight=1)
        
        # Create the text widget with proper font settings from settings
        text_widget = ctk.CTkTextbox(
            container,
            wrap="word",
            activate_scrollbars=False,
            fg_color="transparent",
            border_width=0,
            width=max_width - 40,
            height=1,  # Start with minimal height
            font=(self.settings.message_font_family, self.settings.message_font_size)  # Use settings font!
        )
        text_widget.grid(row=0, column=0, sticky="ew")
        
        # Insert text
        text_widget.insert("1.0", text.strip())
        
        # Update widget to calculate proper size
        text_widget.update_idletasks()
        
        # Get the actual content height using the correct font metrics
        content_height = text_widget._textbox.count("1.0", "end", "displaylines")[0] + 1
        line_height = self.settings.message_font_size + 4  # Base line height on font size
        
        # Set the height to match content exactly
        final_height = (content_height * line_height) + 1
        text_widget.configure(height=final_height)
        text_widget.configure(state="disabled")
    
    def _create_code_block(self, code: str, bubble: ctk.CTkFrame):
        """Create a code block"""
        code_frame = ctk.CTkFrame(
            bubble,
            fg_color="#2b2b2b",
            corner_radius=8
        )
        code_frame.pack(padx=15, pady=5, fill="x")
        
        code_text = ctk.CTkTextbox(
            code_frame,
            fg_color="#2b2b2b",
            text_color="#e6e6e6",
            font=("Courier", 12),
            height=100,
            wrap="none"
        )
        code_text.pack(padx=10, pady=10, fill="x")
        code_text.insert("1.0", code)
        code_text.configure(state="disabled")
        
        # Adjust height based on content
        line_count = len(code.split('\n'))
        code_text.configure(height=min(line_count * 20, 300))
    
    def _scroll_to_bottom(self):
        """Scroll chat to the bottom"""
        try:
            self.chat_frame._parent_canvas.yview_moveto(1.0)
        except:
            pass 
    
    def update_theme_color(self, color: str):
        """Update theme color for all assistant message bubbles and progress bar"""
        # Update all assistant message bubbles
        for container in self.chat_frame.winfo_children():
            if isinstance(container, ctk.CTkFrame):
                # Get the inner container that holds the bubble
                inner_container = next((child for child in container.winfo_children() 
                                     if isinstance(child, ctk.CTkFrame)), None)
                if inner_container:
                    # Get the message bubble
                    bubble = next((child for child in inner_container.winfo_children() 
                                if isinstance(child, ctk.CTkFrame) 
                                and child.cget("fg_color") != "transparent"), None)
                    if bubble:
                        # Only update assistant messages (not user messages which are #404040)
                        if bubble.cget("fg_color") != "#404040":
                            bubble.configure(fg_color=color)
        
        # Update progress bar color
        if hasattr(self, 'progress_bar'):
            self.progress_bar.configure(progress_color=color)
    
    def update_font_settings(self, font_family: str = None, font_size: int = None):
        """Update font settings for all message bubbles"""
        # Update all text widgets in message bubbles
        for container in self.chat_frame.winfo_children():
            if isinstance(container, ctk.CTkFrame):
                # Navigate through the widget hierarchy to find text widgets
                inner_container = next((child for child in container.winfo_children() 
                                     if isinstance(child, ctk.CTkFrame)), None)
                if inner_container:
                    bubble = next((child for child in inner_container.winfo_children() 
                                if isinstance(child, ctk.CTkFrame)), None)
                    if bubble:
                        # Find the text container inside the bubble
                        text_container = next((child for child in bubble.winfo_children() 
                                            if isinstance(child, ctk.CTkFrame)), None)
                        if text_container:
                            # Find and update the text widget
                            text_widget = next((child for child in text_container.winfo_children() 
                                             if isinstance(child, ctk.CTkTextbox)), None)
                            if text_widget:
                                # Update font settings
                                current_font = text_widget.cget("font")
                                new_family = font_family if font_family else current_font[0]
                                new_size = font_size if font_size else current_font[1]
                                
                                # Configure new font
                                text_widget.configure(font=(new_family, new_size))
                                
                                # Recalculate height based on new font
                                text_widget.update_idletasks()
                                content_height = text_widget._textbox.count("1.0", "end", "displaylines")[0] + 1
                                line_height = new_size + 4
                                final_height = (content_height * line_height) + 1
                                text_widget.configure(height=final_height) 
    
    def _show_loading(self):
        """Show loading indicator and disable sidebar"""
        self.is_processing = True
        self.progress_bar.place(relx=0.5, rely=0.5, relwidth=0.99, anchor="center")
        self.progress_bar.start()
        
        # Disable sidebar buttons
        if hasattr(self.parent, 'sidebar'):
            self.parent.sidebar.disable_interaction()

    def _hide_loading(self):
        """Hide loading indicator and re-enable sidebar"""
        self.is_processing = False
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.progress_bar.place_forget()
        
        # Re-enable sidebar buttons
        if hasattr(self.parent, 'sidebar'):
            self.parent.sidebar.enable_interaction() 