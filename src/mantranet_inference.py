# import os
# import io
# import sys
# import json
# import fitz
# import torch
# import numpy as np
# import pandas as pd
# from PIL import Image
# from flask import Flask, request, jsonify
# from google.cloud import storage
# from tqdm import tqdm
# from pathlib import Path
# from torch.utils.data import Dataset, DataLoader

# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# sys.path.append(PROJECT_ROOT)
# from models.mantranet.MantraNet.mantranet import MantraNet

# app = Flask(__name__)
# ROOT = Path(__file__).resolve().parent.parent
# cred_path = ROOT / "data" / "turing-agent-358210-a38a4820a9ce.json"

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path)

# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# PROJECT_ROOT = Path.cwd().parent
# IMAGE_ROOT = PROJECT_ROOT / "data" / "images"
# IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
# print(PROJECT_ROOT)
# print(ROOT)

# # =========================
# # PDF Prefix in GCS
# # =========================
# BUCKET_NAME = "capstone-ii-applicant-documents"
# PDF_PREFIX = "applicant-documents-pdf/"
# META_PREFIX = "applicant-metadata/"

# client = storage.Client()
# bucket = client.bucket(BUCKET_NAME)



# # =========================
# # Load ManTraNet once
# # =========================
# MODEL_DIR = ROOT / "models" / "mantranet" / "MantraNet"

# model = MantraNet(device=DEVICE)

# # clean = lambda x: {k.replace("module.", ""): v for k, v in x.items()}


# model.IMTFE.load_state_dict(torch.load(MODEL_DIR/"IMTFEv4.pt", map_location=DEVICE))
# model.AnomalyDetector.load_state_dict(torch.load(MODEL_DIR/"AnomalyDetectorv4.pt", map_location=DEVICE))
# model.load_state_dict(torch.load(MODEL_DIR/"MantraNetv4.pt", map_location=DEVICE), strict=False)
# model.to(DEVICE).eval()


# # =========================
# # Helpers
# # =========================
# def download_pdf_bytes(blob):
#     raw = blob.download_as_bytes()

#     try:
#         data = json.loads(raw)
#         if isinstance(data, dict):
#             if "file" in data and "data" in data["file"]:
#                 return bytes(data["file"]["data"])
#             if "data" in data and isinstance(data["data"], list):
#                 return bytes(data["data"])
#     except Exception:
#         pass

#     return raw


# def pdf_to_images(pdf_bytes, dpi=200):
#     images = []
#     try:
#         with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
#             zoom = dpi / 72
#             matrix = fitz.Matrix(zoom, zoom)
#             for i in range(len(doc)):
#                 pix = doc.load_page(i).get_pixmap(matrix=matrix)
#                 img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                 images.append(img)
#     except Exception as e:
#         print(f"PDF conversion failed: {e}")
#     return images


# def fraud_score(mask: torch.Tensor):
#     m = mask.detach().cpu().numpy()
#     return float(m.mean() + m.max()) / 2.0


# class PageDataset(Dataset):
#     def __init__(self, df):
#         self.df = df

#     def __len__(self):
#         return len(self.df)

#     def __getitem__(self, i):
#         row = self.df.iloc[i]
#         img = Image.open(row["image_path"]).convert("RGB")
#         img = img.resize((512, 512))
#         img = torch.tensor(np.array(img)).permute(2,0,1).float() / 255.0
#         return img, row


# def end_to_end_pipeline(applicant_id):
#     print(f"PROCESSING → {applicant_id}")

#     # Step 1: Pull docs from GCS
#     blobs = list(bucket.list_blobs(prefix=f"{PDF_PREFIX}{applicant_id}/"))
#     records = []

#     for blob in tqdm(blobs, desc="Downloading+Converting PDFs"):
#         if not blob.name.lower().endswith(".pdf"):
#             continue

#         pdf_bytes = download_pdf_bytes(blob)
#         doc_id = blob.name.split("/")[-1]

#         images = pdf_to_images(pdf_bytes)
#         if not images:
#             continue

#         out_dir = IMAGE_ROOT / applicant_id
#         out_dir.mkdir(parents=True, exist_ok=True)

