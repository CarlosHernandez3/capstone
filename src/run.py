import requests
resp = requests.post("http://localhost:8000/score/applicant_1")
print(resp.json())
