"""
Synthetic Dataset Generator for Career Recommendation AI System.
Generates realistic student profiles for ML training.
NOTE: This is a SYNTHETIC/DEMO dataset for academic demonstration only.
      It does NOT represent actual employment outcomes.
"""

import numpy as np
import pandas as pd
import random
import os

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Career Role Definitions ---
CAREER_ROLES = [
    "Software Developer",
    "Data Analyst",
    "Data Scientist",
    "AI/ML Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Cloud Engineer"
]

SKILL_CATEGORIES = {
    "programming": ["python", "java", "c", "cpp", "javascript", "typescript"],
    "frontend": ["html", "css", "react", "nextjs"],
    "backend": ["nodejs", "fastapi", "restapi"],
    "database": ["sql", "mysql", "postgresql", "mongodb"],
    "datascience": ["pandas", "numpy", "statistics", "powerbi", "tableau"],
    "aiml": ["sklearn", "tensorflow", "pytorch", "machine_learning", "deep_learning"],
    "cloud": ["aws", "gcp", "azure"],
    "devops": ["docker", "kubernetes", "git", "linux"],
    "core": ["dsa"]
}

ALL_SKILLS = [s for group in SKILL_CATEGORIES.values() for s in group]

PREFERRED_DOMAINS_BY_CAREER = {
    "Software Developer":   ["Web Development", "Software Engineering"],
    "Data Analyst":         ["Data Science", "Business Intelligence"],
    "Data Scientist":       ["Data Science", "Artificial Intelligence"],
    "AI/ML Engineer":       ["Artificial Intelligence", "Machine Learning"],
    "Frontend Developer":   ["Web Development", "UI/UX"],
    "Backend Developer":    ["Web Development", "Software Engineering"],
    "Cloud Engineer":       ["Cloud Computing", "DevOps"]
}

# --- Skill relevance profiles per career ---
CAREER_SKILL_PROFILES = {
    "Software Developer":   {"dsa": 0.95, "python": 0.75, "java": 0.80, "sql": 0.70, "git": 0.85, "restapi": 0.60, "cpp": 0.60, "c": 0.55},
    "Data Analyst":         {"sql": 0.95, "pandas": 0.90, "numpy": 0.80, "statistics": 0.88, "powerbi": 0.80, "tableau": 0.70, "python": 0.75},
    "Data Scientist":       {"python": 0.95, "pandas": 0.90, "numpy": 0.88, "sklearn": 0.92, "machine_learning": 0.95, "statistics": 0.88, "sql": 0.75, "deep_learning": 0.65},
    "AI/ML Engineer":       {"python": 0.98, "machine_learning": 0.98, "deep_learning": 0.95, "sklearn": 0.90, "tensorflow": 0.85, "pytorch": 0.88, "fastapi": 0.65, "docker": 0.60},
    "Frontend Developer":   {"html": 0.98, "css": 0.98, "javascript": 0.98, "react": 0.95, "typescript": 0.88, "nextjs": 0.80, "git": 0.80},
    "Backend Developer":    {"python": 0.90, "nodejs": 0.80, "sql": 0.90, "mysql": 0.82, "postgresql": 0.78, "fastapi": 0.88, "restapi": 0.90, "docker": 0.70},
    "Cloud Engineer":       {"aws": 0.95, "gcp": 0.80, "azure": 0.80, "docker": 0.90, "kubernetes": 0.88, "linux": 0.90, "git": 0.85}
}


