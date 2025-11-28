import json
from pathlib import Path
from typing import Optional

# Path to your ground truth JSON file
# Adjust this if your file is in a different folder
GROUND_TRUTH_PATH = Path(__file__).parent / "ground_truth.json"


def load_ground_truth(path: Path = GROUND_TRUTH_PATH) -> dict:
    """
    Load the ground truth JSON file into a Python dictionary.

    This is separated into its own function so it can be reused or
    mocked in tests later.
    """
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def validate_document(applicant_id: str, doc_id: str) -> bool:
   
    data = load_ground_truth()

    applicant = data.get(applicant_id)
    if applicant is None:
        # Applicant not found in ground truth
        return False

    doc_entry: Optional[dict] = applicant.get(doc_id)
    if doc_entry is None:
        # Document not found for this applicant
        return False

    return bool(doc_entry.get("real", False))

if __name__ == "__main__":
    # Example test values; change these to match your JSON
    test_applicant = "applicant_1"
    test_doc = "54673"

    result = validate_document(test_applicant, test_doc)
    print(f"Validation result for {test_applicant}, doc {test_doc}: {result}")
