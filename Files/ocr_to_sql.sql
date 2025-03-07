-- Create a table to store education details
CREATE TABLE education (
    id INT AUTO_INCREMENT PRIMARY KEY,
    degree_name VARCHAR(255),
    university_name VARCHAR(255),
    start_date DATE,
    end_date DATE
);

-- Create a table to store professional experience
CREATE TABLE professional_experience (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(255),
    company_name VARCHAR(255),
    start_date DATE,
    end_date DATE
);
