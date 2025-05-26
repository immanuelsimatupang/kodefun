import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

# Configuration
DATABASE = 'kodefun.db'
SECRET_KEY = os.urandom(24) # In a real app, use a fixed, secure key. For development, this is fine.

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DATABASE'] = DATABASE # For convenience if we need app.config['DATABASE'] later

# --- Database Helper Functions ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row # Access columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(force_recreate=False):
    """Initializes the database using schema.sql."""
    db_path = app.config['DATABASE']
    db_exists = os.path.exists(db_path)

    if force_recreate and db_exists:
        try:
            os.remove(db_path)
            print(f"Removed existing database {db_path}.")
            db_exists = False
        except OSError as e:
            print(f"Error removing database {db_path}: {e}")
            return # Exit if we can't remove the DB

    if not db_exists:
        try:
            with app.app_context(): # Ensures g is available
                db = get_db()
                with app.open_resource('schema.sql', mode='r') as f:
                    db.cursor().executescript(f.read())
                db.commit()
                print(f"Initialized the database {db_path} from schema.sql.")
        except Exception as e:
            print(f"Error initializing database: {e}")
            # Potentially re-raise or handle more gracefully
    else:
        print(f"Database {db_path} already exists. Skipping initialization.")

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        
        if error is None:
            try:
                # Check if username or email already exists
                user_by_username = db.execute('SELECT user_id FROM Users WHERE username = ?', (username,)).fetchone()
                user_by_email = db.execute('SELECT user_id FROM Users WHERE email = ?', (email,)).fetchone()

                if user_by_username:
                    error = f"Username {username} is already taken."
                elif user_by_email:
                    error = f"Email {email} is already registered."
                
                if error is None:
                    db.execute(
                        'INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)',
                        (username, email, generate_password_hash(password))
                    )
                    db.commit()
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for('login'))
            except sqlite3.IntegrityError: # Should be caught by above checks, but as a safeguard
                error = "Username or email already exists (database integrity error)."
            except Exception as e:
                error = f"An unexpected error occurred: {e}"
        
        if error:
            flash(error, 'danger')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username'] # Can be username or email
        password = request.form['password']
        db = get_db()
        error = None
        user = None

        # Try to fetch user by username or email
        user = db.execute(
            'SELECT * FROM Users WHERE username = ? OR email = ?', (username_or_email, username_or_email)
        ).fetchone()

        if user is None:
            error = 'Incorrect username/email or password.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect username/email or password.'

        if error is None and user:
            session.clear()
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['xp_points'] = user['xp_points'] # Store other relevant info
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash(error, 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'info')
        return redirect(url_for('login'))
    # Fetch fresh user data if needed, or use session data
    # For now, session data is fine for username and xp_points
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# --- Learning Content Display Routes ---

@app.route('/learning_paths')
def learning_paths():
    if 'user_id' not in session:
        flash('Please log in to view learning paths.', 'info')
        return redirect(url_for('login'))
    
    db = get_db()
    paths = db.execute('SELECT path_id, path_name, path_description FROM LearningPaths').fetchall()
    return render_template('learning_paths.html', paths=paths)

@app.route('/learning_paths/<int:path_id>/tracks')
def learning_path_tracks(path_id):
    if 'user_id' not in session:
        flash('Please log in to view tracks.', 'info')
        return redirect(url_for('login'))

    db = get_db()
    current_path = db.execute('SELECT path_id, path_name FROM LearningPaths WHERE path_id = ?', (path_id,)).fetchone()
    if not current_path:
        flash('Learning path not found.', 'danger')
        return redirect(url_for('learning_paths'))
        
    tracks = db.execute(
        'SELECT track_id, track_name, track_description, total_duration_weeks FROM Tracks WHERE path_id = ? ORDER BY track_name', (path_id,)
    ).fetchall()
    return render_template('tracks.html', current_path=current_path, tracks=tracks)

