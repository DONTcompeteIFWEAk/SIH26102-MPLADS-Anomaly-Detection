import pandas as pd
import numpy as np
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

ML_FILE = DATA_DIR / "real_mplads_works_anomaly_v2.csv"

OUTPUT_FILE = (
    DATA_DIR
    / "real_mplads_works_hybrid_risk.csv"
)


print("=" * 75)
print("REAL MPLADS WORK-LEVEL HYBRID RISK ENGINE")
print("=" * 75)


# =========================================================
# 1. LOAD REAL WORK-LEVEL ML RESULTS
# =========================================================

if not ML_FILE.exists():

    raise FileNotFoundError(
        f"\nV2 ML result not found:\n{ML_FILE}"
    )


df = pd.read_csv(
    ML_FILE,
    low_memory=False
)


print(
    f"\nRecords loaded: {len(df):,}"
)


# =========================================================
# 2. VERIFY REQUIRED COLUMNS
# =========================================================

required_columns = [
    "work_id",
    "mp_name",
    "state",
    "constituency",
    "work",
    "category",
    "allocation_amount",
    "ml_risk_score",
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print("\nMissing columns:")

    for column in missing_columns:
        print(f"  - {column}")

    raise ValueError(
        "Required columns are missing."
    )


# =========================================================
# 3. HELPER FUNCTIONS
# =========================================================

def numeric_value(row, column):

    if column not in row.index:
        return np.nan

    value = pd.to_numeric(
        pd.Series([row[column]]),
        errors="coerce"
    ).iloc[0]

    return value


def flag_value(row, column):

    if column not in row.index:
        return False

    value = str(
        row[column]
    ).strip().lower()

    return value in [
        "true",
        "1",
        "yes",
        "y",
    ]


# =========================================================
# 4. DATA QUALITY SCORE
# =========================================================
#
# Data quality is deliberately kept separate from ML.
#
# A missing field does NOT automatically mean an anomaly.
# It contributes only to the evidence-quality indicator.
# =========================================================

def calculate_data_quality(row):

    score = 100

    penalties = {
        "missing_city": 5,
        "missing_ward": 5,
        "missing_block": 5,
        "missing_village": 5,
        "missing_status": 10,
        "missing_constituency": 15,
    }

    for column, penalty in penalties.items():

        if flag_value(row, column):

            score -= penalty

    return max(
        0,
        score
    )


df["data_quality_score_v2"] = (
    df.apply(
        calculate_data_quality,
        axis=1
    )
)


# =========================================================
# 5. DATA QUALITY RISK
# =========================================================
#
# Higher = poorer data quality.
# This is NOT an anomaly score.
# =========================================================

df["data_quality_risk"] = (
    100
    - df["data_quality_score_v2"]
)


# =========================================================
# 6. BEHAVIORAL RULE SIGNALS
# =========================================================
#
# These rules are intentionally conservative.
#
# They identify patterns that deserve verification.
# They do NOT establish fraud.
# =========================================================


# ---------------------------------------------------------
# Rule 1: unusually high allocation compared with peers
# ---------------------------------------------------------

df["rule_high_state_allocation"] = (
    pd.to_numeric(
        df["allocation_vs_state_median"],
        errors="coerce"
    ) >= 2
)


df["rule_high_constituency_allocation"] = (
    pd.to_numeric(
        df["allocation_vs_constituency_median"],
        errors="coerce"
    ) >= 2
)


df["rule_high_category_allocation"] = (
    pd.to_numeric(
        df["allocation_vs_category_median"],
        errors="coerce"
    ) >= 2
)


# ---------------------------------------------------------
# Rule 2: repeated work description
# ---------------------------------------------------------

df["rule_repeated_description"] = (
    pd.to_numeric(
        df["same_work_description_count"],
        errors="coerce"
    ) >= 5
)


# ---------------------------------------------------------
# Rule 3: unusually long description
# ---------------------------------------------------------

df["rule_long_description"] = (
    pd.to_numeric(
        df["work_description_length"],
        errors="coerce"
    ) > 500
)


# =========================================================
# 7. RULE SCORE
# =========================================================
#
# Maximum = 100
#
# The score measures how many independent screening signals
# are present.
# =========================================================

rule_weights = {
    "rule_high_state_allocation": 25,
    "rule_high_constituency_allocation": 25,
    "rule_high_category_allocation": 20,
    "rule_repeated_description": 20,
    "rule_long_description": 10,
}


df["work_rule_score"] = 0


for rule, weight in rule_weights.items():

    df.loc[
        df[rule],
        "work_rule_score"
    ] += weight


df["work_rule_score"] = (
    df["work_rule_score"]
    .clip(upper=100)
)


# =========================================================
# 8. EVIDENCE COUNT
# =========================================================

rule_columns = list(
    rule_weights.keys()
)


df["behavioral_signal_count"] = (
    df[rule_columns]
    .sum(axis=1)
)


# =========================================================
# 9. HYBRID SCORE
# =========================================================
#
# ML = 60%
# Rule evidence = 40%
#
# Data quality is NOT directly added to the hybrid risk
# score. It is displayed separately so missing information
# cannot artificially turn a normal work into a high-risk
# work.
# =========================================================

df["work_hybrid_risk_score"] = (
    0.60 * df["ml_risk_score"]
    + 0.40 * df["work_rule_score"]
)


# =========================================================
# 10. SCREENING FLAG
# =========================================================
#
# Use the top 5% of hybrid scores for the initial
# investigation queue.
#
# This is a screening threshold for this dataset only.
# =========================================================

hybrid_threshold = np.percentile(
    df["work_hybrid_risk_score"],
    95
)


df["work_hybrid_flag"] = (
    df["work_hybrid_risk_score"]
    >= hybrid_threshold
)


# =========================================================
# 11. RISK LEVEL
# =========================================================
#
# The investigation flag and risk level are separate.
#
# A record can have HIGH risk without necessarily being
# selected for the top-5% investigation queue.
# =========================================================

def risk_level(score):

    if score >= 90:
        return "CRITICAL"

    if score >= 75:
        return "HIGH"

    if score >= 50:
        return "MEDIUM"

    return "LOW"


df["work_hybrid_risk_level"] = (
    df["work_hybrid_risk_score"]
    .apply(risk_level)
)


# =========================================================
# 12. PRIMARY EXPLANATION
# =========================================================

def generate_explanation(row):

    reasons = []

    ml_score = numeric_value(
        row,
        "ml_risk_score"
    )

    rule_score = numeric_value(
        row,
        "work_rule_score"
    )

    if (
        ml_score >= 85
    ):
        reasons.append(
            "high behavioral anomaly score"
        )


    if flag_value(
        row,
        "rule_high_state_allocation"
    ):

        reasons.append(
            "allocation substantially above "
            "state peer pattern"
        )


    if flag_value(
        row,
        "rule_high_constituency_allocation"
    ):

        reasons.append(
            "allocation substantially above "
            "constituency peer pattern"
        )


    if flag_value(
        row,
        "rule_high_category_allocation"
    ):

        reasons.append(
            "allocation substantially above "
            "category peer pattern"
        )


    if flag_value(
        row,
        "rule_repeated_description"
    ):

        reasons.append(
            "repeated work-description pattern"
        )


    if flag_value(
        row,
        "rule_long_description"
    ):

        reasons.append(
            "unusually long work description"
        )


    if not reasons:

        return (
            "No major explicit behavioral rule triggered; "
            "ML score indicates relative statistical unusualness"
        )


    return "; ".join(reasons)


df["work_hybrid_explanation"] = (
    df.apply(
        generate_explanation,
        axis=1
    )
)


# =========================================================
# 13. RECOMMENDED ACTION
# =========================================================

def recommended_action(row):

    score = numeric_value(
        row,
        "work_hybrid_risk_score"
    )

    signal_count = numeric_value(
        row,
        "behavioral_signal_count"
    )

    quality = numeric_value(
        row,
        "data_quality_score_v2"
    )


    if score >= 90:

        return (
            "Audit attention required"
        )


    if (
        score >= 75
        or signal_count >= 2
    ):

        return (
            "Requires verification"
        )


    if quality < 70:

        return (
            "Data quality review"
        )


    if score >= 50:

        return (
            "Enhanced monitoring"
        )


    return (
        "Routine monitoring"
    )


df["recommended_action"] = (
    df.apply(
        recommended_action,
        axis=1
    )
)


# =========================================================
# 14. DATA SOURCE METADATA
# =========================================================

df["data_source"] = (
    "REAL_MPLADS_WORKS"
)

df["ground_truth_available"] = (
    False
)


# =========================================================
# 15. SAVE
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# 16. SUMMARY
# =========================================================

print("\n" + "=" * 75)
print("WORK-LEVEL HYBRID SUMMARY")
print("=" * 75)

print(
    f"Records                  : "
    f"{len(df):,}"
)

print(
    f"ML weight                : 60%"
)

print(
    f"Rule weight              : 40%"
)

print(
    f"Hybrid threshold         : "
    f"{hybrid_threshold:.2f}"
)

print(
    f"Hybrid flagged           : "
    f"{df['work_hybrid_flag'].sum():,}"
)


# =========================================================
# 17. RISK DISTRIBUTION
# =========================================================

print("\nRisk distribution")
print("-" * 75)

distribution = (
    df[
        "work_hybrid_risk_level"
    ]
    .value_counts()
    .reindex(
        [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
        ],
        fill_value=0
    )
)


for level, count in distribution.items():

    print(
        f"{level:<12}: {count:,}"
    )


# =========================================================
# 18. RULE SIGNAL COUNTS
# =========================================================

print("\nBehavioral rule signals")
print("-" * 75)

for rule in rule_columns:

    count = int(
        df[rule].sum()
    )

    print(
        f"{rule:<40}: {count:,}"
    )


# =========================================================
# 19. DATA QUALITY
# =========================================================

print("\nData quality")
print("-" * 75)

print(
    f"Average quality score: "
    f"{df['data_quality_score_v2'].mean():.2f}"
)

print(
    f"Records below 70    : "
    f"{(df['data_quality_score_v2'] < 70).sum():,}"
)


# =========================================================
# 20. TOP 15
# =========================================================

print("\n" + "=" * 75)
print("TOP 15 HYBRID-RISK RECORDS")
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
        "ml_risk_score",
        "work_rule_score",
        "work_hybrid_risk_score",
        "work_hybrid_risk_level",
        "behavioral_signal_count",
        "data_quality_score_v2",
        "recommended_action",
        "work_hybrid_explanation",
    ]
    if column in df.columns
]


print(
    df
    .sort_values(
        "work_hybrid_risk_score",
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
# 21. FINAL MESSAGE
# =========================================================

print("\n" + "=" * 75)
print("WORK-LEVEL HYBRID ENGINE COMPLETE")
print("=" * 75)

print(
    "\nOutput:"
)

print(
    OUTPUT_FILE
)

print(
    "\nIMPORTANT:"
)

print(
    "This engine produces screening and prioritization signals."
)

print(
    "It does not establish fraud or confirmed irregularity."
)

print(
    "Records should be reviewed by authorized officers/auditors."
)