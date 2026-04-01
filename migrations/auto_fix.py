import sqlite3
import os

def migrate():
    db_path = os.environ.get('DB_PATH', 'news.db')
    conn = sqlite3.connect(db_path)
    try:
        conn.execute('ALTER TABLE articles ADD COLUMN published_date TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE articles ADD COLUMN author_name TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
