import sqlite3
import os
import json

DATABASE_PATH = 'kodefun.db'

def get_db_connection():
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file '{DATABASE_PATH}' not found.")
        return None
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def ensure_practice_assessment_and_get_id(conn, course_name_filter, assessment_type, weight, description):
    """Ensures an assessment of a specific type and weight exists for a course, then returns its ID."""
    cursor = conn.cursor()
    
    cursor.execute("SELECT course_id FROM Courses WHERE course_name LIKE ?", (f'%{course_name_filter}%',))
    course_row = cursor.fetchone()
    if not course_row:
        print(f"Error: Course matching '{course_name_filter}' not found. Cannot create '{assessment_type}' assessment.")
        return None
    course_id = course_row['course_id']
    print(f"Found Course ID {course_id} for '{course_name_filter}'.")

    cursor.execute("""
        SELECT assessment_id FROM Assessments 
        WHERE course_id = ? AND assessment_type = ? AND weight_percentage = ? AND description = ?
    """, (course_id, assessment_type, weight, description))
    assessment_row = cursor.fetchone()

    if assessment_row:
        assessment_id = assessment_row['assessment_id']
        print(f"'{assessment_type}' Assessment '{description}' (ID: {assessment_id}) already exists for Course ID {course_id}.")
        return assessment_id
    else:
        try:
            cursor.execute("""
                INSERT INTO Assessments (course_id, assessment_type, description, weight_percentage) 
                VALUES (?, ?, ?, ?)
            """, (course_id, assessment_type, description, weight))
            assessment_id = cursor.lastrowid
            conn.commit()
            print(f"Created '{assessment_type}' Assessment '{description}' (ID: {assessment_id}) for Course ID {course_id}.")
            return assessment_id
        except sqlite3.Error as e:
            print(f"Error creating '{assessment_type}' assessment '{description}' for Course ID {course_id}: {e}")
            conn.rollback()
            return None

def populate_coding_exercises(conn, assessment_id):
    """Populates CodingExercises and CodingExerciseTestCases for a given assessment_id."""
    cursor = conn.cursor()

    exercises_data = [
        {
            "title": "Add Two Numbers",
            "description": "Write a function called 'add' that takes two numbers (a, b) and returns their sum.",
            "starter_code": "function add(a, b) {\n  // Your code here\n  return 0; \n}",
            "function_name": "add",
            "test_cases": [
                {"input_data": '[2, 3]', "expected_output": '5', "description": "Positive numbers"},
                {"input_data": '[-1, 1]', "expected_output": '0', "description": "Negative and positive"},
                {"input_data": '[0, 0]', "expected_output": '0', "description": "Zeroes"}
            ]
        },
        {
            "title": "Reverse String",
            "description": "Write a function called 'reverse' that takes a string and returns the reversed string.",
            "starter_code": "function reverse(str) {\n  // Your code here\n  return '';\n}",
            "function_name": "reverse",
            "test_cases": [
                {"input_data": '["hello"]', "expected_output": '"olleh"', "description": "Simple string"},
                {"input_data": '[""]', "expected_output": '""', "description": "Empty string"},
                {"input_data": '["JavaScript"]', "expected_output": '"tpircSavaJ"', "description": "Longer string"}
            ]
        }
    ]

    print(f"\n--- Populating Coding Exercises for Assessment ID: {assessment_id} ---")
    for ex_data in exercises_data:
        cursor.execute("SELECT exercise_id FROM CodingExercises WHERE assessment_id = ? AND title = ?", (assessment_id, ex_data["title"]))
        exercise_row = cursor.fetchone()
        
        exercise_id = None
        if exercise_row:
            exercise_id = exercise_row['exercise_id']
            print(f"Exercise '{ex_data['title']}' already exists (ID: {exercise_id}). Verifying test cases...")
        else:
            try:
                cursor.execute("""
                    INSERT INTO CodingExercises (assessment_id, title, description, starter_code, function_name) 
                    VALUES (?, ?, ?, ?, ?)
                """, (assessment_id, ex_data["title"], ex_data["description"], ex_data["starter_code"], ex_data["function_name"]))
                exercise_id = cursor.lastrowid
                print(f"Inserted Exercise (ID: {exercise_id}): '{ex_data['title']}'")
            except sqlite3.Error as e:
                print(f"Error inserting exercise '{ex_data['title']}': {e}")
                conn.rollback()
                continue

        if exercise_id:
            for tc_data in ex_data["test_cases"]:
                # Check if test case already exists (e.g. by input_data and expected_output for simplicity)
                cursor.execute("""
                    SELECT test_case_id FROM CodingExerciseTestCases 
                    WHERE exercise_id = ? AND input_data = ? AND expected_output = ?
                """, (exercise_id, tc_data["input_data"], tc_data["expected_output"]))
                tc_row = cursor.fetchone()

                if tc_row:
                    # print(f"  Test Case for input '{tc_data['input_data']}' already exists. Skipping.")
                    pass
                else:
                    try:
                        cursor.execute("""
                            INSERT INTO CodingExerciseTestCases (exercise_id, input_data, expected_output, description) 
                            VALUES (?, ?, ?, ?)
                        """, (exercise_id, tc_data["input_data"], tc_data["expected_output"], tc_data.get("description")))
                        # print(f"  Inserted Test Case for Exercise ID {exercise_id}: Input '{tc_data['input_data']}' -> Expected '{tc_data['expected_output']}'")
                    except sqlite3.Error as e:
                        print(f"  Error inserting test case for input '{tc_data['input_data']}': {e}")
                        conn.rollback()
            conn.commit()

def main():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        js_level1_course_name_filter = "LEVEL 1: JavaScript Fundamentals"
        # Ensure a "Practice" assessment exists, e.g. "JS Variables Practice"
        practice_assessment_id = ensure_practice_assessment_and_get_id(conn, js_level1_course_name_filter, 
                                                                       "Practice", 40, "JS Fundamentals Practice Exercises")

        if practice_assessment_id:
            populate_coding_exercises(conn, practice_assessment_id)
            print("\nCoding exercise data population script completed.")
        else:
            print("\nCoding exercise data population script could not proceed without a valid Practice Assessment ID.")

    except Exception as e:
        print(f"An error occurred during script execution: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    main()
