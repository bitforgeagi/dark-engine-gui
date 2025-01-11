import customtkinter as ctk
from PIL import Image
import os
import requests
import threading
import webbrowser
from pathlib import Path
from .startup_check import OllamaSystemCheck
import json

class WelcomeDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Dark Engine GUI")
        
        # First withdraw to prevent flickering
        self.withdraw()
        
        # Set initial size
        dialog_width = 500
        dialog_height = 800
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate center position
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        # Set geometry with calculated position
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Make dialog modal and center it
        self.transient(parent)
        self.grab_set()
        
        # Configure theme colors
        self.colors = {
            "bg": "#1C1C1C",            # Dark background
            "button": "#333333",       # Dark gray button
            "button_hover": "#4D4D4D", # Slightly lighter gray hover
            "text": "#FFFFFF",         # White text
            "text_secondary": "#AAAAAA",
            "success": "#00FF00",      # Bright green for status
            "error": "#FF0000"         # Bright red for status
        }
        
        # Configure theme
        self.configure(fg_color=self.colors["bg"])
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Store parent reference
        self.parent = parent
        
        # Initialize UI
        self.setup_ui()
        
        # Add selected_model attribute
        self.selected_model = None
        
        # Show the window after it's fully configured
        self.deiconify()
        self.focus_force()
        
    def setup_ui(self):
        try:
            # Load and display logo
            logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
            logo_image = Image.open(logo_path)
            
            # Calculate aspect ratio and maintain it
            aspect_ratio = logo_image.width / logo_image.height
            target_height = 150
            target_width = int(target_height * aspect_ratio)
            
            # Create CTkImage directly from the original image
            logo_photo = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(target_width, target_height)
            )
            
            logo_label = ctk.CTkLabel(self, image=logo_photo, text="")
            logo_label.pack(pady=(40, 20))
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="Dark Engine GUI",
            font=("Helvetica", 24, "bold"),
            text_color=self.colors["text"]
        )
        title.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            self,
            text="Your AI-Powered Development Assistant",
            font=("Helvetica", 14),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack(pady=(0, 30))
        
        # Status frame
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(fill="x", padx=40, pady=10)
        self.check_system_status()
        
    def check_system_status(self):
        """Check Ollama system status and display appropriate UI"""
        # Clear status frame
        for widget in self.status_frame.winfo_children():
            widget.destroy()
            
        success, message = OllamaSystemCheck.check_system()
        
        if not success:
            self.show_setup_required_ui(message)
        else:
            self.show_model_selection_ui()
    
    def show_setup_required_ui(self, message):
        """Show UI for when Ollama needs to be installed"""
        # Status indicator
        status_label = ctk.CTkLabel(
            self.status_frame,
            text="⚠️ AI Server Status: Offline",
            font=("Helvetica", 16, "bold"),
            text_color=self.colors["error"]
        )
        status_label.pack(pady=(20, 10))
        
        # Error message
        error_msg = ctk.CTkLabel(
            self.status_frame,
            text=message,
            wraplength=400,
            text_color=self.colors["text_secondary"]
        )
        error_msg.pack(pady=10)
        
        # Setup instructions
        instructions = ctk.CTkLabel(
            self.status_frame,
            text="To get started:\n\n1. Install Ollama from ollama.ai\n2. Start the Ollama service\n3. Return here to download models",
            justify="left",
            font=("Helvetica", 12),
            text_color=self.colors["text_secondary"]
        )
        instructions.pack(pady=20)
        
        # Button frame
        button_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # Ollama website button
        website_btn = ctk.CTkButton(
            button_frame,
            text="Download Ollama",
            command=lambda: webbrowser.open("https://ollama.ai"),
            font=("Helvetica", 12),
            height=40,
            fg_color=self.colors["button"],
            hover_color=self.colors["button_hover"]
        )
        website_btn.pack(side="left", padx=10)
        
        # Documentation button
        docs_btn = ctk.CTkButton(
            button_frame,
            text="View Setup Guide",
            command=lambda: webbrowser.open("https://darkengine.ai/docs/setup"),
            font=("Helvetica", 12),
            height=40,
            fg_color=self.colors["button"],
            hover_color=self.colors["button_hover"]
        )
        docs_btn.pack(side="left", padx=10)
        
        # Retry button
        retry_btn = ctk.CTkButton(
            self.status_frame,
            text="↻ Check Again",
            command=self.check_system_status,
            font=("Helvetica", 12),
            height=40,
            fg_color=self.colors["button"],
            hover_color=self.colors["button_hover"]
        )
        retry_btn.pack(pady=20)
    
    def show_model_selection_ui(self):
        """Show UI for selecting/downloading models"""
        # Status indicator with checkmark (centered)
        status_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 20))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="✓ AI Server Status: Online",
            font=("Helvetica", 16),
            text_color=self.colors["success"]
        )
        status_label.pack(anchor="center")
        
        # INSTALLED MODELS SECTION
        installed_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        installed_frame.pack(fill="x", pady=(20, 30))
        
        installed_label = ctk.CTkLabel(
            installed_frame,
            text="Start with installed model:",
            font=("Helvetica", 14, "bold"),
            text_color=self.colors["text"]
        )
        installed_label.pack(pady=(0, 10))
        
        # Installed models dropdown
        installed_models = self.get_installed_models()
        if installed_models:
            self.installed_var = ctk.StringVar(value=installed_models[0])
            installed_dropdown = ctk.CTkOptionMenu(
                installed_frame,
                variable=self.installed_var,
                values=installed_models,
                width=300,
                height=32,
                font=("Helvetica", 12),
                fg_color=self.colors["button"],
                button_color=self.colors["button"],
                button_hover_color=self.colors["button_hover"],
                dropdown_fg_color=self.colors["bg"],
                dropdown_hover_color=self.colors["button_hover"]
            )
            installed_dropdown.pack(pady=5)
            
            start_btn = ctk.CTkButton(
                installed_frame,
                text="Start",
                command=lambda: self.start_with_model(self.installed_var.get()),
                font=("Helvetica", 12),
                height=32,
                width=300,
                fg_color=self.colors["button"],
                hover_color=self.colors["button_hover"]
            )
            start_btn.pack(pady=5)
            
            # Move refresh button here, after the start button
            refresh_btn = ctk.CTkButton(
                installed_frame,
                text="↻ Refresh Models",
                width=150,  # Make it smaller than the main buttons
                height=25,  # Make it slightly smaller height
                command=self.refresh_models,
                font=("Helvetica", 12),
                fg_color=self.colors["button"],
                hover_color=self.colors["button_hover"]
            )
            refresh_btn.pack(pady=5)
        else:
            no_models_label = ctk.CTkLabel(
                installed_frame,
                text="No models installed yet",
                font=("Helvetica", 12),
                text_color=self.colors["text_secondary"]
            )
            no_models_label.pack(pady=5)
        
        # Separator
        separator = ctk.CTkFrame(self.status_frame, height=2, fg_color="#2E2E2E")
        separator.pack(fill="x", pady=20)
        
        # DOWNLOAD NEW MODEL SECTION
        download_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        download_frame.pack(fill="x", pady=10)
        
        download_label = ctk.CTkLabel(
            download_frame,
            text="Recommended Models:",
            font=("Helvetica", 14, "bold"),
            text_color=self.colors["text"]
        )
        download_label.pack(pady=(0, 10))
        
        # Get installed models and filter available models
        installed_models = self.get_installed_models()
        
        # Filter out installed models and normalize model names for comparison
        def normalize_model_name(name):
            """Normalize model names for comparison by removing version tags"""
            return name.split(':')[0].lower()
        
        installed_normalized = [normalize_model_name(m) for m in installed_models]
        available_models = [m for m in self.get_available_models() 
                           if normalize_model_name(m) not in installed_normalized]
        
        if available_models:
            self.download_var = ctk.StringVar(value=available_models[0])
            download_dropdown = ctk.CTkOptionMenu(
                download_frame,
                variable=self.download_var,
                values=available_models,
                width=300,
                height=32,
                font=("Helvetica", 12),
                fg_color=self.colors["button"],
                button_color=self.colors["button"],
                button_hover_color=self.colors["button_hover"],
                dropdown_fg_color=self.colors["bg"],
                dropdown_hover_color=self.colors["button_hover"]
            )
            download_dropdown.pack(pady=5)
            
            # Download button and progress bar
            self.download_btn = ctk.CTkButton(
                download_frame,
                text="Download",
                command=lambda: self.download_model(self.download_var.get()),
                font=("Helvetica", 12),
                height=32,
                width=300,
                fg_color=self.colors["button"],
                hover_color=self.colors["button_hover"]
            )
            self.download_btn.pack(pady=5)
        else:
            # Show message when all recommended models are installed
            no_models_label = ctk.CTkLabel(
                download_frame,
                text="All recommended models are already installed",
                font=("Helvetica", 12),
                text_color=self.colors["text_secondary"]
            )
            no_models_label.pack(pady=5)
        
        # Progress bar (hidden initially)
        self.progress_bar = ctk.CTkProgressBar(
            download_frame,
            mode="indeterminate",
            height=4,
            width=300,
            progress_color=self.colors["button"],
            fg_color="#404040"
        )
        self.progress_bar.pack(pady=5)
        self.progress_bar.pack_forget()
    
    def download_model(self, model_name: str):
        """Download selected model with progress tracking"""
        self.download_btn.configure(state="disabled")
        self.progress_bar.pack()
        self.progress_bar.set(0)  # Reset progress
        self.progress_bar.configure(mode="determinate")  # Change to determinate mode
        
        def download():
            try:
                response = requests.post(
                    "http://localhost:11434/api/pull",
                    json={"name": model_name},
                    stream=True
                )
                
                if response.status_code == 200:
                    total_size = 0
                    downloaded = 0
                    
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if 'total' in data:
                                total_size = data['total']
                            if 'completed' in data:
                                downloaded = data['completed']
                                if total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    self.after(0, lambda: self.update_progress(progress))
                    
                    self.after(0, lambda: self.download_complete(model_name))
                else:
                    self.after(0, self.download_error)
            except Exception as e:
                self.after(0, lambda: self.download_error(str(e)))
        
        threading.Thread(target=download, daemon=True).start()
    
    def download_complete(self, model_name: str):
        """Handle successful model download"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()  # Hide progress bar
        self.action_btn.configure(
            text=f"Start with {model_name}",
            command=lambda: self.start_with_model(model_name),
            state="normal"
        )
    
    def download_error(self, msg=None):
        """Handle download error"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.download_btn.configure(state="normal", text="Download")
        error_message = msg if msg else "An error occurred while downloading."
        self.show_toast(error_message)
    
    def get_installed_models(self) -> list:
        """Get list of installed Ollama models"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                return [model["name"] for model in response.json().get("models", [])]
        except:
            return []
        return []
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        return [
            "llama2:latest",
            "mistral:latest", 
            "gemma:latest"
        ]
    
    def start_with_model(self, model_name: str):
        """Start the app with selected model"""
        # Update settings with selected model
        self.parent.settings_manager.settings.model_name = model_name
        self.parent.settings_manager.save_settings()  # Save to persist the choice
        
        self.selected_model = model_name
        self.destroy()
    
    def update_progress(self, percentage: float):
        """Update progress bar with download progress"""
        self.progress_bar.set(percentage / 100)
        self.download_btn.configure(text=f"Downloading... {percentage:.1f}%")
    
    def refresh_models(self):
        """Refresh the list of installed models"""
        installed_models = self.get_installed_models()
        available_models = [m for m in self.get_available_models() 
                           if m not in installed_models]
        
        # Update installed models dropdown
        if hasattr(self, 'installed_var') and installed_models:
            current_model = self.installed_var.get()
            new_model = current_model if current_model in installed_models else installed_models[0]
            self.installed_var.set(new_model)
            for widget in self.status_frame.winfo_children():
                if isinstance(widget, ctk.CTkOptionMenu) and widget.cget("variable") == self.installed_var:
                    widget.configure(values=installed_models)
        
        # Update download models dropdown
        if hasattr(self, 'download_var'):
            current_model = self.download_var.get()
            new_model = current_model if current_model in available_models else (available_models[0] if available_models else "")
            self.download_var.set(new_model)
            for widget in self.status_frame.winfo_children():
                if isinstance(widget, ctk.CTkOptionMenu) and widget.cget("variable") == self.download_var:
                    widget.configure(values=available_models)
        
        # Show success message
        self.show_toast("Models refreshed successfully")
    
    def show_toast(self, message: str, duration: int = 2000):
        """Show a temporary toast message"""
        toast = ctk.CTkLabel(
            self,
            text=message,
            font=("Helvetica", 12),
            fg_color=self.colors["button"],
            corner_radius=6,
            text_color=self.colors["text"]
        )
        toast.place(relx=0.5, rely=0.9, anchor="center")
        self.after(duration, toast.destroy)