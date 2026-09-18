from typing import List

def analyze_sql_optimization(query: str) -> List[str]:
    """Analyzes query and provides optimization recommendations."""
    tips = []
    q_upper = query.upper()
    
    if "LIMIT" not in q_upper:
        tips.append("Consider adding a 'LIMIT' clause to prevent returning excessive rows.")
        
    if "SELECT *" in q_upper:
        tips.append("Avoid 'SELECT *'; specify explicit column names to optimize memory usage.")
        
    if "LIKE '%" in q_upper:
        tips.append("Leading wildcard search ('LIKE %term%') prevents index usage and requires a full table scan.")
        
    if not tips:
        tips.append("Query structure is optimized and well-formed.")
        
    return tips
