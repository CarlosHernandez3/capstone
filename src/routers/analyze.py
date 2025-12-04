from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.storage import save_applicant_documents
from backend.services.analyzer import analyze_files
from backend.models import Applicant

router = APIRouter()   


@router.post("/analyze")
async def analyze_applicant(
    applicant_id: int = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    # Make sure the applicant exists
    applicant = (
        db.query(Applicant)
        .filter(Applicant.id == applicant_id)
        .first()
    )
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    # Save the uploaded PDFs to disk and ocuments table
    docs = save_applicant_documents(db, applicant_id, files)

    analyzed_applicant = analyze_files(db, applicant, docs)

    # Return a clean response
    return {
        "message": "files uploaded and analyzed",
        "applicant_id": analyzed_applicant.id,
        "risk_score": analyzed_applicant.risk_score,
        "risk_label": getattr(analyzed_applicant, "risk_label", None),
        "uploaded_files": [Path(d.s3_key).name for d in docs],
    }
