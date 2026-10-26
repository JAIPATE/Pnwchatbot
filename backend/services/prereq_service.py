from typing import Dict, List
from backend.database import execute_query

def get_prerequisites_for_course(course_code: str, campus_code: str = "HAMMOND") -> Dict:
    """Fetches prerequisite chain and formats visual node graph."""
    clean_code = course_code.strip().upper()
    
    rows = execute_query(
        """
        SELECT id, course_code, course_title, prerequisite_code, minimum_grade, campus_availability
        FROM course_prerequisites
        WHERE UPPER(course_code) = ?
        """,
        (clean_code,)
    )
    
    nodes = []
    edges = []
    
    # Target node
    nodes.append({"id": clean_code, "label": clean_code, "type": "target"})
    
    for row in rows:
        prereq = row["prerequisite_code"]
        nodes.append({"id": prereq, "label": f"{prereq} (Min Grade: {row['minimum_grade']})", "type": "prereq"})
        edges.append({"from": prereq, "to": clean_code, "label": f"Requires {row['minimum_grade']}"})
        
    return {
        "target_course": clean_code,
        "prerequisites": rows,
        "nodes": nodes,
        "edges": edges
    }

def list_all_courses_with_prereqs() -> List[Dict]:
    return execute_query("SELECT DISTINCT course_code, course_title FROM course_prerequisites ORDER BY course_code")
