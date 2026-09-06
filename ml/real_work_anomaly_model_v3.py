import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "real_mplads_works_processed.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "real_mplads_works_anomaly_v3.csv"
)


print("=" * 75)
print("REAL MPLADS WORK-LEVEL ANOMALY MODEL V3")
print("=" * 75)


# =========================================================
# 1. LOAD DATA
# =========================================================

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"\nRows loaded: {len(df):,}")
print(f"Columns available: {len(df.columns)}")


# =========================================================
# 2. BEHAVIORAL ML FEATURES
# =========================================================
#
# V3 deliberately excludes:
#
#   missing_city
#   missing_ward
#   missing_block
#   missing_village
#   missing_status
#   is_unsanctioned
#   is_sanctioned
#   is_ongoing
#   is_completed
#   approval_pending
#
# These are NOT discarded from the dataset.
# They remain available for the Data Quality / Rule layer.
#
# ML is focused on unusual behavioral patterns.
# =========================================================

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

    "work_word_count",

    "same_work_description_count",
]


available_features = [
    column
    for column in feature_candidates
    if column in df.columns
]


missing_features = [
    column
    for column in feature_candidates
    if column not in df.columns
]


print("\n" + "=" * 75)
print("FEATURE SELECTION")
print("=" * 75)

print(
    f"Behavioral features selected: "
    f"{len(available_features)}"
)

for feature in available_features:
    print(f"  ✓ {feature}")


if missing_features:

    print("\nUnavailable features:")

    for feature in missing_features:
        print(f"  ! {feature}")


if len(available_features) < 5:

    raise ValueError(
        "Too few behavioral features are available."
    )


# =========================================================
# 3. PREPARE FEATURES
# =========================================================

X = df[
    available_features
].copy()


for column in X.columns:

    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )


# Replace infinity
X = X.replace(
    [np.inf, -np.inf],
    np.nan
)


# Median imputation
for column in X.columns:

    median_value = X[column].median()

    if pd.isna(median_value):
        median_value = 0

    X[column] = X[column].fillna(
        median_value
    )


# =========================================================
# 4. REMOVE CONSTANT FEATURES
# =========================================================

constant_features = [
    column
    for column in X.columns
    if X[column].nunique(dropna=False) <= 1
]


if constant_features:

    print("\nRemoving constant features:")

    for feature in constant_features:
        print(f"  - {feature}")

    X = X.drop(
        columns=constant_features
    )


print(
    f"\nFinal ML feature count: "
    f"{X.shape[1]}"
)


# =========================================================
# 5. STANDARDIZATION
# =========================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# =========================================================
# 6. ISOLATION FOREST
# =========================================================

print("\nTraining Isolation Forest...")

if_model = IsolationForest(
    n_estimators=400,
    contamination=0.05,
    random_state=42,
    n_jobs=-1
)

if_model.fit(X_scaled)


if_raw = (
    -if_model.score_samples(X_scaled)
)


# =========================================================
# 7. LOF
# =========================================================
#
# Important V3 improvement:
#
# The dataset contains repeated feature profiles.
# LOF can become unstable when many identical vectors
# participate directly in the neighborhood calculation.
#
# Therefore:
#
# 1. Create unique behavioral feature profiles.
# 2. Fit LOF on those profiles.
# 3. Map each profile's LOF score back to all records.
#
# This prevents the duplicate-value warning from V2.
# =========================================================

print(
    "\nPreparing unique behavioral profiles for LOF..."
)


feature_keys = list(X.columns)


unique_X = X.drop_duplicates(
    subset=feature_keys
).reset_index(drop=True)


print(
    f"Original profiles : {len(X):,}"
)

print(
    f"Unique profiles    : {len(unique_X):,}"
)

print(
    f"Repeated profiles  : "
    f"{len(X) - len(unique_X):,}"
)


unique_scaled = scaler.transform(
    unique_X
)


# Choose a neighborhood size safely.
#
# 35 gives LOF a more stable local neighborhood than
# V1/V2's 20 while remaining computationally reasonable.

n_neighbors = min(
    35,
    len(unique_X) - 1
)


