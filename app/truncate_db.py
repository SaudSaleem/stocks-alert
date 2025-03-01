import sqlite3
from app.database import SQLALCHEMY_DATABASE_URL

# Extract the database path from the URL
db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")

def truncate_tables():
    print(f"Truncating tables in database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Delete data from each table
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # Skip SQLite internal tables
                cursor.execute(f"DELETE FROM {table_name}")
                print(f"Truncated table: {table_name}")
        
        # Check if sqlite_sequence exists before trying to delete from it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
        if cursor.fetchone():  # If sqlite_sequence exists
            cursor.execute("DELETE FROM sqlite_sequence")

        # Re-enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        print("All tables truncated successfully")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error truncating tables: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    truncate_tables()
