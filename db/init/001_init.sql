-- MySQL schema init

-- Ensure using the correct database (created by container env)
USE code_platform;

-- Users
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rating INT NOT NULL DEFAULT 1500,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Challenges
CREATE TABLE IF NOT EXISTS challenges (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    difficulty ENUM('easy','medium','hard') NOT NULL DEFAULT 'easy',
    description MEDIUMTEXT NOT NULL,
    starter_code JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_challenges_difficulty (difficulty)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Test Cases
CREATE TABLE IF NOT EXISTS test_cases (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    challenge_id BIGINT UNSIGNED NOT NULL,
    input_text MEDIUMTEXT NOT NULL,
    expected_output MEDIUMTEXT NOT NULL,
    is_hidden TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_test_cases_challenge FOREIGN KEY (challenge_id)
        REFERENCES challenges(id) ON DELETE CASCADE,
    INDEX idx_test_cases_challenge (challenge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Submissions
CREATE TABLE IF NOT EXISTS submissions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    challenge_id BIGINT UNSIGNED NOT NULL,
    language VARCHAR(32) NOT NULL,
    code MEDIUMTEXT NOT NULL,
    status ENUM('queued','running','passed','failed','error') NOT NULL DEFAULT 'queued',
    runtime_ms INT NULL,
    memory_kb INT NULL,
    score INT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_submissions_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_submissions_challenge FOREIGN KEY (challenge_id)
        REFERENCES challenges(id) ON DELETE CASCADE,
    INDEX idx_submissions_user (user_id),
    INDEX idx_submissions_challenge (challenge_id),
    INDEX idx_submissions_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ratings history (optional)
CREATE TABLE IF NOT EXISTS rating_history (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    previous_rating INT NOT NULL,
    new_rating INT NOT NULL,
    reason VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rating_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_rating_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;