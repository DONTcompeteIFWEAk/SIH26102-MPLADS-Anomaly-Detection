import pandas as pd
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
import joblib
import os


# =========================================================
# SIH26102 - LOCAL OUTLIER FACTOR ANOMALY DETECTION
# Controlled Feature Configuration
# =========================================================


# ---------------------------------------------------------
# 1. LOAD PROCESSED DATA
# ---------------------------------------------------------

input_path = "data/processed_mplads.csv"
output_path = "data/lof_results.csv"

df = pd.read_csv(input_path)

print("=" * 60)
print("SIH26102 LOCAL OUTLIER FACTOR")
print("=" * 60)

print(f"\nProjects loaded: {len(df)}")


# ---------------------------------------------------------
# 2. SELECT CONTROLLED ML FEATURES
# ---------------------------------------------------------
#
# LOF works by comparing a project with its local
# neighbourhood.
#
# Therefore we avoid unnecessary binary/derived signals
# that can distort neighbourhood distances.
#
# These features capture:
#
#   Financial behaviour
#   UC behaviour
#   Delay behaviour
#   Spending intensity
#
# ---------------------------------------------------------

features = [

    # Financial features
    "sanctioned_amount",
    "actual_expenditure",
    "expenditure_ratio",
    "expenditure_difference",
    "expenditure_deviation_pct",
    "absolute_expenditure_deviation_pct",

    # Delay features
    "completion_delay_days",
    "project_duration_days",
    "delay_to_duration_ratio",

    # UC / utilization features
    "uc_amount",
    "uc_ratio",
    "uc_expenditure_difference",
    "uc_discrepancy_pct",
    "missing_uc",

    # Spending intensity
    "expenditure_per_duration_day",
    "expenditure_per_elapsed_day",
]


# ---------------------------------------------------------
# 3. CHECK FEATURES
# ---------------------------------------------------------

missing_features = [
    feature
    for feature in features
    if feature not in df.columns
]

if missing_features:

    print("\nERROR: Required ML features are missing:")

    for feature in missing_features:
        print(f"  - {feature}")

    print("\nRun feature engineering first:")
    print("python ml/feature_engineering.py")

    raise SystemExit(1)


print(f"\nML features selected: {len(features)}")

for feature in features:
    print(f"  ✓ {feature}")


# ---------------------------------------------------------
# 4. CREATE FEATURE MATRIX
# ---------------------------------------------------------

X = df[features].copy()


# ---------------------------------------------------------
# 5. SAFETY CHECK
# ---------------------------------------------------------

X = X.replace(
    [float("inf"), float("-inf")],
    0
)

X = X.fillna(0)


# ---------------------------------------------------------
# 6. SCALE FEATURES
# ---------------------------------------------------------

print("\nScaling ML features...")

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ---------------------------------------------------------
# 7. CREATE LOF MODEL
# ---------------------------------------------------------

print("\nCreating Local Outlier Factor...")

model = LocalOutlierFactor(

    n_neighbors=20,

    contamination=0.05,

    n_jobs=-1
)


# ---------------------------------------------------------
# 8. TRAIN + PREDICT
# ---------------------------------------------------------

print("Training LOF model...")

predictions = model.fit_predict(X_scaled)


# ---------------------------------------------------------
# 9. STORE PREDICTIONS
# ---------------------------------------------------------

df["lof_prediction"] = predictions


# LOF:
#
# -1 = anomaly
#  1 = normal

df["lof_anomaly"] = (
    df["lof_prediction"] == -1
).astype(int)


# ---------------------------------------------------------
# 10. RAW LOF SCORE
# ---------------------------------------------------------
#
# negative_outlier_factor_
#
# Values closer to -1:
#     more normal
#
# More negative values:
#     more anomalous
#
# ---------------------------------------------------------

df["lof_score"] = (
    model.negative_outlier_factor_
)


# ---------------------------------------------------------
# 11. NORMALIZED LOF RISK SCORE
# ---------------------------------------------------------
#
# Convert LOF score to 0-100.
#
# More negative LOF score
#       ↓
# Higher anomaly risk
#
# ---------------------------------------------------------

score_min = df["lof_score"].min()
score_max = df["lof_score"].max()

if score_max != score_min:

    df["lof_risk"] = (

        (
            score_max
            - df["lof_score"]
        )

        /

        (
            score_max
            - score_min
        )

    ) * 100

else:

    df["lof_risk"] = 0


# ---------------------------------------------------------
# 12. DISPLAY RESULTS
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("MODEL RESULTS")
print("-" * 60)

print(
    f"Total projects       : {len(df)}"
)

print(
    f"Anomalies detected   : "
    f"{int(df['lof_anomaly'].sum())}"
)

print(
    f"Normal projects      : "
    f"{int(len(df) - df['lof_anomaly'].sum())}"
)


# ---------------------------------------------------------
# 13. TOP SUSPICIOUS PROJECTS
# ---------------------------------------------------------

print("\nTop 10 suspicious projects:")

result = df.sort_values(
    "lof_risk",
    ascending=False
).head(10)


display_columns = [

    "project_id",

    "sanctioned_amount",

    "actual_expenditure",

    "expenditure_ratio",

    "completion_delay_days",

    "missing_uc",

    "uc_discrepancy_pct",

    "lof_score",

    "lof_risk",

    "lof_anomaly",
]


print(
    result[
        display_columns
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 14. SAVE RESULTS
# ---------------------------------------------------------

os.makedirs(
    "data",
    exist_ok=True
)

df.to_csv(
    output_path,
    index=False
)


# ---------------------------------------------------------
# 15. SAVE MODEL
# ---------------------------------------------------------

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    model,
    "models/lof_model.pkl"
)


# ---------------------------------------------------------
# 16. SAVE SCALER
# ---------------------------------------------------------

joblib.dump(
    scaler,
    "models/lof_scaler.pkl"
)


# ---------------------------------------------------------
# 17. SAVE FEATURE LIST
# ---------------------------------------------------------

joblib.dump(
    features,
    "models/lof_features.pkl"
)


# ---------------------------------------------------------
# 18. FINAL OUTPUT
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("LOF COMPLETED")
print("=" * 60)

print(
    f"Projects processed : {len(df)}"
)

print(
    f"ML features        : {len(features)}"
)

print(
    f"Anomalies detected : "
    f"{int(df['lof_anomaly'].sum())}"
)

print(
    f"\nResults saved to:"
    f"\n{output_path}"
)

print(
    "\nModel saved to:"
    "\nmodels/lof_model.pkl"
)

print(
    "\nScaler saved to:"
    "\nmodels/lof_scaler.pkl"
)

print(
    "\nFeature list saved to:"
    "\nmodels/lof_features.pkl"
)

print("=" * 60)