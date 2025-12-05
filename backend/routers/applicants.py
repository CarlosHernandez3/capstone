from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from google.cloud import storage
import os
from datetime import datetime, timedelta
import uuid
import httpx
from services.storage import save_new_applicant, load_applicants, get_applicant_count

router = APIRouter()

# AI Analysis API endpoint - configure this with your actual API URL
AI_ANALYSIS_API_URL = os.getenv("AI_ANALYSIS_API_URL", "http://localhost:5000/analyze")

# Initialize GCS client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__), '..', 'gcp-credentials.json')
storage_client = storage.Client(project='turing-agent-358210')

BUCKET_NAME = 'capstone-ii-applicant-documents'

# Create bucket if it doesn't exist
def ensure_bucket_exists():
    bucket = storage_client.bucket(BUCKET_NAME)
    if not bucket.exists():
        bucket = storage_client.create_bucket(BUCKET_NAME, location='US')
        print(f'Created bucket: {BUCKET_NAME}')
    return bucket

# Create bucket if it doesn't exist
def ensure_bucket_exists():
    """Create the bucket if it doesn't already exist"""
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        if not bucket.exists():
            bucket = storage_client.create_bucket(BUCKET_NAME, location='US')
            print(f"Created bucket: {BUCKET_NAME}")
        return bucket
    except Exception as e:
        print(f"Error ensuring bucket exists: {e}")
        return storage_client.bucket(BUCKET_NAME)

@router.get("/applicants")
def get_applicants():
    """Get all applicants from S3 metadata"""
    return load_applicants()

@router.post("/applicants")
async def create_applicant(
    name: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Create a new applicant:
    1. Upload PDFs to S3
    2. Send to analyzer
    3. Save metadata to S3
    """
    if not files:
        raise HTTPException(status_code=400, detail="At least one document is required")
    
    applicant_id = str(uuid.uuid4())
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get applicant number for folder name
    applicant_number = get_applicant_count() + 1
    applicant_folder = f"applicant_{applicant_number}"
    
    # Upload files to GCS
    bucket = ensure_bucket_exists()
    uploaded_documents = []
    file_data_for_analysis = []
    
    for file in files:
        try:
            # GCS path: applicant-documents-pdf/applicant_#/filename.pdf
            gcs_path = f"applicant-documents-pdf/{applicant_folder}/{file.filename}"
            file_content = await file.read()
            
            # Upload to GCS
            blob = bucket.blob(gcs_path)
            blob.upload_from_string(
                file_content,
                content_type=file.content_type or 'application/pdf'
            )
            
            # Generate signed URL (7 days)
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET"
            )
            
            uploaded_documents.append({
                "name": file.filename,
                "url": url
            })
            
            file_data_for_analysis.append({
                "filename": file.filename,
                "content": file_content,
                "gcs_path": gcs_path,
                "gcs_url": url,
                "applicant_folder": applicant_folder
            })
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload {file.filename} to GCS: {str(e)}"
            )
    
    # Send applicant ID to AI analysis API
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                AI_ANALYSIS_API_URL,
                json={"applicant_id": applicant_folder}
            )
            
            if response.status_code == 200:
                analysis_result = response.json()
                risk_score = analysis_result.get("riskScore", 0.5)
                summary = analysis_result.get("summary", "Analysis completed")
                analyzed_docs = analysis_result.get("documents", [])
                
                # Update uploaded documents with per-document analysis results
                for uploaded_doc in uploaded_documents:
                    # Find matching document in analysis results by name
                    matching_analysis = next(
                        (ad for ad in analyzed_docs if ad.get("name") == uploaded_doc["name"]),
                        None
                    )
                    
                    if matching_analysis:
                        # New structure fields
                        uploaded_doc["documentType"] = matching_analysis.get("documentType", "unknown")
                        uploaded_doc["isAuthentic"] = matching_analysis.get("isAuthentic", 0)
                        uploaded_doc["isManipulated"] = matching_analysis.get("isManipulated", 0)
                        uploaded_doc["governmentVerified"] = matching_analysis.get("governmentVerified", 0)
                        uploaded_doc["ocrMatches"] = matching_analysis.get("ocrMatches", 0)
                    else:
                        # Fallback if document not in analysis results
                        uploaded_doc["documentType"] = "unknown"
                        uploaded_doc["isAuthentic"] = 0
                        uploaded_doc["isManipulated"] = 0
                        uploaded_doc["governmentVerified"] = 0
                        uploaded_doc["ocrMatches"] = 0
                
                # Build fraud checks from document validation results
                fraud_checks = []
                for doc in uploaded_documents:
                    doc_name = doc["name"]
                    doc_type = doc.get("documentType", "Document")
                    
                    # Authenticity check
                    fraud_checks.append({
                        "label": f"{doc_name} - Authenticity",
                        "status": "pass" if doc.get("isAuthentic") == 1 else "fail",
                        "details": f"{doc_type} verified as authentic" if doc.get("isAuthentic") == 1 else f"{doc_type} authentication failed"
                    })
                    
                    # Manipulation check
                    fraud_checks.append({
                        "label": f"{doc_name} - Manipulation Check",
                        "status": "fail" if doc.get("isManipulated") == 1 else "pass",
                        "details": f"Document shows signs of manipulation" if doc.get("isManipulated") == 1 else f"No manipulation detected"
                    })
                    
                    # Government verification
                    fraud_checks.append({
                        "label": f"{doc_name} - Government Verification",
                        "status": "pass" if doc.get("governmentVerified") == 1 else "fail",
                        "details": f"Document found in government records" if doc.get("governmentVerified") == 1 else f"Document not verified in government database"
                    })
                    
                    # OCR match
                    fraud_checks.append({
                        "label": f"{doc_name} - Data Match",
                        "status": "pass" if doc.get("ocrMatches") == 1 else "fail",
                        "details": f"OCR data matches application" if doc.get("ocrMatches") == 1 else f"Discrepancy between OCR and application data"
                    })
            else:
                raise Exception(f"API returned status {response.status_code}: {response.text}")
        
    except Exception as e:
        print(f"AI Analysis API failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        risk_score = 0.0
        summary = f"Documents uploaded successfully. AI analysis is pending or unavailable."
        
        # Set default values for all documents
        for doc in uploaded_documents:
            doc["documentType"] = "unknown"
            doc["isAuthentic"] = 0
            doc["isManipulated"] = 0
            doc["governmentVerified"] = 0
            doc["ocrMatches"] = 0
        
        fraud_checks = [
            {
                "label": "Analysis Status",
                "status": "warning",
                "details": "AI analysis could not be completed at this time"
            }
        ]
    
    # Create applicant record
    applicant = {
        "id": applicant_id,
        "name": name,
        "applicationDate": today,
        "riskScore": risk_score,
        "summary": summary,
        "documents": uploaded_documents,
        "fraudChecks": fraud_checks,
        "applicantNumber": applicant_number,
        "applicantFolder": applicant_folder
    }
    
    # Save to GCS metadata
    save_new_applicant(applicant)
    
    return applicant
