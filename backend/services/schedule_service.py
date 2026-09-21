from typing import List, Dict
from datetime import datetime
from backend.database import execute_query

def get_academic_schedule(term: str = None) -> List[Dict]:
    """Retrieves schedule deadlines for term and checks current date validity."""
    if term:
        query = "SELECT * FROM academic_schedules WHERE term = ? ORDER BY deadline_date ASC"
        rows = execute_query(query, (term,))
    else:
        query = "SELECT * FROM academic_schedules ORDER BY deadline_date ASC"
        rows = execute_query(query)
        
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    formatted_rows = []
    for row in rows:
        item = dict(row)
        item["is_expired"] = item["deadline_date"] < current_date
        formatted_rows.append(item)
        
    return formatted_rows
