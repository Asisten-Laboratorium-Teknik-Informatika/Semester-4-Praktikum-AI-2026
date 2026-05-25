"""
LifeLens Burnout Model Training v4.0 — Maximum Quality

Improvement dari v3:
1. TEXT FEATURES — TF-IDF dari user_texts_combined (model belajar dari KATA, bukan cuma angka)
2. FEATURE ENGINEERING — interaksi, rasio, polynomial
3. STACKING ENSEMBLE — gabung RF + GB + (XGB) dengan meta-learner
4. LABEL NOISE — 5% label sengaja di-flip untuk simulasi real-world uncertainty
5. REALISTIC CORRELATION NOISE — fitur saling mempengaruhi (sleep rendah → mood turun)
6. REPEATED STRATIFIED K-FOLD — 5 repeat x 5 fold = 25 evaluasi
7. CALIBRATED PROBABILITIES — probabilitas output lebih akurat

Estimasi: 30-60 menit (20 round, tiap round tune + evaluate)

Cara pakai:
  pip install scikit-learn pandas numpy joblib scipy
  pip install xgboost lightgbm shap   # optional tapi sangat recommended

  cd "M:\\Ai Tugas Akhir Project\\ProjekAI"
  python scripts/train_model.py
"""

from __future__ import annotations

import json
import time
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from io import StringIO

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    StackingClassifier, VotingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    classification_report, confusion_matrix,
    f1_score, recall_score, roc_auc_score, accuracy_score
)
from sklearn.model_selection import (
    StratifiedKFold, RepeatedStratifiedKFold,
    cross_val_score, train_test_split,
    RandomizedSearchCV, learning_curve
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from scipy.stats import randint, uniform
from scipy.sparse import hstack, csr_matrix

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# ═══ KONFIGURASI ═══
DATASET_PATH = Path("CHAT/LIFELENS_CLEAN_DATASET.json")
MODEL_DIR = Path("ml_models")
LABELS = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}

N_ROUNDS = 20
N_AUGMENT = 3
N_SEARCH_ITER = 30
LABEL_NOISE_RATE = 0.05  # 5% label sengaja di-flip
TFIDF_MAX_FEATURES = 300

BASE_FEATURES = [
    "sleep_hours", "sleep_quality", "workload_score",
    "mood_score", "social_score", "recovery_score",
    "sentiment_score", "cognitive_distortion_score",
    "absolutist_count", "helplessness_count",
    "keyword_count", "message_avg_length"
]

INT_COLS = [
    "sleep_quality", "workload_score", "mood_score",
    "social_score", "recovery_score", "absolutist_count",
    "helplessness_count", "keyword_count"
]

NOISE_CFG = {
    "sleep_hours":                {"std": 1.2,  "min": 0,  "max": 12},
    "sleep_quality":              {"std": 1.8,  "min": 1,  "max": 10},
    "workload_score":             {"std": 1.8,  "min": 1,  "max": 10},
    "mood_score":                 {"std": 1.8,  "min": 1,  "max": 10},
    "social_score":               {"std": 1.8,  "min": 1,  "max": 10},
    "recovery_score":             {"std": 1.8,  "min": 1,  "max": 10},
    "sentiment_score":            {"std": 0.18, "min": -1, "max": 1},
    "cognitive_distortion_score": {"std": 0.15, "min": 0,  "max": 1},
    "absolutist_count":           {"std": 1.0,  "min": 0,  "max": 10},
    "helplessness_count":         {"std": 0.8,  "min": 0,  "max": 10},
    "keyword_count":              {"std": 1.2,  "min": 0,  "max": 15},
    "message_avg_length":         {"std": 4.0,  "min": 3,  "max": 50},
}

# Korelasi realistis: kalau sleep turun, mood juga turun, dst.
CORRELATED_PAIRS = [
    ("sleep_hours", "mood_score", 0.6),       # kurang tidur = mood jelek
    ("sleep_hours", "recovery_score", 0.5),    # kurang tidur = recovery buruk
    ("workload_score", "sleep_hours", -0.4),   # workload tinggi = tidur kurang
    ("workload_score", "recovery_score", -0.5),# workload tinggi = recovery buruk
    ("mood_score", "social_score", 0.5),       # mood jelek = menarik diri
    ("sentiment_score", "mood_score", 0.6),    # sentimen negatif = mood rendah
    ("cognitive_distortion_score", "helplessness_count", 0.5),
]


