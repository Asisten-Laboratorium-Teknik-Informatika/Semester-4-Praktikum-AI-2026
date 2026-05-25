"""
Prediction service — kompatibel dengan model v4 (TF-IDF + engineered features)
dan fallback ke v1 (base features only) atau rule-based.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import os

import joblib
import numpy as np
import pandas as pd

MODEL_DIR = Path("ml_models")
MODEL_PATH = MODEL_DIR / "burnout_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
TFIDF_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"

RISK_LABELS = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}

BASE_FEATURES = [
    "sleep_hours", "sleep_quality", "workload_score",
    "mood_score", "social_score", "recovery_score",
    "sentiment_score", "cognitive_distortion_score",
    "absolutist_count", "helplessness_count",
    "keyword_count", "message_avg_length"
]

# Cache loaded assets
_cached_assets = None


def _as_float(features: dict[str, Any], key: str, default: float) -> float:
    try:
        return float(features.get(key, default))
    except (TypeError, ValueError):
        return default


# ═══════════════════════════════════════
#  RULE-BASED FALLBACK
# ═══════════════════════════════════════

def rule_based_predict(features: dict[str, Any]) -> dict[str, Any]:
    """Fallback rule-based scoring saat model belum tersedia."""
    score = 0
    factors: list[str] = []

    sleep = _as_float(features, "sleep_hours", 7)
    workload = _as_float(features, "workload_score", 5)
    mood = _as_float(features, "mood_score", 5)
    recovery = _as_float(features, "recovery_score", 5)
    sentiment = _as_float(features, "sentiment_score", 0)
    social = _as_float(features, "social_score", 5)
    distortion = _as_float(features, "cognitive_distortion_score", 0)

    if sleep < 4:
        score += 3; factors.append("Tidur sangat kurang")
    elif sleep < 5.5:
        score += 2; factors.append("Tidur kurang")
    elif sleep < 6.5:
        score += 1; factors.append("Tidur agak kurang")

    if workload >= 9:
        score += 3; factors.append("Beban kerja sangat tinggi")
    elif workload >= 7:
        score += 2; factors.append("Beban kerja tinggi")

    if mood <= 3:
        score += 3; factors.append("Suasana hati sangat rendah")
    elif mood <= 5:
        score += 1; factors.append("Suasana hati menurun")

    if recovery <= 3:
        score += 2; factors.append("Pemulihan harian buruk")

    if sentiment <= -0.5:
        score += 2; factors.append("Sentimen sangat negatif")
    elif sentiment <= -0.2:
        score += 1; factors.append("Sentimen negatif")

    if social <= 3:
        score += 1; factors.append("Interaksi sosial rendah")

    if distortion >= 0.6:
        score += 2; factors.append("Distorsi kognitif terdeteksi")

    if score >= 8:
        level = "HIGH"
    elif score >= 4:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_level": level,
        "score": score,
        "factors": factors[:3],
        "source": "rule_based",
    }


# ═══════════════════════════════════════
#  FEATURE ENGINEERING (match training)
# ═══════════════════════════════════════

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Harus PERSIS sama dengan yang di train_model.py."""
    out = df.copy()

    # Rasio
    out["recovery_workload_ratio"] = (out["recovery_score"] + 0.1) / (out["workload_score"] + 0.1)
    out["sleep_workload_ratio"] = (out["sleep_hours"] + 0.1) / (out["workload_score"] + 0.1)
    out["social_mood_ratio"] = (out["social_score"] + 0.1) / (out["mood_score"] + 0.1)

    # Interaksi
    out["sleep_x_mood"] = out["sleep_hours"] * out["mood_score"]
    out["workload_x_distortion"] = out["workload_score"] * out["cognitive_distortion_score"]
    out["sentiment_x_mood"] = out["sentiment_score"] * out["mood_score"]

    # Aggregasi
    out["wellbeing_score"] = (
        out["mood_score"] + out["social_score"] + out["recovery_score"] + out["sleep_quality"]
    ) / 4.0
    out["stress_score"] = (
        out["workload_score"] + out["cognitive_distortion_score"] * 10 +
        out["absolutist_count"] + out["helplessness_count"]
    ) / 4.0
    out["balance_score"] = out["wellbeing_score"] - out["stress_score"]

    # Non-linear
    out["sleep_deficit"] = np.maximum(0, 7 - out["sleep_hours"])
    out["extreme_workload"] = (out["workload_score"] >= 8).astype(int)
    out["social_isolation"] = (out["social_score"] <= 3).astype(int)
    out["severe_sentiment"] = (out["sentiment_score"] <= -0.5).astype(int)

    return out


