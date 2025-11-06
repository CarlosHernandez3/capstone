import zipfile
import io
import os
import pickle
import boto3

from dotenv import load_dotenv

# import sys, os
# print(">>> Executable:", sys.executable)
# print(">>> CWD:", os.getcwd())
# print(">>> sys.path:", sys.path[:3])


# === Configuration ===
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "giggso-florida-loan-data-share")
CACHE_PATH = os.getenv("CACHE_PATH", "data/document_groups.pkl")


def extract_from_s3():
    """Extracts all zip files from S3 into grouped lists."""
    print("Extracting files from S3...")

    # Create base client and detect region
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # List all ZIPs
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=BUCKET_NAME)
    zip_keys = []
    for page in pages:
        for obj in page.get("Contents", []):
            if obj["Key"].lower().endswith(".zip"):
                zip_keys.append(obj["Key"])

    print(f"Found {len(zip_keys)} zip files in bucket '{BUCKET_NAME}'")

    # Extract ZIPs into memory
    document_groups = []
    for zip_key in zip_keys:
        print(f"⬇Downloading & extracting: {zip_key}")
        zip_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=zip_key)
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
                print(f"Extracted: {filename}")

        document_groups.append({
            "zip_name": zip_key,
            "documents": zip_docs
        })

    print(f"\nExtracted {len(document_groups)} zip files total.")
    return document_groups


def get_document_groups(force_refresh: bool = False):
    """
    Returns the document_groups list.
    Loads from cache if available, otherwise pulls from S3 and caches it.
    """
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    # Load cached data
    if not force_refresh and os.path.exists(CACHE_PATH):
        print(f"Loading cached data from {CACHE_PATH}")
        with open(CACHE_PATH, "rb") as f:
            return pickle.load(f)

    # Otherwise extract and cache
    document_groups = extract_from_s3()
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(document_groups, f)
    print(f"Cached extracted data at {CACHE_PATH}")
    return document_groups

if __name__ == "__main__":
    print("Starting S3 extraction pipeline...")
    print(f"Cache path: {CACHE_PATH}")

    document_groups = get_document_groups(force_refresh=False)

    print(f"\nExtraction complete. Loaded {len(document_groups)} document groups.")