if n_neighbors < 2:

    raise ValueError(
        "Not enough unique behavioral profiles for LOF."
    )


print(
    f"LOF neighbors: {n_neighbors}"
)


lof_model = LocalOutlierFactor(
    n_neighbors=n_neighbors,
    contamination=0.05,
    novelty=False,
    n_jobs=-1
)


lof_model.fit_predict(
    unique_scaled
)


unique_lof_raw = (
    -lof_model.negative_outlier_factor_
)


# =========================================================
# 8. MAP LOF SCORE BACK TO ORIGINAL RECORDS
# =========================================================

unique_X_for_mapping = unique_X.copy()

unique_X_for_mapping[
    "_lof_raw"
] = unique_lof_raw


lof_mapping = {}

for _, row in unique_X_for_mapping.iterrows():

    key = tuple(
        row[column]
        for column in feature_keys
    )

    lof_mapping[key] = row["_lof_raw"]


lof_raw = []

for _, row in X.iterrows():

    key = tuple(
        row[column]
        for column in feature_keys
    )

    lof_raw.append(
        lof_mapping[key]
    )


lof_raw = np.asarray(
    lof_raw,
    dtype=float
)


# =========================================================
# 9. PERCENTILE NORMALIZATION
# =========================================================

def percentile_score(values):

    return (
        pd.Series(values)
        .rank(
            method="average",
            pct=True
        )
        .to_numpy()
        * 100
    )


if_score = percentile_score(
    if_raw
)

lof_score = percentile_score(
    lof_raw
)


# =========================================================
# 10. ENSEMBLE ML SCORE
# =========================================================
#
# 50% Isolation Forest
# 50% LOF
#
# Both models are converted to the same 0-100 scale first.
# =========================================================

ml_risk_score = (
    0.50 * if_score
    + 0.50 * lof_score
)


# =========================================================
# 11. SCREENING THRESHOLD
# =========================================================
#
# Top 5% is used only as a screening threshold for this
# dataset.
#
# It does NOT mean 5% of MPLADS works are fraudulent.
# =========================================================

threshold = np.percentile(
    ml_risk_score,
    95
)


ml_anomaly_flag = (
    ml_risk_score >= threshold
)


# =========================================================
# 12. RISK LEVEL
# =========================================================

def risk_level(score):

    if score >= 90:
        return "CRITICAL"

    if score >= 75:
        return "HIGH"

    if score >= 50:
        return "MEDIUM"

    return "LOW"


risk_levels = [
    risk_level(score)
    for score in ml_risk_score
]


# =========================================================
# 13. BEHAVIORAL EXPLANATION
# =========================================================

def explain_record(row):

    reasons = []

    # Allocation behavior
    if (
        "allocation_vs_state_median" in row.index
        and pd.notna(
            row["allocation_vs_state_median"]
        )
        and row["allocation_vs_state_median"] >= 2
    ):

        reasons.append(
            "allocation substantially above "
            "state-level pattern"
        )


    if (
        "allocation_vs_constituency_median" in row.index
        and pd.notna(
            row[
                "allocation_vs_constituency_median"
            ]
        )
        and row[
            "allocation_vs_constituency_median"
        ] >= 2
    ):

        reasons.append(
            "allocation substantially above "
            "constituency-level pattern"
        )


    if (
        "allocation_vs_category_median" in row.index
        and pd.notna(
            row[
                "allocation_vs_category_median"
            ]
        )
        and row[
            "allocation_vs_category_median"
        ] >= 2
    ):

        reasons.append(
            "allocation substantially above "
            "category-level pattern"
        )


    # Repeated work description
    if (
        "same_work_description_count" in row.index
        and pd.notna(
            row["same_work_description_count"]
        )
        and row[
            "same_work_description_count"
        ] >= 5
    ):

        reasons.append(
            "repeated work-description pattern"
        )


    # Unusually long description
    if (
        "work_description_length" in row.index
        and pd.notna(
            row["work_description_length"]
        )
        and row[
            "work_description_length"
        ] > 500
    ):

        reasons.append(
            "unusually long work description"
        )


    if not reasons:

        return (
            "Statistically unusual behavioral pattern "
            "identified by the ML ensemble"
        )


    return "; ".join(reasons)


