from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ------------------------ CONFIG ------------------------

DATA_PATH = "data/risk-model-dataset.csv"

# Pick ONE model for now (you can switch later)
MODEL_PATH = "models/best_logreg_model.joblib"
# MODEL_PATH = "models/best_random_forest.joblib"
# MODEL_PATH = "models/best_xgb_model.joblib"

TARGET_COL = "Loan_Default_Risk"

# ------------------------ APP INIT ------------------------

app = FastAPI(title="Loan Risk Model API")

try:
    # 1) Load dataset
    df = pd.read_csv(DATA_PATH)

    # 2) Split into features/target like in the notebook
    y = df[TARGET_COL]
    X_raw = df.drop(columns=[TARGET_COL])

    # Save the original feature names – these are what the JSON is expected to send
    RAW_FEATURE_COLS = X_raw.columns.tolist()

    # 3) Figure out categorical vs numeric columns (same logic as notebook)
    cat_cols = X_raw.select_dtypes(include=["object"]).columns.tolist()
    num_cols = X_raw.select_dtypes(include=["int64", "float64"]).columns.tolist()

    # 4) Fit OneHotEncoder on ALL rows (same as notebook)
    ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    X_cat = ohe.fit_transform(X_raw[cat_cols])

    X_cat_df = pd.DataFrame(
        X_cat,
        columns=ohe.get_feature_names_out(cat_cols),
        index=X_raw.index,
    )

    X_num = X_raw[num_cols].copy()
    X_full = pd.concat([X_num, X_cat_df], axis=1)

    # 5) Do train/test split and fit StandardScaler on X_train[num_cols]
    X_train, X_test, y_train, y_test = train_test_split(
        X_full, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train[num_cols] = scaler.fit_transform(X_train[num_cols])

    # Keep final column order (VERY important so model sees features in same order)
    FINAL_FEATURE_COLS = X_full.columns.tolist()

    # 6) Load trained model
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


# ------------------------ HELPERS ------------------------

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
    Take raw applicant JSON (keys = original CSV feature names),
    run SAME preprocessing as training, and return a 2D numpy array
    ready for model.predict_proba().
    """

    # 1) Check for missing or extra fields
    missing = [col for col in RAW_FEATURE_COLS if col not in payload]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {missing}",
        )

    # Optional: warn about unexpected keys
    extras = [k for k in payload.keys() if k not in RAW_FEATURE_COLS]
    if extras:
        print(f"Warning: extra fields in payload (ignored): {extras}")

    # 2) Build one-row DataFrame in the correct column order
    raw_row = {col: payload[col] for col in RAW_FEATURE_COLS}
    input_raw = pd.DataFrame([raw_row])

    # 3) Apply OneHotEncoder to categorical columns
    input_cat = ohe.transform(input_raw[cat_cols])
    input_cat_df = pd.DataFrame(
        input_cat,
        columns=ohe.get_feature_names_out(cat_cols),
        index=input_raw.index,
    )

    # 4) Scale numeric columns using the same scaler
    input_num = input_raw[num_cols].copy()
    input_num[num_cols] = scaler.transform(input_num[num_cols])

    # 5) Concatenate num + cat and reorder columns
    input_full = pd.concat([input_num, input_cat_df], axis=1)
    input_full = input_full[FINAL_FEATURE_COLS]

    return input_full.to_numpy()


# ------------------------ ENDPOINTS ------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok" if model is not None else "error",
        "model_loaded": model is not None,
        "expected_features": RAW_FEATURE_COLS,
    }


@app.post("/api/risk-score")
def get_risk_score(payload: Dict[str, Any]):
    if model is None or ohe is None or scaler is None:
        raise HTTPException(status_code=500, detail="Model or preprocessors not loaded.")

    # Preprocess JSON into model-ready numpy array
    X_input = preprocess_single_applicant(payload)

    # Get probability of default (assumes class 1 = default)
    try:
        proba = model.predict_proba(X_input)[0, 1]
    except AttributeError:
        # Fallback if model lacks predict_proba (shouldn't happen with your models)
        pred = model.predict(X_input)[0]
        proba = float(pred)

    p_default = float(proba)
    label = probability_to_label(p_default)

    return {
        "probability_of_default": round(p_default, 4),
        "risk_label": label,
    }
