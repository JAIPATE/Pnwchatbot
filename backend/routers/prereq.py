from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from backend.services.prereq_service import get_prerequisites_for_course, list_all_courses_with_prereqs

router = APIRouter(prefix="/api/prerequisites", tags=["prerequisites"])

@router.get("")
def read_prerequisites(course_code: Optional[str] = Query(None)):
    if not course_code:
        return list_all_courses_with_prereqs()
    return get_prerequisites_for_course(course_code)
