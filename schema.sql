-- Users Table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    xp_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LearningPaths Table
CREATE TABLE LearningPaths (
    path_id INT AUTO_INCREMENT PRIMARY KEY,
    path_name VARCHAR(255) NOT NULL,
    path_description TEXT
);

-- Tracks Table
CREATE TABLE Tracks (
    track_id INT AUTO_INCREMENT PRIMARY KEY,
    track_name VARCHAR(255) NOT NULL,
    track_description TEXT,
    path_id INT,
    total_duration_weeks INT,
    FOREIGN KEY (path_id) REFERENCES LearningPaths(path_id)
);

-- Courses Table
CREATE TABLE Courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    track_id INT,
    course_name VARCHAR(255) NOT NULL,
    course_level_number INT NOT NULL,
    duration_days INT,
    core_concepts TEXT,
    interactive_elements_description TEXT,
    order_in_track INT,
    FOREIGN KEY (track_id) REFERENCES Tracks(track_id)
);

-- Assessments Table
CREATE TABLE Assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT,
    assessment_type VARCHAR(50), -- Enum-like: 'Theory', 'Practice', 'Project', 'Live Coding'
    description TEXT,
    weight_percentage INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

-- UserProgress Table
CREATE TABLE UserProgress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    course_id INT,
    status VARCHAR(50), -- Enum-like: 'locked', 'unlocked', 'in_progress', 'completed', 'failed'
    current_score_theory INT DEFAULT 0,
    current_score_practice INT DEFAULT 0,
    current_score_project INT DEFAULT 0,
    current_score_live_coding INT DEFAULT 0,
    total_score INT DEFAULT 0,
    attempts INT DEFAULT 0,
    unlocked_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    last_attempt_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

-- Achievements Table
CREATE TABLE Achievements (
    achievement_id INT AUTO_INCREMENT PRIMARY KEY,
    achievement_name VARCHAR(255) NOT NULL,
    description TEXT,
    criteria TEXT,
    xp_bonus INT DEFAULT 0,
    achievement_type VARCHAR(50) -- Enum-like: 'Single Programming', 'Multi Programming', 'Universal'
);

-- UserAchievements Table
CREATE TABLE UserAchievements (
    user_achievement_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    achievement_id INT,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (achievement_id) REFERENCES Achievements(achievement_id)
);

-- Forum Categories Table
CREATE TABLE ForumCategories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

-- Forum Threads Table
CREATE TABLE ForumThreads (
    thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES ForumCategories(category_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Forum Posts Table
CREATE TABLE ForumPosts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES ForumThreads(thread_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
kodefun-initial-build

-- Quiz System Tables
CREATE TABLE IF NOT EXISTS QuizQuestions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'multiple-choice', -- e.g., 'multiple-choice', 'true-false'
    FOREIGN KEY (assessment_id) REFERENCES Assessments(assessment_id)
);

CREATE TABLE IF NOT EXISTS QuizChoices (
    choice_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    choice_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES QuizQuestions(question_id)
);

CREATE TABLE IF NOT EXISTS UserQuizAttempts (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    assessment_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL, -- For context and linking back to UserProgress easily
    attempt_number INTEGER DEFAULT 1,
    score INTEGER, -- e.g., percentage or raw score
    max_score INTEGER, -- Max possible score for this quiz instance
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (assessment_id) REFERENCES Assessments(assessment_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

CREATE TABLE IF NOT EXISTS UserQuizAnswers (
    user_answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    chosen_choice_id INTEGER, -- Can be NULL if user skips a question (not implemented yet)
    is_correct BOOLEAN, -- Recorded at time of answering
    FOREIGN KEY (attempt_id) REFERENCES UserQuizAttempts(attempt_id),
    FOREIGN KEY (question_id) REFERENCES QuizQuestions(question_id),
    FOREIGN KEY (chosen_choice_id) REFERENCES QuizChoices(choice_id)
);

-- Coding Exercise Tables
CREATE TABLE IF NOT EXISTS CodingExercises (
    exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    starter_code TEXT,
    function_name VARCHAR(100) DEFAULT 'solve', 
    FOREIGN KEY (assessment_id) REFERENCES Assessments(assessment_id)
);

CREATE TABLE IF NOT EXISTS CodingExerciseTestCases (
    test_case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    input_data TEXT,  -- JSON string for arguments array, e.g., '[1, 2]' or '["hello"]'
    expected_output TEXT, -- JSON string for expected result, e.g., '3' or '"olleh"'
    is_hidden BOOLEAN DEFAULT FALSE,
    description TEXT, -- Optional description for the test case
    FOREIGN KEY (exercise_id) REFERENCES CodingExercises(exercise_id)
);

CREATE TABLE IF NOT EXISTS UserCodingSubmissions (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    assessment_id INTEGER NOT NULL, 
    course_id INTEGER NOT NULL,
    submitted_code TEXT NOT NULL,
    passed_tests INTEGER NOT NULL,
    total_tests INTEGER NOT NULL,
    score INTEGER NOT NULL, -- Percentage: (passed_tests / total_tests) * 100
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    results_details TEXT, -- JSON string of individual test results if needed
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (exercise_id) REFERENCES CodingExercises(exercise_id),
    FOREIGN KEY (assessment_id) REFERENCES Assessments(assessment_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
main
