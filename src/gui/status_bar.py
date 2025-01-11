import customtkinter as ctk

class StatusBar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Store parent reference to access settings
        self.parent = parent
        
        # Create status indicator and text
        self.indicator = ctk.CTkLabel(
            self,
            text="●",
            text_color=parent.settings.theme_color,
            font=("Helvetica", 14)
        )
        self.indicator.pack(side="left", padx=5)
        
        self.text = ctk.CTkLabel(
            self,
            text="AI-Server (On)",
            font=("Helvetica", 12)
        )
        self.text.pack(side="left")
    
    def update_status(self, is_connected: bool):
        """Update connection status"""
        # Always get current theme color directly from parent
        current_color = self.parent.settings.theme_color
        
        # Update indicator color based on connection status
        if is_connected:
            self.indicator.configure(text_color=current_color)
        else:
            self.indicator.configure(text_color="#ff0000")
            
        # Update status text
        self.text.configure(
            text=f"AI-Server ({'On' if is_connected else 'Off'})"
        ) 