from fastapi import APIRouter, Query
from typing import Optional
from backend.services.schedule_service import get_academic_schedule

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

@router.get("")
def read_schedule(term: Optional[str] = Query(None)):
    return get_academic_schedule(term)
