import sqlite3
import os

DATABASE_PATH = 'kodefun.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    if not os.path.exists(DATABASE_PATH):
        print(f"DB_VERIFIER_ERROR: Database file '{DATABASE_PATH}' not found.")
        return None
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_user_exists(username=None, email=None):
    """Checks if a user exists by username or email and returns the user row if found."""
    conn = get_db_connection()
    if not conn:
        return None
    
    user = None
    try:
        cursor = conn.cursor()
        if username:
            cursor.execute("SELECT user_id, username, email, password_hash, xp_points FROM Users WHERE username = ?", (username,))
        elif email:
            cursor.execute("SELECT user_id, username, email, password_hash, xp_points FROM Users WHERE email = ?", (email,))
        user = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"DB_VERIFIER_ERROR: SQLite error while checking user: {e}")
        return None # Indicate error
    finally:
        if conn:
            conn.close()
    return user

def get_user_id(username):
    user = check_user_exists(username=username)
    if user:
        return user['user_id']
    return None

if __name__ == '__main__':
    # Example usage (for direct testing of this script, not part of automated tests)
    print("--- Direct DB Verifier Tests ---")
    # Test Case 1: Check a non-existent user
    print("Checking non_existent_user:", check_user_exists(username='non_existent_user'))
    
    # To test further, you would need app.py to have run and created users.
    # For example, if 'testuser1' was created:
    # test_user = check_user_exists(username='testuser1')
    # if test_user:
    #     print("Found testuser1:", dict(test_user))
    #     print("Password hash for testuser1:", test_user['password_hash'])
    #     print("User ID for testuser1:", get_user_id('testuser1'))
    # else:
    #     print("testuser1 not found (expected if not created yet).")
    print("--- End Direct DB Verifier Tests ---")
