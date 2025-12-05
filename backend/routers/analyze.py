from fastapi import APIRouter, UploadFile, File
from services.analyzer import analyze_files

router = APIRouter()

@router.post("/analyze")
async def analyze(files: list[UploadFile] = File(...)):
    return await analyze_files(files)
