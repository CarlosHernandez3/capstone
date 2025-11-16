import uuid
from datetime import date

from services.storage import save_new_applicant

async def analyze_files(files):
    # For now: simple placeholder logic (MVP)
    file_names = [file.filename for file in files]

    result = {
        "id": str(uuid.uuid4()),
        "name": "Unknown",
        "applicationDate": str(date.today()),
        "riskScore": 0.5,
        "summary": "No readable text found. (MVP)",
        "documents": [{"name": name, "url": None} for name in file_names],
    }

    save_new_applicant(result)
    return result