#         for page_idx, img in enumerate(images):
#             img_path = out_dir / f"{Path(doc_id).stem}_page{page_idx}.png"
#             img.save(img_path)

#             records.append({
#                 "applicant_id": applicant_id,
#                 "doc_id": doc_id,
#                 "page_idx": page_idx,
#                 "image_path": str(img_path)
#             })

#     if not records:
#         return None

#     df_pages = pd.DataFrame(records)

#     # Step 2: ManTraNet Scoring
#     loader = DataLoader(PageDataset(df_pages), batch_size=1)

#     page_scores = []
#     for imgs, row in tqdm(loader, desc="Running ManTraNet"):
#         imgs = imgs.to(DEVICE)
#         with torch.no_grad():
#             heatmap = model(imgs)[0,0]
#             score = fraud_score(heatmap)

#         rec = row.to_dict()
#         rec["fraud_score"] = score
#         page_scores.append(rec)

#     page_df = pd.DataFrame(page_scores)

#     # Step 3: Aggregate
#     doc_df = page_df.groupby("doc_id")["fraud_score"].max().reset_index()
#     applicant_score = float(doc_df["fraud_score"].max())

#     return {
#         "applicant_id": applicant_id,
#         "applicant_score": applicant_score,
#         "documents": [
#             {
#                 "doc_id": doc,
#                 "score": float(score),
#                 "pages": page_df[page_df["doc_id"] == doc]
#                         [["page_idx","fraud_score"]]
#                         .assign(fraud_score=lambda x: x.fraud_score.astype(float))
#                         .to_dict(orient="records")
#             }
#             for doc, score in zip(doc_df["doc_id"], doc_df["fraud_score"])
#         ]
#     }


# # =========================
# # API ROUTE
# # =========================
# @app.route("/process_applicant")
# def process_applicant():
#     applicant_id = request.args.get("applicant_id")
#     if not applicant_id:
#         return jsonify({"error": "Missing applicant_id"}), 400

#     result = end_to_end_pipeline(applicant_id)
#     if result is None:
#         return jsonify({"error": "No valid PDFs found"}), 404

#     return jsonify(result)


# if __name__ == "__main__":
#     print("Server Running on http://localhost:8000")
#     app.run(host="0.0.0.0", port=8000, debug=False)


import os
import json
from pathlib import Path
from flask import Flask, jsonify
from google.cloud import storage
from tqdm import tqdm
import torch
from PIL import Image
import fitz
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

