"""
Hybrid Career Recommendation Engine.
Combines ML model probability with multi-dimensional compatibility scoring:
  - Skill Compatibility      30%
  - Academic Compatibility   15%
  - Project Compatibility    15%
  - Certification Relevance  10%
  - Aptitude Compatibility   10%
  - Interest Alignment       10%
  - Domain Alignment         10%
  (Weights are configurable via environment variables)
"""

import os
import sys
import json
import logging
import joblib
import numpy as np
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from preprocessing.feature_engineering import student_profile_to_features, LABEL_INVERSE
from explainability.shap_explainer import explain_with_shap, generate_human_readable_text
from explainability.lime_explainer import explain_with_lime
from skill_gap.gap_analyzer import analyze_skill_gap, generate_learning_roadmap

logger = logging.getLogger("career_ai.recommendation")

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
CAREER_LABELS = [
    "Software Developer", "Data Analyst", "Data Scientist",
    "AI/ML Engineer", "Frontend Developer", "Backend Developer", "Cloud Engineer"
]

PROFICIENCY_SCORE_MAP = {"NONE": 0, "BEGINNER": 1, "INTERMEDIATE": 2, "ADVANCED": 3}


def _load_model():
    model_path = os.path.join(ARTIFACTS_DIR, "career_model.joblib")
    feat_path = os.path.join(ARTIFACTS_DIR, "feature_columns.json")
    if not os.path.exists(model_path):
        return None, None
    model = joblib.load(model_path)
    with open(feat_path) as f:
        feature_cols = json.load(f)
    return model, feature_cols


def _skill_compatibility(student_skills: List[Dict], career_skills: List[Dict]) -> float:
    """Weighted skill match score 0-100."""
    student_map = {s["skill_id"]: PROFICIENCY_SCORE_MAP.get(s.get("proficiency_level", "NONE"), 0)
                   for s in student_skills}
    total_weight = sum(cs.get("importance_weight", 1.0) for cs in career_skills if cs.get("is_required", True))
    if total_weight == 0:
        return 50.0
    earned = 0.0
    for cs in career_skills:
        if not cs.get("is_required", True):
            continue
        sid = cs["skill_id"]
        weight = cs.get("importance_weight", 1.0)
        required_level = PROFICIENCY_SCORE_MAP.get(cs.get("min_proficiency", "INTERMEDIATE"), 2)
        student_level = student_map.get(sid, 0)
        if required_level > 0:
            ratio = min(1.0, student_level / required_level)
        else:
            ratio = 1.0 if student_level > 0 else 0.0
        earned += weight * ratio
    return round(min(100.0, (earned / total_weight) * 100), 1)


def _academic_compatibility(academic: Dict, career: Dict) -> float:
    """Score how student's academics meet career minimums. 0-100."""
    if not academic:
        return 50.0
    cgpa = academic.get("cgpa") or 0
    min_cgpa = career.get("min_cgpa", 6.0)
    tenth = academic.get("tenth_percentage") or 0
    twelfth = academic.get("twelfth_percentage") or 0

    cgpa_score = min(100.0, (cgpa / max(min_cgpa, 0.1)) * 85) if min_cgpa > 0 else 80.0
    academic_avg = (tenth + twelfth) / 2 if (tenth and twelfth) else 65.0
    return round((cgpa_score * 0.6 + min(100.0, academic_avg) * 0.4), 1)


def _project_compatibility(projects: List[Dict], expected_domains: List[str]) -> float:
    """Match project count, complexity, and domain relevance. 0-100."""
    if not projects:
        return 30.0
    base = min(100.0, len(projects) * 20)  # each project adds 20%
    complexity_bonus = 0.0
    domain_bonus = 0.0
    for p in projects:
        c = p.get("complexity", "LOW")
        complexity_bonus += {"LOW": 5, "MEDIUM": 10, "HIGH": 20}.get(c, 5)
        project_domain = (p.get("domain") or "").lower()
        if any(d.lower() in project_domain for d in expected_domains):
            domain_bonus += 15
    return round(min(100.0, base + complexity_bonus * 0.2 + domain_bonus * 0.1), 1)


