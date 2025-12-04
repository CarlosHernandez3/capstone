from pathlib import Path
from typing import List

from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.models import Applicant, Document

UPLOAD_DIR = Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_new_applicant(db: Session, name: str) -> Applicant:
    applicant = Applicant(name=name)
    db.add(applicant)
    db.commit()
    db.refresh(applicant)
    return applicant


def load_applicants(db: Session) -> list[Applicant]:
    return db.query(Applicant).all()


def save_applicant_documents(
    db: Session, applicant_id: int, files: List[UploadFile]
) -> list[Document]:
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if applicant is None:
        return []

    saved_docs: list[Document] = []

    for upload in files:
        original_name = Path(upload.filename).name
        dest_path = UPLOAD_DIR / f"{applicant_id}_{original_name}"

        with dest_path.open("wb") as out_file:
            out_file.write(upload.file.read())

        doc = Document(
            applicant_id=applicant_id,
            document_type="pdf",  # or infer from file extension
            s3_key=str(dest_path) # temporarily store the local file path here
        )

    db.add(doc)
    saved_docs.append(doc)

    db.commit()
    for doc in saved_docs:
        db.refresh(doc)

    return saved_docs
