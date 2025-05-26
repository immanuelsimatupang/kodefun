import sqlite3
import os

DATABASE_PATH = 'kodefun.db'

def get_db_connection():
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file '{DATABASE_PATH}' not found.")
        return None
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_text(text):
    """Helper to normalize text for comparison (e.g., strip whitespace, handle None)."""
    if text is None:
        return ""
    return " ".join(text.strip().split())


KEY_COURSES_DATA = [
    # === JavaScript Mastery ===
    {
        "course_name": "LEVEL 1: JavaScript Fundamentals",
        "expected_core_concepts": "Variables, data types, operators\nFunctions dan scope\nControl structures (if/else, loops)\nBasic DOM manipulation",
        "expected_interactive_elements": "JS Console Playground: Real-time code execution\nVariable Inspector: Visualize variable changes\nDOM Builder: Interactive HTML manipulation"
    },
    {
        "course_name": "LEVEL 5: JavaScript Frameworks Introduction", 
        "expected_core_concepts": "Component architecture\nState management\nRouting\nBuild tools introduction",
        "expected_interactive_elements": "Framework-specific examples and mini-projects." # Using generic placeholder as per subtask note
    },
    {
        "course_name": "LEVEL 12: JavaScript Capstone Project", 
        "expected_core_concepts": "Minimum 1000 lines of code\nFull documentation\nTesting coverage >80%\nDeployment to production\nCode review dan presentation",
        "expected_interactive_elements": "" # Empty as per subtask
    },

    # === PHP Mastery ===
    # For PHP and WebDev, using content from populate_courses.py as the 'expected' baseline
    # as specific new content was not provided for these in the prompt, other than for JS L1.
    # Adjusting PHP course names to match subtask instructions.
    {
        "course_name": "LEVEL 1: PHP Fundamentals",
        "expected_core_concepts": "Variables, data types, operators, control flow, basic syntax.", # From populate_courses.py
        "expected_interactive_elements": "Interactive code editor, syntax quizzes." # From populate_courses.py
    },
    {
        "course_name": "LEVEL 4: PHP Framework Introduction - Laravel", 
        # Content for "LEVEL 11: Introduction to a PHP Framework (e.g., Laravel/Symfony Basics)" from populate_courses.py used as proxy
        "expected_core_concepts": "Core concepts of a modern PHP framework, routing, controllers, views.", 
        "expected_interactive_elements": "Building a small application using a framework."
    },
    {
        "course_name": "LEVEL 11-12: PHP Capstone Project", 
        # Content for "LEVEL 12: Capstone Project - Advanced PHP Application" from populate_courses.py used as proxy
        "expected_core_concepts": "Comprehensive project showcasing mastery of PHP and framework usage.",
        "expected_interactive_elements": "Major capstone project with portfolio potential."
    },

    # === Web Development Stack ===
    {
        "course_name": "L1: Frontend - HTML5 Semantics & Accessibility",
        "expected_core_concepts": "HTML5: Semantic markup, accessibility best practices, structuring web pages.",
        "expected_interactive_elements": "Static responsive website (Part 1: HTML structure)" # This was the project name, makes sense as interactive element.
    },
    {
        "course_name": "L3: Frontend - JavaScript DOM & Events",
        "expected_core_concepts": "JavaScript: DOM manipulation, event handling, basic asynchronous operations (Fetch API).",
        "expected_interactive_elements": "Interactive web components and dynamic content updates"
    },
    {
        "course_name": "L6: Backend - MySQL & Full-Stack Integration",
        "expected_core_concepts": "MySQL: Database design, advanced queries, integration with Laravel. Full-stack project development.",
        "expected_interactive_elements": "Full-stack web application with frontend and backend (Part 3: Integration)"
    }
]


def verify_and_update_courses(conn):
    cursor = conn.cursor()
    print("--- Verifying and Updating Course Content ---")

    for course_data in KEY_COURSES_DATA:
        course_name = course_data["course_name"]
        expected_cc = course_data["expected_core_concepts"]
        expected_ie = course_data["expected_interactive_elements"]
        
        print(f"\nChecking Course: '{course_name}'")

        cursor.execute("SELECT course_id, core_concepts, interactive_elements_description FROM Courses WHERE course_name = ?", (course_name,))
        row = cursor.fetchone()

        if not row:
            print(f"  STATUS: Course NOT FOUND in database.")
            continue

        course_id = row["course_id"]
        current_cc = row["core_concepts"]
        current_ie = row["interactive_elements_description"]
        
        needs_update = False
        update_fields = {}

        # Normalize for comparison, but use expected for update
        if normalize_text(current_cc) != normalize_text(expected_cc):
            needs_update = True
            update_fields["core_concepts"] = expected_cc
            print(f"  Core Concepts: MISMATCH. Current='{current_cc}', Expected='{expected_cc}'")
        else:
            print(f"  Core Concepts: OK.")

        if normalize_text(current_ie) != normalize_text(expected_ie):
            needs_update = True
            update_fields["interactive_elements_description"] = expected_ie
            print(f"  Interactive Elements: MISMATCH. Current='{current_ie}', Expected='{expected_ie}'")
        else:
            print(f"  Interactive Elements: OK.")

        if needs_update:
            sql_update_parts = []
            sql_update_values = []
            for field, value in update_fields.items():
                sql_update_parts.append(f"{field} = ?")
                sql_update_values.append(value)
            
            sql_update_query = f"UPDATE Courses SET {', '.join(sql_update_parts)} WHERE course_id = ?"
            sql_update_values.append(course_id)
            
            try:
                cursor.execute(sql_update_query, tuple(sql_update_values))
                conn.commit()
                print(f"  STATUS: Updated course ID {course_id} successfully.")
            except sqlite3.Error as e:
                conn.rollback()
                print(f"  STATUS: FAILED to update course ID {course_id}. Error: {e}")
        else:
            print(f"  STATUS: No update needed for course ID {course_id}.")

def main():
    conn = get_db_connection()
    if conn is None:
        return

    try:
        verify_and_update_courses(conn)
        print("\n--- Verification and Update Script Completed ---")
    except Exception as e:
        print(f"An error occurred during script execution: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    main()
