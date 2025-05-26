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
