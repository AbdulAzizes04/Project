"""
Database Initializer and Seeder for Explainable AI Career Recommendation System.
Works with both MySQL (primary) and SQLite (zero-config fallback).
"""

import sys
import os
import logging
from datetime import date

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database import engine, Base, SessionLocal  # type: ignore
from app.models import (  # type: ignore
    User, StudentProfile, AcademicRecord, AptitudeScore, CareerInterest,
    Skill, SkillAlias, StudentSkill, Certification, StudentCertification,
    Project, StudentProject, CareerRole, CareerSkill, LearningResource
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("init_db")


def initialize_and_seed():
    logger.info(f"Target database engine dialect: {engine.dialect.name}")
    logger.info("Creating all tables via SQLAlchemy metadata...")
    Base.metadata.create_all(bind=engine)
    logger.info("All tables created successfully.")

    db = SessionLocal()
    try:
        # 1. Users
        if db.query(User).count() == 0:
            logger.info("Seeding Users (Admin & Demo Student)...")
            admin_user = User(
                id=1,
                email="admin@careerai.edu",
                password_hash="$2b$12$Y1avdz9LPAPdGPQ5uUdCveXPwTdxIXSkAYxotdrGhd4ehT0i8jUMy",  # Admin@123
                role="ADMIN",
                is_active=True
            )
            student_user = User(
                id=2,
                email="student@careerai.edu",
                password_hash="$2b$12$K7vLwHkKGNqQal4TDxDQ0ubjJOXI284uKnoUlog1bN6RzSGTRjYPG",  # Student@123
                role="STUDENT",
                is_active=True
            )
            db.add_all([admin_user, student_user])
            db.commit()

        # 2. Student Profile & Records
        if db.query(StudentProfile).count() == 0:
            logger.info("Seeding Student Profile & Records for 'Abdul Aziz'...")
            profile = StudentProfile(
                id=1,
                user_id=2,
                name="Abdul Aziz",
                phone="+91 9876543210",
                location="Rajampet, Andhra Pradesh",
                batch="2023-2027",
                branch="Artificial Intelligence and Data Science",
                bio="Final year B.Tech AIDS student passionate about machine learning, explainable AI, and full-stack software development."
            )
            db.add(profile)
            db.commit()

            academic = AcademicRecord(
                student_id=1,
                tenth_percentage=92.50,
                twelfth_percentage=89.00,
                cgpa=8.65,
                semester_scores={"sem1": 8.4, "sem2": 8.5, "sem3": 8.7, "sem4": 8.6, "sem5": 8.8, "sem6": 8.9},
                core_subject_performance={"Data Structures & Algorithms": 88, "Database Management Systems": 92, "Machine Learning": 90, "Operating Systems": 84, "Computer Networks": 82, "Deep Learning": 89}
            )
            aptitude = AptitudeScore(
                student_id=1,
                quantitative_score=85.00,
                logical_reasoning_score=88.00,
                verbal_score=82.00,
                technical_aptitude_score=92.00,
                total_score=86.75,
                assessment_date=date(2026, 2, 15)
            )
            interest = CareerInterest(
                student_id=1,
                preferred_domains=["Artificial Intelligence", "Data Science", "Web Development"],
                career_interests=["AI/ML Engineer", "Data Scientist", "Software Developer"],
                preferred_technologies=["Python", "PyTorch", "FastAPI", "React", "SQL"],
                soft_skills={"communication": 4, "leadership": 4, "teamwork": 5, "problem_solving": 5}
            )
            db.add_all([academic, aptitude, interest])
            db.commit()

        # 3. Skills
        if db.query(Skill).count() == 0:
            logger.info("Seeding 35 Standardized Skills...")
            skills_data = [
                (1, 'HTML', 'Frontend', 'Standard markup language for web documents.'),
                (2, 'CSS', 'Frontend', 'Style sheet language for web presentation.'),
                (3, 'JavaScript', 'Programming', 'High-level scripting language.'),
                (4, 'TypeScript', 'Programming', 'Typed superset of JavaScript.'),
                (5, 'React', 'Frontend', 'UI component library.'),
                (6, 'Next.js', 'Frontend', 'Full-stack React framework.'),
                (7, 'Node.js', 'Backend', 'JavaScript backend runtime.'),
                (8, 'Python', 'Programming', 'General-purpose language for AI/ML and backend.'),
                (9, 'Java', 'Programming', 'Class-based OOP language.'),
                (10, 'C', 'Programming', 'Procedural computer programming language.'),
                (11, 'C++', 'Programming', 'High-performance OOP language with templates.'),
                (12, 'SQL', 'Database', 'Relational database query language.'),
                (13, 'MySQL', 'Database', 'Relational database management system.'),
                (14, 'PostgreSQL', 'Database', 'Object-relational open source database.'),
                (15, 'MongoDB', 'Database', 'Document NoSQL database.'),
                (16, 'Pandas', 'Data Science', 'Data manipulation and analysis library.'),
                (17, 'NumPy', 'Data Science', 'Numerical multi-dimensional arrays library.'),
                (18, 'Scikit-learn', 'AI/ML', 'Classical machine learning algorithms in Python.'),
                (19, 'TensorFlow', 'AI/ML', 'Machine learning and deep neural networks platform.'),
                (20, 'PyTorch', 'AI/ML', 'Deep learning framework for tensors and dynamic neural networks.'),
                (21, 'Machine Learning', 'AI/ML', 'Statistical algorithms learning patterns from empirical data.'),
                (22, 'Deep Learning', 'AI/ML', 'Multi-layer neural network architectures.'),
                (23, 'Statistics', 'Data Science', 'Probability, hypothesis testing, and inferential statistics.'),
                (24, 'Power BI', 'Data Science', 'Business analytics and visualization suite.'),
                (25, 'Tableau', 'Data Science', 'Interactive visual analytics platform.'),
                (26, 'AWS', 'Cloud', 'Amazon Web Services cloud computing platform.'),
                (27, 'GCP', 'Cloud', 'Google Cloud Platform services.'),
                (28, 'Azure', 'Cloud', 'Microsoft enterprise cloud platform.'),
                (29, 'Docker', 'DevOps', 'Application containerization platform.'),
                (30, 'Kubernetes', 'DevOps', 'Container orchestration engine.'),
                (31, 'Git', 'DevOps', 'Distributed source code version control.'),
                (32, 'FastAPI', 'Backend', 'High-performance Python asynchronous web framework.'),
                (33, 'Linux', 'DevOps', 'Unix-like operating system environment.'),
                (34, 'Data Structures & Algorithms', 'Core', 'Algorithmic efficiency and data structuring principles.'),
                (35, 'REST API', 'Backend', 'Hypermedia API design and HTTP protocols.')
            ]
            for sid, name, cat, desc in skills_data:
                db.add(Skill(id=sid, name=name, category=cat, description=desc))
            db.commit()

        # 4. Skill Aliases
        if db.query(SkillAlias).count() == 0:
            logger.info("Seeding Skill Aliases for Normalization...")
            aliases_data = [
                (3, 'JS'), (3, 'Javascript'), (3, 'Java Script'), (3, 'vanilla js'),
                (4, 'TS'), (4, 'Typescript'),
                (5, 'ReactJS'), (5, 'React.js'), (5, 'react-js'),
                (6, 'NextJS'), (6, 'Next.js'),
                (7, 'NodeJS'), (7, 'Node.js'), (7, 'node'),
                (8, 'Py'), (8, 'Python3'), (8, 'Python 3'),
                (11, 'Cpp'), (11, 'C plus plus'),
                (12, 'Structured Query Language'), (12, 'Relational SQL'),
                (16, 'Pandas Library'), (17, 'Numpy Library'),
                (18, 'Sklearn'), (18, 'scikit learn'),
                (19, 'TF'), (19, 'Tensorflow'),
                (20, 'Torch'), (20, 'Pytorch'),
                (21, 'ML'), (21, 'Machine-Learning'),
                (22, 'DL'), (22, 'Deep-Learning'), (22, 'Neural Networks'),
                (24, 'PowerBI'), (24, 'MS Power BI'),
                (26, 'Amazon Web Services'), (26, 'Amazon Cloud'),
                (27, 'Google Cloud Platform'), (27, 'Google Cloud'),
                (28, 'Microsoft Azure'), (28, 'MS Azure'),
                (31, 'GitHub'), (31, 'Version Control Git'),
                (32, 'Fast API'),
                (34, 'DSA'), (34, 'Data Structures')
            ]
            for sid, alias in aliases_data:
                db.add(SkillAlias(skill_id=sid, alias=alias))
            db.commit()

        # 5. Student Skills
        if db.query(StudentSkill).count() == 0:
            logger.info("Seeding Student Skills for Demo Student...")
            student_skills_data = [
                (8, 'ADVANCED'),   # Python
                (16, 'ADVANCED'),  # Pandas
                (17, 'ADVANCED'),  # NumPy
                (18, 'ADVANCED'),  # Scikit-learn
                (20, 'INTERMEDIATE'), # PyTorch
                (21, 'ADVANCED'),  # ML
                (22, 'INTERMEDIATE'), # DL
                (12, 'ADVANCED'),  # SQL
                (13, 'INTERMEDIATE'), # MySQL
                (3, 'INTERMEDIATE'), # JS
                (5, 'INTERMEDIATE'), # React
                (32, 'ADVANCED'),  # FastAPI
                (31, 'INTERMEDIATE'), # Git
                (34, 'ADVANCED')   # DSA
            ]
            for sid, prof in student_skills_data:
                db.add(StudentSkill(student_id=1, skill_id=sid, proficiency_level=prof, verified=True))
            db.commit()

        # 6. Student Certifications & Projects
        if db.query(StudentCertification).count() == 0:
            logger.info("Seeding Student Certifications and Projects...")
            db.add(StudentCertification(
                student_id=1,
                certification_name="Machine Learning Specialization",
                issuer="DeepLearning.AI / Coursera",
                issue_date=date(2025, 8, 10),
                domain="Artificial Intelligence",
                verification_url="https://coursera.org/verify/ML-SPEC-2025-101"
            ))
            db.add(StudentProject(
                student_id=1,
                project_name="Explainable AI Career Recommendation System",
                description="An intelligent recommendation system utilizing SHAP, LIME, and skill analytics for B.Tech students.",
                technologies=["Python", "FastAPI", "Scikit-learn", "SHAP", "LIME", "React", "Next.js"],
                domain="Artificial Intelligence",
                complexity="HIGH",
                role="Lead Full-Stack ML Engineer",
                duration_months=6,
                project_url="https://github.com/career-ai/project"
            ))
            db.commit()

        # 7. Career Roles
        if db.query(CareerRole).count() == 0:
            logger.info("Seeding 7 Career Roles and Requirements...")
            roles_data = [
                (1, "Software Developer", "software-developer", "Engineers robust software applications, writes clean code, and builds algorithmic solutions.", 6.50, 60.0, 60.0, 65.0, "ENTRY", "₹6,00,000 - ₹14,00,000"),
                (2, "Data Analyst", "data-analyst", "Interprets complex datasets, builds descriptive dashboards, uncovers business insights using SQL and BI.", 6.50, 60.0, 60.0, 65.0, "ENTRY", "₹5,00,000 - ₹11,00,000"),
                (3, "Data Scientist", "data-scientist", "Develops predictive statistical models, analyzes unstructured data, and engineers ML pipelines.", 7.00, 65.0, 65.0, 75.0, "INTERMEDIATE", "₹8,00,000 - ₹18,00,000"),
                (4, "AI/ML Engineer", "aiml-engineer", "Designs, trains, and deploys scalable machine learning and deep learning models into production.", 7.50, 70.0, 70.0, 80.0, "ADVANCED", "₹10,00,000 - ₹22,00,000"),
                (5, "Frontend Developer", "frontend-developer", "Builds responsive, accessible, interactive web applications using modern JavaScript/TypeScript.", 6.00, 60.0, 60.0, 60.0, "ENTRY", "₹5,50,000 - ₹13,00,000"),
                (6, "Backend Developer", "backend-developer", "Architects reliable server-side APIs, database schemas, authentication layers, and business logic.", 6.50, 60.0, 60.0, 65.0, "INTERMEDIATE", "₹6,50,000 - ₹15,00,000"),
                (7, "Cloud Engineer", "cloud-engineer", "Deploys, manages, and automates multi-cloud infrastructure, CI/CD pipelines, and containerization.", 6.50, 60.0, 60.0, 70.0, "INTERMEDIATE", "₹7,00,000 - ₹16,00,000")
            ]
            for rid, name, slug, desc, cgpa, tenth, twelfth, apt, diff, sal in roles_data:
                role = CareerRole(
                    id=rid, name=name, slug=slug, description=desc,
                    min_cgpa=cgpa, min_tenth_pct=tenth, min_twelfth_pct=twelfth,
                    min_aptitude_score=apt, difficulty_level=diff, salary_range=sal
                )
                db.add(role)
            db.commit()

        # 8. Career Skills
        if db.query(CareerSkill).count() == 0:
            logger.info("Seeding Career Skills associations...")
            career_skills_map = [
                # Software Developer (Role 1)
                (1, 34, 5.0, True, 'ADVANCED'),      # DSA
                (1, 8, 4.0, True, 'INTERMEDIATE'),    # Python
                (1, 9, 4.0, True, 'INTERMEDIATE'),    # Java
                (1, 12, 4.0, True, 'INTERMEDIATE'),   # SQL
                (1, 31, 3.5, True, 'INTERMEDIATE'),   # Git
                (1, 35, 3.5, False, 'INTERMEDIATE'),  # REST API
                # Data Analyst (Role 2)
                (2, 12, 5.0, True, 'ADVANCED'),      # SQL
                (2, 16, 4.5, True, 'ADVANCED'),      # Pandas
                (2, 17, 4.0, True, 'INTERMEDIATE'),  # NumPy
                (2, 23, 4.5, True, 'ADVANCED'),      # Statistics
                (2, 24, 4.0, True, 'INTERMEDIATE'),  # Power BI
                (2, 25, 3.5, False, 'INTERMEDIATE'), # Tableau
                (2, 8, 4.0, True, 'INTERMEDIATE'),   # Python
                # Data Scientist (Role 3)
                (3, 8, 5.0, True, 'ADVANCED'),       # Python
                (3, 16, 4.5, True, 'ADVANCED'),      # Pandas
                (3, 17, 4.5, True, 'ADVANCED'),      # NumPy
                (3, 18, 5.0, True, 'ADVANCED'),      # Scikit-learn
                (3, 21, 5.0, True, 'ADVANCED'),      # Machine Learning
                (3, 23, 4.5, True, 'ADVANCED'),      # Statistics
                (3, 12, 4.0, True, 'INTERMEDIATE'),  # SQL
                (3, 22, 3.5, False, 'INTERMEDIATE'), # Deep Learning
                # AI/ML Engineer (Role 4)
                (4, 8, 5.0, True, 'ADVANCED'),       # Python
                (4, 21, 5.0, True, 'ADVANCED'),      # Machine Learning
                (4, 22, 5.0, True, 'ADVANCED'),      # Deep Learning
                (4, 18, 4.5, True, 'ADVANCED'),      # Scikit-learn
                (4, 19, 4.0, True, 'INTERMEDIATE'),  # TensorFlow
                (4, 20, 4.5, True, 'ADVANCED'),      # PyTorch
                (4, 32, 3.5, False, 'INTERMEDIATE'), # FastAPI
                (4, 29, 3.5, False, 'INTERMEDIATE'), # Docker
                # Frontend Developer (Role 5)
                (5, 1, 4.5, True, 'ADVANCED'),       # HTML
                (5, 2, 4.5, True, 'ADVANCED'),       # CSS
                (5, 3, 5.0, True, 'ADVANCED'),       # JavaScript
                (5, 4, 4.5, True, 'ADVANCED'),       # TypeScript
                (5, 5, 5.0, True, 'ADVANCED'),       # React
                (5, 6, 4.0, False, 'INTERMEDIATE'),  # Next.js
                (5, 31, 3.5, True, 'INTERMEDIATE'),  # Git
                # Backend Developer (Role 6)
                (6, 8, 4.5, True, 'ADVANCED'),       # Python
                (6, 7, 4.0, True, 'INTERMEDIATE'),   # Node.js
                (6, 12, 4.5, True, 'ADVANCED'),      # SQL
                (6, 13, 4.0, True, 'INTERMEDIATE'),  # MySQL
                (6, 14, 4.0, False, 'INTERMEDIATE'), # PostgreSQL
                (6, 32, 4.5, True, 'ADVANCED'),      # FastAPI
                (6, 35, 4.5, True, 'ADVANCED'),      # REST API
                (6, 29, 3.5, False, 'INTERMEDIATE'), # Docker
                # Cloud Engineer (Role 7)
                (7, 26, 5.0, True, 'ADVANCED'),      # AWS
                (7, 27, 4.0, False, 'INTERMEDIATE'), # GCP
                (7, 28, 4.0, False, 'INTERMEDIATE'), # Azure
                (7, 29, 4.5, True, 'ADVANCED'),      # Docker
                (7, 30, 4.5, True, 'INTERMEDIATE'),  # Kubernetes
                (7, 33, 4.5, True, 'ADVANCED'),      # Linux
                (7, 31, 4.0, True, 'INTERMEDIATE')   # Git
            ]
            for cid, sid, weight, req, min_prof in career_skills_map:
                db.add(CareerSkill(
                    career_id=cid, skill_id=sid, importance_weight=weight,
                    is_required=req, min_proficiency=min_prof
                ))
            db.commit()

        # 9. Learning Resources
        if db.query(LearningResource).count() == 0:
            logger.info("Seeding Curated Learning Resources...")
            resources_data = [
                (4, "TypeScript for Professional JavaScript Developers", "COURSE", "Coursera", "https://www.coursera.org/learn/typescript-fundamentals", 15, "INTERMEDIATE"),
                (6, "Complete Next.js App Router Mastery", "COURSE", "Next.js Docs", "https://nextjs.org/learn", 20, "INTERMEDIATE"),
                (20, "Deep Learning with PyTorch: Zero to GANs", "COURSE", "FreeCodeCamp", "https://www.freecodecamp.org/news/pytorch-deep-learning/", 30, "INTERMEDIATE"),
                (29, "Docker for Data Scientists & ML Engineers", "TUTORIAL", "YouTube", "https://www.youtube.com/watch?v=fqMOX6JJhGo", 8, "BEGINNER"),
                (30, "Kubernetes for Absolute Beginners - Hands-on", "COURSE", "Udemy", "https://www.udemy.com/course/learn-kubernetes/", 12, "INTERMEDIATE"),
                (26, "AWS Certified Cloud Practitioner Essentials", "COURSE", "AWS Skill Builder", "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials", 16, "BEGINNER"),
                (24, "Data Modeling & Dashboarding in Power BI", "COURSE", "Microsoft Learn", "https://learn.microsoft.com/en-us/training/paths/power-bi-data-analyst/", 18, "BEGINNER"),
                (18, "Hands-on Machine Learning with Scikit-learn", "BOOK", "O Reilly Media", "https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/", 45, "ADVANCED"),
                (34, "Mastering Data Structures and Algorithms with LeetCode", "COURSE", "Coursera", "https://www.coursera.org/specializations/data-structures-algorithms", 40, "ADVANCED")
            ]
            for sid, title, rtype, plat, url, hours, diff in resources_data:
                db.add(LearningResource(
                    skill_id=sid, title=title, resource_type=rtype, platform=plat,
                    url=url, estimated_hours=hours, difficulty=diff
                ))
            db.commit()

        logger.info("=== Database successfully initialized and seeded! ===")
    except Exception as exc:
        db.rollback()
        logger.error(f"Error during database initialization/seeding: {exc}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_and_seed()