def _certification_compatibility(certs: List[Dict], career_name: str) -> float:
    """Score certification relevance to career. 0-100."""
    if not certs:
        return 20.0
    domain_keywords = {
        "AI/ML Engineer": ["machine learning", "deep learning", "ai", "ml", "tensorflow", "pytorch"],
        "Data Scientist": ["data science", "machine learning", "statistics", "python", "pandas"],
        "Data Analyst": ["data analyst", "power bi", "tableau", "sql", "business intelligence"],
        "Software Developer": ["software", "programming", "java", "python", "algorithms"],
        "Frontend Developer": ["javascript", "react", "frontend", "web", "html"],
        "Backend Developer": ["backend", "api", "python", "node", "database"],
        "Cloud Engineer": ["aws", "cloud", "azure", "gcp", "kubernetes", "devops"],
    }
    keywords = domain_keywords.get(career_name, [])
    score = 20.0
    for cert in certs:
        cert_text = f"{cert.get('certification_name', '')} {cert.get('domain', '')}".lower()
        if any(kw in cert_text for kw in keywords):
            score += 25.0
        else:
            score += 10.0
    return round(min(100.0, score), 1)


def _aptitude_compatibility(aptitude: Dict, career: Dict) -> float:
    """Score aptitude against career minimum. 0-100."""
    if not aptitude:
        return 50.0
    total = aptitude.get("total_score") or aptitude.get("aptitude_total") or 0
    min_apt = career.get("min_aptitude_score", 60.0)
    return round(min(100.0, (total / max(min_apt, 1.0)) * 80), 1)


def _interest_compatibility(interests: Dict, career_name: str) -> float:
    """Score career interest alignment. 0-100."""
    if not interests:
        return 50.0
    career_interests = [c.lower() for c in (interests.get("career_interests") or [])]
    if not career_interests:
        return 50.0
    career_lower = career_name.lower()
    if any(career_lower in ci or ci in career_lower for ci in career_interests):
        return 95.0
    return 40.0


def _domain_compatibility(interests: Dict, career: Dict) -> float:
    """Score domain preference alignment. 0-100."""
    if not interests:
        return 50.0
    preferred_domains = [d.lower() for d in (interests.get("preferred_domains") or [])]
    career_domains_map = {
        "software-developer": ["software engineering", "web development"],
        "data-analyst": ["data science", "business intelligence"],
        "data-scientist": ["data science", "artificial intelligence"],
        "aiml-engineer": ["artificial intelligence", "machine learning"],
        "frontend-developer": ["web development", "ui/ux"],
        "backend-developer": ["software engineering", "web development"],
        "cloud-engineer": ["cloud computing", "devops"],
    }
    career_domains = career_domains_map.get(career.get("slug", ""), [])
    if not preferred_domains or not career_domains:
        return 50.0
    if any(any(pd in cd or cd in pd for cd in career_domains) for pd in preferred_domains):
        return 90.0
    return 40.0


def _matching_missing_skills(student_skills: List[Dict], career_skills: List[Dict]):
    student_ids = {s["skill_id"] for s in student_skills}
    matching = [cs["skill_name"] for cs in career_skills if cs["skill_id"] in student_ids and cs.get("is_required")]
    missing = [cs["skill_name"] for cs in career_skills if cs["skill_id"] not in student_ids and cs.get("is_required")]
    return matching, missing


