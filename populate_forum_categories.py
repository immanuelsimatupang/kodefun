import sqlite3
import os

DATABASE_PATH = 'kodefun.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file '{DATABASE_PATH}' not found. Please run app.py or update_schema.py first.")
        return None
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON") # Ensure foreign key constraints are active
    return conn

def populate_categories(conn):
    """Populates the ForumCategories table with sample categories."""
    cursor = conn.cursor()
    
    categories_data = [
        ("General Discussion", "Talk about anything related to coding, learning, or KodeFun!"),
        ("JavaScript Track Help", "Get help and discuss topics related to the JavaScript Mastery Track."),
        ("PHP Track Help", "Get help and discuss topics related to the PHP Mastery Track."),
        ("Web Development Stack Q&A", "Ask questions and share insights about the Web Development Stack track."),
        ("Project Show-off", "Share your completed projects and get feedback from the community.")
    ]
    
    print("\n--- Populating ForumCategories ---")
    for name, description in categories_data:
        try:
            cursor.execute("SELECT category_id FROM ForumCategories WHERE name = ?", (name,))
            existing_category = cursor.fetchone()
            if existing_category:
                print(f"Category '{name}' already exists (ID: {existing_category['category_id']}). Skipping.")
            else:
                cursor.execute("INSERT INTO ForumCategories (name, description) VALUES (?, ?)", (name, description))
                category_id = cursor.lastrowid
                print(f"Inserted Category: '{name}' (ID: {category_id})")
        except sqlite3.IntegrityError: # Should be caught by the check above, but as a safeguard
            print(f"Category '{name}' likely already exists (IntegrityError). Skipping.")
        except sqlite3.Error as e:
            print(f"SQLite error while inserting category '{name}': {e}")
            conn.rollback() # Rollback on error for this specific item
    
    conn.commit()
    print("\n--- Finished populating ForumCategories ---")

def main():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        # First, ensure the table exists by trying to create it (idempotently)
        # This step is ideally handled by update_schema.py, but as a safeguard:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ForumCategories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) UNIQUE NOT NULL,
            description TEXT
        );""")
        conn.commit()

        populate_categories(conn)
        print("\nForum categories population script completed successfully.")
    except Exception as e:
        print(f"An error occurred during forum categories population: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    main()
