from typing import Dict, Optional, List
import customtkinter as ctk
from ..settings import SettingsManager
from ..model import OllamaAPI
from ..settings_dialog import SettingsDialog
from ..startup_check import OllamaSystemCheck
from ..memory.sidebar import MemorySidebar
from ..memory.database import ChatMemoryDB
from datetime import datetime
from ..utils import TokenManager
from .chat_area import ChatArea
from .input_area import InputArea
from ..welcome_dialog import WelcomeDialog
from .status_bar import StatusBar

def center_window(window, width, height):
    """Center a window on the screen"""
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set geometry
    window.geometry(f"{width}x{height}+{x}+{y}")

class ModernChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set window title
        self.title("Dark Engine")
        
        # Set initial size
        width = 1200
        height = 800
        
        # Center window
        center_window(self, width, height)
        
        # Initialize memory database
        self.memory_db = ChatMemoryDB()
        self.memory_db.debug_print_contents()
        
        # Initialize settings first
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        
        # Show welcome dialog and get selected model
        selected_model = self.show_welcome_dialog()
        if not selected_model:  # User closed welcome dialog without selecting model
            self.destroy()
            return
            
        # Initialize API with selected model
        self.api = OllamaAPI(model=selected_model)
        
        # Initialize token manager
        self.token_manager = TokenManager(self.settings)
        self.api.token_manager = self.token_manager
        
        # Apply saved settings
        self.api.conversation_history[0] = {
            "role": "system",
            "content": self.settings.system_prompt
        }
        
        # Configure window
        self.setup_window()
        self.setup_ui()
        self._setup_bindings()
        
        # Add loading state
        self.is_processing = False
        self.current_chat_id = None
    
    def setup_window(self):
        """Configure main window settings"""
        self.title("Dark Engine GUI")
        self.geometry("1000x800")
        self.minsize(800, 600)
        self.maxsize(1920, 1080)
        
        # Center the window on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1000) // 2
        y = (screen_height - 800) // 2
        self.geometry(f"1000x800+{x}+{y}")
        
        # Set theme
        ctk.set_appearance_mode(self.settings.theme)
        ctk.set_default_color_theme("blue")
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def setup_ui(self):
        """Setup main UI components"""
        # Add sidebar
        self.sidebar = MemorySidebar(
            self,
            on_chat_selected=self.load_chat,
            on_new_chat=self.new_chat
        )
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(10, 0), pady=10)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Configure main frame grid
        self.main_frame.grid_rowconfigure(0, weight=1)  # Chat area
        self.main_frame.grid_rowconfigure(1, weight=0)  # Input area
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Add components
        self.chat_area = ChatArea(self.main_frame, self.settings)
        self.input_area = InputArea(self.main_frame, self.settings, self.send_message)
        
        # Remove status bar - it's already in settings
        # self.status_bar = StatusBar(self)
        # self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

    def check_system_status(self) -> bool:
        """Check if system is ready and show welcome dialog if needed"""
        welcome = WelcomeDialog(self)
        self.wait_window(welcome)
        
        # Recheck system status
        success, _ = OllamaSystemCheck.check_system()
        if not success:
            self.destroy()
            return False
        
        return True

    def load_chat(self, chat_id: int):
        """Load a saved chat"""
        # Don't allow chat switching while processing
        if self.is_processing:
            return
        
        # Don't reload if it's the current chat
        if self.current_chat_id == chat_id:
            return
        
        chat_data = self.memory_db.get_chat(chat_id)
        if not chat_data:
            return
        
        # Clear current chat
        for widget in self.chat_area.chat_frame.winfo_children():
            widget.destroy()
        
        # Set current chat ID in both app and sidebar
        self.current_chat_id = chat_id
        self.sidebar.current_chat_id = chat_id  # Sync the ID with sidebar
        
        # Update highlighting immediately
        for btn in self.sidebar._chat_buttons:
            if btn.winfo_exists():
                is_current = btn._chat_id == chat_id
                btn.configure(text_color="white" if is_current else "gray")
        
        # Load messages
        self.api.conversation_history = chat_data["messages"]
        
        # Display messages
        for msg in chat_data["messages"]:
            if msg["role"] not in ["system"]:  # Skip system messages
                self.chat_area._append_to_chat(msg["content"], sender=msg["role"])
        
        # Force geometry update and scroll refresh
        self.chat_area.chat_frame.update_idletasks()
        self.after(100, self._ensure_chat_visible)

    def new_chat(self, folder_id=None):
        """Create a new chat and return its ID"""
        # Clear the chat window by removing all widgets
        for widget in self.chat_area.chat_frame.winfo_children():
            widget.destroy()
        
        # Reset conversation history
        self.api.conversation_history = [{
            "role": "system",
            "content": self.settings.system_prompt
        }]
        
        # Don't create a new chat in database until first message is sent
        self.current_chat_id = None
        
        return None  # Return None to indicate no database entry yet

    def _ensure_chat_visible(self):
        """Ensure chat content is visible after loading"""
        # Force another geometry update
        self.chat_area.chat_frame.update_idletasks()
        # Update the scroll region
        self.chat_area.chat_frame._parent_canvas.configure(
            scrollregion=self.chat_area.chat_frame._parent_canvas.bbox("all")
        )
        # Scroll to show content
        self.chat_area.chat_frame._parent_canvas.yview_moveto(0.0)

    def open_settings_dialog(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        dialog.transient(self)  # Make dialog transient to main window
        dialog.grab_set()       # Make dialog modal
        dialog.focus_force()    # Force focus to dialog
        dialog.wait_window()    # Wait for dialog to close
        
        # Update the API instance with the new system prompt
        self.api.conversation_history[0] = {
            "role": "system",
            "content": self.settings.system_prompt
        }

    def send_message(self, event=None):
        """Send a message to the API"""
        if self.is_processing:
            return
        
        user_text = self.input_area.input_field.get("1.0", "end-1c").strip()
        if not user_text:
            return

        # Check message length
        is_valid, error_msg = self.token_manager.check_input_length(user_text)
        if not is_valid:
            self._show_token_warning(error_msg)
            return
        
        # Add timestamp to message
        timestamp = datetime.now().isoformat()
        
        # Check if this is the first message in a chat
        is_first_message = len(self.api.conversation_history) <= 1
        
        # Add timestamp to user message
        self.api.conversation_history.append({
            "role": "user",
            "content": user_text,
            "timestamp": timestamp
        })
        
        self.chat_area._append_to_chat(user_text, sender="user")
        self.input_area.input_field.delete("1.0", "end")
        self.input_area._update_input_height()
        
        # Show loading and disable sidebar
        self.is_processing = True
        self.chat_area.progress_bar.place(relx=0.5, rely=0.5, relwidth=0.99, anchor="center")
        self.chat_area.progress_bar.start()
        self.input_area.input_field.configure(state="disabled")
        self.input_area.send_button.configure(state="disabled")
        self.sidebar.disable_interaction()  # Disable sidebar here
        
        # Use async response
        self.api.get_response_async(
            user_text,
            callback=lambda response: self._handle_response(response, is_first_message),
            temperature=self.settings.temperature
        )
        
        # Auto-save after sending message
        self.after(1000, self.save_current_chat)

    def _show_loading(self):
        """Show loading indicator"""
        self.is_processing = True
        self.chat_area.progress_bar.place(relx=0.5, rely=0.5, relwidth=0.99, anchor="center")
        self.chat_area.progress_bar.start()
        self.input_area.input_field.configure(state="disabled")
        self.input_area.send_button.configure(state="disabled")

    def _hide_loading(self):
        """Hide loading indicator"""
        self.is_processing = False
        self.chat_area.progress_bar.stop()
        self.chat_area.progress_bar.set(0)
        self.chat_area.progress_bar.place_forget()
        self.input_area.input_field.configure(state="normal")
        self.input_area.send_button.configure(state="normal")

    def _handle_response(self, response: str, is_first_message: bool = False):
        """Handle async response from API"""
        self.after(0, lambda: self._process_response(response, is_first_message))

    def _process_response(self, response: str, is_first_message: bool = False):
        """Process the response from the API"""
        response = response.strip()
        self.chat_area._append_to_chat(response, sender="assistant")
        
        # Hide loading and re-enable sidebar
        self.is_processing = False
        self.chat_area.progress_bar.stop()
        self.chat_area.progress_bar.set(0)
        self.chat_area.progress_bar.place_forget()
        self.input_area.input_field.configure(state="normal")
        self.input_area.send_button.configure(state="normal")
        self.sidebar.enable_interaction()  # Re-enable sidebar here
        
        # Handle chat saving/updating
        if is_first_message:
            title = self.api.conversation_history[1]["content"]
            title = title[:18] + "..." if len(title) > 18 else title
            self.memory_db.rename_chat(self.current_chat_id, title)
            self.sidebar.load_contents()
        else:
            self.after(1000, self.save_current_chat)

    def save_current_chat(self):
        """Save the current chat"""
        if len(self.api.conversation_history) <= 1:  # Only system message
            return
        
        # Get first user message for title
        first_msg = next((msg for msg in self.api.conversation_history if msg["role"] == "user"), None)
        if not first_msg:
            return
        
        # Create abbreviated title from first message
        title = first_msg["content"][:18] + "..." if len(first_msg["content"]) > 12 else first_msg["content"]
        
        if self.current_chat_id is None:
            # Create new chat
            self.current_chat_id = self.memory_db.save_chat(
                title=title,
                messages=self.api.conversation_history,
                model_name=self.api.model,
                folder_id=self.sidebar.current_folder_id
            )
            # Update sidebar's current chat ID to ensure proper highlighting
            self.sidebar.current_chat_id = self.current_chat_id
        else:
            # Update existing chat
            self.memory_db.update_chat(
                chat_id=self.current_chat_id,
                messages=self.api.conversation_history
            )
        
        # Refresh sidebar with proper highlighting
        self.sidebar.load_contents()

    def check_connection_status(self):
        """Periodically check Ollama connection status"""
        success, _ = OllamaSystemCheck.check_system()
        is_connected = success
        
        # Update status bar
        self.status_bar.indicator.configure(
            text_color="#00ff00" if is_connected else "#ff0000"
        )
        self.status_bar.text.configure(
            text=f"AI-Server ({'On' if is_connected else 'Off'})"
        )
        
        # Check again in 5 seconds
        self.after(5000, self.check_connection_status)

    def _setup_bindings(self):
        """Setup keyboard bindings"""
        self.input_area.input_field.bind("<Return>", self._handle_return)
        self.input_area.input_field.bind("<Shift-Return>", self._handle_shift_return)
        self.bind("<Control-b>", lambda e: self.sidebar.toggle_sidebar())

    def _handle_return(self, event):
        """Send message on Enter, unless Shift is held"""
        if not event.state & 0x1:  # No Shift key
            self.send_message()
            return "break"  # Prevent default newline

    def _handle_shift_return(self, event):
        """Allow newline when Shift+Enter is pressed"""
        return None  # Allow default behavior

    def _show_token_warning(self, message: str):
        """Show token limit warning in UI"""
        warning = ctk.CTkLabel(
            self.chat_area.chat_frame,
            text=message,
            text_color="orange",
            font=("Helvetica", 12)
        )
        warning.pack(pady=5)
        # Auto-remove warning after 5 seconds
        self.after(5000, warning.destroy)

    def update_theme_color(self, color):
        """Update UI elements with new theme color"""
        # Update sidebar buttons
        self.sidebar.folder_action_btn.configure(fg_color=color)
        self.sidebar.new_chat_btn.configure(fg_color=color)
        
        # Update input area
        self.input_area.send_button.configure(fg_color=color)
        self.input_area.send_button.configure(hover_color=color)
        
        # Update chat area message bubbles
        self.chat_area.update_theme_color(color)
        
        # Update status bar indicator if connected
        if hasattr(self, 'status_bar'):
            success, _ = OllamaSystemCheck.check_system()
            self.status_bar.update_status(success)  # This will use the new theme color
        
        # Update settings
        self.settings.theme_color = color

    def show_welcome_dialog(self) -> str:
        """Show welcome dialog and return selected model"""
        welcome = WelcomeDialog(self)
        self.wait_window(welcome)
        return getattr(welcome, 'selected_model', None)

    def handle_chat_selected(self, chat_id: int):
        """Handle chat selection from sidebar"""
        try:
            # Get chat from database
            chat_data = self.memory_db.get_chat(chat_id)
            if not chat_data:
                print(f"Warning: No chat data found for id {chat_id}")
                return
            
            # Preserve current messages if this is the current chat
            if hasattr(self, 'current_chat_id') and self.current_chat_id == chat_id:
                return
            
            # Update the conversation history
            self.api.conversation_history = chat_data['messages']
            
            # Update the chat area
            self.chat_area.clear_messages()
            for message in chat_data['messages'][1:]:  # Skip system message
                self.chat_area.add_message(
                    message['content'],
                    is_user=message['role'] == 'user'
                )
            
            # Update current chat ID
            self.current_chat_id = chat_id
            
        except Exception as e:
            print(f"Error loading chat: {e}")
            messagebox.showerror("Error", f"Failed to load chat: {str(e)}")

    def update_message_fonts(self, font_family: str = None, font_size: int = None):
        """Update font settings for all messages"""
        if font_family:
            self.settings.message_font_family = font_family
        if font_size:
            self.settings.message_font_size = font_size
        
        # Update existing messages
        self.chat_area.update_font_settings(font_family, font_size)
        
        # Save settings
        self.settings_manager.save_settings()

