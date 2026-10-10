
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "chat_history.db"


def initialize_database():
    """Create tables and safely upgrade the existing database."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT 'New Chat',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

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

        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(messages)"
            ).fetchall()
        }

        if "conversation_id" not in columns:
            connection.execute(
                "ALTER TABLE messages ADD COLUMN conversation_id INTEGER"
            )

        # Keep all existing messages together in one legacy conversation.
        existing_messages = connection.execute(
            """
            SELECT COUNT(*)
            FROM messages
            WHERE conversation_id IS NULL
            """
        ).fetchone()[0]

        if existing_messages:
            conversation_id = connection.execute(
                """
                SELECT id FROM conversations
                WHERE title = 'Previous Chat'
                ORDER BY id
                LIMIT 1
                """
            ).fetchone()

            if conversation_id is None:
                cursor = connection.execute(
                    """
                    INSERT INTO conversations (title)
                    VALUES ('Previous Chat')
                    """
                )
                conversation_id = cursor.lastrowid
            else:
                conversation_id = conversation_id[0]

            connection.execute(
                """
                UPDATE messages
                SET conversation_id = ?
                WHERE conversation_id IS NULL
                """,
                (conversation_id,),
            )


def create_conversation(title="New Chat"):
    """Create a conversation and return its ID."""
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,),
        )
        return cursor.lastrowid


def list_conversations():
    """Return conversations newest first."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            ORDER BY id DESC
            """
        ).fetchall()

    return [
        {"id": row[0], "title": row[1], "created_at": row[2]}
        for row in rows
    ]


def save_message(conversation_id, role, content):
    """Save a message to a specific conversation."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (conversation_id, role, content),
        )


def load_messages(conversation_id):
    """Load messages belonging to one conversation."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (conversation_id,),
        ).fetchall()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]
