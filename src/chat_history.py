
import sqlite3
from pathlib import Path

# Store the database in the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "chat_history.db"


def initialize_database():
    """Create the messages table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_message(role, content):
    """Save one message to the database."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            (role, content),
        )


def load_messages():
    """Load saved messages in their original order."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            ORDER BY id
            """
        ).fetchall()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]
