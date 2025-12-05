# capstone/src/api/main.py

import os
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import fitz  # PyMuPDF
from google.cloud import storage

# ----------------------------------------
# 0. PROJECT PATHS & ENV SETUP
# ----------------------------------------

# This file lives at capstone/src/api/main.py
THIS_FILE = Path(__file__).resolve()
ROOT = THIS_FILE.parents[2]  # -> capstone/
SRC_DIR = ROOT / "src"
MODEL_DIR = ROOT / "models" / "mantranet" / "MantraNet"
IMAGE_ROOT = ROOT / "data" / "images"
IMAGE_ROOT.mkdir(parents=True, exist_ok=True)

# GCP credentials (adjust filename if needed)
CREDS_PATH = ROOT / "data" / "turing-agent-358210-a38a4820a9ce.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CREDS_PATH)

# Make sure we can import model code
import sys
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from models.mantranet.MantraNet.mantranet import MantraNet  # type: ignore

# ----------------------------------------
# 1. CONFIG
# ----------------------------------------

BUCKET_NAME = "capstone-ii-applicant-documents"
PDF_PREFIX = "applicant-documents-pdf/"

MAX_DOCS_PER_APPLICANT = 3  # only process first N docs

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ----------------------------------------
# 2. GCS CLIENT
# ----------------------------------------

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

# ----------------------------------------
# 3. PDF HELPERS
# ----------------------------------------

def download_pdf_bytes(blob) -> bytes:
    """
    Download raw bytes from GCS.
    If the object is a JSON wrapper (Node Buffer style), unwrap it.
    """
    raw = blob.download_as_bytes()

    # Try to detect JSON-wrapped content (as seen earlier in your pipeline)
    try:
        import json
        data = json.loads(raw)

        # Case: Node.js Buffer { file: { data: [...] } }
        if isinstance(data, dict) and "file" in data and "data" in data["file"]:
            return bytes(data["file"]["data"])

        # Case: { data: [...] }
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            return bytes(data["data"])

        # Otherwise, assume raw PDF
        return raw

    except Exception:
        # Not JSON -> assume raw PDF
        return raw


def pdf_bytes_to_images_force(pdf_bytes: bytes, dpi: int = 200) -> List[Image.Image]:
    """
    Rasterize every PDF page to an image using PyMuPDF.
    dpi=200 is a good compromise between speed and quality.
    """
    images: List[Image.Image] = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)

            for i in range(len(doc)):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                images.append(img)
    except Exception as e:
        print(f"[WARN] PDF conversion failed: {e}")
    return images


def build_image_dataset_for_applicant(
    applicant_id: str,
    max_docs: int = MAX_DOCS_PER_APPLICANT,
    dpi: int = 200,
) -> pd.DataFrame:
    """
    For a single applicant_id:
      - list their PDFs in GCS
      - take the first `max_docs` documents
      - convert all their pages to PNG images under data/images/<applicant_id>/
      - return a DataFrame with one row per page:
            applicant_id, doc_id, page_idx, image_path
    """
    prefix = f"{PDF_PREFIX}{applicant_id}/"
    blobs_iter = bucket.list_blobs(prefix=prefix)

    records: List[Dict[str, Any]] = []
    docs_seen = 0

    for blob in blobs_iter:
        if not blob.name.lower().endswith(".pdf"):
            continue

        doc_id = blob.name.split("/")[-1]

        docs_seen += 1
        if docs_seen > max_docs:
            break

        pdf_bytes = download_pdf_bytes(blob)
        pages = pdf_bytes_to_images_force(pdf_bytes, dpi=dpi)

        if not pages:
            print(f"[WARN] No pages rendered for {blob.name}")
            continue

        out_dir = IMAGE_ROOT / applicant_id
        out_dir.mkdir(parents=True, exist_ok=True)

        for page_idx, img in enumerate(pages):
            img_name = f"{Path(doc_id).stem}_page{page_idx}.png"
            img_path = out_dir / img_name
            img.save(img_path)

            records.append({
                "applicant_id": applicant_id,
                "doc_id": doc_id,
                "page_idx": page_idx,
                "image_path": str(img_path),
            })

    df = pd.DataFrame(records)
    return df

# ----------------------------------------
# 4. DATASET & SCORING
# ----------------------------------------

data_transform = transforms.Compose([
    transforms.ToTensor()
])


