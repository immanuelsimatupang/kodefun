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
kodefun-initial-build
);""",
        "QuizQuestions": """
CREATE TABLE IF NOT EXISTS QuizQuestions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'multiple-choice',
    FOREIGN KEY (assessment_id) REFERENCES Assessments(assessment_id)
);""",
        "QuizChoices": """
CREATE TABLE IF NOT EXISTS QuizChoices (
    choice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    choice_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES QuizQuestions(question_id)
);""",
        "UserQuizAttempts": """
CREATE TABLE IF NOT EXISTS UserQuizAttempts (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    assessment_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    attempt_number INTEGER DEFAULT 1,
    score INTEGER,
    max_score INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (assessment_id) REFERENCES Assessments(assessment_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);""",
        "UserQuizAnswers": """
CREATE TABLE IF NOT EXISTS UserQuizAnswers (
    user_answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    chosen_choice_id INTEGER,
    is_correct BOOLEAN,
    FOREIGN KEY (attempt_id) REFERENCES UserQuizAttempts(attempt_id),
    FOREIGN KEY (question_id) REFERENCES QuizQuestions(question_id),
    FOREIGN KEY (chosen_choice_id) REFERENCES QuizChoices(choice_id)
);""",
        "CodingExercises": """
CREATE TABLE IF NOT EXISTS CodingExercises (
    exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    starter_code TEXT,
    function_name VARCHAR(100) DEFAULT 'solve', 
    FOREIGN KEY (assessment_id) REFERENCES Assessments(assessment_id)
);""",
        "CodingExerciseTestCases": """
CREATE TABLE IF NOT EXISTS CodingExerciseTestCases (
    test_case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    input_data TEXT,
    expected_output TEXT,
    is_hidden BOOLEAN DEFAULT FALSE,
    description TEXT,
    FOREIGN KEY (exercise_id) REFERENCES CodingExercises(exercise_id)
);""",
        "UserCodingSubmissions": """
CREATE TABLE IF NOT EXISTS UserCodingSubmissions (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    assessment_id INTEGER NOT NULL, 
    course_id INTEGER NOT NULL,
    submitted_code TEXT NOT NULL,
    passed_tests INTEGER NOT NULL,
    total_tests INTEGER NOT NULL,
    score INTEGER NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    results_details TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (exercise_id) REFERENCES CodingExercises(exercise_id),
    FOREIGN KEY (assessment_id) REFERENCES Assessments(assessment_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);"""
    }

    print("--- Checking and Applying New Schema Parts (Forum, Quiz & Coding Exercise Tables) ---")
);"""
    }

    print("--- Checking and Applying New Schema Parts (Forum Tables) ---")
main
    applied_count = 0
    for table_name, table_sql in new_tables_schemas.items():
        if not table_exists(cursor, table_name):
            try:
                print(f"Creating table '{table_name}'...")
kodefun-initial-build
                cursor.executescript(table_sql)
                cursor.executescript(table_sql) # Use executescript for potentially multiple statements or complex definitions
main
                conn.commit()
                print(f"Table '{table_name}' created successfully.")
                applied_count += 1
            except sqlite3.Error as e:
                print(f"Error creating table '{table_name}': {e}")
kodefun-initial-build
                conn.rollback()
                conn.rollback() # Rollback on error for this table
main
        else:
            print(f"Table '{table_name}' already exists. Skipping.")
            
    if applied_count > 0:
        print(f"\nApplied {applied_count} new table(s) to the schema.")
    else:
kodefun-initial-build
        print("\nNo new tables needed to be applied. Schema likely up-to-date for these specific tables.")
        print("\nNo new forum tables needed to be applied. Schema likely up-to-date for forum features.")
 main

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
