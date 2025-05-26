import sqlite3
import os

DATABASE_PATH = 'kodefun.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file '{DATABASE_PATH}' not found. Please run app.py first to create it.")
        return None
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    # Enable foreign key constraint enforcement for this connection
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def populate_learning_paths(conn):
    """Populates the LearningPaths table."""
    cursor = conn.cursor()
    paths_data = [
        ("Single Programming Path", "Focus on mastering a single programming language or technology."),
        ("Multi Programming Path", "Focus on combining multiple technologies to build complete applications or specialize in a broader domain.")
    ]
    path_ids = {}
    print("\n--- Populating LearningPaths ---")
    for name, description in paths_data:
        try:
            cursor.execute("INSERT INTO LearningPaths (path_name, path_description) VALUES (?, ?)", (name, description))
            path_id = cursor.lastrowid
            path_ids[name] = path_id
            print(f"Inserted LearningPath: '{name}' (ID: {path_id})")
        except sqlite3.IntegrityError:
            # In case the script is run multiple times, fetch existing ID
            cursor.execute("SELECT path_id FROM LearningPaths WHERE path_name = ?", (name,))
            existing_path = cursor.fetchone()
            if existing_path:
                path_ids[name] = existing_path['path_id']
                print(f"LearningPath '{name}' already exists (ID: {path_ids[name]}).")
            else:
                print(f"Error: Could not insert or find LearningPath '{name}'.")
                # Handle error or raise exception
    conn.commit()
    return path_ids

def populate_tracks(conn, path_ids):
    """Populates the Tracks table."""
    cursor = conn.cursor()
    tracks_data = [
        ("JavaScript Mastery Track", "Fokus mendalam pada satu bahasa pemrograman JavaScript.", path_ids.get("Single Programming Path"), 16),
        ("PHP Mastery Track", "Fokus mendalam pada satu bahasa pemrograman PHP.", path_ids.get("Single Programming Path"), 16),
        ("Web Development Stack", "Kombinasi teknologi untuk spesialisasi Web Development.", path_ids.get("Multi Programming Path"), 20)
    ]
    track_ids = {}
    print("\n--- Populating Tracks ---")
    for name, description, path_id, duration in tracks_data:
        if path_id is None:
            print(f"Error: Could not find parent path_id for Track '{name}'. Skipping.")
            continue
        try:
            cursor.execute("INSERT INTO Tracks (track_name, track_description, path_id, total_duration_weeks) VALUES (?, ?, ?, ?)",
                           (name, description, path_id, duration))
            track_id = cursor.lastrowid
            track_ids[name] = track_id
            print(f"Inserted Track: '{name}' (ID: {track_id}) under Path ID: {path_id}")
        except sqlite3.IntegrityError:
            cursor.execute("SELECT track_id FROM Tracks WHERE track_name = ?", (name,))
            existing_track = cursor.fetchone()
            if existing_track:
                track_ids[name] = existing_track['track_id']
                print(f"Track '{name}' already exists (ID: {track_ids[name]}).")
            else:
                print(f"Error: Could not insert or find Track '{name}'.")
    conn.commit()
    return track_ids

