from typing import List
from sqlalchemy.orm import Session

from backend.models import Applicant, Document, ExtractedField

def run_pdf_ocr(local_path: str) -> str:
    """
    TEMP STUB 
    """
    try:
        size = 0
        with open(local_path, "rb") as f:
            chunk = f.read(8192)
            while chunk:
                size += len(chunk)
                chunk = f.read(8192)
        return f"[DEMO OCR]."
    except Exception as e:
        return f"[DEMO OCR] Error reading file {local_path}: {e}"


def analyze_files(
    db: Session,
    applicant: Applicant,
    documents: List[Document],
):
    # temporary dummy risk score
    applicant.risk_score = 0.0
    applicant.risk_label = "Unknown"

    for doc in documents:

        if doc.document_type == "pdf" and doc.s3_key:
            try:
                # call your new OCR
                raw_text = run_pdf_ocr(doc.s3_key)

                field = ExtractedField(
                    document_id=doc.id,
                    field_name="raw_text",
                    value=raw_text,
                    source="pdf_ocr",
                    validated=False,
                )
                db.add(field)

            except Exception as e:
                error_field = ExtractedField(
                    document_id=doc.id,
                    field_name="pdf_error",
                    value=str(e),
                    source="pdf_ocr",
                    validated=False,
                )
                db.add(error_field)

    db.commit()
    db.refresh(applicant)
    return applicant
