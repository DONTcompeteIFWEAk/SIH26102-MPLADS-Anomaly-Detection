import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "real_mplads_works_processed.csv"
OUTPUT_FILE = BASE_DIR / "data" / "real_mplads_works_anomaly_v2.csv"


print("=" * 70)
print("REAL MPLADS WORK-LEVEL ANOMALY MODEL V2")
print("=" * 70)


# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded: {len(df):,}")
print(f"Columns available: {len(df.columns)}")


# ---------------------------------------------------------
# 2. SELECT BEHAVIORAL / NUMERICAL FEATURES
# ---------------------------------------------------------
#
# V2 intentionally avoids using administrative status flags
# such as:
#   - is_completed
#   - is_ongoing
#   - is_sanctioned
#   - approval_pending
#
# Those are better handled separately by the rule engine.
#
# The ML model should focus on unusual:
#   - allocation amounts
#   - timing
#   - recommendation behavior
#   - relative allocation patterns
#   - work-description behavior
#   - data-quality patterns
# ---------------------------------------------------------

feature_candidates = [
    "allocation_amount_log",
    "allocation_vs_state_median",
    "allocation_vs_constituency_median",
    "allocation_vs_category_median",
    "days_since_recommendation",
    "recommendation_year",
    "recommendation_month",
    "recommendation_quarter",
    "work_description_length",
    "work_description_word_count",
    "same_work_description_count",
    "missing_city",
    "missing_ward",
    "missing_block",
    "missing_village",
    "missing_status",
    "missing_approval",
]


available_features = [
    col for col in feature_candidates
    if col in df.columns
]

missing_features = [
    col for col in feature_candidates
    if col not in df.columns
]


print("\nML feature selection")
print("-" * 70)

print(f"Selected features: {len(available_features)}")

for feature in available_features:
    print(f"  ✓ {feature}")

if missing_features:
    print("\nMissing features:")
    for feature in missing_features:
        print(f"  ! {feature}")


if len(available_features) < 5:
    raise ValueError(
        "Too few ML features available. Check the preprocessing output."
    )


# ---------------------------------------------------------
# 3. PREPARE FEATURES
# ---------------------------------------------------------

X = df[available_features].copy()

# Convert everything to numeric
for column in X.columns:
    X[column] = pd.to_numeric(X[column], errors="coerce")


# Replace infinities
X = X.replace([np.inf, -np.inf], np.nan)


# Median imputation
for column in X.columns:
    median_value = X[column].median()

    if pd.isna(median_value):
        median_value = 0

    X[column] = X[column].fillna(median_value)


# ---------------------------------------------------------
# 4. REMOVE ZERO-VARIANCE FEATURES
# ---------------------------------------------------------

constant_features = [
    column
    for column in X.columns
    if X[column].nunique(dropna=False) <= 1
]

if constant_features:
    print("\nRemoving constant features:")

    for feature in constant_features:
        print(f"  - {feature}")

    X = X.drop(columns=constant_features)


print(f"\nFinal feature count: {X.shape[1]}")


# ---------------------------------------------------------
# 5. STANDARDIZATION
# ---------------------------------------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ---------------------------------------------------------
# 6. ISOLATION FOREST
# ---------------------------------------------------------

print("\nTraining Isolation Forest...")

if_model = IsolationForest(
    n_estimators=300,
    contamination=0.05,
    random_state=42,
    n_jobs=-1
)

if_model.fit(X_scaled)

if_raw = -if_model.score_samples(X_scaled)


# ---------------------------------------------------------
# 7. LOCAL OUTLIER FACTOR
# ---------------------------------------------------------

print("Training Local Outlier Factor...")

lof_model = LocalOutlierFactor(
    n_neighbors=20,
    contamination=0.05,
    novelty=False,
    n_jobs=-1
)

lof_labels = lof_model.fit_predict(X_scaled)

lof_raw = -lof_model.negative_outlier_factor_


# ---------------------------------------------------------
# 8. PERCENTILE NORMALIZATION
# ---------------------------------------------------------

def percentile_score(values):
    """
    Converts anomaly scores into a 0-100 percentile scale.
    Higher = more unusual.
    """
    return pd.Series(values).rank(
        method="average",
        pct=True
    ).to_numpy() * 100


if_score = percentile_score(if_raw)
lof_score = percentile_score(lof_raw)


# ---------------------------------------------------------
# 9. V2 ENSEMBLE
# ---------------------------------------------------------
#
# Isolation Forest:
#   detects global isolation
#
# LOF:
#   detects local density anomalies
#
# Equal weighting keeps V2 easy to interpret and compare
# against V1.
# ---------------------------------------------------------

ml_risk_score = (
    0.50 * if_score
    + 0.50 * lof_score
)


