from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from data_schemas.employment import Employment
from data_schemas.paystub_item import PaystubItem
from data_schemas.document import DocumentEvidence

class ApplicantProfile(BaseModel):
    first_name: str
    last_name: str
    dob: Optional[date] = None
    ssn_last4: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    employment: Optional[Employment] = None
    paystubs: List[PaystubItem] = Field(default_factory=list)
    documents: List[DocumentEvidence] = Field(default_factory=list)