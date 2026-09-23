-- =============================================================================
-- EXPLAINABLE AI FRAMEWORK FOR PERSONALIZED CAREER RECOMMENDATION
-- Seed Data (MySQL 8.0+)
-- Department of Artificial Intelligence and Data Science
-- =============================================================================

USE career_ai_db;

-- -----------------------------------------------------------------------------
-- 1. SEED USERS (Admin and Demo Student)
-- Passwords:
-- Admin:   Admin@123   -> $2b$12$Y1avdz9LPAPdGPQ5uUdCveXPwTdxIXSkAYxotdrGhd4ehT0i8jUMy
-- Student: Student@123 -> $2b$12$K7vLwHkKGNqQal4TDxDQ0ubjJOXI284uKnoUlog1bN6RzSGTRjYPG
-- -----------------------------------------------------------------------------
INSERT INTO users (id, email, password_hash, role, is_active) VALUES
(1, 'admin@careerai.edu', '$2b$12$Y1avdz9LPAPdGPQ5uUdCveXPwTdxIXSkAYxotdrGhd4ehT0i8jUMy', 'ADMIN', TRUE),
(2, 'student@careerai.edu', '$2b$12$K7vLwHkKGNqQal4TDxDQ0ubjJOXI284uKnoUlog1bN6RzSGTRjYPG', 'STUDENT', TRUE);

-- -----------------------------------------------------------------------------
-- 2. SEED STUDENT PROFILE
-- -----------------------------------------------------------------------------
INSERT INTO student_profiles (id, user_id, name, phone, location, batch, branch, bio) VALUES
(1, 2, 'Abdul Aziz', '+91 9876543210', 'Rajampet, Andhra Pradesh', '2023-2027', 'Artificial Intelligence and Data Science', 'Final year B.Tech AIDS student passionate about machine learning, explainable AI, and full-stack software development.');

-- -----------------------------------------------------------------------------
-- 3. SEED ACADEMIC RECORDS
-- -----------------------------------------------------------------------------
INSERT INTO academic_records (student_id, tenth_percentage, twelfth_percentage, cgpa, semester_scores, core_subject_performance) VALUES
(1, 92.50, 89.00, 8.65,
 '{"sem1": 8.4, "sem2": 8.5, "sem3": 8.7, "sem4": 8.6, "sem5": 8.8, "sem6": 8.9}',
 '{"Data Structures & Algorithms": 88, "Database Management Systems": 92, "Machine Learning": 90, "Operating Systems": 84, "Computer Networks": 82, "Deep Learning": 89}');

-- -----------------------------------------------------------------------------
-- 4. SEED APTITUDE SCORES
-- -----------------------------------------------------------------------------
INSERT INTO aptitude_scores (student_id, quantitative_score, logical_reasoning_score, verbal_score, technical_aptitude_score, total_score, assessment_date) VALUES
(1, 85.00, 88.00, 82.00, 92.00, 86.75, '2026-02-15');

-- -----------------------------------------------------------------------------
-- 5. SEED CAREER INTERESTS
-- -----------------------------------------------------------------------------
INSERT INTO career_interests (student_id, preferred_domains, career_interests, preferred_technologies, soft_skills) VALUES
(1,
 '["Artificial Intelligence", "Data Science", "Web Development"]',
 '["AI/ML Engineer", "Data Scientist", "Software Developer"]',
 '["Python", "PyTorch", "FastAPI", "React", "SQL"]',
 '{"communication": 4, "leadership": 4, "teamwork": 5, "problem_solving": 5}');

