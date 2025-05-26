import sqlite3
import os

DATABASE_PATH = 'kodefun.db'

def get_db_connection():
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file '{DATABASE_PATH}' not found.")
        return None
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def ensure_assessment(conn, course_id, assessment_type, weight, description):
    """Ensures an assessment of a specific type, weight, and description exists for a course."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT assessment_id FROM Assessments 
        WHERE course_id = ? AND assessment_type = ? AND weight_percentage = ? AND description = ?
    """, (course_id, assessment_type, weight, description))
    assessment_row = cursor.fetchone()

    if assessment_row:
        assessment_id = assessment_row['assessment_id']
        print(f"Assessment '{description}' (Type: {assessment_type}, Weight: {weight}%, ID: {assessment_id}) already exists for Course ID {course_id}.")
        return assessment_id
    else:
        try:
            cursor.execute("""
                INSERT INTO Assessments (course_id, assessment_type, description, weight_percentage) 
                VALUES (?, ?, ?, ?)
            """, (course_id, assessment_type, description, weight))
            assessment_id = cursor.lastrowid
            conn.commit()
            print(f"CREATED Assessment '{description}' (Type: {assessment_type}, Weight: {weight}%, ID: {assessment_id}) for Course ID {course_id}.")
            return assessment_id
        except sqlite3.Error as e:
            print(f"Error creating assessment '{description}' for Course ID {course_id}: {e}")
            conn.rollback()
            return None

def main():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        # Get course_id for "LEVEL 1: JavaScript Fundamentals"
        cursor.execute("SELECT course_id FROM Courses WHERE course_name LIKE '%LEVEL 1: JavaScript Fundamentals%'")
        course_row = cursor.fetchone()
        
        if not course_row:
            print(f"Error: Course 'LEVEL 1: JavaScript Fundamentals' not found. Cannot ensure assessments.")
            return
        
        js_level1_course_id = course_row['course_id']
        print(f"Found Course 'LEVEL 1: JavaScript Fundamentals' with ID: {js_level1_course_id}.")
        print("\n--- Ensuring Assessments for LEVEL 1: JavaScript Fundamentals ---")

        # 1. Theory Assessment (should have been created by populate_quiz_data.py)
        ensure_assessment(conn, js_level1_course_id, "Theory", 20, "Theory Quiz")
        
        # 2. Practice Assessment (should have been created by populate_coding_exercise_data.py)
        ensure_assessment(conn, js_level1_course_id, "Practice", 40, "JS Fundamentals Practice Exercises")
        
        # 3. Project Assessment
        ensure_assessment(conn, js_level1_course_id, "Project", 25, "Mini Challenge: Interactive calculator")
        
        # 4. Live Coding Assessment
        ensure_assessment(conn, js_level1_course_id, "Live Coding", 15, "Live Coding (15 min): Form validation script")

        print("\n--- Assessment verification/creation process completed. ---")

    except Exception as e:
        print(f"An error occurred during script execution: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    main()
