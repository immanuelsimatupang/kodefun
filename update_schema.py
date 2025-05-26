import sqlite3
import os

DATABASE_PATH = 'kodefun.db'
SCHEMA_PATH = 'schema.sql'

def table_exists(cursor, table_name):
    """Checks if a table exists in the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    return cursor.fetchone() is not None

def apply_new_schema_parts(conn):
    """
    Applies only the new parts of the schema (Forum tables) if they don't exist.
    Reads the entire schema.sql but specifically looks for Forum table creations.
    """
    cursor = conn.cursor()
    
    new_tables_schemas = {
        "ForumCategories": """
CREATE TABLE ForumCategories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);""",
        "ForumThreads": """
CREATE TABLE ForumThreads (
    thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES ForumCategories(category_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);""",
        "ForumPosts": """
CREATE TABLE ForumPosts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES ForumThreads(thread_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);"""
    }

    print("--- Checking and Applying New Schema Parts (Forum Tables) ---")
    applied_count = 0
    for table_name, table_sql in new_tables_schemas.items():
        if not table_exists(cursor, table_name):
            try:
                print(f"Creating table '{table_name}'...")
                cursor.executescript(table_sql) # Use executescript for potentially multiple statements or complex definitions
                conn.commit()
                print(f"Table '{table_name}' created successfully.")
                applied_count += 1
            except sqlite3.Error as e:
                print(f"Error creating table '{table_name}': {e}")
                conn.rollback() # Rollback on error for this table
        else:
            print(f"Table '{table_name}' already exists. Skipping.")
            
    if applied_count > 0:
        print(f"\nApplied {applied_count} new table(s) to the schema.")
    else:
        print("\nNo new forum tables needed to be applied. Schema likely up-to-date for forum features.")

def main():
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file '{DATABASE_PATH}' not found. Please run app.py or flask init-db first.")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    try:
        apply_new_schema_parts(conn)
    except Exception as e:
        print(f"An error occurred during schema update: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    main()