-- -----------------------------------------------------------------------------
-- 6. SEED CENTRALIZED SKILLS CATALOG (35+ Standardized Skills)
-- -----------------------------------------------------------------------------
INSERT INTO skills (id, name, category, description) VALUES
(1, 'HTML', 'Frontend', 'Standard markup language for documents designed to be displayed in a web browser.'),
(2, 'CSS', 'Frontend', 'Style sheet language used for describing the presentation of a document.'),
(3, 'JavaScript', 'Programming', 'High-level, interpreted scripting language that conforms to the ECMAScript specification.'),
(4, 'TypeScript', 'Programming', 'Strict syntactical superset of JavaScript adding optional static typing.'),
(5, 'React', 'Frontend', 'Open-source, front end, JavaScript library for building user interfaces or UI components.'),
(6, 'Next.js', 'Frontend', 'React framework for server-side rendering and static web applications.'),
(7, 'Node.js', 'Backend', 'Open-source, cross-platform, back-end JavaScript runtime environment.'),
(8, 'Python', 'Programming', 'High-level, general-purpose programming language renowned for AI and Data Science.'),
(9, 'Java', 'Programming', 'High-level, class-based, object-oriented programming language designed for portability.'),
(10, 'C', 'Programming', 'General-purpose, procedural computer programming language supporting structured programming.'),
(11, 'C++', 'Programming', 'General-purpose programming language created as an extension of C with OOP features.'),
(12, 'SQL', 'Database', 'Domain-specific language used in programming and managing relational databases.'),
(13, 'MySQL', 'Database', 'Open-source relational database management system based on SQL.'),
(14, 'PostgreSQL', 'Database', 'Free and open-source relational database management system emphasizing extensibility.'),
(15, 'MongoDB', 'Database', 'Source-available cross-platform document-oriented database program classified as NoSQL.'),
(16, 'Pandas', 'Data Science', 'Software library written for data manipulation and analysis in Python.'),
(17, 'NumPy', 'Data Science', 'Library adding support for large, multi-dimensional arrays and matrices in Python.'),
(18, 'Scikit-learn', 'AI/ML', 'Machine learning library for Python featuring classification, regression, and clustering.'),
(19, 'TensorFlow', 'AI/ML', 'Free and open-source software library for machine learning and artificial intelligence.'),
(20, 'PyTorch', 'AI/ML', 'Open source machine learning framework based on the Torch library.'),
(21, 'Machine Learning', 'AI/ML', 'Study of computer algorithms that improve automatically through experience and data.'),
(22, 'Deep Learning', 'AI/ML', 'Part of machine learning methods based on artificial neural networks with representation learning.'),
(23, 'Statistics', 'Data Science', 'Mathematical discipline concerned with data collection, analysis, interpretation, and presentation.'),
(24, 'Power BI', 'Data Science', 'Interactive data visualization software product developed by Microsoft for BI.'),
(25, 'Tableau', 'Data Science', 'Interactive data visualization software company focused on business intelligence.'),
(26, 'AWS', 'Cloud', 'Comprehensive, evolving cloud computing platform provided by Amazon.'),
(27, 'GCP', 'Cloud', 'Suite of cloud computing services that runs on the same infrastructure that Google uses.'),
(28, 'Azure', 'Cloud', 'Cloud computing service operated by Microsoft for application management.'),
(29, 'Docker', 'DevOps', 'Set of platform as a service products using OS-level virtualization to deliver software in containers.'),
(30, 'Kubernetes', 'DevOps', 'Open-source system for automating deployment, scaling, and management of containerized apps.'),
(31, 'Git', 'DevOps', 'Distributed version-control system for tracking changes in source code during development.'),
(32, 'FastAPI', 'Backend', 'Modern, fast (high-performance) web framework for building APIs with Python.'),
(33, 'Linux', 'DevOps', 'Family of open-source Unix-like operating systems based on the Linux kernel.'),
(34, 'Data Structures & Algorithms', 'Core', 'Core foundations of computer science for efficient data storage and computational problem-solving.'),
(35, 'REST API', 'Backend', 'Architectural style for distributed hypermedia systems communicating via HTTP.');

-- -----------------------------------------------------------------------------
-- 7. SEED SKILL ALIASES (Normalization System)
-- -----------------------------------------------------------------------------
INSERT INTO skill_aliases (skill_id, alias) VALUES
(3, 'JS'),
(3, 'Javascript'),
(3, 'Java Script'),
(3, 'vanilla js'),
(4, 'TS'),
(4, 'Typescript'),
(5, 'ReactJS'),
(5, 'React.js'),
(5, 'react-js'),
(6, 'NextJS'),
(6, 'Next.js'),
(7, 'NodeJS'),
(7, 'Node.js'),
(7, 'node'),
(8, 'Py'),
(8, 'Python3'),
(8, 'Python 3'),
(11, 'Cpp'),
(11, 'C plus plus'),
(12, 'Structured Query Language'),
(12, 'Relational SQL'),
(16, 'Pandas Library'),
(17, 'Numpy Library'),
(18, 'Sklearn'),
(18, 'scikit learn'),
(19, 'TF'),
(19, 'Tensorflow'),
(20, 'Torch'),
(20, 'Pytorch'),
(21, 'ML'),
(21, 'Machine-Learning'),
(22, 'DL'),
(22, 'Deep-Learning'),
(22, 'Neural Networks'),
(24, 'PowerBI'),
(24, 'MS Power BI'),
(26, 'Amazon Web Services'),
(26, 'Amazon Cloud'),
(27, 'Google Cloud Platform'),
(27, 'Google Cloud'),
(28, 'Microsoft Azure'),
(28, 'MS Azure'),
(31, 'GitHub'),
(31, 'Version Control Git'),
(32, 'Fast API'),
(34, 'DSA'),
(34, 'Data Structures');