def populate_courses_and_assessments(conn, track_ids):
    """Populates Courses and their corresponding Assessments."""
    cursor = conn.cursor()
    print("\n--- Populating Courses and Assessments ---")

    # --- JavaScript Mastery Track Data ---
    js_track_id = track_ids.get("JavaScript Mastery Track")
    if js_track_id:
        js_courses_data = [
            (1, "LEVEL 1: JavaScript Fundamentals", 4, "Variables, data types, operators, control flow (if/else, loops).", "Interactive code editor, quizzes."),
            (2, "LEVEL 2: Functions & Scope", 4, "Function declaration, expressions, arrow functions, scope (global, local, block), closures.", "Code challenges, debugging exercises."),
            (3, "LEVEL 3: Arrays & Objects", 5, "Array methods (map, filter, reduce), object manipulation, JSON.", "Data manipulation tasks, mini-project on data handling."),
            (4, "LEVEL 4: DOM Manipulation", 5, "Selecting elements, modifying content/styles, event handling.", "Building interactive UI components."),
            (5, "LEVEL 5: Asynchronous JavaScript", 6, "Callbacks, Promises, async/await, Fetch API.", "Fetching data from APIs, creating responsive interfaces."),
            (6, "LEVEL 6: OOP in JavaScript", 6, "Prototypes, classes, inheritance, 'this' keyword.", "Object-oriented design challenges."),
            (7, "LEVEL 7: Error Handling & Debugging", 4, "Try/catch, debugging tools, common pitfalls.", "Debugging complex scenarios, writing robust code."),
            (8, "LEVEL 8: ES6+ Features", 4, "Destructuring, spread/rest operators, modules, template literals.", "Refactoring old JS code to modern ES6+."),
            (9, "LEVEL 9: Data Structures & Algorithms (Basic)", 6, "Basic data structures (stacks, queues, linked lists), algorithm concepts.", "Solving algorithmic puzzles."),
            (10, "LEVEL 10: Project - Interactive Web App", 8, "Applying all learned concepts to build a complete interactive application.", "Full project development cycle."),
            (11, "LEVEL 11: Introduction to Node.js & Express", 6, "Backend JavaScript, Node.js basics, Express framework for APIs.", "Building simple REST APIs."),
            (12, "LEVEL 12: Capstone Project - Full-Stack JS App", 8, "Full-stack JavaScript application development incorporating frontend and backend skills.", "Major capstone project with portfolio potential.")
        ]
        insert_courses_for_track(conn, js_track_id, js_courses_data, default_assessments_single_prog)

    # --- PHP Mastery Track Data ---
    php_track_id = track_ids.get("PHP Mastery Track")
    if php_track_id:
        php_courses_data = [
            (1, "LEVEL 1: PHP Fundamentals", 4, "Variables, data types, operators, control flow, basic syntax.", "Interactive code editor, syntax quizzes."),
            (2, "LEVEL 2: Functions & Arrays", 4, "User-defined functions, built-in functions, array manipulation.", "Function writing challenges, array processing tasks."),
            (3, "LEVEL 3: OOP in PHP (Basic)", 5, "Classes, objects, properties, methods, basic inheritance.", "Simple OOP modeling exercises."),
            (4, "LEVEL 4: Form Handling & Superglobals", 5, "POST/GET requests, form validation, $_SERVER, $_SESSION, $_COOKIE.", "Building secure and interactive forms."),
            (5, "LEVEL 5: File System & Error Handling", 6, "Reading/writing files, exception handling, logging.", "File manipulation tasks, robust error management."),
            (6, "LEVEL 6: Database Interaction (PDO)", 6, "Connecting to MySQL with PDO, CRUD operations, prepared statements.", "Building a data-driven application component."),
            (7, "LEVEL 7: OOP in PHP (Advanced)", 4, "Namespaces, autoloading, traits, interfaces, abstract classes.", "Advanced OOP design patterns."),
            (8, "LEVEL 8: Introduction to MVC Pattern", 4, "Understanding Model-View-Controller architecture.", "Refactoring a simple app to MVC structure."),
            (9, "LEVEL 9: Basic API Development", 6, "Creating simple RESTful APIs with PHP.", "Building API endpoints for a resource."),
            (10, "LEVEL 10: Project - Dynamic Web Application", 8, "Applying all learned PHP concepts to build a dynamic website.", "Full project development cycle for a PHP app."),
            (11, "LEVEL 11: Introduction to a PHP Framework (e.g., Laravel/Symfony Basics)", 6, "Core concepts of a modern PHP framework, routing, controllers, views.", "Building a small application using a framework."),
            (12, "LEVEL 12: Capstone Project - Advanced PHP Application", 8, "Comprehensive project showcasing mastery of PHP and framework usage.", "Major capstone project with portfolio potential.")
        ]
        insert_courses_for_track(conn, php_track_id, php_courses_data, default_assessments_single_prog)

    # --- Web Development Stack Data ---
    web_dev_track_id = track_ids.get("Web Development Stack")
    if web_dev_track_id:
        web_dev_courses_data = [
            # Level 1-3: Frontend Foundation
            (1, "L1: Frontend - HTML5 Semantics & Accessibility", 7, "HTML5: Semantic markup, accessibility best practices, structuring web pages.", "Static responsive website (Part 1: HTML structure)", 1), # order_in_track
            (2, "L2: Frontend - CSS3 Styling & Layouts", 7, "CSS3: Flexbox, Grid, animations, responsive design principles, preprocessors (Sass/LESS basics).", "Static responsive website (Part 2: CSS styling and layout)", 2),
            (3, "L3: Frontend - JavaScript DOM & Events", 7, "JavaScript: DOM manipulation, event handling, basic asynchronous operations (Fetch API).", "Interactive web components and dynamic content updates", 3),
            # Level 4-6: Backend Integration
            (4, "L4: Backend - PHP Server-Side Logic", 7, "PHP: Core server-side logic, request handling, templating basics.", "Basic CRUD API functionalities (Part 1: PHP Core)", 4),
            (5, "L5: Backend - Laravel Framework", 7, "Laravel: MVC, Eloquent ORM, Blade templating, routing, middleware, database migrations.", "Authentication system and resource management (Part 2: Laravel)", 5),
            (6, "L6: Backend - MySQL & Full-Stack Integration", 7, "MySQL: Database design, advanced queries, integration with Laravel. Full-stack project development.", "Full-stack web application with frontend and backend (Part 3: Integration)", 6),
            # Placeholder for levels 7-12, assuming 20 weeks total, ~7 days per course for ~12 courses
            (7, "L7: Advanced Frontend Techniques", 7, "JS Frameworks (React/Vue basics), State Management, Build Tools (Webpack/Vite).", "Single Page Application component.", 7),
            (8, "L8: API Design & Development", 7, "RESTful API principles, API security (OAuth/JWT), Documentation (Swagger/OpenAPI).", "Comprehensive REST API for a resource.", 8),
            (9, "L9: DevOps & Deployment", 7, "Git advanced, CI/CD pipelines (GitHub Actions/Jenkins), Docker basics, Cloud deployment (AWS/Heroku basics).", "Deploying a full-stack application.", 9),
            (10, "L10: Testing & Quality Assurance", 7, "Unit testing (PHPUnit/Jest), Integration testing, E2E testing (Cypress/Selenium).", "Implementing test suites for an application.", 10),
            (11, "L11: Web Security Fundamentals", 7, "OWASP Top 10, XSS, CSRF, SQL Injection, HTTPS, Content Security Policy.", "Security audit and hardening of an application.", 11),
            (12, "L12: Capstone - Scalable Web Application", 14, "Building a scalable, secure, and well-tested full-stack web application.", "Major capstone project demonstrating full-stack proficiency.", 12) # Capstone usually longer
        ]
        # For Web Dev, the main assessment is the project.
        web_dev_assessments = lambda course_name: [
            (f"Project: {course_name.split(': ', 1)[1] if ': ' in course_name else course_name}", 'Project', 25) # Use part of course name for project description
        ]
        # The last parameter for insert_courses_for_track is 'order_in_track_is_explicit=True'
        insert_courses_for_track(conn, web_dev_track_id, web_dev_courses_data, web_dev_assessments, order_in_track_is_explicit=True)

    conn.commit()
    print("\n--- Finished populating Courses and Assessments ---")

