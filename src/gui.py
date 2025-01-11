def show_welcome_dialog(self):
    """Show welcome dialog and get selected model"""
    # First update the main window to ensure it's drawn
    self.update_idletasks()
    
    # Create and show welcome dialog
    welcome = WelcomeDialog(self)
    
    # Center welcome dialog on main window
    dialog_width = 500  # Match the width from WelcomeDialog
    dialog_height = 800  # Match the height from WelcomeDialog
    
    # Get main window position and size
    main_x = self.winfo_x()
    main_y = self.winfo_y()
    main_width = self.winfo_width()
    main_height = self.winfo_height()
    
    # Calculate center position
    x = main_x + (main_width - dialog_width) // 2
    y = main_y + (main_height - dialog_height) // 2
    
    # Ensure dialog stays on screen
    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()
    
    x = max(0, min(x, screen_width - dialog_width))
    y = max(0, min(y, screen_height - dialog_height))
    
    # Set the welcome dialog position
    welcome.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    # Wait for dialog to close and get selected model
    self.wait_window(welcome)
    return welcome.selected_model 