def generate_recommendations(
    student_data: Dict,
    careers: List[Dict],
    weights: Optional[Dict] = None,
    top_n: int = 5
) -> List[Dict]:
    """
    Main hybrid recommendation function.
    Returns top N career recommendations with scores and explanations.
    """
    # Default configurable weights
    W = weights or {
        "skills": 0.30, "academics": 0.15, "projects": 0.15,
        "certifications": 0.10, "aptitude": 0.10, "interest": 0.10, "domain": 0.10
    }

    model, feature_cols = _load_model()

    student_skills = student_data.get("skills", [])
    academic = student_data.get("academic", {})
    aptitude = student_data.get("aptitude", {})
    interests = student_data.get("interests", {})
    projects = student_data.get("projects", [])
    certifications = student_data.get("certifications", [])

    # Build raw feature dict for ML model
    feat_dict = {}
    if academic:
        feat_dict["cgpa"] = academic.get("cgpa", 0) or 0
        feat_dict["tenth_percentage"] = academic.get("tenth_percentage", 0) or 0
        feat_dict["twelfth_percentage"] = academic.get("twelfth_percentage", 0) or 0
    if aptitude:
        feat_dict["aptitude_quant"] = aptitude.get("quantitative_score", 0) or 0
        feat_dict["aptitude_logical"] = aptitude.get("logical_reasoning_score", 0) or 0
        feat_dict["aptitude_verbal"] = aptitude.get("verbal_score", 0) or 0
        feat_dict["aptitude_technical"] = aptitude.get("technical_aptitude_score", 0) or 0
        feat_dict["aptitude_total"] = aptitude.get("total_score", 0) or 0
    feat_dict["num_projects"] = len(projects)
    feat_dict["project_complexity"] = (
        max(({"LOW": 1, "MEDIUM": 2, "HIGH": 3}.get(p.get("complexity", "LOW"), 1) for p in projects), default=0)
    )
    feat_dict["num_certifications"] = len(certifications)
    feat_dict["cert_relevance"] = 1 if certifications else 0
    feat_dict["interest_match"] = 1 if interests and interests.get("career_interests") else 0
    feat_dict["domain_match"] = 1 if interests and interests.get("preferred_domains") else 0

    # Encode skills
    for s in student_skills:
        skill_name = (s.get("skill_name") or "").lower().replace(" ", "_").replace("/", "").replace("-", "_").replace(".", "")
        key = f"skill_{skill_name}"
        level = PROFICIENCY_SCORE_MAP.get(s.get("proficiency_level", "NONE"), 0)
        feat_dict[key] = level

    # Get ML class probabilities
    ml_probs = {}
    feature_vector = None
    if model and feature_cols:
        try:
            feature_vector = student_profile_to_features(feat_dict, feature_cols)
            probs = model.predict_proba(feature_vector.reshape(1, -1))[0]
            ml_probs = {LABEL_INVERSE[i]: float(p) for i, p in enumerate(probs) if i in LABEL_INVERSE}
        except Exception as exc:
            logger.warning(f"ML prediction failed: {exc}")

    recommendations = []
    for career in careers:
        career_name = career["name"]

        # Component scores
        skill_score = _skill_compatibility(student_skills, career.get("required_skills", []))
        academic_score = _academic_compatibility(academic, career)
        project_score = _project_compatibility(projects, career.get("relevant_domains", []))
        cert_score = _certification_compatibility(certifications, career_name)
        aptitude_score = _aptitude_compatibility(aptitude, career)
        interest_score = _interest_compatibility(interests, career_name)
        domain_score = _domain_compatibility(interests, career)
        ml_prob = ml_probs.get(career_name, 0.14) * 100  # scale to 0-100

        # Hybrid weighted score (ML replaces missing weights)
        compatibility = round(
            skill_score * W["skills"] +
            academic_score * W["academics"] +
            project_score * W["projects"] +
            cert_score * W["certifications"] +
            aptitude_score * W["aptitude"] +
            interest_score * W["interest"] +
            domain_score * W["domain"],
            1
        )

        matching_skills, missing_skills = _matching_missing_skills(student_skills, career.get("required_skills", []))

        recommendations.append({
            "career_id": career["id"],
            "career_name": career_name,
            "career_slug": career.get("slug", ""),
            "career_description": career.get("description", ""),
            "compatibility_score": compatibility,
            "ml_confidence": round(ml_prob, 1),
            "skill_compatibility": skill_score,
            "academic_compatibility": academic_score,
            "project_compatibility": project_score,
            "certification_compatibility": cert_score,
            "aptitude_compatibility": aptitude_score,
            "interest_compatibility": interest_score,
            "domain_compatibility": domain_score,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "feature_vector": feature_vector,
            "feature_cols": feature_cols,
        })

    recommendations.sort(key=lambda x: x["compatibility_score"], reverse=True)
    top_recs = recommendations[:top_n]

    # Assign rank
    for i, rec in enumerate(top_recs):
        rec["rank_order"] = i + 1

    # Add SHAP + LIME explanation for top recommendation
    for rec in top_recs:
        career_name = rec["career_name"]
        class_index = CAREER_LABELS.index(career_name) if career_name in CAREER_LABELS else 0
        fv = rec.get("feature_vector")
        fc = rec.get("feature_cols", [])

        shap_result = None
        lime_result = None

        if fv is not None and len(fc) > 0:
            shap_result = explain_with_shap(fv, fc, class_index)
            lime_result = explain_with_lime(fv, fc, CAREER_LABELS, class_index)

        pos = shap_result["top_positive"] if shap_result else []
        neg = shap_result["top_negative"] if shap_result else []
        human_text = generate_human_readable_text(career_name, pos, neg, rec["compatibility_score"])

        rec["explanation"] = {
            "shap_values": shap_result["all_contributions"] if shap_result else [],
            "lime_values": lime_result["lime_values"] if lime_result else [],
            "top_positive_factors": pos,
            "top_negative_factors": neg,
            "human_readable_text": human_text
        }

    return top_recs
