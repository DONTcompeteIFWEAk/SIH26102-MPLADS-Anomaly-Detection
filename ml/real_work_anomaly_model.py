from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
import joblib

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "data" / "real_mplads_works_processed.csv"
OUTPUT_FILE = BASE_DIR / "data" / "real_work_anomaly_results.csv"

FEATURES = [
    "allocation_amount", "allocation_amount_log", "days_since_recommendation",
    "allocation_vs_state_median", "allocation_vs_constituency_median",
    "allocation_vs_category_median", "work_description_length",
    "work_word_count", "same_work_description_count", "missing_status",
    "missing_constituency", "missing_city", "missing_ward", "missing_block",
    "missing_village", "is_unsanctioned", "is_sanctioned", "is_ongoing",
    "is_completed", "approval_pending", "data_quality_score",
]

df = pd.read_csv(INPUT_FILE, low_memory=False)
features = [c for c in FEATURES if c in df.columns]

X = df[features].apply(pd.to_numeric, errors="coerce")
X = X.replace([np.inf, -np.inf], np.nan)
X = X.fillna(X.median(numeric_only=True))

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

iforest = IsolationForest(
    n_estimators=300, contamination=0.05, random_state=42, n_jobs=-1
)
if_labels = iforest.fit_predict(X_scaled)
if_score = -iforest.score_samples(X_scaled)

lof = LocalOutlierFactor(
    n_neighbors=20, contamination=0.05, n_jobs=-1
)
lof_labels = lof.fit_predict(X_scaled)
lof_score = -lof.negative_outlier_factor_

def percentile_score(values):
    return pd.Series(values).rank(method="average", pct=True).to_numpy() * 100.0

df["iforest_raw_score"] = if_score
df["lof_raw_score"] = lof_score
df["iforest_risk"] = percentile_score(if_score)
df["lof_risk"] = percentile_score(lof_score)
df["real_ml_risk_score"] = 0.5 * df["iforest_risk"] + 0.5 * df["lof_risk"]

threshold = float(df["real_ml_risk_score"].quantile(0.95))
df["real_ml_flag"] = (df["real_ml_risk_score"] >= threshold).astype(int)

def risk_level(score):
    if score >= 90:
        return "CRITICAL"
    if score >= 75:
        return "HIGH"
    if score >= 50:
        return "MEDIUM"
    return "LOW"

df["real_ml_risk_level"] = df["real_ml_risk_score"].apply(risk_level)

df["data_source"] = "REAL_MPLADS_WORKS"
df["ground_truth_available"] = False

df = df.sort_values("real_ml_risk_score", ascending=False).reset_index(drop=True)
df.to_csv(OUTPUT_FILE, index=False)

joblib.dump(
    {"scaler": scaler, "features": features, "contamination": 0.05},
    BASE_DIR / "models" / "real_work_scaler.joblib",
)
joblib.dump(iforest, BASE_DIR / "models" / "real_work_isolation_forest.joblib")

print("REAL MPLADS WORK ANOMALY MODEL COMPLETE")
print(f"Records analyzed: {len(df):,}")
print(f"Features used: {len(features)}")
print(f"ML screening threshold: {threshold:.2f}")
print(f"Potential anomalies flagged: {int(df['real_ml_flag'].sum()):,}")
print(df["real_ml_risk_level"].value_counts())