# ═══════════════════════════════════════
#  MODEL LOADING
# ═══════════════════════════════════════

def _load_assets():
    """Load model + scaler + TF-IDF (jika ada). Cache setelah load pertama."""
    global _cached_assets
    if _cached_assets is not None:
        return _cached_assets

    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        return None

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    tfidf = None
    if TFIDF_PATH.exists():
        try:
            tfidf = joblib.load(TFIDF_PATH)
        except Exception:
            pass

    _cached_assets = {"model": model, "scaler": scaler, "tfidf": tfidf}
    return _cached_assets


# ═══════════════════════════════════════
#  MODEL PREDICTION
# ═══════════════════════════════════════

def model_predict(features: dict[str, Any], user_text: str = "") -> dict[str, Any]:
    """
    Prediksi menggunakan model ML.
    Mendukung model v4 (TF-IDF + engineered) dan v1 (base features only).
    """
    assets = _load_assets()
    if assets is None:
        raise FileNotFoundError("Model belum tersedia.")

    model = assets["model"]
    scaler = assets["scaler"]
    tfidf = assets["tfidf"]

    # Base features default to 'healthy' values if missing, so new users start at LOW risk
    default_baselines = {
        "sleep_hours": 8.0, "sleep_quality": 8.0, "workload_score": 3.0,
        "mood_score": 8.0, "social_score": 8.0, "recovery_score": 8.0,
        "sentiment_score": 0.0, "cognitive_distortion_score": 0.0,
        "absolutist_count": 0.0, "helplessness_count": 0.0,
        "keyword_count": 0.0, "message_avg_length": 20.0
    }
    row_data = {col: _as_float(features, col, default_baselines.get(col, 0.0)) for col in BASE_FEATURES}
    df_row = pd.DataFrame([row_data])

    # Check jika model v4 (pakai TF-IDF + engineered features)
    if tfidf is not None:
        # Engineer features
        df_eng = engineer_features(df_row)

        # Scale numerical
        from scipy.sparse import hstack, csr_matrix
        num_scaled = scaler.transform(df_eng)

        # TF-IDF dari teks user
        tfidf_vec = tfidf.transform([user_text])

        # Combine
        X_combined = hstack([csr_matrix(num_scaled), tfidf_vec])
        predicted_class = int(model.predict(X_combined)[0])

        proba = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X_combined)[0]
    else:
        # Model v1/v2/v3 — base features only
        feature_names = list(getattr(scaler, "feature_names_in_", BASE_FEATURES))
        row = pd.DataFrame([{name: row_data.get(name, 0.0) for name in feature_names}])
        scaled = scaler.transform(row)
        predicted_class = int(model.predict(scaled)[0])

        proba = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(scaled)[0]

    result = {
        "risk_level": RISK_LABELS.get(predicted_class, str(predicted_class)),
        "class_id": predicted_class,
        "source": "ml_model_v4" if tfidf else "ml_model",
    }

    if proba is not None:
        result["probabilities"] = {
            RISK_LABELS.get(i, str(i)): float(v)
            for i, v in enumerate(proba)
        }

    return result


# ═══════════════════════════════════════
#  MAIN API
# ═══════════════════════════════════════

def predict_burnout(features: dict[str, Any], user_text: str = "") -> dict[str, Any]:
    """
    Main prediction function. Dipanggil dari chat endpoint.
    Coba model ML dulu, fallback ke rule-based.
    """
    try:
        result = model_predict(features, user_text)
        result["factors"] = explain_prediction(features, user_text)
        return result
    except Exception:
        return rule_based_predict(features)


def explain_prediction(features: dict[str, Any], user_text: str = "") -> list[str]:
    """
    Jelaskan kenapa level burnout ini diprediksi.
    Coba SHAP dulu (data-driven), fallback ke rule-based.
    """
    if os.environ.get("LIFELENS_DISABLE_SHAP", "1") != "0":
        return _rule_based_explain(features)

    try:
        return _shap_explain(features, user_text)
    except Exception:
        return _rule_based_explain(features)


