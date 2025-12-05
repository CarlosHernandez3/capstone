    import pickle
import torch
from pathlib import Path
from transformers import DonutProcessor, VisionEncoderDecoderModel
from src.pdf_to_img import pdf_to_images
from src.data_loader import (
    get_applicant_docs_by_id,
    CACHE_PATH,
    _all_document_groups
)

# -------------------------------------------------------
# Load DONUT Model Once at Import Time - change to saved model later 
# -------------------------------------------------------

processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base")
model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base")
model.eval()


# -------------------------------------------------------
# SINGLE-PAGE DONUT INFERENCE
# -------------------------------------------------------
def run_donut_fraud_inference(image):
    """
    Runs DONUT fraud analysis on a single PIL image.
    Returns text explanation.
    """

    pixel_values = processor(image, return_tensors="pt").pixel_values

    prompt = (
        "<s_fraud> "
        "Analyze this document for real vs fake indicators based on layout, fonts, alignment, "
        "logos, spacing, and structure. Provide a short explanation. </s_fraud>"
    )

    decoder_input_ids = processor.tokenizer(
        prompt, add_special_tokens=False, return_tensors="pt"
    )["input_ids"]

    with torch.no_grad():
        outputs = model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_length=512,
            early_stopping=True,
            pad_token_id=processor.tokenizer.pad_token_id
        )

    result = processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result


# -------------------------------------------------------
# MULTI-PAGE DONUT INFERENCE
# -------------------------------------------------------
def run_donut_fraud_inference_multipage(pdf_path: str):
    """
    Run DONUT fraud inference on ALL pages of a PDF.
    Returns:
        {
            "page_results": [...],
            "combined_summary": "summary text"
        }
    """
    images = pdf_to_images(pdf_path)
    page_results = []

    print(f"PDF has {len(images)} pages")

    for i, image in enumerate(images):
        print(f"Running DONUT on page {i+1}/{len(images)}")
        result = run_donut_fraud_inference(image)
        page_results.append(result)

    combined_summary = (
        " | ".join(page_results)
        if len(page_results) > 1 else page_results[0]
    )

    return {
        "page_results": page_results,
        "combined_summary": combined_summary
    }


# -------------------------------------------------------
# APPLICANT-LEVEL DONUT PROCESSING
# -------------------------------------------------------
def run_donut_inference_for_applicant(applicant_id: int):
    """
    Runs DONUT multi-page inference for all documents of an applicant.
    Stores:
        - doc["fraud_summary"] (combined summary)
        - doc["fraud_page_scores"] (per-page results)
    """

    global _all_document_groups

    if _all_document_groups is None:
        raise RuntimeError("Applicant data not initialized. Call initialize_applicant_mapping().")

    applicant = get_applicant_docs_by_id(applicant_id)
    if applicant is None:
        raise ValueError(f"No applicant found with ID: {applicant_id}")

    print(f"\nRunning DONUT inference for Applicant {applicant_id}")

    for doc in applicant["documents"]:
        pdf_path = doc["doc_path"]
        doc_id = doc["doc_id"]

        print(f"\nProcessing Document {doc_id}: {pdf_path}")

        result = run_donut_fraud_inference_multipage(pdf_path)

        doc["fraud_summary"] = result["combined_summary"]
        print(f"Stored fraud_summary for doc {doc_id}")

    # Save updated pickle
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(_all_document_groups, f)

    print(f"Updated fraud summaries saved to {CACHE_PATH}")

    return applicant