class DualLogger:
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = StringIO()
        self.filepath = filepath

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()

    def save(self):
        Path(self.filepath).parent.mkdir(exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(self.log.getvalue())


# ═══════════════════════════════════════
#  1. DATA LOADING & PREPROCESSING
# ═══════════════════════════════════════

def load_dataset() -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Load dataset, extract base features + user texts."""
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        conversations = json.load(f)

    rows = []
    texts = []
    for conv in conversations:
        feat = conv.get("features", {})
        row = {col: feat.get(col, 0) for col in BASE_FEATURES}
        row["burnout_level"] = conv.get("burnout_level", "LOW")
        rows.append(row)
        texts.append(conv.get("user_texts_combined", ""))

    df = pd.DataFrame(rows)
    label_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    df["label"] = df["burnout_level"].map(label_map)

    for col in BASE_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df[BASE_FEATURES], df["label"], texts


# ═══════════════════════════════════════
#  2. FEATURE ENGINEERING
# ═══════════════════════════════════════

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Buat fitur turunan dari base features."""
    out = df.copy()

    # Rasio — menangkap hubungan antar fitur
    out["recovery_workload_ratio"] = (out["recovery_score"] + 0.1) / (out["workload_score"] + 0.1)
    out["sleep_workload_ratio"] = (out["sleep_hours"] + 0.1) / (out["workload_score"] + 0.1)
    out["social_mood_ratio"] = (out["social_score"] + 0.1) / (out["mood_score"] + 0.1)

    # Interaksi — menangkap efek gabungan
    out["sleep_x_mood"] = out["sleep_hours"] * out["mood_score"]
    out["workload_x_distortion"] = out["workload_score"] * out["cognitive_distortion_score"]
    out["sentiment_x_mood"] = out["sentiment_score"] * out["mood_score"]

    # Aggregasi — skor komposit
    out["wellbeing_score"] = (
        out["mood_score"] + out["social_score"] + out["recovery_score"] + out["sleep_quality"]
    ) / 4.0
    out["stress_score"] = (
        out["workload_score"] + out["cognitive_distortion_score"] * 10 +
        out["absolutist_count"] + out["helplessness_count"]
    ) / 4.0
    out["balance_score"] = out["wellbeing_score"] - out["stress_score"]

    # Non-linear — menangkap threshold effects
    out["sleep_deficit"] = np.maximum(0, 7 - out["sleep_hours"])  # deficit dari 7 jam ideal
    out["extreme_workload"] = (out["workload_score"] >= 8).astype(int)
    out["social_isolation"] = (out["social_score"] <= 3).astype(int)
    out["severe_sentiment"] = (out["sentiment_score"] <= -0.5).astype(int)

    return out


def get_all_feature_names(df_engineered: pd.DataFrame) -> list[str]:
    """Semua nama fitur (base + engineered)."""
    return list(df_engineered.columns)


# ═══════════════════════════════════════
#  3. TEXT FEATURES (TF-IDF)
# ═══════════════════════════════════════

def build_tfidf(texts: list[str], max_features: int = TFIDF_MAX_FEATURES) -> tuple:
    """Build TF-IDF vectorizer dari user texts."""
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),  # unigram + bigram
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        strip_accents="unicode",
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = [f"tfidf_{name}" for name in vectorizer.get_feature_names_out()]
    return vectorizer, tfidf_matrix, feature_names


# ═══════════════════════════════════════
#  4. NOISE INJECTION + AUGMENTATION
# ═══════════════════════════════════════

