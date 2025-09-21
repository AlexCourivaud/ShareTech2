-- ShareTech Database Initialization
USE sharetech_memory;

-- Create USER table
CREATE TABLE IF NOT EXISTS auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL
) ENGINE=InnoDB;

-- Create USER_PROFILE table for extended fields
CREATE TABLE IF NOT EXISTS accounts_userprofile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    role ENUM('junior', 'senior', 'lead', 'admin') DEFAULT 'junior',
    avatar_url VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create PROJECT table
CREATE TABLE IF NOT EXISTS core_project (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    created_by_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create PROJECT_MEMBER table
CREATE TABLE IF NOT EXISTS core_projectmember (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_project_user (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES core_project(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create NOTE table
CREATE TABLE IF NOT EXISTS core_note (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    project_id INT NOT NULL,
    author_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES core_project(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create TAG table
CREATE TABLE IF NOT EXISTS core_tag (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7) DEFAULT '#6b7280',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create NOTE_TAG table
CREATE TABLE IF NOT EXISTS core_note_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    note_id INT NOT NULL,
    tag_id INT NOT NULL,
    UNIQUE KEY unique_note_tag (note_id, tag_id),
    FOREIGN KEY (note_id) REFERENCES core_note(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES core_tag(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Insert default admin user (password: admin123)
INSERT IGNORE INTO auth_user (username, email, password, first_name, last_name, is_superuser, is_staff) 
VALUES ('admin', 'admin@sharetech.com', 'pbkdf2_sha256$260000$test$hash', 'Admin', 'ShareTech', TRUE, TRUE);

-- Insert admin profile
INSERT IGNORE INTO accounts_userprofile (user_id, role) 
SELECT id, 'admin' FROM auth_user WHERE username = 'admin';

-- Insert default tags
INSERT IGNORE INTO core_tag (name, color) VALUES 
('Documentation', '#3b82f6'),
('Bug', '#ef4444'),
('Feature', '#10b981'),
('Tutorial', '#f59e0b'),
('API', '#8b5cf6');

-- Create demo project
INSERT IGNORE INTO core_project (name, description, created_by_id) 
SELECT 'Projet Demo', 'Projet de démonstration ShareTech', id FROM auth_user WHERE username = 'admin';

-- Add admin to demo project
INSERT IGNORE INTO core_projectmember (project_id, user_id) 
SELECT p.id, u.id FROM core_project p, auth_user u WHERE p.name = 'Projet Demo' AND u.username = 'admin';

-- Add demo note
INSERT IGNORE INTO core_note (title, content, project_id, author_id) 
SELECT 
    'Note de bienvenue', 
    'Bienvenue sur ShareTech ! Cette note de démonstration vous montre comment fonctionne la plateforme.',
    p.id,
    u.id
FROM core_project p, auth_user u 
WHERE p.name = 'Projet Demo' AND u.username = 'admin';