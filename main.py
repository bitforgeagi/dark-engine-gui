# main.py

import tkinter as tk
import os
import sys
from src.gui import ModernChatApp

def get_resource_path(relative_path):
    """Get the absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    app = ModernChatApp()
    app.mainloop()

if __name__ == "__main__":
    main()
