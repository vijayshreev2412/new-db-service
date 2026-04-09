import sqlite3
import os

def migrate():
    db_path = os.environ.get('DB_PATH', 'news.db')
    conn = sqlite3.connect(db_path)
    
    try:
        conn.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError as e:
        print(f'Error adding email column: {e}')

    try:
        conn.execute("ALTER TABLE users ADD COLUMN profile TEXT")
    except sqlite3.OperationalError as e:
        print(f'Error adding profile column: {e}')

    try:
        conn.execute("ALTER TABLE articles ADD COLUMN is_published INTEGER DEFAULT 0")
    except sqlite3.OperationalError as e:
        print(f'Error adding is_published column: {e}')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate()