-- -----------------------------------------------------------------------------
-- 8. SEED STUDENT SKILLS
-- -----------------------------------------------------------------------------
INSERT INTO student_skills (student_id, skill_id, proficiency_level, verified) VALUES
(1, 8, 'ADVANCED', TRUE),      -- Python
(1, 16, 'ADVANCED', TRUE),     -- Pandas
(1, 17, 'ADVANCED', TRUE),     -- NumPy
(1, 18, 'ADVANCED', TRUE),     -- Scikit-learn
(1, 20, 'INTERMEDIATE', TRUE), -- PyTorch
(1, 21, 'ADVANCED', TRUE),     -- Machine Learning
(1, 22, 'INTERMEDIATE', TRUE), -- Deep Learning
(1, 12, 'ADVANCED', TRUE),     -- SQL
(1, 13, 'INTERMEDIATE', TRUE), -- MySQL
(1, 3, 'INTERMEDIATE', TRUE),  -- JavaScript
(1, 5, 'INTERMEDIATE', TRUE),  -- React
(1, 32, 'ADVANCED', TRUE),     -- FastAPI
(1, 31, 'INTERMEDIATE', TRUE), -- Git
(1, 34, 'ADVANCED', TRUE);     -- DSA

-- -----------------------------------------------------------------------------
-- 9. SEED STUDENT CERTIFICATIONS & PROJECTS
-- -----------------------------------------------------------------------------
INSERT INTO student_certifications (student_id, certification_name, issuer, issue_date, domain, verification_url) VALUES
(1, 'Machine Learning Specialization', 'DeepLearning.AI / Coursera', '2025-08-10', 'Artificial Intelligence', 'https://coursera.org/verify/ML-SPEC-2025-101'),
(1, 'Applied Data Science with Python', 'University of Michigan / Coursera', '2025-11-20', 'Data Science', 'https://coursera.org/verify/ADS-MICH-2025-202');

INSERT INTO student_projects (student_id, project_name, description, technologies, domain, complexity, role, duration_months, project_url) VALUES
(1, 'Explainable AI Career Recommendation System', 'An intelligent recommendation system utilizing SHAP, LIME, and skill analytics for B.Tech students.', '["Python", "FastAPI", "Scikit-learn", "SHAP", "LIME", "React", "Next.js"]', 'Artificial Intelligence', 'HIGH', 'Lead Full-Stack ML Engineer', 6, 'https://github.com/career-ai/project'),
(1, 'Deep Learning Medical Image Classifier', 'Convolutional neural network for automated diagnosis of chest X-rays with Grad-CAM visualization.', '["PyTorch", "Python", "OpenCV", "Streamlit"]', 'Deep Learning', 'HIGH', 'ML Developer', 4, 'https://github.com/med-vision/project');

-- -----------------------------------------------------------------------------
-- 10. SEED CAREER ROLES (7 Industry Roles)
-- -----------------------------------------------------------------------------
INSERT INTO career_roles (id, name, slug, description, min_cgpa, min_tenth_pct, min_twelfth_pct, min_aptitude_score, difficulty_level, salary_range, market_demand, is_active) VALUES
(1, 'Software Developer', 'software-developer', 'Engineers robust software applications, writes clean code, builds algorithmic solutions, and collaborates on modern system architectures.', 6.50, 60.00, 60.00, 65.00, 'ENTRY', '₹6,00,000 - ₹14,00,000', 'VERY HIGH', TRUE),
(2, 'Data Analyst', 'data-analyst', 'Interprets complex datasets, builds descriptive dashboards, uncovers business insights using SQL, statistical methods, and visualization tools.', 6.50, 60.00, 60.00, 65.00, 'ENTRY', '₹5,00,000 - ₹11,00,000', 'HIGH', TRUE),
(3, 'Data Scientist', 'data-scientist', 'Develops predictive statistical models, analyzes unstructured data, performs hypothesis testing, and engineers ML pipelines to solve business challenges.', 7.00, 65.00, 65.00, 75.00, 'INTERMEDIATE', '₹8,00,000 - ₹18,00,000', 'VERY HIGH', TRUE),
(4, 'AI/ML Engineer', 'aiml-engineer', 'Designs, trains, fine-tunes, and deploys scalable machine learning and deep learning models into production systems with monitoring and explainability.', 7.50, 70.00, 70.00, 80.00, 'ADVANCED', '₹10,00,000 - ₹22,00,000', 'VERY HIGH', TRUE),
(5, 'Frontend Developer', 'frontend-developer', 'Builds responsive, high-performance, accessible user interfaces and interactive web applications using modern JavaScript/TypeScript frameworks.', 6.00, 60.00, 60.00, 60.00, 'ENTRY', '₹5,50,000 - ₹13,00,000', 'HIGH', TRUE),
(6, 'Backend Developer', 'backend-developer', 'Architects reliable server-side APIs, microservices, database schemas, authentication layers, and handles backend business logic and caching.', 6.50, 60.00, 60.00, 65.00, 'INTERMEDIATE', '₹6,50,000 - ₹15,00,000', 'VERY HIGH', TRUE),
(7, 'Cloud Engineer', 'cloud-engineer', 'Deploys, manages, and automates multi-cloud infrastructure, CI/CD pipelines, container orchestration, and ensures high availability and security.', 6.50, 60.00, 60.00, 70.00, 'INTERMEDIATE', '₹7,00,000 - ₹16,00,000', 'VERY HIGH', TRUE);

