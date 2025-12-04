from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ---------------------------------------------------------
# CONFIG – paths are RELATIVE to where risk_api.py lives
# ---------------------------------------------------------

DATA_PATH = "data/risk-model-dataset.csv"

# Choose which trained model to use
MODEL_PATH = "models/best_logreg_model.joblib"
# MODEL_PATH = "models/best_random_forest.joblib"
# MODEL_PATH = "models/best_xgb_model.joblib"

TARGET_COL = "Loan_Default_Risk"

# ---------------------------------------------------------
# APP INIT – load data, fit preprocessors, load model
# ---------------------------------------------------------

app = FastAPI(title="Loan Risk Model API")

try:
    # 1) Load full dataset
    df = pd.read_csv(DATA_PATH)

    # 2) Split into features/target like in the notebook
    #    IMPORTANT: Applicant_ID is NOT used as a model feature.
    DROP_COLS_FOR_MODEL = [TARGET_COL, "Applicant_ID"]

    y = df[TARGET_COL]
    X_raw = df.drop(columns=DROP_COLS_FOR_MODEL)

    # Keep the raw feature names – this is what the JSON is expected to send
    RAW_FEATURE_COLS = X_raw.columns.tolist()

    # 3) Identify categorical vs numerical columns
    cat_cols = X_raw.select_dtypes(include=["object"]).columns.tolist()
    num_cols = X_raw.select_dtypes(include=["int64", "float64"]).columns.tolist()

    # 4) Fit OneHotEncoder on all rows for categorical columns
    ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    X_cat = ohe.fit_transform(X_raw[cat_cols])

    X_cat_df = pd.DataFrame(
        X_cat,
        columns=ohe.get_feature_names_out(cat_cols),
        index=X_raw.index,
    )

    # 5) Keep numeric columns as-is (for now)
    X_num = X_raw[num_cols].copy()

    # 6) Combine numeric + categorical into one feature matrix
    X_full = pd.concat([X_num, X_cat_df], axis=1)

    # 7) Train/test split and fit StandardScaler on train numeric columns
    X_train, X_test, y_train, y_test = train_test_split(
        X_full, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train[num_cols] = scaler.fit_transform(X_train[num_cols])

    # Save final column ordering so we can reproduce it at inference time
    FINAL_FEATURE_COLS = X_full.columns.tolist()

    # 8) Load trained model
    model = joblib.load(MODEL_PATH)

except Exception as e:
    print(f"*** ERROR during startup: {e}")
    df = None
    model = None
    ohe = None
    scaler = None
    RAW_FEATURE_COLS = []
    cat_cols = []
    num_cols = []
    FINAL_FEATURE_COLS = []


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def probability_to_label(p_default: float) -> str:
    """Map probability of default into a risk bucket."""
    if p_default < 0.2:
        return "Low"
    elif p_default < 0.5:
        return "Medium"
    else:
        return "High"


def preprocess_single_applicant(payload: Dict[str, Any]) -> np.ndarray:
    """
    Take raw applicant JSON (keys = original feature names),
    run SAME preprocessing as training, and return a 2D numpy array
    ready for model.predict_proba().
    """

    if not RAW_FEATURE_COLS:
        raise HTTPException(status_code=500, detail="Preprocessors not initialized.")

    # 1) Validate required fields
    missing = [col for col in RAW_FEATURE_COLS if col not in payload]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {missing}",
        )

    # Optional: warn about any extra keys (ignored)
    extras = [k for k in payload.keys() if k not in RAW_FEATURE_COLS]
    if extras:
        print(f"Warning: extra fields in payload (ignored): {extras}")

    # 2) Build one-row DataFrame in the correct column order
    raw_row = {col: payload[col] for col in RAW_FEATURE_COLS}
    input_raw = pd.DataFrame([raw_row])

    # 3) Apply OHE to categorical columns
    input_cat = ohe.transform(input_raw[cat_cols])
    input_cat_df = pd.DataFrame(
        input_cat,
        columns=ohe.get_feature_names_out(cat_cols),
        index=input_raw.index,
    )

    # 4) Scale numeric columns with the trained scaler
    input_num = input_raw[num_cols].copy()
    input_num[num_cols] = scaler.transform(input_num[num_cols])

    # 5) Concatenate numeric + categorical and reorder columns
    input_full = pd.concat([input_num, input_cat_df], axis=1)
    input_full = input_full[FINAL_FEATURE_COLS]

    return input_full.to_numpy()


# ---------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------

@app.get("/api/health")
def health():
    """
    Health check endpoint.
    Returns whether the model is loaded and which raw features are expected.
    """
    return {
        "status": "ok" if model is not None else "error",
        "model_loaded": model is not None,
        "expected_features": RAW_FEATURE_COLS,
    }


@app.post("/api/risk-score")
def get_risk_score(payload: Dict[str, Any]):
    """
    Main inference endpoint.

    Body: JSON with all features listed in /api/health.expected_features.
    Returns: probability_of_default (float) and risk_label (Low/Medium/High).
    """
    if model is None or ohe is None or scaler is None:
        raise HTTPException(status_code=500, detail="Model or preprocessors not loaded.")

    # Preprocess into model-ready numpy array
    X_input = preprocess_single_applicant(payload)

    # Predict probability of default (assumes class 1 = default)
    try:
        proba = model.predict_proba(X_input)[0, 1]
    except AttributeError:
        # Fallback if model does not implement predict_proba (should not happen here)
        pred = model.predict(X_input)[0]
        proba = float(pred)

    p_default = float(proba)
    label = probability_to_label(p_default)

    return {
        "probability_of_default": round(p_default, 4),
        "risk_label": label,
    }