# =========================================================
# 14. BUILD OUTPUT
# =========================================================

result = df.copy()


result["iforest_risk"] = if_score

result["lof_risk"] = lof_score

result["real_ml_v3_risk_score"] = (
    ml_risk_score
)

result["real_ml_v3_flag"] = (
    ml_anomaly_flag
)

result["real_ml_v3_risk_level"] = (
    risk_levels
)

result["real_ml_v3_explanation"] = (
    result.apply(
        explain_record,
        axis=1
    )
)


# =========================================================
# 15. DATA SOURCE METADATA
# =========================================================

result["data_source"] = (
    "REAL_MPLADS_WORKS"
)

result["ground_truth_available"] = (
    False
)


# =========================================================
# 16. SAVE
# =========================================================

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# 17. SUMMARY
# =========================================================

print("\n" + "=" * 75)
print("V3 MODEL SUMMARY")
print("=" * 75)

print(
    f"Records                 : "
    f"{len(result):,}"
)

print(
    f"ML features             : "
    f"{X.shape[1]}"
)

print(
    f"Unique LOF profiles     : "
    f"{len(unique_X):,}"
)

print(
    f"LOF neighbors           : "
    f"{n_neighbors}"
)

print(
    f"IF score range          : "
    f"{if_score.min():.2f} - "
    f"{if_score.max():.2f}"
)

print(
    f"LOF score range         : "
    f"{lof_score.min():.2f} - "
    f"{lof_score.max():.2f}"
)

print(
    f"ML score range          : "
    f"{ml_risk_score.min():.2f} - "
    f"{ml_risk_score.max():.2f}"
)

print(
    f"95th percentile         : "
    f"{threshold:.2f}"
)

print(
    f"Flagged                 : "
    f"{ml_anomaly_flag.sum():,}"
)


# =========================================================
# 18. RISK DISTRIBUTION
# =========================================================

print("\nRisk distribution")
print("-" * 75)

distribution = (
    result[
        "real_ml_v3_risk_level"
    ]
    .value_counts()
    .reindex(
        [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW"
        ],
        fill_value=0
    )
)


for level, count in distribution.items():

    print(
        f"{level:<12}: {count:,}"
    )


# =========================================================
# 19. TOP 15 RECORDS
# =========================================================

print("\n" + "=" * 75)
print("TOP 15 V3 ML-RISK RECORDS")
print("=" * 75)


display_columns = [
    column
    for column in [
        "work_id",
        "mp_name",
        "state",
        "constituency",
        "category",
        "allocation_amount",
        "real_ml_v3_risk_score",
        "real_ml_v3_risk_level",
        "real_ml_v3_explanation",
    ]
    if column in result.columns
]


print(
    result
    .sort_values(
        "real_ml_v3_risk_score",
        ascending=False
    )
    [
        display_columns
    ]
    .head(15)
    .to_string(
        index=False
    )
)


# =========================================================
# 20. DATA QUALITY IS KEPT SEPARATE
# =========================================================

quality_columns = [
    column
    for column in [
        "missing_city",
        "missing_ward",
        "missing_block",
        "missing_village",
        "missing_status",
        "data_quality_score",
    ]
    if column in result.columns
]


print("\n" + "=" * 75)
print("DATA QUALITY FEATURES")
print("=" * 75)

if quality_columns:

    print(
        "The following fields remain available "
        "for the separate Data Quality layer:"
    )

    for column in quality_columns:
        print(f"  • {column}")

else:

    print(
        "No data-quality fields were found."
    )


# =========================================================
# 21. FINAL MESSAGE
# =========================================================

print("\n" + "=" * 75)
print("V3 COMPLETE")
print("=" * 75)

print(
    "\nOutput:"
)

print(
    OUTPUT_FILE
)

print(
    "\nInterpretation:"
)

print(
    "V3 produces unsupervised behavioral screening signals."
)

print(
    "A high score means the record is statistically unusual,"
)

print(
    "not that fraud or an irregularity has been established."
)

print(
    "Human/audit verification remains necessary."
)