@app.route('/tracks/<int:track_id>/courses')
def track_courses(track_id):
    if 'user_id' not in session:
        flash('Please log in to view courses.', 'info')
        return redirect(url_for('login'))

    db = get_db()
    current_track = db.execute('SELECT track_id, track_name, path_id FROM Tracks WHERE track_id = ?', (track_id,)).fetchone()
    if not current_track:
        flash('Track not found.', 'danger')
        return redirect(url_for('learning_paths'))

    user_id = session['user_id']
    db = get_db()

    # Fetch all courses for the track
    track_courses_list = db.execute(
        'SELECT course_id, course_name, course_level_number, duration_days, order_in_track FROM Courses WHERE track_id = ? ORDER BY order_in_track', (track_id,)
    ).fetchall()

    # Initialize UserProgress if it doesn't exist for this user and track
    for course in track_courses_list:
        progress = db.execute(
            'SELECT progress_id FROM UserProgress WHERE user_id = ? AND course_id = ?', (user_id, course['course_id'])
        ).fetchone()
        if not progress:
            status = 'unlocked' if course['order_in_track'] == 1 else 'locked'
            unlocked_time = datetime.utcnow() if status == 'unlocked' else None
            try:
                db.execute(
                    """INSERT INTO UserProgress 
                       (user_id, course_id, status, unlocked_at, current_score_theory, current_score_practice, current_score_project, current_score_live_coding, total_score, attempts) 
                       VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, 0)""",
                    (user_id, course['course_id'], status, unlocked_time)
                )
                db.commit()
                print(f"Initialized progress for user {user_id}, course {course['course_id']} with status {status}")
            except sqlite3.IntegrityError: # Should not happen if previous check is robust
                db.rollback()
                print(f"Error initializing progress for user {user_id}, course {course['course_id']}. Might be a race condition or other issue.")
            except Exception as e:
                db.rollback()
                print(f"Generic error initializing progress: {e}")


    # Fetch UserProgress for all courses in the track for the current user
    user_progress_data = db.execute(
        """SELECT up.course_id, up.status, up.total_score 
           FROM UserProgress up
           JOIN Courses c ON up.course_id = c.course_id
           WHERE up.user_id = ? AND c.track_id = ?""",
        (user_id, track_id)
    ).fetchall()
    
    # Convert user_progress_data to a dict for easier lookup in the template
    progress_map = {item['course_id']: item for item in user_progress_data}

    return render_template('courses.html', current_track=current_track, courses=track_courses_list, progress_map=progress_map)

@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    if 'user_id' not in session:
        flash('Please log in to view course details.', 'info')
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()

    # Check UserProgress status for this course
    user_progress = db.execute(
        'SELECT * FROM UserProgress WHERE user_id = ? AND course_id = ?', (user_id, course_id)
    ).fetchone()
    
    current_course = db.execute(
        'SELECT c.*, t.track_name, lp.path_id, lp.path_name FROM Courses c JOIN Tracks t ON c.track_id = t.track_id JOIN LearningPaths lp ON t.path_id = lp.path_id WHERE c.course_id = ?', (course_id,)
    ).fetchone()

    if not current_course:
        flash('Course not found.', 'danger')
        return redirect(url_for('learning_paths'))

    if not user_progress:
        # This case should ideally be handled by the track_courses initialization.
        # If reached, means UserProgress was not initialized for this course.
        # Redirect to track page to trigger initialization.
        flash('Course progress not initialized. Please visit the track page first.', 'warning')
        return redirect(url_for('track_courses', track_id=current_course['track_id']))

    if user_progress['status'] == 'locked':
        flash('This course is currently locked. Complete previous courses to unlock.', 'warning')
        return redirect(url_for('track_courses', track_id=current_course['track_id']))

    assessments = db.execute(
        'SELECT assessment_id, assessment_type, description, weight_percentage FROM Assessments WHERE course_id = ? ORDER BY assessment_id', (course_id,)
    ).fetchall()
    
    # Track info for breadcrumbs is now part of current_course query
    track_info = { # Reconstruct track_info for template compatibility if needed, or update template
        'track_id': current_course['track_id'],
        'track_name': current_course['track_name'],
        'path_id': current_course['path_id'],
        'path_name': current_course['path_name']
    }

    return render_template('course_detail.html', current_course=current_course, assessments=assessments, track_info=track_info, user_progress=user_progress)

