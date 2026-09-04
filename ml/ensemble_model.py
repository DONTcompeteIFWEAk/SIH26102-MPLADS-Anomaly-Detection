import pandas as pd
import os


# =========================================================
# SIH26102 - ENSEMBLE ANOMALY DETECTION
# Isolation Forest + LOF
# =========================================================


IF_PATH = "data/ml_results.csv"
LOF_PATH = "data/lof_results.csv"
OUTPUT_PATH = "data/ensemble_results.csv"


IF_WEIGHT = 0.40
LOF_WEIGHT = 0.60


print("=" * 60)
print("SIH26102 ENSEMBLE ANOMALY DETECTION")
print("=" * 60)


# ---------------------------------------------------------
# 1. LOAD RESULTS
# ---------------------------------------------------------

if_df = pd.read_csv(IF_PATH)
lof_df = pd.read_csv(LOF_PATH)


print(
    f"\nIsolation Forest projects : {len(if_df)}"
)

print(
    f"LOF projects              : {len(lof_df)}"
)


# ---------------------------------------------------------
# 2. CHECK REQUIRED COLUMNS
# ---------------------------------------------------------

if_columns = [
    "project_id",
    "ml_anomaly_score",
    "iforest_risk",
]

lof_columns = [
    "project_id",
    "lof_score",
    "lof_risk",
]


for column in if_columns:

    if column not in if_df.columns:

        print(
            f"\nERROR: Missing Isolation Forest column: {column}"
        )

        raise SystemExit(1)


for column in lof_columns:

    if column not in lof_df.columns:

        print(
            f"\nERROR: Missing LOF column: {column}"
        )

        raise SystemExit(1)


# ---------------------------------------------------------
# 3. CHECK PROJECT IDS
# ---------------------------------------------------------

if_ids = set(
    if_df["project_id"]
)

lof_ids = set(
    lof_df["project_id"]
)


if if_ids != lof_ids:

    print(
        "\nERROR: Project IDs do not match."
    )

    raise SystemExit(1)


# ---------------------------------------------------------
# 4. SELECT PROJECT INFORMATION
# ---------------------------------------------------------
#
# Keep the synthetic ground truth and anomaly type.
#
# These are ONLY used for evaluation.
# They are NOT ML input features.
#
# ---------------------------------------------------------

metadata_columns = [

    "project_id",

    "actual_anomaly",

    "anomaly_type",

    "state",

    "district",

    "constituency",

    "sanctioned_amount",

    "actual_expenditure",

    "expenditure_ratio",

    "completion_delay_days",

    "uc_available",

    "uc_amount",

    "missing_uc",

    "uc_discrepancy_pct",

]


available_metadata = [

    column

    for column in metadata_columns

    if column in if_df.columns

]


base_df = if_df[
    available_metadata
].copy()


# ---------------------------------------------------------
# 5. ADD ISOLATION FOREST RESULTS
# ---------------------------------------------------------

if_results = if_df[
    [
        "project_id",
        "ml_anomaly_score",
        "iforest_risk",
        "ml_anomaly",
    ]
].copy()


# ---------------------------------------------------------
# 6. ADD LOF RESULTS
# ---------------------------------------------------------

lof_results = lof_df[
    [
        "project_id",
        "lof_score",
        "lof_risk",
        "lof_anomaly",
    ]
].copy()


# ---------------------------------------------------------
# 7. MERGE
# ---------------------------------------------------------

df = (

    base_df

    .merge(
        if_results,
        on="project_id",
        how="inner"
    )

    .merge(
        lof_results,
        on="project_id",
        how="inner"
    )

)


print(
    f"\nProjects after merge: {len(df)}"
)


# ---------------------------------------------------------
# 8. VERIFY GROUND TRUTH
# ---------------------------------------------------------

if "actual_anomaly" not in df.columns:

    print(
        "\nERROR: actual_anomaly was not preserved."
    )

    print(
        "Check data/ml_results.csv."
    )

    raise SystemExit(1)


if "anomaly_type" not in df.columns:

    print(
        "\nWARNING: anomaly_type is unavailable."
    )


# ---------------------------------------------------------
# 9. PERCENTILE RISK CALIBRATION
# ---------------------------------------------------------
#
# Both models use different score distributions.
#
# Convert their rankings to a common 0-100 scale.
#
# Higher = more anomalous.
#
# ---------------------------------------------------------


def percentile_risk(series):

    return (
        series
        .rank(
            method="average",
            pct=True
        )
        * 100
    )


# Isolation Forest:
#
# Lower decision function = more anomalous.

df["iforest_percentile_risk"] = (
    (-df["ml_anomaly_score"])
    .rank(
        method="average",
        pct=True
    )
    * 100
)


# LOF:
#
# More negative LOF score = more anomalous.

df["lof_percentile_risk"] = (
    (-df["lof_score"])
    .rank(
        method="average",
        pct=True
    )
    * 100
)


# ---------------------------------------------------------
# 10. ENSEMBLE RISK
# ---------------------------------------------------------