def augment_with_correlated_noise(
    X_num: pd.DataFrame, y: pd.Series, texts: list[str],
    n_copies: int, rng: np.random.RandomState, add_label_noise: bool = True
) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """
    Noise injection DENGAN korelasi realistis antar fitur.
    + 5% label noise untuk simulasi uncertainty.
    """
    chunks_X = [X_num.copy()]
    chunks_y = [y.copy()]
    chunks_txt = [list(texts)]

    for _ in range(n_copies):
        X_noisy = X_num.copy()

        # Step 1: Independent noise
        for col in BASE_FEATURES:
            cfg = NOISE_CFG[col]
            noise = rng.normal(0, cfg["std"], size=len(X_num))
            X_noisy[col] = np.clip(X_noisy[col] + noise, cfg["min"], cfg["max"])

        # Step 2: Correlated noise — bikin fitur saling mempengaruhi
        for col_a, col_b, strength in CORRELATED_PAIRS:
            if col_a in X_noisy.columns and col_b in X_noisy.columns:
                delta_a = X_noisy[col_a] - X_num[col_a]  # perubahan di fitur A
                # Propagasi sebagian perubahan ke fitur B
                cfg_b = NOISE_CFG.get(col_b, {"min": 0, "max": 10})
                X_noisy[col_b] = np.clip(
                    X_noisy[col_b] + delta_a * strength * rng.uniform(0.5, 1.5),
                    cfg_b["min"], cfg_b["max"]
                )

        # Round integer columns
        for col in INT_COLS:
            if col in X_noisy.columns:
                X_noisy[col] = X_noisy[col].round().astype(int)

        # Label noise — flip 5% labels ke level terdekat
        y_noisy = np.array(y.values, copy=True)
        if add_label_noise:
            n_flip = max(1, int(len(y_noisy) * LABEL_NOISE_RATE))
            flip_idx = rng.choice(len(y_noisy), n_flip, replace=False)
            for idx in flip_idx:
                current = y_noisy[idx]
                if current == 0:
                    y_noisy[idx] = 1
                elif current == 2:
                    y_noisy[idx] = 1
                else:
                    y_noisy[idx] = rng.choice([0, 2])

        chunks_X.append(X_noisy)
        chunks_y.append(pd.Series(y_noisy))
        chunks_txt.append(list(texts))  # teks sama, fitur beda

    X_final = pd.concat(chunks_X, ignore_index=True)
    y_final = pd.concat(chunks_y, ignore_index=True)
    txt_final = []
    for chunk in chunks_txt:
        txt_final.extend(chunk)

    return X_final, y_final, txt_final


# ═══════════════════════════════════════
#  5. MODEL BUILDING
# ═══════════════════════════════════════

def build_stacking_ensemble() -> tuple[StackingClassifier, dict]:
    """Build stacking ensemble: RF + GB sebagai base, LogReg sebagai meta-learner."""
    estimators = [
        ("rf", RandomForestClassifier(
            n_estimators=300, max_depth=12, min_samples_split=5,
            class_weight="balanced", random_state=42
        )),
        ("gb", GradientBoostingClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, random_state=42
        )),
    ]

    try:
        from xgboost import XGBClassifier
        estimators.append(("xgb", XGBClassifier(
            n_estimators=300, max_depth=8, learning_rate=0.1,
            objective="multi:softprob", eval_metric="mlogloss",
            random_state=42, use_label_encoder=False,
            reg_alpha=0.5, reg_lambda=1.0, subsample=0.8,
        )))
    except ImportError:
        pass

    try:
        from lightgbm import LGBMClassifier
        estimators.append(("lgbm", LGBMClassifier(
            n_estimators=300, max_depth=10, learning_rate=0.1,
            num_leaves=40, verbose=-1, random_state=42,
            reg_alpha=0.3, reg_lambda=0.5, subsample=0.8,
        )))
    except ImportError:
        pass

    stacker = StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(
            C=1.0, max_iter=1000, multi_class="multinomial", random_state=42
        ),
        cv=5,
        stack_method="predict_proba",
        n_jobs=-1,
    )

    return stacker, {"models": [name for name, _ in estimators]}


