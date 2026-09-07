import os
import sys
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

INPUT_FILE = DATA_DIR / "real_mplads_works_processed.csv"
OUTPUT_HYBRID_FILE = DATA_DIR / "real_mplads_works_hybrid_risk.csv"

MODELS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 75)
print("SIH26102 — REAL MPLADS ENSEMBLE ML MODEL TRAINING")
print("=" * 75)

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

print(f"\n[1/7] Loading processed works from {INPUT_FILE.name}...")
df = pd.read_csv(INPUT_FILE, low_memory=False)
print(f"  Loaded {len(df):,} works with {len(df.columns)} columns")

# =========================================================
# 2. FEATURE SELECTION
# =========================================================
feature_columns = [
    "allocation_amount_log",
    "allocation_vs_state_median",
    "allocation_vs_constituency_median",
    "allocation_vs_category_median",
    "days_since_recommendation",
    "recommendation_year",
    "recommendation_month",
    "recommendation_quarter",
    "work_description_length",
    "work_word_count",
    "same_work_description_count",
    "same_work_location_count",
    "split_tender_flag",
    "cluster_work_flag",
    "prolonged_inaction_flag"
]

available_features = [c for c in feature_columns if c in df.columns]
print(f"\n[2/7] Selected {len(available_features)} behavioral features:")
for f in available_features:
    print(f"  - {f}")

X = df[available_features].copy()
for col in X.columns:
    X[col] = pd.to_numeric(X[col], errors="coerce")

# Impute median
medians_dict = {}
for col in X.columns:
    med = float(X[col].median())
    if pd.isna(med):
        med = 0.0
    medians_dict[col] = med
    X[col] = X[col].fillna(med)

