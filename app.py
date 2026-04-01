import sqlite3


def migrate():
    # Connect to the SQLite database
    conn = sqlite3.connect('news_db.sqlite')
    cursor = conn.cursor()

    # Add 'email' and 'profile' columns to 'users' table if they don't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        print("Column 'email' already exists in 'users' table.")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN profile TEXT")
    except sqlite3.OperationalError:
        print("Column 'profile' already exists in 'users' table.")

    # Add 'is_published' column to 'articles' table if it doesn't exist
    # Renaming column is not possible with ALTER TABLE ALTER COLUMN
    # instead, we just add the correct column that is needed
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN is_published INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        print("Column 'is_published' already exists in 'articles' table.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


if __name__ == '__main__':
    migrate()