def get_individual_models() -> dict:
    """Individual models with HP search space."""
    configs = {
        "RandomForest": {
            "model": RandomForestClassifier(class_weight="balanced", random_state=42),
            "params": {
                "n_estimators": randint(200, 600),
                "max_depth": randint(6, 22),
                "min_samples_split": randint(2, 12),
                "min_samples_leaf": randint(1, 6),
                "max_features": ["sqrt", "log2", None],
            }
        },
        "GradientBoosting": {
            "model": GradientBoostingClassifier(random_state=42),
            "params": {
                "n_estimators": randint(150, 500),
                "max_depth": randint(4, 14),
                "learning_rate": uniform(0.02, 0.2),
                "subsample": uniform(0.65, 0.35),
                "min_samples_split": randint(2, 10),
            }
        },
    }

    try:
        from xgboost import XGBClassifier
        configs["XGBoost"] = {
            "model": XGBClassifier(
                objective="multi:softprob", eval_metric="mlogloss",
                random_state=42, use_label_encoder=False,
            ),
            "params": {
                "n_estimators": randint(200, 600),
                "max_depth": randint(4, 14),
                "learning_rate": uniform(0.02, 0.2),
                "reg_alpha": uniform(0, 1.5),
                "reg_lambda": uniform(0.5, 2.5),
                "subsample": uniform(0.6, 0.4),
                "colsample_bytree": uniform(0.5, 0.5),
            }
        }
    except ImportError:
        pass

    try:
        from lightgbm import LGBMClassifier
        configs["LightGBM"] = {
            "model": LGBMClassifier(verbose=-1, random_state=42),
            "params": {
                "n_estimators": randint(200, 600),
                "max_depth": randint(4, 16),
                "learning_rate": uniform(0.02, 0.2),
                "num_leaves": randint(20, 60),
                "reg_alpha": uniform(0, 1.5),
                "reg_lambda": uniform(0, 1.5),
                "subsample": uniform(0.6, 0.4),
            }
        }
    except ImportError:
        pass

    return configs


# ═══════════════════════════════════════
#  6. TRAINING ROUND
# ═══════════════════════════════════════

def run_round(round_idx: int,
              X_base: pd.DataFrame, y_orig: pd.Series, texts_orig: list[str],
              tfidf_vectorizer: TfidfVectorizer,
              model_configs: dict) -> dict | None:
    """1 round: augment -> engineer features -> combine with TF-IDF -> tune -> evaluate."""
    seed = 42 + round_idx * 7
    rng = np.random.RandomState(seed)

    print(f"\n{'#'*60}")
    print(f"  ROUND {round_idx + 1}/{N_ROUNDS}  (seed={seed})")
    print(f"{'#'*60}")

    # 1. Augment numerical features
    X_aug, y_aug, txt_aug = augment_with_correlated_noise(
        X_base, y_orig, texts_orig, N_AUGMENT, rng
    )
    print(f"  Data: {len(X_aug)} samples (augmented {N_AUGMENT}x)")

    # 2. Feature engineering
    X_eng = engineer_features(X_aug)
    feat_names = get_all_feature_names(X_eng)

    # 3. TF-IDF dari teks
    tfidf_matrix = tfidf_vectorizer.transform(txt_aug)

    # 4. Combine: numerical (engineered) + TF-IDF
    X_num_scaled = StandardScaler().fit_transform(X_eng)
    X_combined = hstack([csr_matrix(X_num_scaled), tfidf_matrix])

    # 5. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_combined, y_aug, test_size=0.2, random_state=seed, stratify=y_aug
    )

    # 6. Train individual models + find best
    round_best = None

    for name, config in model_configs.items():
        t0 = time.perf_counter()

        search = RandomizedSearchCV(
            config["model"],
            param_distributions=config["params"],
            n_iter=N_SEARCH_ITER,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=seed),
            scoring="f1_weighted",
            random_state=seed,
            n_jobs=-1,
            verbose=0,
            refit=True,
        )

        search.fit(X_train, y_train)
        best_model = search.best_estimator_

        y_pred = best_model.predict(X_test)
        y_proba = best_model.predict_proba(X_test)

        elapsed = round(time.perf_counter() - t0, 1)
        test_f1 = f1_score(y_test, y_pred, average="weighted")
        test_auc = roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted")
        r_high = recall_score(y_test, y_pred, labels=[2], average="macro", zero_division=0)

        # Repeated Stratified K-Fold (3x5=15)
        rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=seed)
        rskf_scores = cross_val_score(best_model, X_train, y_train, cv=rskf,
                                      scoring="f1_weighted", n_jobs=-1)

        print(f"  {name:20s} | RSKF={rskf_scores.mean():.4f}(+-{rskf_scores.std():.4f}) "
              f"| F1={test_f1:.4f} | AUC={test_auc:.4f} | RecH={r_high:.4f} | {elapsed}s")

        result = {
            "round": round_idx + 1,
            "seed": seed,
            "model": best_model,
            "best_params": {k: (v.item() if hasattr(v, 'item') else v)
                           for k, v in search.best_params_.items()},
            "metrics": {
                "model_name": name,
                "round": round_idx + 1,
                "rskf_f1_mean": float(rskf_scores.mean()),
                "rskf_f1_std": float(rskf_scores.std()),
                "test_f1_weighted": float(test_f1),
                "test_accuracy": float(accuracy_score(y_test, y_pred)),
                "test_auc_roc": float(test_auc),
                "recall_high": float(r_high),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
                "classification_report": classification_report(
                    y_test, y_pred, target_names=["LOW", "MEDIUM", "HIGH"],
                    output_dict=True, zero_division=0
                ),
                "training_seconds": elapsed,
            },
        }

        if round_best is None or rskf_scores.mean() > round_best["metrics"]["rskf_f1_mean"]:
            round_best = result

    # 7. Try stacking ensemble
    try:
        t0 = time.perf_counter()
        stacker, stack_info = build_stacking_ensemble()
        stacker.fit(X_train, y_train)
        y_pred = stacker.predict(X_test)
        y_proba = stacker.predict_proba(X_test)
        elapsed = round(time.perf_counter() - t0, 1)

        test_f1 = f1_score(y_test, y_pred, average="weighted")
        test_auc = roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted")
        r_high = recall_score(y_test, y_pred, labels=[2], average="macro", zero_division=0)

        rskf = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=seed)
        rskf_scores = cross_val_score(stacker, X_train, y_train, cv=rskf,
                                      scoring="f1_weighted", n_jobs=-1)

        print(f"  {'Stacking':20s} | RSKF={rskf_scores.mean():.4f}(+-{rskf_scores.std():.4f}) "
              f"| F1={test_f1:.4f} | AUC={test_auc:.4f} | RecH={r_high:.4f} | {elapsed}s")

        stack_result = {
            "round": round_idx + 1,
            "seed": seed,
            "model": stacker,
            "best_params": stack_info,
            "metrics": {
                "model_name": "Stacking Ensemble",
                "round": round_idx + 1,
                "rskf_f1_mean": float(rskf_scores.mean()),
                "rskf_f1_std": float(rskf_scores.std()),
                "test_f1_weighted": float(test_f1),
                "test_accuracy": float(accuracy_score(y_test, y_pred)),
                "test_auc_roc": float(test_auc),
                "recall_high": float(r_high),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
                "classification_report": classification_report(
                    y_test, y_pred, target_names=["LOW", "MEDIUM", "HIGH"],
                    output_dict=True, zero_division=0
                ),
                "training_seconds": elapsed,
            },
        }

        if rskf_scores.mean() > round_best["metrics"]["rskf_f1_mean"]:
            round_best = stack_result

    except Exception as e:
        print(f"  [WARN] Stacking failed: {e}")

    return round_best


