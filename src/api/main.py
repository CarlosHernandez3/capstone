from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import date

from .schemas import Applicant, ApplicantDocument
from ..services.ocr import run_ocr_on_files
from ..services.risk import analyze_text_and_score_risk

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FAKE_DB = []

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/applicants", response_model=List[Applicant])
def get_applicants():
    return FAKE_DB

@app.post("/api/analyze", response_model=Applicant)
async def analyze(files: List[UploadFile] = File(...)):
    file_bytes = [await f.read() for f in files]
    docs = [ApplicantDocument(name=f.filename) for f in files]

    text = run_ocr_on_files(file_bytes)

    risk, summary, name = analyze_text_and_score_risk(text)

    new = Applicant(
        id=str(len(FAKE_DB) + 1),
        name=name,
        applicationDate=str(date.today()),
        riskScore=risk,
        summary=summary,
        documents=docs
    )

    FAKE_DB.append(new)
    return new