def default_assessments_single_prog(course_name):
    """Returns a list of default assessments for single programming track courses."""
    return [
        ("Mini Challenge", 'Project', 25),
        ("Live Coding Session", 'Live Coding', 15)
    ]

def insert_courses_for_track(conn, track_id, courses_data, assessment_generator_func, order_in_track_is_explicit=False):
    """Helper function to insert courses and their assessments for a given track."""
    cursor = conn.cursor()
    order_counter = 1
    for course_info in courses_data:
        if order_in_track_is_explicit:
            level_num, name, duration, concepts, interactive_desc, order = course_info
        else:
            level_num, name, duration, concepts, interactive_desc = course_info
            order = order_counter

        try:
            cursor.execute("""
                INSERT INTO Courses (track_id, course_name, course_level_number, duration_days, core_concepts, interactive_elements_description, order_in_track)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (track_id, name, level_num, duration, concepts, interactive_desc, order))
            course_id = cursor.lastrowid
            print(f"  Inserted Course: '{name}' (ID: {course_id}) for Track ID: {track_id}")

            assessments = assessment_generator_func(name) # Pass course_name for context if needed by generator
            for assessment_name, assessment_type, weight in assessments:
                try:
                    cursor.execute("""
                        INSERT INTO Assessments (course_id, assessment_type, description, weight_percentage)
                        VALUES (?, ?, ?, ?)
                    """, (course_id, assessment_type, assessment_name, weight))
                    print(f"    Inserted Assessment: '{assessment_name}' for Course ID: {course_id}")
                except sqlite3.IntegrityError:
                    print(f"    Assessment '{assessment_name}' for Course ID: {course_id} might already exist.")
            
            if not order_in_track_is_explicit:
                order_counter += 1

        except sqlite3.IntegrityError:
            # Fetch existing course_id if name and track_id match, to allow rerunning for assessments
            cursor.execute("SELECT course_id FROM Courses WHERE course_name = ? AND track_id = ?", (name, track_id))
            existing_course = cursor.fetchone()
            if existing_course:
                course_id = existing_course['course_id']
                print(f"  Course '{name}' (ID: {course_id}) already exists for Track ID: {track_id}. Checking/adding assessments.")
                # Re-run assessment insertion for existing course
                assessments = assessment_generator_func(name)
                for assessment_name, assessment_type, weight in assessments:
                    # Check if specific assessment already exists
                    cursor.execute("SELECT assessment_id FROM Assessments WHERE course_id = ? AND description = ? AND assessment_type = ?", (course_id, assessment_name, assessment_type))
                    existing_assessment = cursor.fetchone()
                    if not existing_assessment:
                        try:
                            cursor.execute("""
                                INSERT INTO Assessments (course_id, assessment_type, description, weight_percentage)
                                VALUES (?, ?, ?, ?)
                            """, (course_id, assessment_type, assessment_name, weight))
                            print(f"    Inserted Assessment: '{assessment_name}' for Course ID: {course_id}")
                        except sqlite3.IntegrityError:
                             print(f"    Error inserting assessment '{assessment_name}' for Course ID: {course_id} (IntegrityError).")
                    else:
                        print(f"    Assessment '{assessment_name}' for Course ID: {course_id} already exists.")
            else:
                print(f"  Error: Could not insert or find Course '{name}' for Track ID: {track_id}.")
        except Exception as e:
            print(f"  An unexpected error occurred for course '{name}': {e}")


def main():
    """Main function to orchestrate the population of the database."""
    conn = get_db_connection()
    if conn is None:
        return

    try:
        path_ids = populate_learning_paths(conn)
        if not path_ids:
            print("Stopping: LearningPaths population failed or returned empty.")
            return

        track_ids = populate_tracks(conn, path_ids)
        if not track_ids:
            print("Stopping: Tracks population failed or returned empty.")
            return
            
        populate_courses_and_assessments(conn, track_ids)
        
        print("\nDatabase population script completed successfully.")
    except Exception as e:
        print(f"An error occurred during database population: {e}")
        conn.rollback() # Rollback any changes if an error occurs
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    main()
