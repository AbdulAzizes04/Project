"""
Skill Gap Analysis & Learning Priority Engine.
Compares student skills vs. career requirements to compute gap statuses
and prioritized learning roadmaps.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("career_ai.skill_gap")

PROFICIENCY_SCORE = {"NONE": 0, "BEGINNER": 1, "INTERMEDIATE": 2, "ADVANCED": 3}


def analyze_skill_gap(
    student_skills: List[Dict],       # [{"skill_id": 1, "name": "Python", "proficiency_level": "ADVANCED"}, ...]
    career_skills: List[Dict],        # [{"skill_id": 1, "name": "Python", "importance_weight": 5.0, "is_required": True, "min_proficiency": "ADVANCED"}, ...]
) -> Dict[str, Any]:
    """
    Compute gap status for each career-required skill:
    - STRONG:   Student has skill at or above required proficiency
    - MODERATE: Student has skill but below required proficiency
    - MISSING:  Student does not have skill
    """
    student_skill_map = {s["skill_id"]: s["proficiency_level"] for s in student_skills}

    strong_skills = []
    moderate_skills = []
    missing_skills = []
    total_required = 0
    matched_required = 0

    for cs in career_skills:
        sid = cs["skill_id"]
        name = cs["skill_name"]
        required_level = cs.get("min_proficiency", "INTERMEDIATE")
        importance = cs.get("importance_weight", 1.0)
        is_required = cs.get("is_required", True)

        student_level = student_skill_map.get(sid, "NONE")
        s_score = PROFICIENCY_SCORE.get(student_level, 0)
        r_score = PROFICIENCY_SCORE.get(required_level, 2)

        item = {
            "skill_id": sid,
            "skill_name": name,
            "skill_category": cs.get("skill_category", "General"),
            "student_level": student_level,
            "required_level": required_level,
            "is_required": is_required,
            "importance_weight": importance,
        }

        if is_required:
            total_required += 1

        if s_score >= r_score:
            item["gap_status"] = "STRONG"
            item["learning_priority"] = "LOW"
            item["priority_score"] = 0.0
            strong_skills.append(item)
            if is_required:
                matched_required += 1
        elif s_score > 0:
            item["gap_status"] = "MODERATE"
            # Priority: importance × proficiency gap
            gap = (r_score - s_score) / r_score
            priority_score = round(importance * gap * 20, 1)
            item["learning_priority"] = "HIGH" if priority_score > 5.0 else "MEDIUM"
            item["priority_score"] = priority_score
            moderate_skills.append(item)
        else:
            item["gap_status"] = "MISSING"
            priority_score = round(importance * (5.0 if is_required else 3.0), 1)
            item["learning_priority"] = "HIGH" if is_required and importance >= 4.0 else "MEDIUM" if importance >= 3.0 else "LOW"
            item["priority_score"] = priority_score
            missing_skills.append(item)

    # Sort by priority score descending
    moderate_skills.sort(key=lambda x: x["priority_score"], reverse=True)
    missing_skills.sort(key=lambda x: x["priority_score"], reverse=True)

    skill_coverage = round((matched_required / total_required * 100) if total_required > 0 else 0.0, 1)

    return {
        "strong_skills": strong_skills,
        "moderate_skills": moderate_skills,
        "missing_skills": missing_skills,
        "skill_coverage_percent": skill_coverage,
        "total_required": total_required,
        "matched_required": matched_required
    }


def generate_learning_roadmap(
    missing_skills: List[Dict],
    moderate_skills: List[Dict],
    learning_resources: List[Dict]  # [{"skill_id": ..., "title": ..., "url": ..., "estimated_hours": ..., "difficulty": ...}, ...]
) -> List[Dict]:
    """
    Generate a weekly learning roadmap.
    HIGH priority items assigned first, then MEDIUM, then LOW.
    Returns a list of milestone items with week assignments.
    """
    roadmap = []
    week = 1
    resource_map = {}
    for r in learning_resources:
        sid = r.get("skill_id")
        if sid not in resource_map:
            resource_map[sid] = []
        resource_map[sid].append(r)

    # Combine and sort: HIGH missing first, then HIGH moderate, then MEDIUM
    all_items = (
        [s for s in missing_skills if s["learning_priority"] == "HIGH"] +
        [s for s in moderate_skills if s["learning_priority"] == "HIGH"] +
        [s for s in missing_skills if s["learning_priority"] == "MEDIUM"] +
        [s for s in moderate_skills if s["learning_priority"] == "MEDIUM"] +
        [s for s in missing_skills if s["learning_priority"] == "LOW"]
    )

    for item in all_items:
        sid = item["skill_id"]
        resources = resource_map.get(sid, [])
        resource_url = resources[0]["url"] if resources else None
        resource_title = resources[0]["title"] if resources else f"Learn {item['skill_name']}"
        hours = resources[0]["estimated_hours"] if resources else 10

        roadmap.append({
            "week": week,
            "skill_id": sid,
            "skill_name": item["skill_name"],
            "title": resource_title,
            "resource_url": resource_url,
            "estimated_hours": hours,
            "gap_status": item["gap_status"],
            "learning_priority": item["learning_priority"],
            "status": "NOT_STARTED",
            "progress_percent": 0
        })
        # Move to next week approximately every 15-20 hours
        if len(roadmap) % 2 == 0:
            week += 1

    # Add final project milestone
    if all_items:
        week += 1
        roadmap.append({
            "week": week,
            "skill_id": None,
            "skill_name": "Portfolio Project",
            "title": "Build a capstone project applying all learned skills",
            "resource_url": None,
            "estimated_hours": 30,
            "gap_status": "MISSING",
            "learning_priority": "HIGH",
            "status": "NOT_STARTED",
            "progress_percent": 0
        })

    return roadmap