# =========================================================
# 3. SCALING & PREPARATION
# =========================================================
print("\n[3/7] Standardizing features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# =========================================================
# 4. ENSEMBLE ANOMALY MODELS
# =========================================================
print("\n[4/7] Training Anomaly Ensemble...")

# 4A. Isolation Forest
print("  - Training Isolation Forest (n_estimators=300)...")
if_model = IsolationForest(
    n_estimators=300,
    contamination=0.05,
    random_state=42,
    n_jobs=-1
)
if_model.fit(X_scaled)
if_raw = -if_model.score_samples(X_scaled)

# 4B. Local Outlier Factor (LOF) with Profile Deduplication
print("  - Training Local Outlier Factor (LOF)...")
unique_X = X.drop_duplicates().reset_index(drop=True)
unique_scaled = scaler.transform(unique_X)
n_neighbors = min(35, len(unique_scaled) - 1)

lof_model = LocalOutlierFactor(
    n_neighbors=n_neighbors,
    contamination=0.05,
    novelty=False,
    n_jobs=-1
)
lof_model.fit_predict(unique_scaled)
unique_lof_raw = -lof_model.negative_outlier_factor_

# Map LOF back
unique_map_df = unique_X.copy()
unique_map_df["_lof"] = unique_lof_raw
feature_tuple_keys = [tuple(x) for x in unique_X.to_numpy()]
lof_dict = dict(zip(feature_tuple_keys, unique_lof_raw))

all_tuples = [tuple(x) for x in X.to_numpy()]
lof_raw = np.array([lof_dict.get(t, 1.0) for t in all_tuples], dtype=float)

# 4C. PCA Reconstruction Outlier Score
print("  - Computing PCA statistical reconstruction error...")
pca = PCA(n_components=min(5, X_scaled.shape[1]), random_state=42)
X_pca = pca.fit_transform(X_scaled)
X_reconstructed = pca.inverse_transform(X_pca)
pca_raw = np.mean(np.square(X_scaled - X_reconstructed), axis=1)

# =========================================================
# 5. NORMALIZATION & ENSEMBLE SCORING
# =========================================================
print("\n[5/7] Calibrating Ensemble Scores...")

def percentile_score(values):
    return pd.Series(values).rank(pct=True).to_numpy() * 100.0

if_score = percentile_score(if_raw)
lof_score = percentile_score(lof_raw)
pca_score = percentile_score(pca_raw)

# Ensemble blend: 45% IF + 35% LOF + 20% PCA
ml_risk_score = (0.45 * if_score) + (0.35 * lof_score) + (0.20 * pca_score)

df["if_anomaly_score"] = np.round(if_score, 2)
df["lof_anomaly_score"] = np.round(lof_score, 2)
df["pca_anomaly_score"] = np.round(pca_score, 2)
df["real_ml_risk_score"] = np.round(ml_risk_score, 2)

# =========================================================
# 6. CAG DOMAIN RULE ENGINE
# =========================================================
print("\n[6/7] Applying CAG-Inspired Domain Rules...")

df["rule_high_state_allocation"] = (df["allocation_vs_state_median"] >= 3.0).astype(int)
df["rule_high_constituency_allocation"] = (df["allocation_vs_constituency_median"] >= 3.0).astype(int)
df["rule_high_category_allocation"] = (df["allocation_vs_category_median"] >= 3.0).astype(int)
df["rule_repeated_description"] = (df["same_work_description_count"] >= 30).astype(int)
df["rule_split_tender"] = df["split_tender_flag"]
df["rule_cluster_work"] = df["cluster_work_flag"]
df["rule_prolonged_inaction"] = df["prolonged_inaction_flag"]

vague_desc = (df["work_description_length"] < 15) & (df["allocation_amount"] > 500000)
df["rule_vague_description"] = vague_desc.astype(int)

# Rule score calculation (max 100)
rule_score = (
    df["rule_split_tender"] * 25 +
    df["rule_cluster_work"] * 25 +
    df["rule_high_state_allocation"] * 15 +
    df["rule_high_constituency_allocation"] * 15 +
    df["rule_repeated_description"] * 10 +
    df["rule_prolonged_inaction"] * 10 +
    df["rule_vague_description"] * 10
).clip(0, 100)

df["work_rule_score"] = np.round(rule_score, 2)

# Hybrid Risk Score: 60% ML Ensemble + 40% CAG Domain Rules
df["hybrid_risk_score"] = np.round((0.60 * df["real_ml_risk_score"]) + (0.40 * df["work_rule_score"]), 2)

def get_risk_level(s):
    if s >= 75: return "CRITICAL"
    if s >= 55: return "HIGH"
    if s >= 35: return "MEDIUM"
    return "LOW"

df["hybrid_risk_level"] = df["hybrid_risk_score"].apply(get_risk_level)
df["hybrid_risk_flag"] = (df["hybrid_risk_score"] >= 65.0).astype(int)

# =========================================================
# 7. EXPLAINABILITY & AUDIT RECOMMENDATIONS
# =========================================================
print("\n[7/7] Generating Explainability and Audit Actions...")

def generate_explanation_and_action(row):
    reasons = []
    actions = []

    if row["rule_split_tender"] == 1:
        reasons.append(f"Potential tender-splitting detected (allocation ₹{int(row['allocation_amount']):,} is just below statutory threshold)")
        actions.append("Verify tender records and procurement method under GFR Rule 149")

    if row["rule_cluster_work"] == 1:
        reasons.append(f"Work description repeated {int(row['same_work_location_count'])} times in the exact same village/block")
        actions.append("Conduct physical site audit to prevent ghost assets")

    if row["rule_high_state_allocation"] == 1:
        reasons.append(f"Allocation is {row['allocation_vs_state_median']:.1f}x higher than state median for similar works")
        actions.append("Review detailed project estimate (DPR) and schedule of rates (SOR)")

    if row["rule_repeated_description"] == 1:
        reasons.append(f"Generic work description repeated {int(row['same_work_description_count'])} times across scheme")
        actions.append("Demand geo-tagged photographs and specific location details")

    if row["rule_prolonged_inaction"] == 1:
        reasons.append(f"Work unsanctioned despite {int(row['days_since_recommendation'])} days elapsed since MP recommendation")
        actions.append("Issue show-cause inquiry to District Implementing Authority for administrative delay")

    if row["rule_vague_description"] == 1:
        reasons.append("Vague work description despite high fund allocation (> ₹5 Lakh)")
        actions.append("Obtain comprehensive scope of work document from implementing agency")

    if not reasons:
        reasons.append("Project indicators align within standard developmental distribution")
        actions.append("Standard routine audit screening")

    explanation = " | ".join(reasons[:3])
    recommended_action = " | ".join(actions[:2])
    return explanation, recommended_action

explanations_actions = df.apply(generate_explanation_and_action, axis=1)
df["hybrid_risk_explanation"] = [ea[0] for ea in explanations_actions]
df["recommended_action"] = [ea[1] for ea in explanations_actions]

# Save output dataset
OUTPUT_HYBRID_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_HYBRID_FILE, index=False)
print(f"\n[OK] Saved final hybrid dataset: {OUTPUT_HYBRID_FILE} ({len(df):,} rows)")

# Save ML Model Artifacts
scaler_path = MODELS_DIR / "real_work_scaler.pkl"
if_model_path = MODELS_DIR / "real_work_isolation_forest.pkl"
pca_path = MODELS_DIR / "real_work_pca.pkl"
metadata_path = MODELS_DIR / "real_work_metadata.json"

joblib.dump(scaler, scaler_path)
joblib.dump(if_model, if_model_path)
joblib.dump(pca, pca_path)

risk_distribution = df["hybrid_risk_level"].value_counts().to_dict()
metadata = {
    "model_version": "3.1.0-real-mplads",
    "total_training_records": len(df),
    "features": available_features,
    "feature_medians": medians_dict,
    "risk_distribution": risk_distribution,
    "critical_threshold": 75.0,
    "high_threshold": 55.0,
    "medium_threshold": 35.0,
    "weights": {
        "isolation_forest": 0.45,
        "local_outlier_factor": 0.35,
        "pca_reconstruction": 0.20,
        "ml_weight": 0.60,
        "rule_weight": 0.40
    }
}

with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"[OK] Saved model artifacts to {MODELS_DIR}")
print(f"     - Scaler: {scaler_path.name}")
print(f"     - Isolation Forest: {if_model_path.name}")
print(f"     - PCA: {pca_path.name}")
print(f"     - Metadata: {metadata_path.name}")
print("\nRisk Distribution:")
for level, count in risk_distribution.items():
    pct = (count / len(df)) * 100
    print(f"  {level:<10}: {count:>6,} ({pct:.1f}%)")

print("\n" + "=" * 75)
print("TRAINING & BENCHMARKING COMPLETE")
print("=" * 75)
