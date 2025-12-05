import json
import os
from google.cloud import storage

# Initialize GCS client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__), '..', 'gcp-credentials.json')
storage_client = storage.Client(project='turing-agent-358210')

BUCKET_NAME = 'capstone-ii-applicant-documents'
METADATA_KEY = 'applicant-metadata/applicants.json'

def load_applicants():
    """Load all applicants from GCS"""
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(METADATA_KEY)
        
        if blob.exists():
            content = blob.download_as_text()
            return json.loads(content)
        else:
            return []
    except Exception as e:
        print(f"Error loading from GCS: {str(e)}")
        return []

def save_new_applicant(applicant):
    """Save new applicant to GCS"""
    applicants = load_applicants()
    applicants.append(applicant)
    
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(METADATA_KEY)
        blob.upload_from_string(
            json.dumps(applicants, indent=2),
            content_type='application/json'
        )
        print(f"Saved applicant {applicant['id']} to GCS")
    except Exception as e:
        print(f"Error saving to GCS: {str(e)}")

def get_applicant_count():
    """Get the current count of applicants"""
    applicants = load_applicants()
    return len(applicants)
