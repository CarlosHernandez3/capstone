from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.models import Applicant, Document, ExtractedField

from backend.database import get_db
from backend.services.storage import load_applicants, save_new_applicant

router = APIRouter()


@router.get("/applicants")
def get_applicants(db: Session = Depends(get_db)):
    return load_applicants(db)


@router.post("/applicants")
def create_applicant(name: str, db: Session = Depends(get_db)):
    applicant = save_new_applicant(db, name)
    return applicant

@router.get("/applicants/{applicant_id}")
def get_applicant_detail(
    applicant_id: int,
    db: Session = Depends(get_db),
):
    # load the applicant
    applicant = (
        db.query(Applicant)
        .filter(Applicant.id == applicant_id)
        .first()
    )
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    # load their documents
    docs = (
        db.query(Document)
        .filter(Document.applicant_id == applicant.id)
        .all()
    )

    # build response shape, using the relationship d.fields
    return {
        "id": applicant.id,
        "name": applicant.name,
        "external_applicant_id": applicant.external_applicant_id,
        "risk_score": applicant.risk_score,
        "documents": [
            {
                "id": d.id,
                "document_type": d.document_type,
                "s3_key": d.s3_key,
                "fields": [
                    {
                        "id": f.id,
                        "field_name": f.field_name,
                        "value": f.value,
                        "source": f.source,
                        "validated": f.validated,
                    }
                    for f in d.fields  # uses SQLAlchemy relationship
                ],
            }
            for d in docs
        ],
    }
