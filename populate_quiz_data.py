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

def ensure_theory_assessment_and_get_id(conn, course_name_filter, assessment_type, weight):
    """Ensures an assessment of a specific type and weight exists for a course, then returns its ID."""
    cursor = conn.cursor()
    
    # Get course_id for "LEVEL 1: JavaScript Fundamentals"
    cursor.execute("SELECT course_id FROM Courses WHERE course_name LIKE ?", (f'%{course_name_filter}%',))
    course_row = cursor.fetchone()
    if not course_row:
        print(f"Error: Course matching '{course_name_filter}' not found. Cannot create Theory assessment.")
        return None
    course_id = course_row['course_id']
    print(f"Found Course ID {course_id} for '{course_name_filter}'.")

    # Check if the specific Theory assessment already exists
    cursor.execute("""
        SELECT assessment_id FROM Assessments 
        WHERE course_id = ? AND assessment_type = ? AND weight_percentage = ?
    """, (course_id, assessment_type, weight))
    assessment_row = cursor.fetchone()

    if assessment_row:
        assessment_id = assessment_row['assessment_id']
        print(f"'{assessment_type}' Assessment (ID: {assessment_id}, Weight: {weight}%) already exists for Course ID {course_id}.")
        return assessment_id
    else:
        # Create the Theory assessment if it doesn't exist
        try:
            cursor.execute("""
                INSERT INTO Assessments (course_id, assessment_type, description, weight_percentage) 
                VALUES (?, ?, ?, ?)
            """, (course_id, assessment_type, f"{assessment_type} Quiz", weight))
            assessment_id = cursor.lastrowid
            conn.commit()
            print(f"Created '{assessment_type}' Assessment (ID: {assessment_id}, Weight: {weight}%) for Course ID {course_id}.")
            return assessment_id
        except sqlite3.Error as e:
            print(f"Error creating '{assessment_type}' assessment for Course ID {course_id}: {e}")
            conn.rollback()
            return None

def populate_quiz_questions_and_choices(conn, assessment_id):
    """Populates QuizQuestions and QuizChoices for a given assessment_id."""
    cursor = conn.cursor()

    quiz_data = [
        {
            "question": "Which keyword is used to declare a variable that cannot be reassigned in JavaScript?",
            "choices": [
                {"text": "var", "correct": False},
                {"text": "let", "correct": False},
                {"text": "const", "correct": True},
                {"text": "static", "correct": False}
            ]
        },
        {
            "question": "What will `console.log(typeof 'hello')` output?",
            "choices": [
                {"text": "string", "correct": True},
                {"text": "object", "correct": False},
                {"text": "undefined", "correct": False},
                {"text": "text", "correct": False}
            ]
        },
        {
            "question": "Which of the following is NOT a primitive data type in JavaScript?",
            "choices": [
                {"text": "Number", "correct": False},
                {"text": "String", "correct": False},
                {"text": "Boolean", "correct": False},
                {"text": "Object", "correct": True}
            ]
        }
    ]

    print(f"\n--- Populating Quiz Questions & Choices for Assessment ID: {assessment_id} ---")
    for item in quiz_data:
        question_text = item["question"]
        
        cursor.execute("SELECT question_id FROM QuizQuestions WHERE assessment_id = ? AND question_text = ?", (assessment_id, question_text))
        question_row = cursor.fetchone()
        
        question_id = None
        if question_row:
            question_id = question_row['question_id']
            print(f"Question '{question_text[:30]}...' already exists (ID: {question_id}). Verifying choices...")
        else:
            try:
                cursor.execute("INSERT INTO QuizQuestions (assessment_id, question_text) VALUES (?, ?)", (assessment_id, question_text))
                question_id = cursor.lastrowid
                print(f"Inserted Question (ID: {question_id}): '{question_text[:30]}...'")
            except sqlite3.Error as e:
                print(f"Error inserting question '{question_text[:30]}...': {e}")
                conn.rollback()
                continue # Skip to next question if this one failed

        if question_id:
            # Check and insert choices
            for choice_item in item["choices"]:
                choice_text = choice_item["text"]
                is_correct = choice_item["correct"]
                
                cursor.execute("SELECT choice_id FROM QuizChoices WHERE question_id = ? AND choice_text = ?", (question_id, choice_text))
                choice_row = cursor.fetchone()
                
                if choice_row:
                    # print(f"  Choice '{choice_text}' for Question ID {question_id} already exists. Skipping.")
                    pass
                else:
                    try:
                        cursor.execute("INSERT INTO QuizChoices (question_id, choice_text, is_correct) VALUES (?, ?, ?)", (question_id, choice_text, is_correct))
                        # print(f"  Inserted Choice for Question ID {question_id}: '{choice_text}' (Correct: {is_correct})")
                    except sqlite3.Error as e:
                        print(f"  Error inserting choice '{choice_text}' for Question ID {question_id}: {e}")
                        conn.rollback()
                        # Decide if we should break or continue with other choices for this question
            conn.commit() # Commit after each question and its choices are processed (or attempted)

def main():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        # Ensure a "Theory" assessment exists for "LEVEL 1: JavaScript Fundamentals"
        js_level1_course_name_filter = "LEVEL 1: JavaScript Fundamentals"
        theory_assessment_id = ensure_theory_assessment_and_get_id(conn, js_level1_course_name_filter, "Theory", 20)

        if theory_assessment_id:
            populate_quiz_questions_and_choices(conn, theory_assessment_id)
            print("\nQuiz data population script completed.")
        else:
            print("\nQuiz data population script could not proceed without a valid Theory Assessment ID.")

    except Exception as e:
        print(f"An error occurred during script execution: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    main()
