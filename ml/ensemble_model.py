import pandas as pd
import numpy as np
import os
import joblib

print("=" * 60)
print("SIH26102 ML ENSEMBLE")
print("=" * 60)

# ---------------------------------------------------------
# LOAD MODEL RESULTS
# ---------------------------------------------------------

iforest_path = "data/ml_results.csv"
lof_path = "data/lof_results.csv"

iforest = pd.read_csv(iforest_path)
lof = pd.read_csv(lof_path)

print(f"\nIsolation Forest projects: {len(iforest)}")
print(f"LOF projects             : {len(lof)}")

# ---------------------------------------------------------
# VERIFY PROJECT ALIGNMENT
# ---------------------------------------------------------

iforest = iforest.sort_values("project_id").reset_index(drop=True)
lof = lof.sort_values("project_id").reset_index(drop=True)

if not iforest["project_id"].equals(lof["project_id"]):
    raise ValueError(
        "Project IDs do not match between Isolation Forest and LOF results."
    )

df = iforest.copy()

# ---------------------------------------------------------
# NORMALIZE ISOLATION FOREST SCORE
# ---------------------------------------------------------
#
# Isolation Forest:
# lower decision_function = more anomalous
#
# Convert to:
# 0   = least anomalous
# 100 = most anomalous

iforest_score = df["ml_anomaly_score"]

iforest_min = iforest_score.min()
iforest_max = iforest_score.max()

if iforest_max == iforest_min:
    df["iforest_risk"] = 0
else:
    df["iforest_risk"] = (
        (iforest_max - iforest_score)
        /
        (iforest_max - iforest_min)
    ) * 100

# ---------------------------------------------------------
# NORMALIZE LOF SCORE
# ---------------------------------------------------------
#
# LOF:
# more negative = more anomalous
#
# Convert to:
# 0   = least anomalous
# 100 = most anomalous

lof_score = lof["lof_anomaly_score"]

lof_min = lof_score.min()
lof_max = lof_score.max()

if lof_max == lof_min:
    df["lof_risk"] = 0
else:
    df["lof_risk"] = (
        (lof_max - lof_score)
        /
        (lof_max - lof_min)
    ) * 100

# ---------------------------------------------------------
# ADD LOF INFORMATION
# ---------------------------------------------------------

df["lof_anomaly_score"] = lof["lof_anomaly_score"]
df["lof_anomaly"] = lof["lof_anomaly"]

# ---------------------------------------------------------
# ENSEMBLE
# ---------------------------------------------------------
#
# LOF currently performs better on our synthetic dataset,
# therefore it receives a slightly higher weight.
#
# These weights are NOT final production weights.

IFOREST_WEIGHT = 0.40
LOF_WEIGHT = 0.60

df["ensemble_ml_risk"] = (
    IFOREST_WEIGHT * df["iforest_risk"]
    +
    LOF_WEIGHT * df["lof_risk"]
)

df["ensemble_ml_risk"] = (
    df["ensemble_ml_risk"]
    .clip(0, 100)
)

# ---------------------------------------------------------
# ENSEMBLE CLASSIFICATION
# ---------------------------------------------------------
#
# We use the top 5% as anomalies because both individual
# models were configured with contamination=0.05.
#
# This threshold is for synthetic development only.

threshold = df["ensemble_ml_risk"].quantile(0.95)

df["ensemble_anomaly"] = (
    df["ensemble_ml_risk"] >= threshold
).astype(int)

# ---------------------------------------------------------
# RISK LEVEL
# ---------------------------------------------------------

def get_ml_risk_level(score):

    if score >= 75:
        return "CRITICAL"

    elif score >= 50:
        return "HIGH"

    elif score >= 25:
        return "MEDIUM"

    else:
        return "LOW"


df["ensemble_risk_level"] = (
    df["ensemble_ml_risk"]
    .apply(get_ml_risk_level)
)

# ---------------------------------------------------------
# EXPLANATION
# ---------------------------------------------------------

def generate_explanation(row):

    reasons = []

    if row["iforest_risk"] >= 75:
        reasons.append(
            "Isolation Forest detected a strong outlier pattern"
        )

    if row["lof_risk"] >= 75:
        reasons.append(
            "LOF detected a strong local outlier pattern"
        )

    if row["actual_expenditure"] > row["sanctioned_amount"]:
        reasons.append(
            "Expenditure exceeds sanctioned amount"
        )

    if row["completion_delay_days"] > 180:
        reasons.append(
            "Severe completion delay"
        )

    if row["missing_uc"] == 1:
        reasons.append(
            "Utilization Certificate is missing"
        )

    if (
        row["uc_available"] == 1
        and row["actual_expenditure"] > 0
        and abs(
            row["uc_amount"] -
            row["actual_expenditure"]
        ) > 0.20 * row["actual_expenditure"]
    ):
        reasons.append(
            "UC amount significantly differs from expenditure"
        )

    if not reasons:
        reasons.append(
            "No major anomaly pattern identified"
        )

    return "; ".join(reasons)


df["ensemble_explanation"] = df.apply(
    generate_explanation,
    axis=1
)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

os.makedirs("models", exist_ok=True)

output_path = "data/ensemble_results.csv"

df.to_csv(
    output_path,
    index=False
)

# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("ENSEMBLE RESULTS")
print("-" * 60)

print(
    f"Isolation Forest weight : {IFOREST_WEIGHT:.0%}"
)

print(
    f"LOF weight              : {LOF_WEIGHT:.0%}"
)

print(
    f"Ensemble threshold      : {threshold:.4f}"
)

print(
    f"Ensemble anomalies      : "
    f"{df['ensemble_anomaly'].sum()}"
)

print("\nTop 10 ensemble anomalies:")

display_columns = [
    "project_id",
    "actual_anomaly",
    "iforest_risk",
    "lof_risk",
    "ensemble_ml_risk",
    "ensemble_risk_level",
    "ensemble_explanation"
]

print(
    df.sort_values(
        "ensemble_ml_risk",
        ascending=False
    )
    .head(10)[display_columns]
    .to_string(index=False)
)

print("\n" + "-" * 60)
print(f"Results saved to: {output_path}")
print("-" * 60)

print("\nML ensemble completed successfully.")