# ---------------------------------------------------------
# 10. FLAG TOP 5%
# ---------------------------------------------------------
#
# This threshold is a screening threshold for the current
# dataset. It is NOT a claim that 5% of real MPLADS works
# are anomalous.
# ---------------------------------------------------------

threshold = np.percentile(
    ml_risk_score,
    95
)

ml_anomaly_flag = (
    ml_risk_score >= threshold
)


# ---------------------------------------------------------
# 11. RISK LEVEL
# ---------------------------------------------------------

def risk_level(score):

    if score >= 90:
        return "CRITICAL"

    elif score >= 75:
        return "HIGH"

    elif score >= 50:
        return "MEDIUM"

    return "LOW"


risk_levels = [
    risk_level(score)
    for score in ml_risk_score
]


# ---------------------------------------------------------
# 12. BUILD OUTPUT
# ---------------------------------------------------------

result = df.copy()

result["if_anomaly_score"] = if_score
result["lof_anomaly_score"] = lof_score
result["ml_risk_score"] = ml_risk_score
result["ml_anomaly_flag"] = ml_anomaly_flag
result["ml_risk_level"] = risk_levels


# ---------------------------------------------------------
# 13. EXPLANATION
# ---------------------------------------------------------

def generate_explanation(row):

    reasons = []

    if (
        "allocation_vs_state_median" in row.index
        and pd.notna(row["allocation_vs_state_median"])
        and row["allocation_vs_state_median"] > 2
    ):
        reasons.append(
            "allocation substantially above state median"
        )

    if (
        "allocation_vs_constituency_median" in row.index
        and pd.notna(row["allocation_vs_constituency_median"])
        and row["allocation_vs_constituency_median"] > 2
    ):
        reasons.append(
            "allocation substantially above constituency median"
        )

    if (
        "allocation_vs_category_median" in row.index
        and pd.notna(row["allocation_vs_category_median"])
        and row["allocation_vs_category_median"] > 2
    ):
        reasons.append(
            "allocation substantially above category median"
        )

    if (
        "same_work_description_count" in row.index
        and pd.notna(row["same_work_description_count"])
        and row["same_work_description_count"] >= 5
    ):
        reasons.append(
            "repeated work description pattern"
        )

    if (
        "missing_city" in row.index
        and row["missing_city"] == 1
    ):
        reasons.append("missing city information")

    if (
        "missing_ward" in row.index
        and row["missing_ward"] == 1
    ):
        reasons.append("missing ward information")

    if (
        "missing_block" in row.index
        and row["missing_block"] == 1
    ):
        reasons.append("missing block information")

    if (
        "missing_village" in row.index
        and row["missing_village"] == 1
    ):
        reasons.append("missing village information")

    if (
        "missing_status" in row.index
        and row["missing_status"] == 1
    ):
        reasons.append("missing status information")

    if not reasons:
        return "Statistically unusual pattern identified by the ML ensemble"

    return "; ".join(reasons)


result["ml_explanation"] = result.apply(
    generate_explanation,
    axis=1
)


# ---------------------------------------------------------
# 14. DATA SOURCE FLAGS
# ---------------------------------------------------------

result["data_source"] = "REAL_MPLADS_WORKS"
result["ground_truth_available"] = False


# ---------------------------------------------------------
# 15. SAVE
# ---------------------------------------------------------

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# 16. SUMMARY
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("V2 MODEL SUMMARY")
print("=" * 70)

print(f"Records              : {len(result):,}")
print(f"ML features          : {X.shape[1]}")
print(f"IF score range       : {if_score.min():.2f} - {if_score.max():.2f}")
print(f"LOF score range      : {lof_score.min():.2f} - {lof_score.max():.2f}")
print(f"ML score range       : {ml_risk_score.min():.2f} - {ml_risk_score.max():.2f}")
print(f"95th percentile      : {threshold:.2f}")
print(f"Flagged              : {ml_anomaly_flag.sum():,}")


print("\nRisk distribution")
print("-" * 70)

print(
    result["ml_risk_level"]
    .value_counts()
    .reindex(
        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        fill_value=0
    )
)


print("\nTop 10 ML-risk records")
print("-" * 70)

display_columns = [
    col
    for col in [
        "MP NAME",
        "STATE",
        "CONSTITUENCY",
        "WORK",
        "ALLOCATION AMOUNT",
        "ml_risk_score",
        "ml_risk_level",
        "ml_explanation",
    ]
    if col in result.columns
]

print(
    result
    .sort_values("ml_risk_score", ascending=False)
    [display_columns]
    .head(10)
    .to_string(index=False)
)


print("\nOutput saved to:")
print(OUTPUT_FILE)

print("\nIMPORTANT:")
print(
    "These are ML screening signals from real MPLADS work data."
)
print(
    "They are NOT findings of fraud or confirmed irregularity."
)
print(
    "Human/audit verification is required."
)