def __init__(self):
    super().__init__()
    
    # Initialize settings first
    self.settings_manager = SettingsManager()
    
    # Initialize token manager
    self.token_manager = TokenManager()
    
    # Initialize API with settings
    self.api = OllamaAPI(on_error=self.handle_error)
    self.api.token_manager = self.token_manager
    self.api.initialize_with_settings(self.settings_manager.settings)
    
    # Rest of initialization... 