# =============================================
# CONFIG
# =============================================
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(
    Path(__file__).resolve().parents[1] / "data" / "turing-agent-358210-a38a4820a9ce.json"
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
IMAGE_ROOT = DATA_DIR / "images"

bucket_name = "capstone-ii-applicant-documents"
PDF_PREFIX = "applicant-documents-pdf"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Fix Python import path
import sys
sys.path.append(str(ROOT))

from models.mantranet.MantraNet.mantranet import MantraNet


# =============================================
# LOAD MODEL
# =============================================
def load_mantranet():
    model_dir = ROOT / "models" / "mantranet" / "MantraNet"
    model = MantraNet(device=DEVICE)

    # Remove “module.” prefix if present
    clean = lambda x: {k.replace("module.", ""): v for k, v in x.items()}

    model.IMTFE.load_state_dict(clean(torch.load(model_dir/"IMTFEv4.pt", map_location=DEVICE)))
    model.AnomalyDetector.load_state_dict(clean(torch.load(model_dir/"AnomalyDetectorv4.pt", map_location=DEVICE)))
    model.load_state_dict(clean(torch.load(model_dir/"MantraNetv4.pt", map_location=DEVICE)), strict=False)

    model.to(DEVICE)
    model.eval()
    return model

model = load_mantranet()
print("ManTraNet loaded!", flush=True)


# =============================================
# HELPERS
# =============================================
client = storage.Client()
bucket = client.bucket(bucket_name)

def download_pdf_bytes(blob):
    raw = blob.download_as_bytes()
    try:
        data = json.loads(raw)
        if "file" in data and "data" in data["file"]:
            return bytes(data["file"]["data"])
        if "data" in data:
            return bytes(data["data"])
    except:
        pass
    return raw


def render_pdf_pages(pdf_bytes, dpi=144):
    images = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            for i in range(len(doc)):
                pix = doc.load_page(i).get_pixmap(matrix=mat, alpha=False)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                images.append(img)
    except Exception as e:
        print("PDF rendering failed:", e)
    return images


class FraudDataset(Dataset):
    def __init__(self, rows):
        self.rows = rows
        self.tf = transforms.ToTensor()
    def __len__(self): return len(self.rows)
    def __getitem__(self, i):
        row = self.rows.iloc[i]
        img = Image.open(row["image_path"]).convert("RGB")
        return self.tf(img).float(), row["image_path"], row["doc_id"], row["page_idx"]


def fraud_score(mask):
    m = mask.detach().cpu().numpy()
    return float(m.mean() + m.max()) / 2.0


# =============================================
# MAIN PROCESS FOR ONE APPLICANT
# =============================================
def run_pipeline(applicant_id):
    print(f"Processing applicant: {applicant_id}")

    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    records = []

    for blob in tqdm(bucket.list_blobs(prefix=f"{PDF_PREFIX}/{applicant_id}")):
        if not blob.name.endswith(".pdf"):
            continue
        pdf_bytes = download_pdf_bytes(blob)

        parts = blob.name.split("/")
        _, app, filename = parts[-3:]
        doc_id = filename

        imgs = render_pdf_pages(pdf_bytes)
        if not imgs:
            continue

        out_dir = IMAGE_ROOT / app
        out_dir.mkdir(parents=True, exist_ok=True)

        for i, img in enumerate(imgs):
            p = out_dir / f"{Path(doc_id).stem}_p{i}.png"
            img.save(p)
            records.append({
                "applicant_id": app,
                "doc_id": doc_id,
                "page_idx": i,
                "image_path": str(p)
            })

    df = pd.DataFrame(records)
    if df.empty:
        return {"error": "No docs/images found"}

    # Run ManTraNet
    dataset = FraudDataset(df)
    loader = DataLoader(dataset, batch_size=1, shuffle=False)

    results = []
    for imgs, paths, docs, pages in tqdm(loader):
        imgs = imgs.to(DEVICE)
        with torch.no_grad():
            heat = model(imgs)[0][0]
        results.append({
            "image_path": paths[0],
            "doc_id": docs[0],
            "page_idx": int(pages[0]),
            "fraud_score": fraud_score(heat)
        })

    scores = pd.DataFrame(results)

    doc_scores = scores.groupby("doc_id")["fraud_score"].max()
    app_score = float(doc_scores.max())

    return {
        "applicant_id": applicant_id,
        "documents": doc_scores.to_dict(),
        "final_fraud_score": app_score
    }


# =============================================
# FLASK API
# =============================================
app = Flask(__name__)
@app.route("/score/<applicant_id>", methods=["POST"])
def score_applicant(applicant_id):
    try:
        print(f"Running full scoring pipeline for {applicant_id}...")

        results = run_pipeline(applicant_id)

        return jsonify({
            "status": "success",
            "applicant_id": applicant_id,
            "documents_scored": len(results),
            "results_file": f"fraud_scores_{applicant_id}.csv"
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "applicant_id": applicant_id,
            "message": str(e)
        }), 500



@app.route("/")
def home():
    return {"status": "running", "usage": "/score/<applicant_id>"}

# if __name__ == "__main__":
#     import requests
#     import time
    
#     # Give server a moment to start when running locally
#     time.sleep(2)

#     test_applicant = "applicant_1"  # change as needed
#     print(f"Triggering scoring for: {test_applicant}")

#     url = f"http://localhost:8000/score/{test_applicant}"
#     resp = requests.post(url)

#     print("Server response:")
#     try:
#         print(resp.json())
#     except:
#         print(resp.text)

if __name__ == "__main__":
    print("Server Running on http://localhost:8000")
    app.run(host="0.0.0.0", port=8000)