-- -----------------------------------------------------------------------------
-- 11. SEED CAREER SKILL REQUIREMENTS & WEIGHTS
-- -----------------------------------------------------------------------------
-- 1. Software Developer
INSERT INTO career_skills (career_id, skill_id, importance_weight, is_required, min_proficiency) VALUES
(1, 34, 5.0, TRUE, 'ADVANCED'),      -- DSA
(1, 8, 4.0, TRUE, 'INTERMEDIATE'),     -- Python
(1, 9, 4.0, TRUE, 'INTERMEDIATE'),     -- Java
(1, 12, 4.0, TRUE, 'INTERMEDIATE'),    -- SQL
(1, 31, 3.5, TRUE, 'INTERMEDIATE'),    -- Git
(1, 35, 3.5, FALSE, 'INTERMEDIATE');   -- REST API

-- 2. Data Analyst
INSERT INTO career_skills (career_id, skill_id, importance_weight, is_required, min_proficiency) VALUES
(2, 12, 5.0, TRUE, 'ADVANCED'),      -- SQL
(2, 16, 4.5, TRUE, 'ADVANCED'),      -- Pandas
(2, 17, 4.0, TRUE, 'INTERMEDIATE'),  -- NumPy
(2, 23, 4.5, TRUE, 'ADVANCED'),      -- Statistics
(2, 24, 4.0, TRUE, 'INTERMEDIATE'),  -- Power BI
(2, 25, 3.5, FALSE, 'INTERMEDIATE'), -- Tableau
(2, 8, 4.0, TRUE, 'INTERMEDIATE');   -- Python

-- 3. Data Scientist
INSERT INTO career_skills (career_id, skill_id, importance_weight, is_required, min_proficiency) VALUES
(3, 8, 5.0, TRUE, 'ADVANCED'),       -- Python
(3, 16, 4.5, TRUE, 'ADVANCED'),      -- Pandas
(3, 17, 4.5, TRUE, 'ADVANCED'),      -- NumPy
(3, 18, 5.0, TRUE, 'ADVANCED'),      -- Scikit-learn
(3, 21, 5.0, TRUE, 'ADVANCED'),      -- Machine Learning
(3, 23, 4.5, TRUE, 'ADVANCED'),      -- Statistics
(3, 12, 4.0, TRUE, 'INTERMEDIATE'),  -- SQL
(3, 22, 3.5, FALSE, 'INTERMEDIATE'); -- Deep Learning

-- 4. AI/ML Engineer
INSERT INTO career_skills (career_id, skill_id, importance_weight, is_required, min_proficiency) VALUES
(4, 8, 5.0, TRUE, 'ADVANCED'),       -- Python
(4, 21, 5.0, TRUE, 'ADVANCED'),      -- Machine Learning
(4, 22, 5.0, TRUE, 'ADVANCED'),      -- Deep Learning
(4, 18, 4.5, TRUE, 'ADVANCED'),      -- Scikit-learn
(4, 19, 4.0, TRUE, 'INTERMEDIATE'),  -- TensorFlow
(4, 20, 4.5, TRUE, 'ADVANCED'),      -- PyTorch
(4, 32, 3.5, FALSE, 'INTERMEDIATE'), -- FastAPI
(4, 29, 3.5, FALSE, 'INTERMEDIATE'); -- Docker

