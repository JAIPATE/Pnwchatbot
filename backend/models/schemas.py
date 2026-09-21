from pydantic import BaseModel
from typing import List, Optional

class CampusItem(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool

class CampusSelectRequest(BaseModel):
    campus_id: int

class Citation(BaseModel):
    document_title: str
    section_title: str
    source_url: str

class ChatRequest(BaseModel):
    query: str
    campus_id: Optional[int] = 1
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response_text: str
    is_grounded: bool
    citations: List[Citation]
    session_id: str

class ScheduleItem(BaseModel):
    id: int
    term: str
    event_name: str
    deadline_date: str
    refund_percentage: int
    notes: Optional[str] = None

class PrereqItem(BaseModel):
    id: int
    course_code: str
    course_title: str
    prerequisite_code: str
    minimum_grade: str
    campus_availability: str

class PrereqGraphResponse(BaseModel):
    target_course: str
    prerequisites: List[PrereqItem]
    nodes: List[dict]
    edges: List[dict]
