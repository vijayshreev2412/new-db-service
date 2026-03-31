"""
Migration: init_schema
Creates the initial database schema with the intentional bugs intact.
Run this to set up a fresh database.
"""
import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "news.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            published INTEGER DEFAULT 0
        )
    """)

    # Intentionally missing email and profile columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL
        )
    """)

    cursor.execute("INSERT OR IGNORE INTO articles (id, title, category) VALUES (1, 'Breaking News', 'politics')")
    cursor.execute("INSERT OR IGNORE INTO articles (id, title, category) VALUES (2, 'Sports Update', 'sports')")

    conn.commit()
    conn.close()
    print("init_schema migration complete.")


if __name__ == "__main__":
    migrate()
