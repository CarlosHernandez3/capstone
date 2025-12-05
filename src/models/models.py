from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from ..database import Base  # uses Base from backend/database.py


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True)
    # matches applicant_id in the CSVs
    external_applicant_id = Column(Integer, unique=True, index=True)
    name = Column(String, nullable=True)

    # risk score from the model
    risk_score = Column(Float, nullable=True)

    # One applicant → many documents
    documents = relationship("Document", back_populates="applicant")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"))
    document_type = Column(String)   
    s3_key = Column(String, nullable=True)  

    applicant = relationship("Applicant", back_populates="documents")
    fields = relationship("ExtractedField", back_populates="document")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))

    field_name = Column(String)   # from CSV
    value = Column(Text)          # from CSV

    source = Column(String)       # 'gemini_kpi' or 'validated'
    validated = Column(Boolean, nullable=True)

    document = relationship("Document", back_populates="fields")