df["ensemble_ml_risk"] = (

    IF_WEIGHT
    * df["iforest_percentile_risk"]

    +

    LOF_WEIGHT
    * df["lof_percentile_risk"]

)


# ---------------------------------------------------------
# 11. SYNTHETIC BENCHMARK THRESHOLD
# ---------------------------------------------------------
#
# Top 5% is used ONLY because the synthetic dataset contains
# 5% injected anomalies.
#
# Production thresholds must be calibrated using real
# historical/audit outcomes.
#
# ---------------------------------------------------------

ensemble_threshold = (
    df["ensemble_ml_risk"]
    .quantile(0.95)
)


df["ensemble_anomaly"] = (

    df["ensemble_ml_risk"]
    >= ensemble_threshold

).astype(int)


# ---------------------------------------------------------
# 12. RISK LEVEL
# ---------------------------------------------------------

def get_risk_level(score):

    if score >= 90:
        return "CRITICAL"

    elif score >= 75:
        return "HIGH"

    elif score >= 50:
        return "MEDIUM"

    else:
        return "LOW"


df["ensemble_risk_level"] = (
    df["ensemble_ml_risk"]
    .apply(get_risk_level)
)


# ---------------------------------------------------------
# 13. EXPLANATION
# ---------------------------------------------------------

def generate_explanation(row):

    reasons = []


    if row["iforest_percentile_risk"] >= 90:

        reasons.append(
            "Isolation Forest identified an unusual pattern"
        )


    if row["lof_percentile_risk"] >= 90:

        reasons.append(
            "LOF identified a strong local outlier pattern"
        )


    if (
        "expenditure_ratio" in row.index
        and row["expenditure_ratio"] > 1
    ):

        reasons.append(
            "expenditure exceeds sanctioned amount"
        )


    if (
        "completion_delay_days" in row.index
        and row["completion_delay_days"] > 180
    ):

        reasons.append(
            "significant completion delay"
        )


    if (
        "missing_uc" in row.index
        and row["missing_uc"] == 1
    ):

        reasons.append(
            "utilization certificate unavailable"
        )


    if (
        "uc_discrepancy_pct" in row.index
        and abs(row["uc_discrepancy_pct"]) > 20
    ):

        reasons.append(
            "material UC-expenditure discrepancy"
        )


    if not reasons:

        reasons.append(
            "statistical anomaly pattern"
        )


    return "; ".join(reasons)


df["ensemble_explanation"] = (
    df.apply(
        generate_explanation,
        axis=1
    )
)


# ---------------------------------------------------------
# 14. DISPLAY RESULTS
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("ENSEMBLE RESULTS")
print("-" * 60)


print(
    f"Isolation Forest weight : {IF_WEIGHT:.0%}"
)

print(
    f"LOF weight              : {LOF_WEIGHT:.0%}"
)

print(
    f"ML threshold            : "
    f"{ensemble_threshold:.2f}"
)

print(
    f"ML anomalies            : "
    f"{int(df['ensemble_anomaly'].sum())}"
)


# ---------------------------------------------------------
# 15. RISK DISTRIBUTION
# ---------------------------------------------------------

print("\nRisk distribution:")


distribution = (
    df["ensemble_risk_level"]
    .value_counts()
)


for level in [

    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",

]:

    print(

        f"{level:<10}: "
        f"{int(distribution.get(level, 0))}"

    )


# ---------------------------------------------------------
# 16. TOP PROJECTS
# ---------------------------------------------------------

print("\nTop 15 ensemble projects:")


top_projects = (

    df.sort_values(
        "ensemble_ml_risk",
        ascending=False
    )

    .head(15)

)


display_columns = [

    "project_id",

    "actual_anomaly",

    "iforest_percentile_risk",

    "lof_percentile_risk",

    "ensemble_ml_risk",

    "ensemble_risk_level",

    "ensemble_anomaly",

]


if "anomaly_type" in df.columns:

    display_columns.insert(
        2,
        "anomaly_type"
    )


print(

    top_projects[
        display_columns
    ]

    .to_string(
        index=False
    )

)


# ---------------------------------------------------------
# 17. SAVE
# ---------------------------------------------------------

os.makedirs(
    "data",
    exist_ok=True
)


df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ---------------------------------------------------------
# 18. FINAL OUTPUT
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("ENSEMBLE MODEL COMPLETED")
print("=" * 60)


print(
    f"Projects processed : {len(df)}"
)

print(
    f"IF weight          : {IF_WEIGHT:.0%}"
)

print(
    f"LOF weight         : {LOF_WEIGHT:.0%}"
)

print(
    f"ML anomalies       : "
    f"{int(df['ensemble_anomaly'].sum())}"
)

print(
    "\nGround truth preserved:"
)

print(
    f"actual_anomaly : "
    f"{'YES' if 'actual_anomaly' in df.columns else 'NO'}"
)

print(
    f"anomaly_type   : "
    f"{'YES' if 'anomaly_type' in df.columns else 'NO'}"
)

print(
    "\nResults saved to:"
    "\ndata/ensemble_results.csv"
)

print("=" * 60)