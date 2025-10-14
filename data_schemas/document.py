from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

class DocumentEvidence(BaseModel):
    doc_type: Literal["driver_license","passport","ssn_card","utility_bill","bank_statement","paystub","w2","other"]
    issuer: Optional[str] = None
    id_number_masked: Optional[str] = None
    issued_on: Optional[date] = None
    name_on_doc: Optional[str] = None
    address_on_doc: Optional[str] = None