def gen_student_profile(career_label: str, student_id: int) -> dict:
    """Generate one realistic student profile biased toward the target career."""

    profile = CAREER_SKILL_PROFILES[career_label]
    noise = random.uniform(0.05, 0.20)

    # Generate all skills with probability based on career relevance
    skill_dict = {}
    for skill in ALL_SKILLS:
        base_prob = profile.get(skill, 0.15)
        prob = min(1.0, max(0.0, base_prob + random.gauss(0, noise)))
        # 0 = no skill, 1 = beginner, 2 = intermediate, 3 = advanced
        if random.random() < prob:
            if prob > 0.7:
                level = random.choices([1, 2, 3], weights=[0.15, 0.40, 0.45])[0]
            elif prob > 0.4:
                level = random.choices([1, 2, 3], weights=[0.30, 0.50, 0.20])[0]
            else:
                level = random.choices([1, 2], weights=[0.70, 0.30])[0]
            skill_dict[skill] = level
        else:
            skill_dict[skill] = 0

    # Academics - correlated with career difficulty
    if career_label in ["AI/ML Engineer", "Data Scientist"]:
        cgpa = round(random.gauss(8.2, 0.6), 2)
        tenth = round(random.gauss(88, 6), 1)
        twelfth = round(random.gauss(85, 7), 1)
    elif career_label in ["Cloud Engineer", "Backend Developer"]:
        cgpa = round(random.gauss(7.8, 0.7), 2)
        tenth = round(random.gauss(83, 7), 1)
        twelfth = round(random.gauss(80, 8), 1)
    else:
        cgpa = round(random.gauss(7.5, 0.8), 2)
        tenth = round(random.gauss(80, 8), 1)
        twelfth = round(random.gauss(78, 9), 1)

    cgpa = max(5.0, min(10.0, cgpa))
    tenth = max(50.0, min(100.0, tenth))
    twelfth = max(50.0, min(100.0, twelfth))

    # Aptitude
    if career_label in ["AI/ML Engineer", "Data Scientist"]:
        quant = round(random.gauss(82, 10), 1)
        logical = round(random.gauss(85, 9), 1)
    else:
        quant = round(random.gauss(72, 12), 1)
        logical = round(random.gauss(74, 12), 1)
    verbal = round(random.gauss(68, 12), 1)
    technical = round(random.gauss(75, 11), 1)
    aptitude_total = round((quant + logical + verbal + technical) / 4, 1)

    # Projects (0-4)
    project_domains = PREFERRED_DOMAINS_BY_CAREER[career_label]
    num_projects = random.choices([0, 1, 2, 3, 4], weights=[0.05, 0.20, 0.40, 0.25, 0.10])[0]
    project_complexity_avg = random.choices([1, 2, 3], weights=[0.20, 0.50, 0.30])[0]  # 1=LOW 2=MED 3=HIGH

    # Certifications
    num_certs = random.choices([0, 1, 2, 3], weights=[0.20, 0.40, 0.30, 0.10])[0]
    cert_relevant = 1 if num_certs > 0 and random.random() > 0.3 else 0

    # Interests match (0 or 1)
    interest_match = random.choices([0, 1], weights=[0.25, 0.75])[0]
    domain_match = random.choices([0, 1], weights=[0.20, 0.80])[0]

    row = {
        "student_id": student_id,
        "career_label": career_label,
        "cgpa": cgpa,
        "tenth_percentage": tenth,
        "twelfth_percentage": twelfth,
        "aptitude_quant": max(0, min(100, quant)),
        "aptitude_logical": max(0, min(100, logical)),
        "aptitude_verbal": max(0, min(100, verbal)),
        "aptitude_technical": max(0, min(100, technical)),
        "aptitude_total": max(0, min(100, aptitude_total)),
        "num_projects": num_projects,
        "project_complexity": project_complexity_avg,
        "num_certifications": num_certs,
        "cert_relevance": cert_relevant,
        "interest_match": interest_match,
        "domain_match": domain_match,
    }
    row.update({f"skill_{k}": v for k, v in skill_dict.items()})
    return row


def generate_dataset(n_per_class: int = 750) -> pd.DataFrame:
    """Generate a balanced synthetic dataset across all 7 career roles."""
    print(f"Generating {n_per_class * len(CAREER_ROLES):,} total synthetic student profiles...")
    rows = []
    student_id = 1
    for career in CAREER_ROLES:
        for _ in range(n_per_class):
            rows.append(gen_student_profile(career, student_id))
            student_id += 1
    df = pd.DataFrame(rows)
    return df


def generate_career_roles_csv() -> pd.DataFrame:
    roles = []
    for i, name in enumerate(CAREER_ROLES, 1):
        roles.append({"id": i, "name": name, "difficulty": ["ENTRY", "ENTRY", "INTERMEDIATE", "ADVANCED", "ENTRY", "INTERMEDIATE", "INTERMEDIATE"][i-1]})
    return pd.DataFrame(roles)


def generate_career_skill_requirements_csv() -> pd.DataFrame:
    rows = []
    for career_id, career in enumerate(CAREER_ROLES, 1):
        profile = CAREER_SKILL_PROFILES[career]
        for skill, weight in profile.items():
            rows.append({
                "career_id": career_id,
                "career_name": career,
                "skill_name": skill,
                "importance_weight": round(weight * 5, 2),
                "is_required": 1 if weight >= 0.7 else 0
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    # Generate main dataset (5,250 students = 750 per career × 7 careers)
    df = generate_dataset(n_per_class=750)
    
    out_path = os.path.join(OUTPUT_DIR, "student_profiles.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved student_profiles.csv: {len(df):,} rows, {len(df.columns)} columns -> {out_path}")

    # Career roles reference CSV
    careers_df = generate_career_roles_csv()
    careers_path = os.path.join(OUTPUT_DIR, "career_roles.csv")
    careers_df.to_csv(careers_path, index=False)
    print(f"Saved career_roles.csv: {len(careers_df)} rows -> {careers_path}")

    # Career skill requirements CSV
    req_df = generate_career_skill_requirements_csv()
    req_path = os.path.join(OUTPUT_DIR, "career_skill_requirements.csv")
    req_df.to_csv(req_path, index=False)
    print(f"Saved career_skill_requirements.csv: {len(req_df)} rows -> {req_path}")

    print("\nClass distribution:")
    print(df["career_label"].value_counts())
    print(f"\nDataset shape: {df.shape}")
    print("NOTE: This is a SYNTHETIC/DEMO dataset for academic demonstration only.")
