"""
Prompt Manager for formatting AI prompts for site recommendations and reports.
"""

def build_recommendation_prompt(project_name: str, phase_name: str, delay_pct: float, missing_work: str) -> str:
    return f"""
    Project: {project_name}
    Current Phase: {phase_name}
    Delay: {delay_pct}%
    Missing Work: {missing_work}
    Provide actionable construction recovery plan.
    """
