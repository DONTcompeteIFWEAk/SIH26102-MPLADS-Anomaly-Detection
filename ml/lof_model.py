import pandas as pd
import numpy as np
import os

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
import joblib

print("=" * 60)
print("SIH26102 LOCAL OUTLIER FACTOR MODEL")
print("=" * 60)

# ---------------------------------------------------------
# LOAD PROCESSED DATA
# ---------------------------------------------------------

input_path = "data/processed_mplads.csv"

df = pd.read_csv(input_path)

print(f"\nProjects loaded: {len(df)}")

# ---------------------------------------------------------
# FEATURE SELECTION
# ---------------------------------------------------------
# Do NOT include actual_anomaly.
# It is our synthetic ground-truth label and must never
# be given to the ML model.

features = [
    "sanctioned_amount",
    "actual_expenditure",
    "expenditure_ratio",
    "expenditure_difference",
    "expenditure_deviation_pct",
    "absolute_expenditure_deviation_pct",

    "completion_delay_days",
    "project_duration_days",
    "delay_to_duration_ratio",

    "uc_amount",
    "uc_ratio",
    "uc_expenditure_difference",
    "uc_discrepancy_pct",

    "missing_uc",

    "expenditure_per_duration_day",
    "expenditure_per_elapsed_day"
]

# Check that all features exist
missing_features = [
    feature
    for feature in features
    if feature not in df.columns
]

if missing_features:
    raise ValueError(
        f"Missing features: {missing_features}"
    )

X = df[features].copy()

# ---------------------------------------------------------
# CLEAN DATA
# ---------------------------------------------------------

X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

X = X.fillna(0)

# ---------------------------------------------------------
# STANDARDIZATION
# ---------------------------------------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# ---------------------------------------------------------
# LOCAL OUTLIER FACTOR
# ---------------------------------------------------------

print("\nTraining Local Outlier Factor...")

lof = LocalOutlierFactor(
    n_neighbors=20,
    contamination=0.05
)

predictions = lof.fit_predict(X_scaled)

# ---------------------------------------------------------
# CONVERT PREDICTIONS
# ---------------------------------------------------------
#
# LOF:
#     1  = normal
#    -1  = anomaly
#
# Our format:
#     0  = normal
#     1  = anomaly

df["lof_prediction"] = predictions

df["lof_anomaly"] = (
    df["lof_prediction"] == -1
).astype(int)

# ---------------------------------------------------------
# ANOMALY SCORE
# ---------------------------------------------------------
#
# negative_outlier_factor_:
# more negative = more anomalous
#
# We retain the original LOF score.

df["lof_anomaly_score"] = (
    lof.negative_outlier_factor_
)

# ---------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------

os.makedirs("models", exist_ok=True)

output_path = "data/lof_results.csv"

df.to_csv(
    output_path,
    index=False
)

joblib.dump(
    scaler,
    "models/lof_scaler.pkl"
)

joblib.dump(
    lof,
    "models/lof_model.pkl"
)

# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("LOF RESULTS")
print("-" * 60)

print(
    f"Normal projects   : "
    f"{(df['lof_anomaly'] == 0).sum()}"
)

print(
    f"Anomalous projects: "
    f"{(df['lof_anomaly'] == 1).sum()}"
)

print("\nTop 10 LOF anomalies:")

display_columns = [
    "project_id",
    "actual_anomaly",
    "lof_anomaly_score",
    "sanctioned_amount",
    "actual_expenditure",
    "completion_delay_days",
    "missing_uc",
    "uc_ratio"
]

print(
    df.sort_values(
        "lof_anomaly_score",
        ascending=True
    )
    .head(10)[display_columns]
    .to_string(index=False)
)

print("\n" + "-" * 60)
print(f"Results saved to: {output_path}")
print("-" * 60)

print("\nLOF model completed successfully.")