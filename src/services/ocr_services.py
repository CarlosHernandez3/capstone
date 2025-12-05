import uuid
import json
from pathlib import Path

from google.cloud import storage
from google.cloud import vision

# ------------------------------
# CONFIGURATION
# ------------------------------

GCS_BUCKET_NAME = "capstone-ii-applicant-documents"
TEMP_PDF_PREFIX = "ocr-temp/pdfs/"
TEMP_OCR_OUTPUT_PREFIX = "ocr-temp/output/"

# Clients
storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()


def upload_pdf_to_gcs(local_path: str) -> str:
    """
    Uploads a local PDF to GCS and returns the gs:// URI.
    """
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob_name = TEMP_PDF_PREFIX + f"{uuid.uuid4()}.pdf"
    blob = bucket.blob(blob_name)

    blob.upload_from_filename(local_path)
    return f"gs://{GCS_BUCKET_NAME}/{blob_name}"


def run_async_ocr(gcs_pdf_uri: str) -> str:
    """
    Runs async OCR on a GCS PDF and returns destination prefix.
    """

    output_prefix = TEMP_OCR_OUTPUT_PREFIX + f"{uuid.uuid4()}/"

    gcs_destination_uri = f"gs://{GCS_BUCKET_NAME}/{output_prefix}"

    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature],
        input_config=vision.InputConfig(
            gcs_source=vision.GcsSource(uri=gcs_pdf_uri),
            mime_type="application/pdf"
        ),
        output_config=vision.OutputConfig(
            gcs_destination=vision.GcsDestination(uri=gcs_destination_uri),
            batch_size=10
        )
    )

    operation = vision_client.async_batch_annotate_files(requests=[async_request])
    operation.result(timeout=600)  # wait for OCR to finish

    return output_prefix


def download_ocr_output_text(output_prefix: str) -> str:
    """
    Downloads all JSON OCR output files under the given prefix
    and returns all extracted text as a single string.
    """
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    blobs = list(bucket.list_blobs(prefix=output_prefix))
    if not blobs:
        raise RuntimeError(f"No OCR output files found at prefix: {output_prefix}")

    full_text = []

    for blob in blobs:
        if not blob.name.endswith(".json"):
            continue

        blob_data = blob.download_as_text()
        result = json.loads(blob_data)

        for resp in result.get("responses", []):
            annotation = resp.get("fullTextAnnotation")
            if annotation and "text" in annotation:
                full_text.append(annotation["text"])

    return "\n".join(full_text)


def cleanup_temp_files(prefixes: list[str]):
    """
    Removes temporary PDF and output files from GCS.
    """
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    for prefix in prefixes:
        blobs = list(bucket.list_blobs(prefix=prefix))
        for blob in blobs:
            blob.delete()


def run_pdf_ocr(local_path: str) -> str:
    """
    Full pipeline:
    1. Upload PDF to GCS
    2. Run Vision async batch OCR
    3. Download OCR output
    4. Cleanup
    5. Return OCR text
    """
    gcs_pdf_uri = upload_pdf_to_gcs(local_path)
    output_prefix = run_async_ocr(gcs_pdf_uri)
    text = download_ocr_output_text(output_prefix)

    # cleanup
    cleanup_temp_files([
        TEMP_PDF_PREFIX,
        output_prefix
    ])

    return text
