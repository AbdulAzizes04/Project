-- =============================================================================
-- EXPLAINABLE AI FRAMEWORK FOR PERSONALIZED CAREER RECOMMENDATION
-- Database Schema (MySQL 8.0+)
-- Department of Artificial Intelligence and Data Science
-- =============================================================================

CREATE DATABASE IF NOT EXISTS career_ai_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE career_ai_db;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS model_metrics;
DROP TABLE IF EXISTS student_progress;
DROP TABLE IF EXISTS learning_resources;
DROP TABLE IF EXISTS skill_gaps;
DROP TABLE IF EXISTS recommendation_explanations;
DROP TABLE IF EXISTS career_recommendations;
DROP TABLE IF EXISTS career_projects;
DROP TABLE IF EXISTS career_certifications;
DROP TABLE IF EXISTS career_skills;
DROP TABLE IF EXISTS career_roles;
DROP TABLE IF EXISTS career_interests;
DROP TABLE IF EXISTS aptitude_scores;
DROP TABLE IF EXISTS student_projects;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS student_certifications;
DROP TABLE IF EXISTS certifications;
DROP TABLE IF EXISTS student_skills;
DROP TABLE IF EXISTS skill_aliases;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS academic_records;
DROP TABLE IF EXISTS student_profiles;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- 1. USERS TABLE (Authentication & Authorization)
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('STUDENT', 'ADMIN') NOT NULL DEFAULT 'STUDENT',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. STUDENT PROFILES TABLE (Personal Information)
-- -----------------------------------------------------------------------------
CREATE TABLE student_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(100),
    batch VARCHAR(50),
    branch VARCHAR(100),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_sp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_sp_batch (batch),
    INDEX idx_sp_branch (branch)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. ACADEMIC RECORDS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE academic_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    tenth_percentage DECIMAL(5,2),
    twelfth_percentage DECIMAL(5,2),
    cgpa DECIMAL(4,2),
    semester_scores JSON,              -- {"sem1": 8.2, "sem2": 8.4, ...}
    core_subject_performance JSON,     -- {"dsa": 85, "dbms": 88, "os": 80, "ai": 90}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ar_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    INDEX idx_ar_cgpa (cgpa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. SKILLS TABLE (Centralized Skill Repository)
-- -----------------------------------------------------------------------------
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,     -- Programming, Frontend, Backend, Database, Cloud, AI/ML, DevOps, Core
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_skills_name (name),
    INDEX idx_skills_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 5. SKILL ALIASES TABLE (Normalization Mapping)
-- -----------------------------------------------------------------------------
CREATE TABLE skill_aliases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT NOT NULL,
    alias VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sa_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    INDEX idx_sa_alias (alias)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 6. STUDENT SKILLS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE student_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED') NOT NULL DEFAULT 'INTERMEDIATE',
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ss_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_ss_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_skill (student_id, skill_id),
    INDEX idx_ss_proficiency (proficiency_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 7. CERTIFICATIONS CATALOG TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE certifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    issuer VARCHAR(150) NOT NULL,
    domain VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cert_domain (domain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 8. STUDENT CERTIFICATIONS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE student_certifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    certification_name VARCHAR(200) NOT NULL,
    issuer VARCHAR(150) NOT NULL,
    issue_date DATE,
    domain VARCHAR(100),
    verification_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_sc_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    INDEX idx_sc_domain (domain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 9. PROJECTS CATALOG TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    domain VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_proj_domain (domain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 10. STUDENT PROJECTS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE student_projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    description TEXT,
    technologies JSON,                 -- ["Python", "FastAPI", "React"]
    domain VARCHAR(100),
    complexity ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL DEFAULT 'MEDIUM',
    role VARCHAR(100),
    duration_months INT DEFAULT 1,
    project_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_sp_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    INDEX idx_sp_complexity (complexity),
    INDEX idx_sp_domain (domain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 11. APTITUDE SCORES TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE aptitude_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    quantitative_score DECIMAL(5,2) DEFAULT 0.00,
    logical_reasoning_score DECIMAL(5,2) DEFAULT 0.00,
    verbal_score DECIMAL(5,2) DEFAULT 0.00,
    technical_aptitude_score DECIMAL(5,2) DEFAULT 0.00,
    total_score DECIMAL(5,2) DEFAULT 0.00,
    assessment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_apt_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    INDEX idx_apt_total (total_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 12. CAREER INTERESTS & SOFT SKILLS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE career_interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    preferred_domains JSON,            -- ["Artificial Intelligence", "Web Development"]
    career_interests JSON,             -- ["AI/ML Engineer", "Data Scientist"]
    preferred_technologies JSON,       -- ["Python", "PyTorch", "FastAPI"]
    soft_skills JSON,                  -- {"communication": 4, "leadership": 3, "teamwork": 5, "problem_solving": 4}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ci_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 13. CAREER ROLES TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE career_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    min_cgpa DECIMAL(4,2) DEFAULT 6.00,
    min_tenth_pct DECIMAL(5,2) DEFAULT 60.00,
    min_twelfth_pct DECIMAL(5,2) DEFAULT 60.00,
    min_aptitude_score DECIMAL(5,2) DEFAULT 60.00,
    difficulty_level ENUM('ENTRY', 'INTERMEDIATE', 'ADVANCED') DEFAULT 'ENTRY',
    salary_range VARCHAR(100),
    market_demand VARCHAR(50) DEFAULT 'HIGH',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cr_slug (slug),
    INDEX idx_cr_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 14. CAREER SKILLS TABLE (Requirements & Weights)
-- -----------------------------------------------------------------------------
CREATE TABLE career_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    career_id INT NOT NULL,
    skill_id INT NOT NULL,
    importance_weight DECIMAL(4,2) NOT NULL DEFAULT 1.00, -- 1.00 to 5.00
    is_required BOOLEAN NOT NULL DEFAULT TRUE,            -- Required vs Preferred
    min_proficiency ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED') DEFAULT 'INTERMEDIATE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cs_career FOREIGN KEY (career_id) REFERENCES career_roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_cs_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY uq_career_skill (career_id, skill_id),
    INDEX idx_cs_required (is_required)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 15. CAREER CERTIFICATIONS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE career_certifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    career_id INT NOT NULL,
    certification_name VARCHAR(200) NOT NULL,
    domain VARCHAR(100),
    relevance_weight DECIMAL(4,2) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cc_career FOREIGN KEY (career_id) REFERENCES career_roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 16. CAREER PROJECTS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE career_projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    career_id INT NOT NULL,
    project_type VARCHAR(200) NOT NULL,
    description TEXT,
    suggested_tech JSON,
    relevance_weight DECIMAL(4,2) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cp_career FOREIGN KEY (career_id) REFERENCES career_roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 17. CAREER RECOMMENDATIONS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE career_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    career_id INT NOT NULL,
    compatibility_score DECIMAL(5,2) NOT NULL,           -- Model Compatibility Score (0 - 100%)
    rank_order INT NOT NULL,                             -- Rank 1 to 5
    ml_confidence DECIMAL(5,2) DEFAULT 0.00,
    skill_compatibility DECIMAL(5,2) DEFAULT 0.00,
    academic_compatibility DECIMAL(5,2) DEFAULT 0.00,
    project_compatibility DECIMAL(5,2) DEFAULT 0.00,
    certification_compatibility DECIMAL(5,2) DEFAULT 0.00,
    aptitude_compatibility DECIMAL(5,2) DEFAULT 0.00,
    interest_compatibility DECIMAL(5,2) DEFAULT 0.00,
    domain_compatibility DECIMAL(5,2) DEFAULT 0.00,
    matching_skills JSON,
    missing_skills JSON,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cr_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_cr_career FOREIGN KEY (career_id) REFERENCES career_roles(id) ON DELETE CASCADE,
    INDEX idx_cr_student_rank (student_id, rank_order),
    INDEX idx_cr_score (compatibility_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 18. RECOMMENDATION EXPLANATIONS TABLE (SHAP & LIME XAI)
-- -----------------------------------------------------------------------------
CREATE TABLE recommendation_explanations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recommendation_id INT NOT NULL UNIQUE,
    shap_values JSON,                  -- Local SHAP feature attribution array
    lime_values JSON,                  -- LIME perturbed feature contribution array
    top_positive_factors JSON,         -- Top factors lifting compatibility
    top_negative_factors JSON,         -- Top factors dampening compatibility
    human_readable_text TEXT NOT NULL, -- Transparent, ethical explanatory narrative
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_re_recommendation FOREIGN KEY (recommendation_id) REFERENCES career_recommendations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 19. SKILL GAPS TABLE (Competency Tracking)
-- -----------------------------------------------------------------------------
CREATE TABLE skill_gaps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    career_id INT NOT NULL,
    skill_id INT NOT NULL,
    gap_status ENUM('STRONG', 'MODERATE', 'MISSING') NOT NULL,
    student_level ENUM('NONE', 'BEGINNER', 'INTERMEDIATE', 'ADVANCED') DEFAULT 'NONE',
    required_level ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED') DEFAULT 'INTERMEDIATE',
    learning_priority ENUM('HIGH', 'MEDIUM', 'LOW') NOT NULL,
    priority_score DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_sg_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_sg_career FOREIGN KEY (career_id) REFERENCES career_roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_sg_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_career_skill_gap (student_id, career_id, skill_id),
    INDEX idx_sg_priority (learning_priority),
    INDEX idx_sg_gap (gap_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 20. LEARNING RESOURCES TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE learning_resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    skill_id INT NOT NULL,
    title VARCHAR(250) NOT NULL,
    resource_type ENUM('COURSE', 'DOCUMENTATION', 'BOOK', 'TUTORIAL', 'PROJECT') DEFAULT 'COURSE',
    platform VARCHAR(100),
    url VARCHAR(500) NOT NULL,
    estimated_hours INT DEFAULT 10,
    difficulty ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED') DEFAULT 'BEGINNER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_lr_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    INDEX idx_lr_skill (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 21. STUDENT PROGRESS TABLE (Personal Learning Tracker)
-- -----------------------------------------------------------------------------
CREATE TABLE student_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    skill_id INT NULL,
    item_type ENUM('SKILL', 'COURSE', 'PROJECT', 'CERTIFICATION', 'MILESTONE') NOT NULL,
    title VARCHAR(250) NOT NULL,
    week_number INT DEFAULT 1,
    status ENUM('NOT_STARTED', 'LEARNING', 'COMPLETED') DEFAULT 'NOT_STARTED',
    progress_percent INT DEFAULT 0,
    notes TEXT,
    target_completion_date DATE,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_prog_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_prog_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE SET NULL,
    INDEX idx_prog_status (status),
    INDEX idx_prog_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 22. MODEL METRICS TABLE (ML Auditing & Validation)
-- -----------------------------------------------------------------------------
CREATE TABLE model_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    accuracy DECIMAL(5,4),
    precision_macro DECIMAL(5,4),
    recall_macro DECIMAL(5,4),
    f1_macro DECIMAL(5,4),
    roc_auc DECIMAL(5,4),
    train_samples INT,
    test_samples INT,
    confusion_matrix JSON,
    feature_importance JSON,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mm_model (model_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 23. AUDIT LOGS TABLE
-- -----------------------------------------------------------------------------
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(100) NOT NULL,
    entity VARCHAR(100),
    details JSON,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_al_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_al_action (action),
    INDEX idx_al_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