-- 5. Frontend Developer
INSERT INTO career_skills (career_id, skill_id, importance_weight, is_required, min_proficiency) VALUES
(5, 1, 4.5, TRUE, 'ADVANCED'),       -- HTML
(5, 2, 4.5, TRUE, 'ADVANCED'),       -- CSS
(5, 3, 5.0, TRUE, 'ADVANCED'),       -- JavaScript
(5, 4, 4.5, TRUE, 'ADVANCED'),       -- TypeScript
(5, 5, 5.0, TRUE, 'ADVANCED'),       -- React
(5, 6, 4.0, FALSE, 'INTERMEDIATE'),  -- Next.js
(5, 31, 3.5, TRUE, 'INTERMEDIATE');  -- Git

-- 6. Backend Developer
INSERT INTO career_skills (career_id, skill_id, importance_weight, is_required, min_proficiency) VALUES
(6, 8, 4.5, TRUE, 'ADVANCED'),       -- Python
(6, 7, 4.0, TRUE, 'INTERMEDIATE'),   -- Node.js
(6, 12, 4.5, TRUE, 'ADVANCED'),      -- SQL
(6, 13, 4.0, TRUE, 'INTERMEDIATE'),  -- MySQL
(6, 14, 4.0, FALSE, 'INTERMEDIATE'), -- PostgreSQL
(6, 32, 4.5, TRUE, 'ADVANCED'),      -- FastAPI
(6, 35, 4.5, TRUE, 'ADVANCED'),      -- REST API
(6, 29, 3.5, FALSE, 'INTERMEDIATE'); -- Docker

-- 7. Cloud Engineer
INSERT INTO career_skills (career_id, skill_id, importance_weight, is_required, min_proficiency) VALUES
(7, 26, 5.0, TRUE, 'ADVANCED'),      -- AWS
(7, 27, 4.0, FALSE, 'INTERMEDIATE'), -- GCP
(7, 28, 4.0, FALSE, 'INTERMEDIATE'), -- Azure
(7, 29, 4.5, TRUE, 'ADVANCED'),      -- Docker
(7, 30, 4.5, TRUE, 'INTERMEDIATE'),  -- Kubernetes
(7, 33, 4.5, TRUE, 'ADVANCED'),      -- Linux
(7, 31, 4.0, TRUE, 'INTERMEDIATE');  -- Git

-- -----------------------------------------------------------------------------
-- 12. SEED CURATED LEARNING RESOURCES
-- -----------------------------------------------------------------------------
INSERT INTO learning_resources (skill_id, title, resource_type, platform, url, estimated_hours, difficulty) VALUES
(4, 'TypeScript for Professional JavaScript Developers', 'COURSE', 'Coursera', 'https://www.coursera.org/learn/typescript-fundamentals', 15, 'INTERMEDIATE'),
(6, 'Complete Next.js App Router Mastery', 'COURSE', 'Official Docs / Next.js', 'https://nextjs.org/learn', 20, 'INTERMEDIATE'),
(20, 'Deep Learning with PyTorch: Zero to GANs', 'COURSE', 'FreeCodeCamp', 'https://www.freecodecamp.org/news/pytorch-deep-learning/', 30, 'INTERMEDIATE'),
(29, 'Docker for Data Scientists & ML Engineers', 'TUTORIAL', 'YouTube', 'https://www.youtube.com/watch?v=fqMOX6JJhGo', 8, 'BEGINNER'),
(30, 'Kubernetes for Absolute Beginners - Hands-on', 'COURSE', 'Udemy', 'https://www.udemy.com/course/learn-kubernetes/', 12, 'INTERMEDIATE'),
(26, 'AWS Certified Cloud Practitioner Essentials', 'COURSE', 'AWS Skill Builder', 'https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials', 16, 'BEGINNER'),
(24, 'Data Modeling & Dashboarding in Power BI', 'COURSE', 'Microsoft Learn', 'https://learn.microsoft.com/en-us/training/paths/power-bi-data-analyst/', 18, 'BEGINNER'),
(18, 'Hands-on Machine Learning with Scikit-learn', 'BOOK', 'O Reilly Media', 'https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/', 45, 'ADVANCED'),
(34, 'Mastering Data Structures and Algorithms with LeetCode', 'COURSE', 'Coursera', 'https://www.coursera.org/specializations/data-structures-algorithms', 40, 'ADVANCED');
