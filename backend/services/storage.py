import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "applicants.json")

def load_applicants():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_new_applicant(applicant):
    applicants = load_applicants()
    applicants.append(applicant)
    with open(DATA_PATH, "w") as f:
        json.dump(applicants, f, indent=4)
