import customtkinter as ctk
from typing import Optional, Callable, Dict
from .database import ChatMemoryDB
import tkinter as tk
import tkinter.messagebox as messagebox

class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class MemorySidebar(ctk.CTkFrame):
    def __init__(self, parent, on_chat_selected: Callable, on_new_chat: Callable):
        super().__init__(parent, width=250)
        
        # Store parent reference
        self.parent = parent
        
        # Fixed widths for sidebar states
        self.expanded_width = 250
        self.collapsed_width = 50
        self.is_expanded = True
        
        # Force initial width
        self.configure(width=self.expanded_width)
        self._force_width = True
        
        self.db = ChatMemoryDB()
        self.on_chat_selected = on_chat_selected
        self.on_new_chat = on_new_chat
        self.current_folder_id = None
        self.current_chat_id = None
        
        # Mapping from folder_id to subfolder_container for toggle functionality
        self.folder_containers = {}
        
        # Create context menus
        self._setup_context_menus()
        self.setup_ui()
        self.load_contents()
    
    def _setup_context_menus(self):
        """Setup right-click context menus"""
        # Chat menu
        self.chat_menu = tk.Menu(self, tearoff=0)
        self.chat_menu.add_command(label="Delete", command=lambda: self._delete_chat_by_id())
        self.chat_menu.add_command(label="Rename", command=lambda: self._rename_chat_by_id())
        
        # Folder menu
        self.folder_menu = tk.Menu(self, tearoff=0)
        self.folder_menu.add_command(label="Delete", command=lambda: self._delete_folder_by_id())
        self.folder_menu.add_command(label="Rename", command=lambda: self._rename_folder_by_id())
        
        # Store the current item id
        self.current_chat_id = None
        self.current_folder_id = None
    
    def setup_ui(self):
        """Initial UI setup"""
        # Get theme mode
        is_dark = self.parent.settings.theme == "dark"
        text_color = "white" if is_dark else "#2b2b2b"
        
        # Top control bar with collapse and settings
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        # Left side - collapse button with hamburger menu icon
        self.collapse_btn = ctk.CTkButton(
            self.control_frame,
            text="☰",
            width=30,
            height=24,
            fg_color="transparent",
            text_color=text_color,
            hover_color="#000000" if is_dark else "#d0d0d0",
            command=self.toggle_sidebar
        )
        self.collapse_btn.pack(side="left")
        
        # Right side - settings button
        self.settings_btn = ctk.CTkButton(
            self.control_frame,
            text="⚙️",
            width=30,
            height=24,
            fg_color="transparent",
            text_color=text_color,
            hover_color="#000000" if is_dark else "#d0d0d0",
            command=self.parent.open_settings_dialog
        )
        self.settings_btn.pack(side="right")
        
        # Folder section
        self.folder_header = ctk.CTkFrame(self, fg_color="transparent")
        self.folder_header.pack(fill="x", padx=5, pady=(5,0))
        
        self.folder_label = ctk.CTkLabel(
            self.folder_header,
            text="📁 Folders",
            font=("Helvetica", 12)
        )
        self.folder_label.pack(side="left")
        
        # This button will toggle between "+ New Folder" and "← Exit Folder"
        self.folder_action_btn = ctk.CTkButton(
            self.folder_header,
            text="+ New Folder",
            width=120,
            command=self.create_folder,  # Will be updated when showing folder contents
            fg_color=self.parent.settings.theme_color,
            hover_color="#000000"
        )
        self.folder_action_btn.pack(side="right", padx=5)
        
        # Folder tree
        self.folder_tree = ctk.CTkScrollableFrame(
            self,
            height=200
        )
        self.folder_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Recent/Folder chats header with new chat button
        self.chats_header = ctk.CTkFrame(self, fg_color="transparent")
        self.chats_header.pack(fill="x", padx=5, pady=(5,0))
        
        # Label for Quick Chats/Folder name
        self.chats_label = ctk.CTkLabel(
            self.chats_header,
            text="💬 Chats",
            font=("Helvetica", 12),
            anchor="w"
        )
        self.chats_label.pack(side="left", padx=(10, 0))
        
        # New chat button - text will update based on context
        self.new_chat_btn = ctk.CTkButton(
            self.chats_header,
            text="+ New Chat",
            width=120,
            command=self._handle_new_chat,
            fg_color=self.parent.settings.theme_color,
            hover_color="#000000"
        )
        self.new_chat_btn.pack(side="right", padx=5)
        
        # Recent chats list (scrollable)
        self.recent_list = ctk.CTkScrollableFrame(
            self,
            height=200
        )
        self.recent_list.pack(fill="both", expand=True, padx=5, pady=5)

    def load_contents(self):
        """Load folders and recent chats"""
        # Clear existing content
        for widget in self.folder_tree.winfo_children():
            widget.destroy()
        for widget in self.recent_list.winfo_children():
            widget.destroy()
        
        # Load root folders
        self._load_folder_contents(None, self.folder_tree, 0)
        
        # If we're in a folder, show its contents
        if self.current_folder_id is not None:
            contents = self.db.get_folder_contents(self.current_folder_id)
            folder_name = None
            
            # Find the folder name
            for folder in self.db.get_folder_contents(None)['folders']:
                if folder['id'] == self.current_folder_id:
                    folder_name = folder['name']
                    break
            
            if folder_name:
                # Update header text and buttons
                self.chats_label.configure(text=f"📂 {folder_name}")
                self.new_chat_btn.configure(text=f"+ 💬 in {folder_name}")
                
                # Change folder action button to exit
                self.folder_action_btn.configure(
                    text="← Exit Folder",
                    command=self._handle_back_click
                )
            
            for chat in contents['chats']:
                self.add_chat_item(chat)
        else:
            # Reset to default state
            self.chats_label.configure(text="💬 Quick Chats")
            self.new_chat_btn.configure(text="+ New Chat")
            self.folder_action_btn.configure(
                text="+ New Folder",
                command=self.create_folder
            )
            
            contents = self.db.get_folder_contents(None)
            for chat in contents["chats"]:
                self.add_chat_item(chat)
    
    def _load_folder_contents(self, folder_id: Optional[int], parent_widget: ctk.CTkFrame, level: int):
        """Recursively load folder contents"""
        contents = self.db.get_folder_contents(folder_id)
        print(f"Loading folder contents for folder_id={folder_id}")  # Debug print
        print(f"Folders found: {contents['folders']}")  # NEW DEBUG LINE
        
        # Add folders
        for folder in contents['folders']:
            print(f"Creating folder UI for: {folder['name']}")  # NEW DEBUG LINE
            folder_frame = self.create_folder_item(folder, level, parent_widget)
            folder_frame.pack(fill="x", pady=2)
            
            # Recursively load subfolders
            self._load_folder_contents(folder['id'], folder_frame, level + 1)
    
    def create_folder_item(self, folder: Dict, level: int, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Create a folder item in the tree"""
        # Main row container
        row = ctk.CTkFrame(parent, fg_color="transparent", height=35)
        row.pack(fill="x", pady=1)
        row.pack_propagate(False)  # Force height
        
        # Indent based on level
        if level > 0:
            indent = ctk.CTkFrame(row, width=20 * level, fg_color="transparent")
            indent.pack(side="left")
        
        # Folder button - use closed folder emoji by default
        folder_btn = ctk.CTkButton(
            row,
            text=f"📁 {folder['name']}",  # Default to closed folder
            fg_color="transparent",
            text_color="gray" if folder['id'] != self.current_folder_id else "white",
            hover_color="#333333",
            anchor="w",
            command=lambda fid=folder['id']: self._handle_folder_click(fid)
        )
        folder_btn.pack(side="left", fill="x", expand=True)
        
        # If this is the currently selected folder, show open folder emoji
        if folder['id'] == self.current_folder_id:
            folder_btn.configure(text=f"📂 {folder['name']}")  # Open folder emoji
        
        # Store reference to update colors later
        folder_btn._folder_id = folder['id']  # Store ID for reference
        if not hasattr(self, '_folder_buttons'):
            self._folder_buttons = []
        self._folder_buttons.append(folder_btn)
        
        # Bind double-click for rename
        folder_btn.bind("<Double-Button-1>", lambda e, fid=folder['id']: self._start_rename(e, fid, folder_btn))
        
        # Delete button (initially hidden)
        delete_btn = ctk.CTkButton(
            row,
            text="🗑️",
            width=30,
            fg_color="transparent",
            hover_color="#333333",
            command=lambda fid=folder['id']: self._confirm_folder_delete(fid)
        )
        
        def on_enter(event=None):
            x = row.winfo_width() - delete_btn.winfo_reqwidth() - 5
            y = (row.winfo_height() - delete_btn.winfo_reqheight()) // 2
            delete_btn.place(x=x, y=y)
        
        def on_leave(event=None):
            mouse_x = row.winfo_pointerx() - row.winfo_rootx()
            mouse_y = row.winfo_pointery() - row.winfo_rooty()
            if not (0 <= mouse_x <= row.winfo_width() and 0 <= mouse_y <= row.winfo_height()):
                delete_btn.place_forget()
        
        # Bind hover events
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        delete_btn.bind("<Enter>", on_enter)
        delete_btn.bind("<Leave>", on_leave)
        
        # Bind to configure event to handle resizing
        row.bind("<Configure>", on_enter)
        
        return row
    
    def _handle_folder_click(self, folder_id: int):
        """Handle folder click and update highlighting"""
        # If clicking the currently selected folder, exit it
        if self.current_folder_id == folder_id:
            self._handle_back_click()
            return
        
        self.current_folder_id = folder_id
        self.current_chat_id = None  # Clear chat selection when selecting folder
        
        # Update folder button colors and emojis
        for btn in getattr(self, '_folder_buttons', []):
            if btn.winfo_exists():
                is_selected = btn._folder_id == folder_id
                btn.configure(
                    text_color="white" if is_selected else "gray",
                    text=f"{'📂' if is_selected else '📁'} {btn.cget('text').split(' ', 1)[1]}"
                )
        
        # Reset chat button colors
        for btn in getattr(self, '_chat_buttons', []):
            if btn.winfo_exists():
                btn.configure(text_color="gray")
        
        # Update UI for folder contents
        contents = self.db.get_folder_contents(folder_id)
        folder_name = None
        
        # Find the folder name
        for folder in self.db.get_folder_contents(None)['folders']:
            if folder['id'] == folder_id:
                folder_name = folder['name']
                break
        
        # Update UI
        if folder_name:
            # Update header text and buttons
            self.chats_label.configure(text=f"📂 {folder_name}")
            self.new_chat_btn.configure(text=f"+ 💬 in {folder_name}")
            
            # Change folder action button to exit
            self.folder_action_btn.configure(
                text="← Exit Folder",
                command=self._handle_back_click
            )
        
        # Clear and update recent list
        for widget in self.recent_list.winfo_children():
            widget.destroy()
        
        # Show chats in this folder
        for chat in contents['chats']:
            self.add_chat_item(chat)
    
    def add_chat_item(self, chat: Dict):
        """Add a chat item to the list"""
        # Create container frame
        container = ctk.CTkFrame(self.recent_list, fg_color="transparent")
        container.pack(fill="x", pady=2)
        
        # Create button with chat title - add 💬 emoji before title
        chat_btn = ctk.CTkButton(
            container,
            text=f"💬 {chat['title']}",
            anchor="w",
            fg_color="transparent",
            text_color="white" if chat["id"] == self.current_chat_id else "gray",
            hover_color="#333333",
            command=lambda: self._handle_chat_click(chat["id"])
        )
        chat_btn._chat_id = chat["id"]  # Store chat ID
        chat_btn.pack(side="left", fill="x", expand=True)
        
        # Add double-click binding for rename
        chat_btn.bind("<Double-Button-1>", lambda e, cid=chat["id"]: self._start_rename(e, cid, chat_btn))
        
        # Create delete button with transparent background
        delete_btn = ctk.CTkButton(
            container,
            text="🗑",
            width=30,
            fg_color="transparent",
            hover_color="#333333",
            text_color="gray",
            command=lambda: self.delete_chat(chat["id"])
        )
        delete_btn.pack(side="right")
        
        # Store reference to chat button
        if not hasattr(self, '_chat_buttons'):
            self._chat_buttons = []
        self._chat_buttons.append(chat_btn)
    
    def _show_chat_menu(self, event, chat_id: int):
        """Show chat context menu"""
        self.current_chat_id = chat_id
        self.chat_menu.tk_popup(event.x_root, event.y_root)
    
    def _show_folder_menu(self, event, folder_id: int):
        """Show folder context menu"""
        self.current_folder_id = folder_id
        self.folder_menu.tk_popup(event.x_root, event.y_root)
    
    def _delete_chat_by_id(self):
        """Delete the currently selected chat"""
        if self.current_chat_id is not None:
            self.delete_chat(self.current_chat_id)
            self.current_chat_id = None
    
    def _rename_chat_by_id(self):
        """Rename the currently selected chat"""
        if self.current_chat_id is not None:
            self._rename_chat(self.current_chat_id)
            self.current_chat_id = None
    
    def _delete_folder_by_id(self):
        """Delete the currently selected folder"""
        if self.current_folder_id is not None:
            self._delete_folder(self.current_folder_id)
            self.current_folder_id = None
    
    def _rename_folder_by_id(self):
        """Rename the currently selected folder"""
        if self.current_folder_id is not None:
            self._rename_folder(self.current_folder_id)
            self.current_folder_id = None
    
    def create_folder(self):
        """Create a new folder"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("New Folder")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Make dialog appear on top and centered
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center the dialog
        main_window = self.winfo_toplevel()
        x = main_window.winfo_x() + (main_window.winfo_width() - 300) // 2
        y = main_window.winfo_y() + (main_window.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Add label
        label = ctk.CTkLabel(dialog, text="Enter folder name:")
        label.pack(pady=10)
        
        # Add entry
        entry = ctk.CTkEntry(dialog)
        entry.pack(padx=20, pady=10, fill="x")
        entry.focus()
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def save_folder():
            name = entry.get().strip()
            if name:
                try:
                    folder_id = self.db.create_folder(name)
                    self.load_contents()
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create folder: {str(e)}")
        
        # OK button (black)
        ok_btn = ctk.CTkButton(
            btn_frame,
            text="OK",
            fg_color="#000000",
            hover_color="#2b2b2b",
            command=save_folder
        )
        ok_btn.pack(fill="x", pady=5)
        
        # Cancel button (red)
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="#ff4444",
            hover_color="#ff6666",
            command=dialog.destroy
        )
        cancel_btn.pack(fill="x", pady=5)
        
        # Bind enter key to save
        entry.bind("<Return>", lambda e: save_folder())
        
        # Bind escape key to cancel
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def delete_chat(self, chat_id: int):
        """Delete a chat"""
        # Don't automatically create new chat
        current_folder = self.current_folder_id
        
        # If deleting current chat, clear it first
        if chat_id == self.current_chat_id:
            self.current_chat_id = None
        
        # Delete from database
        self.db.delete_chat(chat_id)
        
        # Refresh sidebar
        self.load_contents()
        
        # Only create new chat if we deleted the current one
        if chat_id == self.current_chat_id:
            self.on_new_chat(current_folder)

    def toggle_folder(self, folder_id: int):
        """Placeholder for expanding/collapsing folder items if desired."""
        # For now, do nothing or implement your desired expand/collapse logic here.
        pass
    
    def _handle_new_chat(self):
        """Handle new chat button click"""
        # Save current chat before creating new one
        if self.current_chat_id is not None:
            self.parent.save_current_chat()
        
        # Clear current chat ID
        self.current_chat_id = None
        
        # Reset all chat button colors to gray
        for btn in getattr(self, '_chat_buttons', []):
            if btn.winfo_exists():
                btn.configure(text_color="gray")
        
        # Create new chat
        self.on_new_chat(self.current_folder_id)

    def _delete_folder(self, folder_id: int):
        """Delete a folder after confirmation"""
        if messagebox.askyesno("Confirm Delete", "Delete this folder and all its contents?"):
            try:
                self.db.delete_folder(folder_id)
                self.load_contents()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete folder: {str(e)}")

    def _rename_folder(self, folder_id: int):
        """Rename a folder"""
        dialog = ctk.CTkInputDialog(
            text="Enter new folder name:",
            title="Rename Folder"
        )
        new_name = dialog.get_input()
        if new_name:
            try:
                self.db.rename_folder(folder_id, new_name)
                self.load_contents()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename folder: {str(e)}")

    def _rename_chat(self, chat_id: int):
        """Rename a chat"""
        dialog = ctk.CTkInputDialog(
            text="Enter new chat name:",
            title="Rename Chat"
        )
        new_name = dialog.get_input()
        if new_name:
            self.db.rename_chat(chat_id, new_name)
            self.load_contents() 

    def _confirm_folder_delete(self, folder_id: int):
        """Show folder deletion confirmation dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Delete Folder")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        # Make dialog appear on top
        dialog.transient(self.winfo_toplevel())  # Set main window as parent
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog relative to the main window
        main_window = self.winfo_toplevel()
        x = main_window.winfo_x() + (main_window.winfo_width() - 300) // 2
        y = main_window.winfo_y() + (main_window.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Message
        msg = ctk.CTkLabel(
            dialog,
            text="Delete folder and...",
            font=("Helvetica", 12, "bold")
        )
        msg.pack(pady=10)
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        # Delete everything
        def delete_everything():
            self.db.delete_folder(folder_id)  # This deletes folder and all chats
            self.load_contents()
            dialog.destroy()
        
        everything_btn = ctk.CTkButton(
            btn_frame,
            text="DELETE EVERYTHING",
            fg_color="#ff4444",
            hover_color="#ff6666",
            command=delete_everything
        )
        everything_btn.pack(fill="x", pady=5)
        
        # Keep chats
        def delete_folder_keep_chats():
            self.db.move_folder_chats_to_root(folder_id)
            self.db.delete_folder(folder_id)
            self.load_contents()
            dialog.destroy()
        
        keep_chats_btn = ctk.CTkButton(
            btn_frame,
            text="Delete Folder, Keep Chats",
            fg_color="#000000",
            hover_color="#2b2b2b",
            command=delete_folder_keep_chats
        )
        keep_chats_btn.pack(fill="x", pady=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="transparent",
            hover_color="#2b2b2b",
            command=dialog.destroy
        )
        cancel_btn.pack(fill="x", pady=5) 

    def _start_rename(self, event, item_id: int, button: ctk.CTkButton):
        """Start inline rename on double-click"""
        # Get current name without icon
        current_name = button.cget("text").replace("📁 ", "").replace("💬 ", "")
        
        # Create entry widget with dimensions
        entry = ctk.CTkEntry(
            button.master,
            width=button.winfo_width() - 30,
            height=25,
            fg_color="#2b2b2b",
            border_color="#404040"
        )
        entry.insert(0, current_name)
        entry.select_range(0, 'end')
        
        # Position entry over the button
        x_offset = 20 if "📁" in button.cget("text") else 25  # Same offset for both emojis
        entry.place(
            x=button.winfo_x() + x_offset,
            y=button.winfo_y() + 5,
            anchor="nw"
        )
        entry.focus_set()
        
        def finish_rename(event=None):
            new_name = entry.get().strip()
            if new_name and new_name != current_name:
                if "📁" in button.cget("text"):  # It's a folder
                    self.db.rename_folder(item_id, new_name)
                    button.configure(text=f"📁 {new_name}")
                else:  # It's a chat
                    self.db.rename_chat(item_id, new_name)
                    button.configure(text=f"💬 {new_name}")
                self.load_contents()  # Refresh to ensure everything is updated
            entry.destroy()
        
        def cancel_rename(event=None):
            entry.destroy()
        
        # Bind events
        entry.bind("<Return>", finish_rename)
        entry.bind("<Escape>", cancel_rename)
        entry.bind("<FocusOut>", finish_rename) 

    def _handle_back_click(self):
        """Handle back button click"""
        # Reset folder button colors and emojis
        for btn in getattr(self, '_folder_buttons', []):
            if btn.winfo_exists():
                btn.configure(
                    text_color="gray",
                    text=f"📁 {btn.cget('text').split(' ', 1)[1]}"  # Reset to closed folder
                )
        
        self.current_folder_id = None
        
        # Reset labels and buttons - restore quick chats label with chat bubble
        self.chats_label.configure(text="💬 Quick Chats")
        self.new_chat_btn.configure(text="+ New Chat")
        
        # Reset folder action button
        self.folder_action_btn.configure(
            text="+ New Folder",
            command=self.create_folder
        )
        
        self.load_contents()

    def _handle_chat_click(self, chat_id: int):
        """Handle chat selection and update highlighting"""
        # Don't process clicks if parent is processing
        if self.parent.is_processing:
            return
        
        # Update current chat ID first
        self.current_chat_id = chat_id
        
        # Update highlighting immediately
        for btn in getattr(self, '_chat_buttons', []):
            if btn.winfo_exists():
                is_current = btn._chat_id == chat_id
                btn.configure(text_color="white" if is_current else "gray")
        
        # Keep folder highlighted if we're in one
        if self.current_folder_id is not None:
            for btn in getattr(self, '_folder_buttons', []):
                if btn.winfo_exists():
                    if btn._folder_id == self.current_folder_id:
                        btn.configure(text_color="white")
        
        # If clicking the same chat, just update highlighting
        if self.parent.current_chat_id == chat_id:
            return
        
        # Only save and load if actually switching chats
        try:
            if self.parent.current_chat_id is not None:
                self.parent.save_current_chat()
            
            self.on_chat_selected(chat_id)
            
        except Exception as e:
            print(f"Error handling chat click: {e}")
            messagebox.showerror("Error", f"Failed to switch chats: {str(e)}")

    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states"""
        if self.is_expanded:
            # Collapse
            self.configure(width=self.collapsed_width)
            self.collapse_btn.configure(text="☰")
            
            # Hide all widgets except collapse button
            for widget in self.winfo_children():
                if widget != self.control_frame:
                    widget.pack_forget()
            
            # In control frame, hide settings button and keep only collapse button
            self.settings_btn.pack_forget()
            
            # Keep collapse button visible
            self.collapse_btn.pack(side="left", padx=5)
            
        else:
            # Expand
            self.configure(width=self.expanded_width)
            self.collapse_btn.configure(text="☰")
            
            # Restore all widgets in correct order
            self.control_frame.pack(fill="x", padx=5, pady=(5, 0))
            self.collapse_btn.pack(side="left")
            self.settings_btn.pack(side="right")
            
            # Restore folder section
            self.folder_header.pack(fill="x", padx=5, pady=(5,0))
            self.folder_tree.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Restore chats section
            self.chats_header.pack(fill="x", padx=5, pady=(5,0))
            self.recent_list.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Refresh contents
            self.load_contents()
        
        self.is_expanded = not self.is_expanded
        self._force_width = True

    def toggle_folder_section(self):
        """Toggle folder section visibility"""
        if self.folder_section.winfo_ismapped():
            self.folder_section.pack_forget()
            self.folder_dropdown.configure(text="▶")
        else:
            self.folder_section.pack(fill="both", expand=True, padx=5, pady=5)
            self.folder_dropdown.configure(text="▼")

    def toggle_recent_section(self):
        """Toggle recent chats section visibility"""
        if self.recent_section.winfo_ismapped():
            self.recent_section.pack_forget()
            self.recent_dropdown.configure(text="▶")
        else:
            self.recent_section.pack(fill="both", expand=True, padx=5, pady=5)
            self.recent_dropdown.configure(text="▼") 

    def save_current_chat(self):
        """Save the current chat"""
        if len(self.api.conversation_history) <= 1:  # Only system message
            return
        
        # Use "New Chat" as default title
        title = "New Chat"
        
        if self.current_chat_id is None:
            # Create new chat
            self.current_chat_id = self.memory_db.save_chat(
                title=title,
                messages=self.api.conversation_history,
                model_name=self.api.model
            )
        else:
            # Update existing chat
            self.memory_db.update_chat(
                chat_id=self.current_chat_id,
                messages=self.api.conversation_history
            )
        
        # Refresh sidebar
        self.sidebar.load_contents() 

    def _add_folder_item(self, folder, parent_frame, level=0):
        """Add a folder item to the tree"""
        # Create container frame with transparent background
        container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        container.pack(fill="x", pady=2)
        
        # Create folder button
        folder_btn = ctk.CTkButton(
            container,
            text=f"📁 {folder['name']}",
            anchor="w",
            fg_color="transparent",
            text_color="gray",
            hover_color="transparent",
            command=lambda: self._handle_folder_click(folder['id'])
        )
        folder_btn._folder_id = folder['id']  # Store folder ID
        folder_btn.pack(side="left", fill="x", expand=True, padx=(20 * level, 0))
        
        # Create delete button with transparent background
        delete_btn = ctk.CTkButton(
            container,
            text="🗑",
            width=30,
            fg_color="transparent",
            hover_color="#333333",
            text_color="gray",
            command=lambda: self._delete_folder(folder['id'])
        )
        delete_btn.pack(side="right")
        
        # Store reference to folder button
        if not hasattr(self, '_folder_buttons'):
            self._folder_buttons = []
        self._folder_buttons.append(folder_btn) 

    def disable_interaction(self):
        """Disable all interactive elements during AI processing"""
        def disable_buttons_recursive(container):
            # Disable all buttons in this container
            for child in container.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(state="disabled")
                elif isinstance(child, ctk.CTkFrame):
                    # Recursively disable buttons in nested frames
                    disable_buttons_recursive(child)
        
        # Disable all chat buttons in recent list
        disable_buttons_recursive(self.recent_list)
        
        # Disable all folder buttons in folder tree
        disable_buttons_recursive(self.folder_tree)
        
        # Disable action buttons
        self.folder_action_btn.configure(state="disabled")
        self.new_chat_btn.configure(state="disabled")
        self.collapse_btn.configure(state="disabled")
        self.settings_btn.configure(state="disabled")

    def enable_interaction(self):
        """Re-enable all interactive elements after AI processing"""
        def enable_buttons_recursive(container):
            # Enable all buttons in this container
            for child in container.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(state="normal")
                elif isinstance(child, ctk.CTkFrame):
                    # Recursively enable buttons in nested frames
                    enable_buttons_recursive(child)
        
        # Enable all chat buttons in recent list
        enable_buttons_recursive(self.recent_list)
        
        # Enable all folder buttons in folder tree
        enable_buttons_recursive(self.folder_tree)
        
        # Enable action buttons
        self.folder_action_btn.configure(state="normal")
        self.new_chat_btn.configure(state="normal")
        self.collapse_btn.configure(state="normal")
        self.settings_btn.configure(state="normal") 