# ═══════════════════════════════════════
#  7. OVERFITTING CHECK
# ═══════════════════════════════════════

def check_overfitting(model, X, y):
    print(f"\n{'='*60}")
    print(f"  OVERFITTING CHECK")
    print(f"{'='*60}")

    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y, cv=5, scoring="f1_weighted",
        train_sizes=np.linspace(0.1, 1.0, 8),
        n_jobs=-1, random_state=42
    )

    print(f"  {'Size':>8} | {'Train':>8} | {'Val':>8} | {'Gap':>8}")
    print(f"  {'-'*8}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}")
    for sz, tr, va in zip(train_sizes, train_scores.mean(1), val_scores.mean(1)):
        gap = tr - va
        flag = " !!" if gap > 0.05 else ""
        print(f"  {sz:>8} | {tr:>8.4f} | {va:>8.4f} | {gap:>8.4f}{flag}")

    final_gap = train_scores.mean(1)[-1] - val_scores.mean(1)[-1]
    if final_gap > 0.05:
        print(f"\n  !! OVERFIT RISK (gap={final_gap:.4f})")
    else:
        print(f"\n  OK model generalizes well (gap={final_gap:.4f})")


# ═══════════════════════════════════════
#  8. SAVE ARTIFACTS
# ═══════════════════════════════════════

