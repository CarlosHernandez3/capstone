from fastapi import APIRouter
from services.storage import load_applicants

router = APIRouter()

@router.get("/applicants")
def get_applicants():
    return load_applicants()
