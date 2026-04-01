import sqlite3


def migrate(database_file):
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Add missing columns to the 'users' table
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN email TEXT;')
    except sqlite3.OperationalError as e:
        if 'duplicate column name: email' not in str(e):
            raise

    try:
        cursor.execute('ALTER TABLE users ADD COLUMN profile TEXT;')
    except sqlite3.OperationalError as e:
        if 'duplicate column name: profile' not in str(e):
            raise

    # No schema changes needed for the articles table as it's a code change only
    print("Migration completed successfully.")
    conn.commit()
    conn.close()


if __name__ == '__main__':
    migrate('news_db.sqlite')
