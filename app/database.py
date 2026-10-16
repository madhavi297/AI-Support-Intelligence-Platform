"""
Database layer for AI Support Intelligence Platform.
Uses Python's standard library sqlite3 for reliable, zero-overhead persistence.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.config import settings


def get_db_connection() -> sqlite3.Connection:
    """
    Creates and returns a connection to the SQLite database.
    Configures row factory to sqlite3.Row so columns can be accessed by name.
    """
    conn = sqlite3.connect(str(settings.DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initializes the SQLite database tables if they do not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            confidence REAL,
            priority TEXT DEFAULT 'Medium',
            priority_reason TEXT,
            status TEXT DEFAULT 'open',
            suggested_response TEXT,
            citations TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Create index on ticket_code and created_at for fast lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_code ON tickets(ticket_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at)")

    conn.commit()
    conn.close()


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """
    Converts a sqlite3.Row object to a regular Python dictionary,
    automatically decoding JSON strings such as citations.
    """
    data = dict(row)
    if "citations" in data and data["citations"]:
        try:
            data["citations"] = json.loads(data["citations"])
        except Exception:
            data["citations"] = []
    else:
        data["citations"] = []
    return data