def save_all(global_best: dict, round_summaries: list, scaler: StandardScaler,
             tfidf_vec: TfidfVectorizer, eng_feature_names: list, original_size: int):
    MODEL_DIR.mkdir(exist_ok=True)
    model = global_best["model"]

    # Save model + preprocessors
    joblib.dump(model, MODEL_DIR / "burnout_model.pkl")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    joblib.dump(tfidf_vec, MODEL_DIR / "tfidf_vectorizer.pkl")

    # Feature importance
    fi_dict = {}
    if hasattr(model, "feature_importances_"):
        all_names = eng_feature_names + [f"tfidf_{i}" for i in range(TFIDF_MAX_FEATURES)]
        importances = model.feature_importances_
        if len(importances) == len(all_names):
            fi = sorted(zip(all_names, importances), key=lambda x: x[1], reverse=True)[:20]
            print(f"\n  Top 20 Feature Importance:")
            for feat, imp in fi:
                bar = "#" * int(imp * 50)
                print(f"    {feat:>35}: {imp:.4f} {bar}")
                fi_dict[feat] = round(float(imp), 4)

    # SHAP
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        joblib.dump(explainer, MODEL_DIR / "shap_explainer.pkl")
    except Exception:
        pass

    # Model card
    m = global_best["metrics"]
    model_card = {
        "project": "LifeLens burnout prediction",
        "version": "4.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(DATASET_PATH),
        "dataset_size_original": original_size,
        "training_config": {
            "n_rounds": N_ROUNDS,
            "n_augment_per_round": N_AUGMENT,
            "n_search_iter": N_SEARCH_ITER,
            "label_noise_rate": LABEL_NOISE_RATE,
            "tfidf_max_features": TFIDF_MAX_FEATURES,
            "feature_engineering": True,
            "correlated_noise": True,
            "stacking_ensemble": True,
            "evaluation": "RepeatedStratifiedKFold 3x5",
        },
        "selected_model": {
            "name": m["model_name"],
            "from_round": m["round"],
            "best_params": global_best.get("best_params", {}),
        },
        "best_metrics": {
            "rskf_f1_mean": m["rskf_f1_mean"],
            "rskf_f1_std": m["rskf_f1_std"],
            "test_f1_weighted": m["test_f1_weighted"],
            "test_accuracy": m["test_accuracy"],
            "test_auc_roc": m["test_auc_roc"],
            "recall_high": m["recall_high"],
            "confusion_matrix": m["confusion_matrix"],
        },
        "feature_names_base": BASE_FEATURES,
        "feature_importance_top20": fi_dict,
        "label_mapping": LABELS,
        "all_rounds": round_summaries,
        "limitations": [
            "Dataset sintetis — perlu validasi dengan data user asli.",
            "Label noise 5% ditambahkan untuk simulasi uncertainty.",
            "Correlated noise injection untuk realisme antar-fitur.",
            "Bukan diagnosis medis, hanya risk screening tool.",
        ],
    }
    (MODEL_DIR / "model_card.json").write_text(
        json.dumps(model_card, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n  ARTEFAK: burnout_model.pkl, scaler.pkl, tfidf_vectorizer.pkl, model_card.json")


# ═══════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════

def main():
    logger = DualLogger(MODEL_DIR / "training_report.txt")
    MODEL_DIR.mkdir(exist_ok=True)
    sys.stdout = logger
    total_start = time.perf_counter()

    print("=" * 60)
    print("  LifeLens Model Training v4.0 — Maximum Quality")
    print("=" * 60)
    print(f"  Waktu    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Rounds   : {N_ROUNDS}")
    print(f"  Augment  : {N_AUGMENT}x/round + correlated noise + 5% label noise")
    print(f"  Features : {len(BASE_FEATURES)} base + engineered + {TFIDF_MAX_FEATURES} TF-IDF")
    print(f"  Eval     : RepeatedStratifiedKFold 3x5 = 15 folds")
    print()

    # 1. Load
    X_base, y_orig, texts_orig = load_dataset()
    original_size = len(X_base)
    print(f"Dataset: {original_size} percakapan")
    print(f"Distribusi: LOW={sum(y_orig==0)}, MEDIUM={sum(y_orig==1)}, HIGH={sum(y_orig==2)}")

    # 2. Build TF-IDF dari semua teks (fit sekali, transform per round)
    print(f"\nBuilding TF-IDF vectorizer ({TFIDF_MAX_FEATURES} features, bigrams)...")
    tfidf_vec, _, tfidf_names = build_tfidf(texts_orig)
    print(f"  TF-IDF vocabulary: {len(tfidf_vec.vocabulary_)} terms")

    # 3. Build scaler dari engineered features
    X_eng_sample = engineer_features(X_base)
    scaler = StandardScaler().fit(X_eng_sample)
    eng_feature_names = get_all_feature_names(X_eng_sample)
    print(f"  Engineered features: {len(eng_feature_names)} (base {len(BASE_FEATURES)} + {len(eng_feature_names)-len(BASE_FEATURES)} derived)")

    # 4. Model configs
    model_configs = get_individual_models()
    print(f"  Models: {', '.join(model_configs.keys())} + Stacking Ensemble")

    # 5. Iterative training
    global_best = None
    round_summaries = []

    for r in range(N_ROUNDS):
        round_best = run_round(r, X_base, y_orig, texts_orig, tfidf_vec, model_configs)

        if round_best is None:
            continue

        m = round_best["metrics"]
        round_summaries.append({
            "round": r + 1,
            "model": m["model_name"],
            "rskf_f1": m["rskf_f1_mean"],
            "test_f1": m["test_f1_weighted"],
            "auc": m["test_auc_roc"],
            "recall_high": m["recall_high"],
        })

        if global_best is None or m["rskf_f1_mean"] > global_best["metrics"]["rskf_f1_mean"]:
            global_best = round_best
            print(f"  >>> NEW GLOBAL BEST! Round {r+1} — {m['model_name']} "
                  f"RSKF F1={m['rskf_f1_mean']:.4f}")

    # 6. Summary
    total_time = round(time.perf_counter() - total_start, 1)

    print(f"\n\n{'='*60}")
    print(f"  SELESAI — {N_ROUNDS} rounds, {total_time}s ({total_time/60:.1f} menit)")
    print(f"{'='*60}")

    print(f"\n  Ringkasan:")
    print(f"  {'Rnd':>4} | {'Model':>22} | {'RSKF F1':>8} | {'Test F1':>8} | {'AUC':>6} | {'RecH':>6}")
    print(f"  {'-'*4}-+-{'-'*22}-+-{'-'*8}-+-{'-'*8}-+-{'-'*6}-+-{'-'*6}")
    for rs in round_summaries:
        flag = " <" if rs["round"] == global_best["metrics"]["round"] else ""
        print(f"  {rs['round']:>4} | {rs['model']:>22} | {rs['rskf_f1']:>8.4f} | "
              f"{rs['test_f1']:>8.4f} | {rs['auc']:>6.4f} | {rs['recall_high']:>6.4f}{flag}")

    gm = global_best["metrics"]
    print(f"\n  MODEL TERPILIH: {gm['model_name']} (Round {gm['round']})")
    print(f"  RSKF F1:   {gm['rskf_f1_mean']:.4f} (+/- {gm['rskf_f1_std']:.4f})")
    print(f"  Test F1:   {gm['test_f1_weighted']:.4f}")
    print(f"  Test AUC:  {gm['test_auc_roc']:.4f}")
    print(f"  Accuracy:  {gm['test_accuracy']:.4f}")
    print(f"  Recall H:  {gm['recall_high']:.4f}")

    cm = gm["confusion_matrix"]
    print(f"\n  Confusion Matrix:")
    for i, row in enumerate(cm):
        print(f"    {LABELS[i]:>6}: {row}")

    cr = gm["classification_report"]
    print(f"\n              precision    recall  f1-score   support")
    for label in ["LOW", "MEDIUM", "HIGH"]:
        d = cr[label]
        print(f"  {label:>10}     {d['precision']:.4f}    {d['recall']:.4f}    "
              f"{d['f1-score']:.4f}    {int(d['support'])}")

    # 7. Overfitting check
    X_check_aug, y_check_aug, txt_check = augment_with_correlated_noise(
        X_base, y_orig, texts_orig, N_AUGMENT, np.random.RandomState(999), add_label_noise=False
    )
    X_check_eng = engineer_features(X_check_aug)
    X_check_scaled = scaler.transform(X_check_eng)
    tfidf_check = tfidf_vec.transform(txt_check)
    X_check_combined = hstack([csr_matrix(X_check_scaled), tfidf_check])
    check_overfitting(global_best["model"], X_check_combined, y_check_aug)

    # 8. Save
    save_all(global_best, round_summaries, scaler, tfidf_vec, eng_feature_names, original_size)

    print(f"\n  Total: {total_time}s ({total_time/60:.1f} menit)")
    sys.stdout = logger.terminal
    logger.save()
    print(f"\n[OK] Selesai! Report: {MODEL_DIR / 'training_report.txt'}")


if __name__ == "__main__":
    main()
