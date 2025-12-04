from typing import List
from pydantic import BaseModel

class ApplicantDocument(BaseModel):
    name: str
    url: str | None = None

class Applicant(BaseModel):
    id: str
    name: str
    applicationDate: str
    riskScore: float
    summary: str
    documents: List[ApplicantDocument]