class FraudImageDataset(Dataset):
    """
    Simple dataset: each item = (image_tensor, applicant_id, doc_id, page_idx, image_path)
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img = Image.open(row["image_path"]).convert("RGB")
        img = data_transform(img).float()  # CxHxW

        return (
            img,
            str(row["applicant_id"]),
            str(row["doc_id"]),
            int(row["page_idx"]),
            str(row["image_path"]),
        )


def fraud_score_from_heatmap(mask: torch.Tensor) -> float:
    """
    Simple scalar aggregation from ManTraNet heatmap.
    """
    mask_np = mask.detach().cpu().numpy()
    mean_val = float(np.mean(mask_np))
    max_val = float(np.max(mask_np))
    return (mean_val + max_val) / 2.0


def load_mantranet_model() -> MantraNet:
    """
    Load ManTraNet model + weights from MODEL_DIR.
    """
    print("ManTraNet: loading weights...")
    model = MantraNet(device=DEVICE)

    imtfe_state = torch.load(MODEL_DIR / "IMTFEv4.pt", map_location=DEVICE)
    ano_state = torch.load(MODEL_DIR / "AnomalyDetectorv4.pt", map_location=DEVICE)
    main_state = torch.load(MODEL_DIR / "MantraNetv4.pt", map_location=DEVICE)

    # Strip possible "module." prefixes
    model.IMTFE.load_state_dict({k.replace("module.", ""): v for k, v in imtfe_state.items()})
    model.AnomalyDetector.load_state_dict({k.replace("module.", ""): v for k, v in ano_state.items()})
    model.load_state_dict({k.replace("module.", ""): v for k, v in main_state.items()}, strict=False)

    model.to(DEVICE)
    model.eval()
    print("ManTraNet loaded on", DEVICE)
    return model


# Load model once at startup
MANTRANET_MODEL = load_mantranet_model()


def score_applicant(applicant_id: str) -> Dict[str, Any]:
    """
    Full pipeline for one applicant:
      - build image DF (up to MAX_DOCS_PER_APPLICANT)
      - run ManTraNet on each page (batch_size=1)
      - aggregate to doc + applicant scores
    Returns a structured dict with the aggregated results.
    """
    # 1) Build image dataset
    df_pages = build_image_dataset_for_applicant(applicant_id, max_docs=MAX_DOCS_PER_APPLICANT, dpi=200)

    if df_pages.empty:
        return {
            "applicant_id": applicant_id,
            "status": "no_docs",
            "message": "No PDF pages were rendered for this applicant.",
            "num_docs": 0,
            "num_pages": 0,
            "document_scores": [],
            "applicant_score": None,
        }

    dataset = FraudImageDataset(df_pages)
    # batch_size=1 to avoid size mismatch (docs have different dimensions)
    loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)

    page_records: List[Dict[str, Any]] = []

    model = MANTRANET_MODEL

    for batch in loader:
        imgs, applicants, docs, pages, paths = batch
        imgs = imgs.to(DEVICE)  # [1, C, H, W]

        with torch.no_grad():
            heatmaps = model(imgs)  # [1, 1, H, W]

        score = fraud_score_from_heatmap(heatmaps[0, 0])

        page_records.append({
            "applicant_id": applicants[0],
            "doc_id": docs[0],
            "page_idx": int(pages[0]),
            "image_path": paths[0],
            "fraud_score": score,
        })

    df_scores = pd.DataFrame(page_records)

    # Doc-level aggregation: max fraud_score per (applicant_id, doc_id)
    doc_scores_df = (
        df_scores.groupby(["applicant_id", "doc_id"])["fraud_score"]
        .max()
        .reset_index()
    )

    # Applicant-level: max over all docs/pages
    applicant_score = float(doc_scores_df["fraud_score"].max())

    # Format results
    document_scores = [
        {
            "doc_id": row["doc_id"],
            "fraud_score": float(row["fraud_score"]),
        }
        for _, row in doc_scores_df.iterrows()
    ]

    result = {
        "applicant_id": applicant_id,
        "status": "completed",
        "num_docs": int(doc_scores_df["doc_id"].nunique()),
        "num_pages": int(df_scores.shape[0]),
        "document_scores": document_scores,
        "applicant_score": applicant_score,
    }
    return result

# ----------------------------------------
# 5. FASTAPI APP
# ----------------------------------------

app = FastAPI(title="ManTraNet Fraud Scoring API")


class ScoreResponse(BaseModel):
    applicant_id: str
    status: str
    num_docs: int
    num_pages: int
    document_scores: List[Dict[str, Any]]
    applicant_score: float | None = None
    message: str | None = None


@app.get("/")
def root():
    return {
        "status": "running",
        "usage": "POST /score/{applicant_id}",
        "docs": "/docs",
    }


@app.post("/score/{applicant_id}", response_model=ScoreResponse)
def score_endpoint(applicant_id: str):
    """
    Trigger scoring for one applicant.

    Example:
      POST http://localhost:8000/score/applicant_1
    """
    try:
        result = score_applicant(applicant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # If no docs, still return 200 with status "no_docs"
    return result
