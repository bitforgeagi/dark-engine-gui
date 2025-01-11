import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json

class ChatMemoryDB:
    def __init__(self):
        self.db_path = Path.home() / ".ollama_chat" / "memories.db"
        print(f"Database path: {self.db_path}")  # Debug print
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database with proper prompt engineering support"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parent_id INTEGER NULL,
                    FOREIGN KEY (parent_id) REFERENCES folders (id)
                )
            """)
            
            # Add timestamp column to messages JSON structure
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    folder_id INTEGER NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT NOT NULL,
                    messages TEXT NOT NULL,  -- Each message will include a timestamp field
                    FOREIGN KEY (folder_id) REFERENCES folders (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    template TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    effectiveness_score FLOAT DEFAULT 0.0  -- Track which templates work best
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS personality_modifiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personality TEXT NOT NULL,
                    effect TEXT NOT NULL,
                    context TEXT,  -- Store when this modifier works best
                    usage_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS writing_styles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    style TEXT NOT NULL,
                    impact TEXT NOT NULL,
                    best_use_cases TEXT,  -- JSON array of scenarios where this style shines
                    performance_metrics TEXT  -- JSON object of effectiveness metrics
                )
            """)
        print("Database initialized")  # Debug print
    
    def create_folder(self, name: str, parent_id: Optional[int] = None) -> int:
        """Create a new folder and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO folders (name, parent_id) VALUES (?, ?)",
                (name, parent_id)
            )
            return cursor.lastrowid
    
    def save_chat(self, title: str, messages: List[Dict], model_name: str, folder_id: Optional[int] = None) -> int:
        """Save a new chat and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """INSERT INTO chats (title, messages, model_name, folder_id) 
                   VALUES (?, ?, ?, ?)""",
                (title, json.dumps(messages), model_name, folder_id)
            )
            return cursor.lastrowid
    
    def get_chat(self, chat_id: int) -> Optional[Dict]:
        """Retrieve a chat by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row["id"],
                        "title": row["title"],
                        "folder_id": row["folder_id"],
                        "created_at": row["created_at"],
                        "last_updated": row["last_updated"],
                        "model_name": row["model_name"],
                        "messages": json.loads(row["messages"])
                    }
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise Exception(f"Failed to retrieve chat: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            raise Exception(f"Failed to parse chat messages: {str(e)}")
        except Exception as e:
            print(f"Error retrieving chat: {e}")
            raise
        return None
    
    def get_folder_contents(self, folder_id: Optional[int] = None) -> Dict:
        """Get contents of a folder"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get subfolders
            cursor = conn.execute(
                "SELECT * FROM folders WHERE parent_id IS ? ORDER BY name",
                (folder_id,)
            )
            folders = [dict(row) for row in cursor.fetchall()]
            
            # Get chats in this folder
            cursor = conn.execute(
                "SELECT * FROM chats WHERE folder_id IS ? ORDER BY created_at DESC",
                (folder_id,)
            )
            chats = []
            for row in cursor.fetchall():
                chat_dict = dict(row)
                chat_dict['messages'] = json.loads(chat_dict['messages'])
                chats.append(chat_dict)
            
            return {
                "folders": folders,
                "chats": chats
            }
    
    def rename_folder(self, folder_id: int, new_name: str):
        """Rename a folder"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE folders SET name = ? WHERE id = ?",
                (new_name, folder_id)
            )
    
    def rename_chat(self, chat_id: int, new_title: str):
        """Rename a chat"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE chats SET title = ? WHERE id = ?",
                (new_title, chat_id)
            )
    
    def move_chat(self, chat_id: int, new_folder_id: Optional[int]):
        """Move a chat to a different folder"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE chats SET folder_id = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?",
                (new_folder_id, chat_id)
            )
    
    def delete_chat(self, chat_id: int):
        """Delete a chat by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    
    def delete_folder(self, folder_id: int):
        """Delete a folder and all its contents"""
        with sqlite3.connect(self.db_path) as conn:
            # First move all chats to root level
            conn.execute(
                "UPDATE chats SET folder_id = NULL WHERE folder_id = ?",
                (folder_id,)
            )
            # Then delete the folder
            conn.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
    
    def debug_print_contents(self):
        """Print all database contents for debugging"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            print("\n=== Database Contents ===")
            
            # Print folders
            cursor = conn.execute("SELECT * FROM folders")
            folders = cursor.fetchall()
            print(f"\nFolders ({len(folders)}):")
            for folder in folders:
                print(f"  - {dict(folder)}")
            
            # Print chats
            cursor = conn.execute("SELECT id, title, folder_id, created_at FROM chats")
            chats = cursor.fetchall()
            print(f"\nChats ({len(chats)}):")
            for chat in chats:
                print(f"  - {dict(chat)}")
            
            print("\n=====================") 
    
    def update_chat(self, chat_id: int, messages: List[Dict]):
        """Update an existing chat's messages"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE chats 
                   SET messages = ?, last_updated = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (json.dumps(messages), chat_id)
            ) 
    
    def debug_print_folders(self):
        """Print all folders for debugging"""
        print("\n=== All Folders ===")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM folders")
            folders = cursor.fetchall()
            for folder in folders:
                print(f"Folder: {dict(folder)}")
        print("=== End Folders ===\n") 
    
    def move_folder_chats_to_root(self, folder_id: int):
        """Move all chats in a folder to root level"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE chats SET folder_id = NULL WHERE folder_id = ?",
                    (folder_id,)
                )
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise Exception(f"Failed to move chats: {str(e)}") 
    
    def get_recent_chats(self, limit: int = 10) -> list:
        """Get most recent chats"""
        with sqlite3.connect(self.db_path) as conn:  # Create connection
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, messages, model_name, created_at
                FROM chats
                WHERE folder_id IS NULL
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            chats = []
            for row in cursor.fetchall():
                chats.append({
                    'id': row[0],
                    'title': row[1],
                    'messages': json.loads(row[2]),
                    'model_name': row[3],
                    'created_at': row[4]
                })
            
            return chats 
    
    def save_prompt_template(self, role: str, template: str):
        """Save a prompt template that actually kicks ass"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO prompt_templates (role, template)
                VALUES (?, ?)
                ON CONFLICT(role) DO UPDATE SET 
                    template = excluded.template,
                    last_used = CURRENT_TIMESTAMP
            """, (role, template))
    
    def get_prompt_template(self, role: str) -> Optional[str]:
        """Get a prompt template that's actually worth a damn"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT template FROM prompt_templates WHERE role = ?",
                (role,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    def update_template_effectiveness(self, role: str, score: float):
        """Track which templates are actually doing their fucking job"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE prompt_templates 
                SET effectiveness_score = (effectiveness_score + ?) / 2
                WHERE role = ?
            """, (score, role)) 