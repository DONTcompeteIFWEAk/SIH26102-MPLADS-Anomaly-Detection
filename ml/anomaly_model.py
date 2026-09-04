import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os


# =========================================================
# SIH26102 - ISOLATION FOREST ANOMALY DETECTION
# Controlled Feature Configuration
# =========================================================


# ---------------------------------------------------------
# 1. LOAD PROCESSED DATA
# ---------------------------------------------------------

input_path = "data/processed_mplads.csv"
output_path = "data/ml_results.csv"

df = pd.read_csv(input_path)

print("=" * 60)
print("SIH26102 ISOLATION FOREST")
print("=" * 60)

print(f"\nProjects loaded: {len(df)}")


# ---------------------------------------------------------
# 2. SELECT CONTROLLED ML FEATURES
# ---------------------------------------------------------
#
# We intentionally use a smaller set of meaningful features.
#
# Too many derived/correlated features can distort
# distance-based and tree-based anomaly detection.
#
# These features represent:
#
#   Financial behaviour
#   UC behaviour
#   Delay behaviour
#   Strong anomaly indicators
#
# ---------------------------------------------------------

features = [

    # Financial features
    "sanctioned_amount",
    "actual_expenditure",
    "expenditure_ratio",
    "expenditure_difference",
    "expenditure_deviation_pct",

    # Delay features
    "completion_delay_days",
    "is_delayed",
    "project_duration_days",

    # UC / utilization features
    "uc_available",
    "uc_amount",
    "uc_ratio",
    "uc_expenditure_difference",
    "missing_uc",

    # Strong financial anomaly indicators
    "excess_expenditure",
    "extreme_expenditure",
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

# Replace infinite values.

X = X.replace(
    [float("inf"), float("-inf")],
    0
)


# Replace missing values.

X = X.fillna(0)


# ---------------------------------------------------------
# 6. SCALE FEATURES
# ---------------------------------------------------------

print("\nScaling ML features...")

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ---------------------------------------------------------
# 7. CREATE ISOLATION FOREST
# ---------------------------------------------------------

print("\nCreating Isolation Forest...")

model = IsolationForest(

    n_estimators=200,

    contamination=0.05,

    random_state=42,

    n_jobs=-1
)


# ---------------------------------------------------------
# 8. TRAIN MODEL
# ---------------------------------------------------------

print("Training model...")

model.fit(X_scaled)


# ---------------------------------------------------------
# 9. GENERATE PREDICTIONS
# ---------------------------------------------------------

print("Generating anomaly predictions...")

df["ml_prediction"] = model.predict(X_scaled)


# Isolation Forest decision function:
#
# Higher value = more normal
# Lower value  = more anomalous


df["ml_anomaly_score"] = (
    model.decision_function(X_scaled)
)


# ---------------------------------------------------------
# 10. ANOMALY FLAG
# ---------------------------------------------------------
#
# Isolation Forest:
#
# -1 = anomaly
#  1 = normal
#
# Convert this to:
#
# 1 = anomaly
# 0 = normal
#
# ---------------------------------------------------------

df["ml_anomaly"] = (
    df["ml_prediction"] == -1
).astype(int)


# ---------------------------------------------------------
# 11. NORMALIZED ISOLATION FOREST RISK
# ---------------------------------------------------------
#
# Convert anomaly score to a 0-100 risk score.
#
# Lower decision_function
#       ↓
# Higher anomaly risk
#
# ---------------------------------------------------------

score_min = df["ml_anomaly_score"].min()
score_max = df["ml_anomaly_score"].max()

if score_max != score_min:

    df["iforest_risk"] = (

        (
            score_max
            - df["ml_anomaly_score"]
        )

        /

        (
            score_max
            - score_min
        )

    ) * 100

else:

    df["iforest_risk"] = 0


# ---------------------------------------------------------
# 12. DISPLAY MODEL SUMMARY
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("MODEL RESULTS")
print("-" * 60)

print(
    f"Total projects       : {len(df)}"
)

print(
    f"Anomalies detected   : "
    f"{int(df['ml_anomaly'].sum())}"
)

print(
    f"Normal projects      : "
    f"{int(len(df) - df['ml_anomaly'].sum())}"
)


# ---------------------------------------------------------
# 13. TOP SUSPICIOUS PROJECTS
# ---------------------------------------------------------

print("\nTop 10 suspicious projects:")

result = df.sort_values(
    "iforest_risk",
    ascending=False
).head(10)


display_columns = [

    "project_id",

    "sanctioned_amount",

    "actual_expenditure",

    "expenditure_ratio",

    "completion_delay_days",

    "uc_available",

    "missing_uc",

    "excess_expenditure",

    "extreme_expenditure",

    "iforest_risk",

    "ml_anomaly",
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
    "models/isolation_forest.pkl"
)


# ---------------------------------------------------------
# 16. SAVE SCALER
# ---------------------------------------------------------

joblib.dump(
    scaler,
    "models/scaler.pkl"
)


# ---------------------------------------------------------
# 17. SAVE FEATURE LIST
# ---------------------------------------------------------

joblib.dump(
    features,
    "models/isolation_forest_features.pkl"
)


# ---------------------------------------------------------
# 18. FINAL OUTPUT
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("ISOLATION FOREST COMPLETED")
print("=" * 60)

print(
    f"Projects processed : {len(df)}"
)

print(
    f"ML features        : {len(features)}"
)

print(
    f"Anomalies detected : "
    f"{int(df['ml_anomaly'].sum())}"
)

print(
    f"\nResults saved to:"
    f"\n{output_path}"
)

print(
    "\nModel saved to:"
    "\nmodels/isolation_forest.pkl"
)

print(
    "\nScaler saved to:"
    "\nmodels/scaler.pkl"
)

print(
    "\nFeature list saved to:"
    "\nmodels/isolation_forest_features.pkl"
)

print("=" * 60)