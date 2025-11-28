import json
from pathlib import Path
from typing import Optional

# Path to your ground truth JSON file
# Adjust this if your file is in a different folder
GROUND_TRUTH_PATH = Path(__file__).parent / "ground_truth.json"


def load_ground_truth(path: Path = GROUND_TRUTH_PATH) -> dict:
    
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def validate_document(applicant_id: str, doc_id: str) -> bool:
    """
    Return True/False depending on whether the document is marked
    as real for the given applicant in the ground-truth file.
    """
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


# -------- Agent Tool Schema & Wrapper --------

# JSON-style schema so an agent or tool manager can register this
CROSS_VALIDATION_TOOL_SCHEMA = {
    "name": "cross_validate_document",
    "description": "Return whether a given document for a given applicant is marked as real in the ground truth dataset.",
    "parameters": {
        "type": "object",
        "properties": {
            "applicant_id": {
                "type": "string",
                "description": "Applicant identifier, e.g. 'applicant_1'."
            },
            "doc_id": {
                "type": "string",
                "description": "Document identifier for that applicant, e.g. '54673'."
            }
        },
        "required": ["applicant_id", "doc_id"]
    }
}


def cross_validate_document_tool(applicant_id: str, doc_id: str) -> dict:
    """
    Wrapper for agent use.
    An agent can call this function with applicant_id and doc_id.
    It returns a JSON-serializable dict with the validation result.
    """
    is_real = validate_document(applicant_id, doc_id)
    return {
        "applicant_id": applicant_id,
        "doc_id": doc_id,
        "is_real": is_real
    }


# -------- Local Manual Test --------

if __name__ == "__main__":
    # Example test values; change these to match your JSON
    test_applicant = "applicant_1"
    test_doc = "54673"

    result = validate_document(test_applicant, test_doc)
    print(f"Validation result for {test_applicant}, doc {test_doc}: {result}")

    # Test the agent wrapper
    wrapper_result = cross_validate_document_tool(test_applicant, test_doc)
    print("Wrapper output:", wrapper_result)

