import zipfile
import io
import os
import pickle
import boto3
from pathlib import Path
from dotenv import load_dotenv

# === Configuration ===
load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" 
DATA_DIR.mkdir(parents=True, exist_ok=True)


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "giggso-florida-loan-data-share")
CACHE_PATH = DATA_DIR / "document_groups.pkl"

# Global variable to store all document groups
_all_document_groups = None


def extract_from_s3():
    """Extracts all zip files from S3 into grouped list of dictionaries containing a list of documents for that applicant."""
    print("Extracting files from S3...")

    # Create base client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # List all ZIPs and assign IDs
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=BUCKET_NAME)
    zip_keys = []
    for page in pages:
        for obj in page.get("Contents", []):
            if obj["Key"].lower().endswith(".zip"):
                zip_keys.append(obj["Key"])

    # Sort to ensure consistent ordering
    zip_keys.sort()
    print(f"Found {len(zip_keys)} zip files in bucket '{BUCKET_NAME}'")

    # Extract ZIPs into memory
    document_groups = []
    for idx, zip_key_item in enumerate(zip_keys):
        applicant_id = idx + 1
        print(f"⬇Downloading & extracting ID {applicant_id}: {zip_key_item}")
        
        zip_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=zip_key_item)
        zip_buffer = io.BytesIO(zip_obj["Body"].read())

        zip_docs = []
        with zipfile.ZipFile(zip_buffer, "r") as z:
            for filename in z.namelist():
                if filename.endswith("/"):
                    continue
                file_data = z.read(filename)
                zip_docs.append({
                    "filename": filename,
                    "content": file_data
                })
                print(f"  Extracted: {filename}")

        document_groups.append({
            "applicant_id": applicant_id,
            "zip_name": zip_key_item,
            "documents": zip_docs
        })

    print(f"\nExtracted {len(document_groups)} zip files total.")
    return document_groups


def get_applicant_docs(force_refresh: bool = False):
    """
    Returns all document_groups.
    
    Args:
        force_refresh: If True, bypasses cache and pulls fresh from S3
        
    Returns:
        List of all document_groups, each with 'applicant_id', 'zip_name', and 'documents'
    """
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    # Load cached data for all documents
    if not force_refresh and os.path.exists(CACHE_PATH):
        print(f"Loading cached data from {CACHE_PATH}")
        with open(CACHE_PATH, "rb") as f:
            return pickle.load(f)

    # Otherwise extract all and cache
    document_groups = extract_from_s3()
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(document_groups, f)
    print(f"Cached extracted data at {CACHE_PATH}")
    return document_groups


def initialize_applicant_mapping(force_refresh: bool = False):
    """
    Loads and caches all document groups in memory.
    Should be called once at application startup.
    
    Args:
        force_refresh: If True, bypasses cache and pulls fresh from S3
    """
    global _all_document_groups
    
    print("Initializing applicant data...")
    _all_document_groups = get_applicant_docs(force_refresh=force_refresh)
    
    print(f"Loaded {len(_all_document_groups)} applicants into memory")
    return _all_document_groups


def get_applicant_docs_by_id(applicant_id: int):
    """
    Returns documents for a given applicant ID from the in-memory mapping.
    
    Args:
        applicant_id: The numeric ID of the applicant (1-indexed)
        
    Returns:
        Dict with 'applicant_id', 'zip_name' and 'documents' for that applicant, or None if not found
        
    Raises:
        RuntimeError: If mapping hasn't been initialized yet
    """
    if _all_document_groups is None:
        raise RuntimeError("Applicant data not initialized. Call initialize_applicant_mapping() first.")
    
    # Find the applicant by ID
    for group in _all_document_groups:
        if group['applicant_id'] == applicant_id:
            return group
    
    return None


def get_total_applicants() -> int:
    """
    Returns the total number of applicants.
    
    Returns:
        Number of applicants, or 0 if data not initialized
    """
    if _all_document_groups is None:
        return 0
    return len(_all_document_groups)


if __name__ == "__main__":
    print("Starting S3 extraction pipeline...")
    print(f"Cache path: {CACHE_PATH}")

    # Initialize the mapping once - loads all data into memory
    initialize_applicant_mapping(force_refresh=False)
    
    print(f"\nTotal applicants: {get_total_applicants()}")
    
    # Now use the ID directly - fetches from in-memory data
    print("\nFetching documents for applicant ID 1...")
    applicant = get_applicant_docs_by_id(1)
    if applicant:
        print(f"  ID: {applicant['applicant_id']}")
        print(f"  Zip: {applicant['zip_name']}")
        print(f"  Documents: {len(applicant['documents'])}")
    