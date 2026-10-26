from fastapi import APIRouter
from backend.database import execute_query

router = APIRouter(prefix="/api/campuses", tags=["campuses"])

@router.get("")
def read_campuses():
    return execute_query("SELECT id, code, name, is_active FROM campuses WHERE is_active = 1")