def _shap_explain(features: dict[str, Any], user_text: str = "") -> list[str]:
    """Gunakan SHAP TreeExplainer untuk penjelasan berbasis data."""
    import shap

    SHAP_PATH = MODEL_DIR / "shap_explainer.pkl"
    if not SHAP_PATH.exists():
        raise FileNotFoundError("SHAP explainer not found")

    assets = _load_assets()
    if assets is None:
        raise FileNotFoundError("Model not loaded")

    explainer = joblib.load(SHAP_PATH)
    model = assets["model"]
    scaler = assets["scaler"]
    tfidf = assets["tfidf"]

    # Build feature row
    row_data = {col: _as_float(features, col, 0) for col in BASE_FEATURES}
    df_row = pd.DataFrame([row_data])

    if tfidf is not None:
        df_eng = engineer_features(df_row)
        from scipy.sparse import hstack, csr_matrix
        num_scaled = scaler.transform(df_eng)
        tfidf_vec = tfidf.transform([user_text])
        X = hstack([csr_matrix(num_scaled), tfidf_vec])
    else:
        feature_names = list(getattr(scaler, "feature_names_in_", BASE_FEATURES))
        row = pd.DataFrame([{name: features.get(name, 0) for name in feature_names}])
        X = scaler.transform(row)

    # Predict class
    predicted_class = int(model.predict(X)[0])

    # SHAP values
    shap_values = explainer.shap_values(X)

    # shap_values bisa berupa list (per class) atau 2D array
    if isinstance(shap_values, list):
        class_shap = shap_values[predicted_class]
    else:
        class_shap = shap_values

    if hasattr(class_shap, 'toarray'):
        class_shap = class_shap.toarray()

    shap_row = np.array(class_shap).flatten()

    # Hanya ambil base features (bukan TF-IDF features)
    n_base = len(BASE_FEATURES)
    shap_base = shap_row[:n_base] if len(shap_row) >= n_base else shap_row

    FACTOR_LABELS = {
        "sleep_hours": "Pola tidur",
        "sleep_quality": "Kualitas tidur",
        "workload_score": "Beban kerja",
        "mood_score": "Suasana hati",
        "social_score": "Interaksi sosial",
        "recovery_score": "Pemulihan harian",
        "sentiment_score": "Sentimen percakapan",
        "cognitive_distortion_score": "Pola pikir negatif",
        "absolutist_count": "Bahasa absolutist",
        "helplessness_count": "Frasa ketidakberdayaan",
        "keyword_count": "Kata kunci burnout",
        "message_avg_length": "Panjang pesan",
    }

    # Sort by absolute SHAP value
    feature_impact = []
    for i, feat_name in enumerate(BASE_FEATURES):
        if i < len(shap_base):
            val = float(shap_base[i])
            direction = "meningkatkan risiko" if val > 0 else "mengurangi risiko"
            label = FACTOR_LABELS.get(feat_name, feat_name)
            feature_impact.append((abs(val), f"{label} ({direction})"))

    feature_impact.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in feature_impact[:3]]


def _rule_based_explain(features: dict[str, Any]) -> list[str]:
    """Fallback: penjelasan berbasis rule."""
    explanations: list[tuple[float, str]] = []

    sleep = _as_float(features, "sleep_hours", 7)
    workload = _as_float(features, "workload_score", 5)
    mood = _as_float(features, "mood_score", 5)
    recovery = _as_float(features, "recovery_score", 7)
    sentiment = _as_float(features, "sentiment_score", 0)
    social = _as_float(features, "social_score", 5)
    distortion = _as_float(features, "cognitive_distortion_score", 0)

    if sleep < 5:
        explanations.append((7 - sleep, f"Tidur hanya {sleep:.1f} jam"))
    elif sleep < 6.5:
        explanations.append((6.5 - sleep, f"Tidur {sleep:.1f} jam (kurang dari ideal)"))

    if workload >= 7:
        explanations.append((workload - 5, f"Beban kerja {workload:.0f}/10"))

    if mood <= 4:
        explanations.append((5 - mood, f"Mood rendah ({mood:.0f}/10)"))

    if recovery <= 4:
        explanations.append((5 - recovery, f"Pemulihan rendah ({recovery:.0f}/10)"))

    if sentiment <= -0.3:
        explanations.append((abs(sentiment), "Sentimen percakapan negatif"))

    if social <= 3:
        explanations.append((5 - social, f"Interaksi sosial rendah ({social:.0f}/10)"))

    if distortion >= 0.5:
        explanations.append((distortion, "Pola bahasa absolutist terdeteksi"))

    explanations.sort(key=lambda item: item[0], reverse=True)
    return [text for _, text in explanations[:3]]
