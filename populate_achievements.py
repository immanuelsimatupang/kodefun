import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'kodefun.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file '{DATABASE_PATH}' not found. Please run app.py first to create it.")
        return None
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def populate_achievements_table(conn):
    """Populates the Achievements table with predefined achievements."""
    cursor = conn.cursor()
    
    achievements_data = [
        ("JavaScript Novice", "Complete LEVEL 1 of JavaScript Mastery Track.", "Complete JavaScript Fundamentals course.", 25, "Single Programming"),
        ("PHP Beginner", "Complete LEVEL 1 of PHP Mastery Track.", "Complete PHP Fundamentals course.", 25, "Single Programming"),
        ("Web Dev Starter", "Complete LEVEL 1 of Web Development Stack.", "Complete Frontend - HTML5 Semantics & Accessibility course.", 30, "Multi Programming"),
        ("Five Courses Down!", "Successfully complete any 5 courses.", "Complete 5 courses across any track.", 50, "Universal"),
        ("First Track Completed!", "Complete all courses in any single track.", "Finish all levels of any track.", 200, "Universal"),
        ("JS Functions Pro", "Master JavaScript functions.", "Complete LEVEL 2: Functions & Scope in JavaScript Mastery Track.", 30, "Single Programming"),
        ("DOM Manipulator", "Conquer DOM Manipulation in JavaScript.", "Complete LEVEL 4: DOM Manipulation in JavaScript Mastery Track.", 35, "Single Programming"),
        ("PHP OOP Basics", "Grasp Object-Oriented Programming in PHP.", "Complete LEVEL 3: OOP in PHP (Basic) in PHP Mastery Track.", 30, "Single Programming"),
        ("Full-Stack Foundation", "Complete the foundational backend and frontend courses in Web Dev Stack.", "Complete L3: Frontend - JavaScript DOM & Events AND L6: Backend - MySQL & Full-Stack Integration.", 100, "Multi Programming"),
        ("Halfway There!", "Complete 6 courses in any single 12-course track.", "Complete 6 courses of a single track.", 75, "Universal")
    ]
    
    print("\n--- Populating Achievements ---")
    for name, description, criteria, xp_bonus, ach_type in achievements_data:
        try:
            cursor.execute("SELECT achievement_id FROM Achievements WHERE achievement_name = ?", (name,))
            existing_achievement = cursor.fetchone()
            if existing_achievement:
                print(f"Achievement '{name}' already exists (ID: {existing_achievement['achievement_id']}). Skipping insertion.")
            else:
                cursor.execute("""
                    INSERT INTO Achievements (achievement_name, description, criteria, xp_bonus, achievement_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, description, criteria, xp_bonus, ach_type))
                achievement_id = cursor.lastrowid
                print(f"Inserted Achievement: '{name}' (ID: {achievement_id}, XP: {xp_bonus}, Type: {ach_type})")
        except sqlite3.Error as e:
            print(f"SQLite error while inserting achievement '{name}': {e}")
            conn.rollback() # Rollback on error for this specific item
            # Decide if you want to stop or continue with next items
    conn.commit()
    print("\n--- Finished populating Achievements ---")

def main():
    """Main function to orchestrate the population of the achievements."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        populate_achievements_table(conn)
        print("\nAchievements population script completed successfully.")
    except Exception as e:
        print(f"An error occurred during achievement population: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    main()