# --- End Learning Content Display Routes ---
# --- Assessment Submission and Completion Routes ---

@app.route('/submit_assessment/<int:course_id>/<int:assessment_id>', methods=['POST'])
def submit_assessment(course_id, assessment_id):
    if 'user_id' not in session:
        flash('Please log in to submit assessments.', 'info')
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()

    user_progress = db.execute(
        'SELECT * FROM UserProgress WHERE user_id = ? AND course_id = ?', (user_id, course_id)
    ).fetchone()

    if not user_progress:
        flash('No progress found for this course.', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

    if user_progress['status'] == 'locked' or user_progress['status'] == 'completed' or user_progress['status'] == 'failed':
        flash(f'Cannot submit assessment for a course with status: {user_progress["status"]}.', 'warning')
        return redirect(url_for('course_detail', course_id=course_id))

    assessment = db.execute(
        'SELECT assessment_type, weight_percentage FROM Assessments WHERE assessment_id = ? AND course_id = ?', (assessment_id, course_id)
    ).fetchone()

    if not assessment:
        flash('Assessment not found.', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

    # Mock scoring: 80% of the assessment's weight
    score_earned = int(0.80 * assessment['weight_percentage'])
    
    field_to_update = None
    if assessment['assessment_type'] == 'Theory':
        field_to_update = 'current_score_theory'
    elif assessment['assessment_type'] == 'Practice':
        field_to_update = 'current_score_practice'
    elif assessment['assessment_type'] == 'Project': # Covers 'Mini Challenge' and 'Project' from schema
        field_to_update = 'current_score_project'
    elif assessment['assessment_type'] == 'Live Coding':
        field_to_update = 'current_score_live_coding'
    
    if not field_to_update:
        flash(f"Unknown assessment type: {assessment['assessment_type']}", 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

    try:
        # Update the specific score component
        db.execute(
            f"UPDATE UserProgress SET {field_to_update} = ?, status = ?, last_attempt_at = ? WHERE progress_id = ?",
            (score_earned, 'in_progress' if user_progress['status'] == 'unlocked' else user_progress['status'], datetime.utcnow(), user_progress['progress_id'])
        )
        # Recalculate total_score after updating a component
        # Fetch all component scores first
        updated_progress_scores = db.execute(
            'SELECT current_score_theory, current_score_practice, current_score_project, current_score_live_coding FROM UserProgress WHERE progress_id = ?',
            (user_progress['progress_id'],)
        ).fetchone()
        
        new_total_score = (updated_progress_scores['current_score_theory'] or 0) + \
                          (updated_progress_scores['current_score_practice'] or 0) + \
                          (updated_progress_scores['current_score_project'] or 0) + \
                          (updated_progress_scores['current_score_live_coding'] or 0)
        
        db.execute(
            "UPDATE UserProgress SET total_score = ? WHERE progress_id = ?",
            (new_total_score, user_progress['progress_id'])
        )
        
        db.commit()
        flash(f"Mock submission for {assessment['assessment_type']} complete! Score: {score_earned}/{assessment['weight_percentage']}", 'success')
    except Exception as e:
        db.rollback()
        flash(f"Error submitting assessment: {e}", 'danger')
        
    return redirect(url_for('course_detail', course_id=course_id))


@app.route('/evaluate_course_completion/<int:course_id>', methods=['POST'])
def evaluate_course_completion(course_id):
    if 'user_id' not in session:
        flash('Please log in.', 'info')
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()

    user_progress = db.execute(
        'SELECT * FROM UserProgress WHERE user_id = ? AND course_id = ?', (user_id, course_id)
    ).fetchone()

    if not user_progress:
        flash('No progress found for this course.', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

    if user_progress['status'] == 'completed' or user_progress['status'] == 'failed':
        flash(f'Course already {user_progress["status"]}.', 'info')
        return redirect(url_for('course_detail', course_id=course_id))
        
    current_total_score = user_progress['total_score'] # This should be up-to-date from submit_assessment
    new_attempts = (user_progress['attempts'] or 0) + 1
    
    new_status = user_progress['status']
    xp_awarded = 0
    course_completed_successfully = False

    if current_total_score >= 70 and new_attempts <= 3:
        new_status = 'completed'
        course_completed_successfully = True
        # Award XP
        current_xp = db.execute('SELECT xp_points FROM Users WHERE user_id = ?', (user_id,)).fetchone()['xp_points']
        xp_to_add = 100 # Fixed XP for completing a course
        new_xp = (current_xp or 0) + xp_to_add
        db.execute('UPDATE Users SET xp_points = ? WHERE user_id = ?', (new_xp, user_id))
        session['xp_points'] = new_xp # Update session
        xp_awarded = xp_to_add
        flash(f'Congratulations! Course passed with {current_total_score} points. You earned {xp_awarded} XP!', 'success')

        # --- Achievement Awarding Logic ---
        # Helper function will be defined above this route or imported
        
        # 1. Course-Specific Achievements
        completed_course_details = db.execute('SELECT course_name, track_id FROM Courses WHERE course_id = ?', (course_id,)).fetchone()
        if completed_course_details:
            # JS Novice (assuming JS Level 1 course name contains "JavaScript Fundamentals" or similar)
            if "javascript fundamentals" in completed_course_details['course_name'].lower() or completed_course_details['course_name'] == "LEVEL 1: JavaScript Fundamentals":
                check_and_award_achievement(user_id, "JavaScript Novice", db)
            # PHP Beginner (assuming PHP Level 1 course name contains "PHP Fundamentals")
            elif "php fundamentals" in completed_course_details['course_name'].lower() or completed_course_details['course_name'] == "LEVEL 1: PHP Fundamentals":
                check_and_award_achievement(user_id, "PHP Beginner", db)
            # Web Dev Starter (assuming Web Dev Level 1 course name)
            elif "html5 semantics & accessibility" in completed_course_details['course_name'].lower() or completed_course_details['course_name'] == "L1: Frontend - HTML5 Semantics & Accessibility":
                check_and_award_achievement(user_id, "Web Dev Starter", db)
            # JS Functions Pro
            elif "functions & scope" in completed_course_details['course_name'].lower() and "javascript" in completed_course_details['course_name'].lower(): # A bit more specific
                 check_and_award_achievement(user_id, "JS Functions Pro", db)
            # DOM Manipulator
            elif "dom manipulation" in completed_course_details['course_name'].lower() and "javascript" in completed_course_details['course_name'].lower():
                 check_and_award_achievement(user_id, "DOM Manipulator", db)
            # PHP OOP Basics
            elif "oop in php (basic)" in completed_course_details['course_name'].lower():
                 check_and_award_achievement(user_id, "PHP OOP Basics", db)
            # Full-Stack Foundation (check for L3 JS and L6 Web Dev Stack completion)
            # This one is more complex as it depends on TWO courses. Simpler to check on completion of L6 if L3 is also done.
            if completed_course_details['course_name'] == "L6: Backend - MySQL & Full-Stack Integration":
                # Check if L3 "L3: Frontend - JavaScript DOM & Events" is also completed by this user
                l3_js_course = db.execute("SELECT course_id FROM Courses WHERE course_name = 'L3: Frontend - JavaScript DOM & Events'").fetchone()
                if l3_js_course:
                    l3_js_progress = db.execute("SELECT status FROM UserProgress WHERE user_id = ? AND course_id = ?", (user_id, l3_js_course['course_id'])).fetchone()
                    if l3_js_progress and l3_js_progress['status'] == 'completed':
                        check_and_award_achievement(user_id, "Full-Stack Foundation", db)


        # 2. General Achievements
        # Count completed courses for the user
        completed_courses_count = db.execute(
            "SELECT COUNT(*) as count FROM UserProgress WHERE user_id = ? AND status = 'completed'", (user_id,)
        ).fetchone()['count']

        if completed_courses_count >= 5:
            check_and_award_achievement(user_id, "Five Courses Down!", db)

        # Check for "First Track Completed!" and "Halfway There!"
        current_track_id = completed_course_details['track_id']
        courses_in_track = db.execute("SELECT course_id FROM Courses WHERE track_id = ?", (current_track_id,)).fetchall()
        total_courses_in_track = len(courses_in_track)
        
        completed_in_track_count = 0
        for course_in_track_item in courses_in_track:
            progress = db.execute("SELECT status FROM UserProgress WHERE user_id = ? AND course_id = ?", (user_id, course_in_track_item['course_id'])).fetchone()
            if progress and progress['status'] == 'completed':
                completed_in_track_count += 1
        
        if completed_in_track_count == total_courses_in_track and total_courses_in_track > 0 : # Ensure track is not empty
            check_and_award_achievement(user_id, "First Track Completed!", db)
        
        # "Halfway There!" (for tracks with at least, say, 10-12 courses typically)
        # Let's assume a track length of 12 for this achievement for simplicity, or check total_courses_in_track
        if total_courses_in_track >= 10 and completed_in_track_count >= 6: # Check for 6 completed in a substantial track
             check_and_award_achievement(user_id, "Halfway There!", db)
        
        # --- End Achievement Awarding Logic ---

        # Unlock next course
        current_course_order = db.execute('SELECT order_in_track, track_id FROM Courses WHERE course_id = ?', (course_id,)).fetchone()
        if current_course_order:
            next_course = db.execute(
                'SELECT course_id FROM Courses WHERE track_id = ? AND order_in_track = ?',
                (current_course_order['track_id'], current_course_order['order_in_track'] + 1)
            ).fetchone()
            if next_course:
                # Ensure UserProgress exists for next course (should have been batch-created as 'locked')
                next_progress = db.execute('SELECT progress_id, status FROM UserProgress WHERE user_id = ? AND course_id = ?', (user_id, next_course['course_id'])).fetchone()
                if next_progress and next_progress['status'] == 'locked':
                     db.execute('UPDATE UserProgress SET status = ?, unlocked_at = ? WHERE progress_id = ?', ('unlocked', datetime.utcnow(), next_progress['progress_id']))
                     flash(f'Next course unlocked!', 'info')
                elif not next_progress: # Should not happen if batch creation is robust
                    db.execute(
                        """INSERT INTO UserProgress (user_id, course_id, status, unlocked_at) VALUES (?, ?, ?, ?)""",
                        (user_id, next_course['course_id'], 'unlocked', datetime.utcnow())
                    ) # other fields default to 0/null
                    flash(f'Next course unlocked (new progress created)!', 'info')


    elif new_attempts <= 3:
        new_status = 'in_progress' # Or a more specific 'failed_attempt' if desired
        flash(f'Your score: {current_total_score}. You need 70 to pass. Attempts left: {3 - new_attempts}. Keep trying!', 'warning')
    else: # attempts > 3 and not passed
        new_status = 'failed'
        flash(f'Your score: {current_total_score}. Maximum attempts ({new_attempts-1}) reached for this course. This course is now marked as failed.', 'danger')

    try:
        db.execute(
            'UPDATE UserProgress SET status = ?, attempts = ?, last_attempt_at = ?, completed_at = ? WHERE progress_id = ?',
            (new_status, new_attempts, datetime.utcnow(), datetime.utcnow() if course_completed_successfully else user_progress['completed_at'], user_progress['progress_id'])
        )
        db.commit()
    except Exception as e:
        db.rollback()
        flash(f"Error updating course completion status: {e}", 'danger')

    return redirect(url_for('course_detail', course_id=course_id))

# --- End Assessment Submission and Completion Routes ---

# --- Achievement Helper Function ---
def check_and_award_achievement(user_id, achievement_name, db):
    """
    Checks if a user should be awarded an achievement and processes it.
    Assumes 'db' is an active database connection.
    Does not commit; commit should be handled by the calling route.
    """
    try:
        achievement = db.execute("SELECT achievement_id, xp_bonus FROM Achievements WHERE achievement_name = ?", (achievement_name,)).fetchone()
        if not achievement:
            print(f"Achievement '{achievement_name}' not found in database.")
            return

        achievement_id = achievement['achievement_id']
        xp_bonus = achievement['xp_bonus']

        # Check if user already has this achievement
        existing_user_achievement = db.execute(
            "SELECT user_achievement_id FROM UserAchievements WHERE user_id = ? AND achievement_id = ?",
            (user_id, achievement_id)
        ).fetchone()

        if existing_user_achievement:
            # print(f"User {user_id} already has achievement '{achievement_name}'.")
            return

        # Award achievement
        db.execute(
            "INSERT INTO UserAchievements (user_id, achievement_id, unlocked_at) VALUES (?, ?, ?)",
            (user_id, achievement_id, datetime.utcnow())
        )
        
        # Update user's XP
        current_xp = db.execute("SELECT xp_points FROM Users WHERE user_id = ?", (user_id,)).fetchone()['xp_points']
        new_xp = (current_xp or 0) + (xp_bonus or 0)
        db.execute("UPDATE Users SET xp_points = ? WHERE user_id = ?", (new_xp, user_id))
        
        # Update session XP if the current user is the one getting the achievement
        if 'user_id' in session and session['user_id'] == user_id:
            session['xp_points'] = new_xp
        
        flash(f"Achievement Unlocked: {achievement_name}! +{xp_bonus} XP", 'success')
        print(f"Awarded achievement '{achievement_name}' to user {user_id}. XP Bonus: {xp_bonus}")

    except sqlite3.Error as e:
        # Handle potential database errors during the process
        # It's important this function doesn't crash the main flow.
        # The calling function should handle commit/rollback.
        print(f"Database error in check_and_award_achievement for '{achievement_name}': {e}")
        # Consider re-raising if the calling function should handle rollback db.rollback()
    except Exception as ex:
        print(f"Generic error in check_and_award_achievement for '{achievement_name}': {ex}")

# --- Leaderboard and User Achievements Routes ---
@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        flash('Please log in to view the leaderboard.', 'info')
        return redirect(url_for('login'))
    
    db = get_db()
    # Fetch top 20 users by XP points
    top_users = db.execute(
        "SELECT username, xp_points FROM Users ORDER BY xp_points DESC, user_id ASC LIMIT 20"
    ).fetchall()
    return render_template('leaderboard.html', users=top_users)

@app.route('/my_achievements')
def my_achievements():
    if 'user_id' not in session:
        flash('Please log in to view your achievements.', 'info')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db = get_db()
    
    user_achievements = db.execute("""
        SELECT a.achievement_name, a.description, a.xp_bonus, ua.unlocked_at
        FROM Achievements a
        JOIN UserAchievements ua ON a.achievement_id = ua.achievement_id
        WHERE ua.user_id = ?
        ORDER BY ua.unlocked_at DESC
    """, (user_id,)).fetchall()
    
    return render_template('my_achievements.html', achievements=user_achievements)

# --- End Leaderboard and User Achievements Routes ---

# --- Adaptive Learning: Path Survey and Personalized Support ---

@app.route('/path_survey', methods=['GET', 'POST'])
def path_survey():
    if 'user_id' not in session:
        flash('Please log in to take the path survey.', 'info')
        return redirect(url_for('login'))

    if request.method == 'POST':
        interest = request.form.get('interest')
        learn_style = request.form.get('learn_style')
        db = get_db()

        # Default suggestion
        suggested_path_name = "Learning Paths"
        suggested_url = url_for('learning_paths')
        suggestion_message = "Based on your choices, exploring our general Learning Paths might be a good start!"

        if interest == 'websites' and learn_style == 'stack':
            # Suggest "Web Development Stack"
            track = db.execute("SELECT track_id, track_name FROM Tracks WHERE track_name LIKE '%Web Development Stack%'").fetchone()
            if track:
                suggested_path_name = track['track_name']
                suggested_url = url_for('track_courses', track_id=track['track_id'])
                suggestion_message = f"We recommend the '{suggested_path_name}' track for you!"
            else: # Fallback if track name changes or not found
                path = db.execute("SELECT path_id, path_name FROM LearningPaths WHERE path_name LIKE '%Multi Programming Path%'").fetchone()
                if path:
                    suggested_path_name = path['path_name']
                    suggested_url = url_for('learning_path_tracks', path_id=path['path_id'])
                    suggestion_message = f"We recommend exploring our '{suggested_path_name}' for web development roles."

        elif interest == 'programming_logic' and learn_style == 'deep_dive':
            # Suggest "JavaScript Mastery Track" (as a default deep dive)
            track = db.execute("SELECT track_id, track_name FROM Tracks WHERE track_name LIKE '%JavaScript Mastery Track%'").fetchone()
            if track:
                suggested_path_name = track['track_name']
                suggested_url = url_for('track_courses', track_id=track['track_id'])
                suggestion_message = f"The '{suggested_path_name}' track would be a great fit for a deep dive into programming fundamentals!"
            else: # Fallback
                path = db.execute("SELECT path_id, path_name FROM LearningPaths WHERE path_name LIKE '%Single Programming Path%'").fetchone()
                if path:
                    suggested_path_name = path['path_name']
                    suggested_url = url_for('learning_path_tracks', path_id=path['path_id'])
                    suggestion_message = f"Consider our '{suggested_path_name}' for a deep dive into a specific language."
        
        elif interest == 'websites' and learn_style == 'deep_dive':
             # Could suggest JS or PHP path
            path = db.execute("SELECT path_id, path_name FROM LearningPaths WHERE path_name LIKE '%Single Programming Path%'").fetchone()
            if path:
                suggested_path_name = path['path_name']
                suggested_url = url_for('learning_path_tracks', path_id=path['path_id'])
                suggestion_message = f"For building websites with a deep focus, check out our '{suggested_path_name}' and choose a language like JavaScript or PHP."


        flash(f"Survey submitted! {suggestion_message}", 'success')
        return redirect(suggested_url)

    return render_template('path_survey.html')

# --- End Adaptive Learning ---

# --- Forum Routes ---
@app.route('/forum')
def forum_index():
    if 'user_id' not in session:
        flash('Please log in to access the forum.', 'info')
        return redirect(url_for('login'))
    db = get_db()
    categories = db.execute("SELECT category_id, name, description FROM ForumCategories ORDER BY name").fetchall()
    return render_template('forum_index.html', categories=categories)

@app.route('/forum/category/<int:category_id>')
def forum_category_threads(category_id):
    if 'user_id' not in session:
        flash('Please log in to view this category.', 'info')
        return redirect(url_for('login'))
    db = get_db()
    category = db.execute("SELECT category_id, name FROM ForumCategories WHERE category_id = ?", (category_id,)).fetchone()
    if not category:
        flash('Forum category not found.', 'danger')
        return redirect(url_for('forum_index'))
    
    threads = db.execute("""
        SELECT t.thread_id, t.title, t.created_at, u.username, COUNT(p.post_id) as post_count, MAX(p.created_at) as last_post_time
        FROM ForumThreads t
        JOIN Users u ON t.user_id = u.user_id
        LEFT JOIN ForumPosts p ON t.thread_id = p.thread_id
        WHERE t.category_id = ?
        GROUP BY t.thread_id, t.title, t.created_at, u.username
        ORDER BY last_post_time DESC, t.created_at DESC
    """, (category_id,)).fetchall()
    return render_template('forum_category_threads.html', category=category, threads=threads)

@app.route('/forum/category/<int:category_id>/create_thread', methods=['GET', 'POST'])
def forum_create_thread(category_id):
    if 'user_id' not in session:
        flash('Please log in to create a thread.', 'info')
        return redirect(url_for('login'))
    
    db = get_db()
    category = db.execute("SELECT category_id, name FROM ForumCategories WHERE category_id = ?", (category_id,)).fetchone()
    if not category:
        flash('Forum category not found.', 'danger')
        return redirect(url_for('forum_index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        user_id = session['user_id']

        if not title or not content:
            flash('Title and content are required to create a thread.', 'warning')
        else:
            try:
                cursor = db.cursor()
                cursor.execute("INSERT INTO ForumThreads (category_id, user_id, title) VALUES (?, ?, ?)",
                               (category_id, user_id, title))
                thread_id = cursor.lastrowid
                db.execute("INSERT INTO ForumPosts (thread_id, user_id, content) VALUES (?, ?, ?)",
                           (thread_id, user_id, content))
                db.commit()
                flash('Thread created successfully!', 'success')
                return redirect(url_for('forum_thread_view', thread_id=thread_id))
            except sqlite3.Error as e:
                db.rollback()
                flash(f'Database error: {e}', 'danger')
        
    return render_template('forum_create_thread.html', category=category)

@app.route('/forum/thread/<int:thread_id>')
def forum_thread_view(thread_id):
    if 'user_id' not in session:
        flash('Please log in to view threads.', 'info')
        return redirect(url_for('login'))
    
    db = get_db()
    thread = db.execute("""
        SELECT t.thread_id, t.title, t.created_at as thread_created_at, u.username as thread_starter_username, c.category_id, c.name as category_name
        FROM ForumThreads t
        JOIN Users u ON t.user_id = u.user_id
        JOIN ForumCategories c ON t.category_id = c.category_id
        WHERE t.thread_id = ?
    """, (thread_id,)).fetchone()

    if not thread:
        flash('Thread not found.', 'danger')
        return redirect(url_for('forum_index'))
        
    posts = db.execute("""
        SELECT p.post_id, p.content, p.created_at, u.username
        FROM ForumPosts p
        JOIN Users u ON p.user_id = u.user_id
        WHERE p.thread_id = ?
        ORDER BY p.created_at ASC
    """, (thread_id,)).fetchall()
    
    return render_template('forum_thread_view.html', thread=thread, posts=posts)

@app.route('/forum/thread/<int:thread_id>/create_post', methods=['POST'])
def forum_create_post(thread_id):
    if 'user_id' not in session:
        flash('Please log in to post a reply.', 'info')
        return redirect(url_for('login'))

    content = request.form.get('content')
    user_id = session['user_id']

    if not content:
        flash('Content is required for a post.', 'warning')
        return redirect(url_for('forum_thread_view', thread_id=thread_id))

    db = get_db()
    # Check if thread exists
    thread = db.execute("SELECT thread_id FROM ForumThreads WHERE thread_id = ?", (thread_id,)).fetchone()
    if not thread:
        flash('Thread not found.', 'danger')
        return redirect(url_for('forum_index'))
        
    try:
        db.execute("INSERT INTO ForumPosts (thread_id, user_id, content) VALUES (?, ?, ?)",
                   (thread_id, user_id, content))
        db.commit()
        flash('Reply posted successfully!', 'success')
    except sqlite3.Error as e:
        db.rollback()
        flash(f'Database error: {e}', 'danger')
        
    return redirect(url_for('forum_thread_view', thread_id=thread_id))

# --- End Forum Routes ---

# --- Placeholder Routes for Mentorship and Collaboration ---
@app.route('/mentorship')
def mentorship():
    if 'user_id' not in session: # Optional: could be public
        flash('Please log in to view mentorship information.', 'info')
        return redirect(url_for('login'))
    return render_template('mentorship.html')

@app.route('/collaboration')
def collaboration():
    if 'user_id' not in session: # Optional: could be public
        flash('Please log in to view collaboration information.', 'info')
        return redirect(url_for('login'))
    return render_template('collaboration.html')

# --- End Placeholder Routes ---


# Command to initialize DB from CLI: flask init-db
@app.cli.command('init-db') # The duplicate logout function that was here has been removed.
def init_db_command():
    """Clear existing data and create new tables."""
    init_db(force_recreate=True)
    print('Database initialized (or re-initialized).')

if __name__ == '__main__':
    # Ensure DB is initialized before running the app for the first time
    # In a production environment, you might run `flask init-db` manually once.
    with app.app_context(): # Need app context for init_db if it uses get_db()
      init_db()
    # For now, Python will use the first definition of logout. # This comment also refers to the removed duplicate.
    app.run(debug=True, host='0.0.0.0', port=5001) # Running on a different port for clarity if needed
