-- Create database and user for the coding platform
CREATE DATABASE IF NOT EXISTS coding_platform;
CREATE USER IF NOT EXISTS 'platform_user'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON coding_platform.* TO 'platform_user'@'%';
FLUSH PRIVILEGES;

USE coding_platform;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    rating INT DEFAULT 1200,
    total_submissions INT DEFAULT 0,
    accepted_submissions INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_rating (rating)
);

-- Problems table
CREATE TABLE IF NOT EXISTS problems (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    difficulty ENUM('Easy', 'Medium', 'Hard') NOT NULL,
    category VARCHAR(50),
    time_limit INT DEFAULT 2000,
    memory_limit INT DEFAULT 256,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    tags VARCHAR(500),
    hints TEXT,
    editorial TEXT,
    constraints TEXT,
    total_submissions INT DEFAULT 0,
    accepted_submissions INT DEFAULT 0,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_slug (slug),
    INDEX idx_difficulty (difficulty),
    INDEX idx_category (category),
    INDEX idx_active (is_active)
);

-- Test cases table
CREATE TABLE IF NOT EXISTS test_cases (
    id INT PRIMARY KEY AUTO_INCREMENT,
    problem_id INT NOT NULL,
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_sample BOOLEAN DEFAULT FALSE,
    is_hidden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(200),
    weight FLOAT DEFAULT 1.0,
    time_limit_override INT,
    memory_limit_override INT,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE,
    INDEX idx_problem_id (problem_id),
    INDEX idx_sample (is_sample),
    INDEX idx_hidden (is_hidden)
);

-- Contests table
CREATE TABLE IF NOT EXISTS contests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    created_by INT,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    max_participants INT,
    registration_start TIMESTAMP,
    registration_end TIMESTAMP,
    is_rated BOOLEAN DEFAULT TRUE,
    contest_type ENUM('Individual', 'Team', 'Educational') DEFAULT 'Individual',
    scoring_type ENUM('ACM', 'IOI', 'AtCoder') DEFAULT 'ACM',
    penalty_per_wrong_submission INT DEFAULT 20,
    FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_start_time (start_time),
    INDEX idx_end_time (end_time),
    INDEX idx_public (is_public)
);

-- Submissions table
CREATE TABLE IF NOT EXISTS submissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    problem_id INT NOT NULL,
    language VARCHAR(20) NOT NULL,
    code TEXT NOT NULL,
    status ENUM('Pending', 'Running', 'Accepted', 'Wrong Answer', 
                'Time Limit Exceeded', 'Memory Limit Exceeded', 
                'Runtime Error', 'Compilation Error', 'System Error') DEFAULT 'Pending',
    runtime INT,
    memory_used INT,
    score DECIMAL(5,2) DEFAULT 0.00,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    contest_id INT,
    compiler_output TEXT,
    error_message TEXT,
    test_cases_passed INT DEFAULT 0,
    total_test_cases INT DEFAULT 0,
    execution_id VARCHAR(100),
    judged_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (problem_id) REFERENCES problems(id),
    FOREIGN KEY (contest_id) REFERENCES contests(id),
    INDEX idx_user_id (user_id),
    INDEX idx_problem_id (problem_id),
    INDEX idx_contest_id (contest_id),
    INDEX idx_status (status),
    INDEX idx_submitted_at (submitted_at)
);

-- Contest problems association table
CREATE TABLE IF NOT EXISTS contest_problems (
    contest_id INT NOT NULL,
    problem_id INT NOT NULL,
    problem_order INT DEFAULT 0,
    points INT DEFAULT 100,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contest_id, problem_id),
    FOREIGN KEY (contest_id) REFERENCES contests(id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);

-- Contest participants association table
CREATE TABLE IF NOT EXISTS contest_participants (
    contest_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_registered BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (contest_id, user_id),
    FOREIGN KEY (contest_id) REFERENCES contests(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);