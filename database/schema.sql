-- Questions table
CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    option_a VARCHAR(500) NOT NULL,
    option_b VARCHAR(500) NOT NULL,
    option_c VARCHAR(500) NOT NULL,
    option_d VARCHAR(500) NOT NULL,
    correct_option CHAR(1) NOT NULL,
    explanation TEXT,
    difficulty ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test attempts table
CREATE TABLE test_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100),
    subject VARCHAR(50) NOT NULL,
    score INT NOT NULL,
    total_questions INT NOT NULL,
    time_taken INT, -- in seconds
    answers JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User stats table
CREATE TABLE user_stats (
    user_id VARCHAR(100) PRIMARY KEY,
    total_tests INT DEFAULT 0,
    avg_score FLOAT DEFAULT 0,
    subjects_attempted JSON,
    last_test_date TIMESTAMP
);