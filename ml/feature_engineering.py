import pandas as pd
import numpy as np
import os


# =========================================================
# SIH26102 - FEATURE ENGINEERING
# =========================================================

# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

input_path = "data/validated_mplads.csv"
output_path = "data/processed_mplads.csv"


# ---------------------------------------------------------
# LOAD VALIDATED DATA
# ---------------------------------------------------------

print("=" * 60)
print("SIH26102 FEATURE ENGINEERING")
print("=" * 60)

if not os.path.exists(input_path):
    print(
        f"\nERROR: Validated dataset not found:"
        f"\n{input_path}"
    )

    print(
        "\nRun the following command first:"
    )

    print(
        "python ml/data_validation.py"
    )

    raise SystemExit(1)


df = pd.read_csv(input_path)

print(
    f"\nInput projects: {len(df)}"
)

print(
    f"Input columns : {len(df.columns)}"
)


# ---------------------------------------------------------
# BASIC SAFETY
# ---------------------------------------------------------

# Keep the original financial values.
#
# We use temporary safe denominators for calculations
# instead of changing the original columns.

sanctioned_safe = df[
    "sanctioned_amount"
].replace(
    0,
    np.nan
)

actual_safe = df[
    "actual_expenditure"
].replace(
    0,
    np.nan
)


# =========================================================
# 1. EXPENDITURE FEATURES
# =========================================================

print(
    "\nCreating expenditure features..."
)


# Actual expenditure as a fraction of sanctioned amount

df["expenditure_ratio"] = (
    df["actual_expenditure"]
    / sanctioned_safe
)


# Difference between actual and sanctioned expenditure

df["expenditure_difference"] = (
    df["actual_expenditure"]
    - df["sanctioned_amount"]
)


# Percentage deviation from sanctioned amount

df["expenditure_deviation_pct"] = (
    df["expenditure_difference"]
    / sanctioned_safe
) * 100


# Absolute percentage deviation

df["absolute_expenditure_deviation_pct"] = (
    df["expenditure_deviation_pct"]
    .abs()
)


# =========================================================
# 2. UTILIZATION CERTIFICATE FEATURES
# =========================================================

print(
    "Creating UC features..."
)


# Difference between UC amount and actual expenditure

df["uc_expenditure_difference"] = (
    df["uc_amount"]
    - df["actual_expenditure"]
)


# UC amount as a fraction of actual expenditure

df["uc_ratio"] = np.where(
    df["actual_expenditure"] > 0,

    df["uc_amount"]
    / actual_safe,

    0
)


# UC discrepancy percentage

df["uc_discrepancy_pct"] = np.where(

    df["actual_expenditure"] > 0,

    (
        df["uc_expenditure_difference"]
        .abs()
        / actual_safe
    ) * 100,

    0
)


# ---------------------------------------------------------
# UC MISMATCH
# ---------------------------------------------------------

# A mismatch is considered significant when the difference
# exceeds 20%.

df["uc_mismatch"] = (
    (
        df["uc_available"] == 1
    )
    &
    (
        df["uc_discrepancy_pct"] > 20
    )
).astype(int)


# ---------------------------------------------------------
# MISSING UC
# ---------------------------------------------------------

df["missing_uc"] = (
    (
        df["uc_available"] == 0
    )
    &
    (
        df["actual_expenditure"] > 0
    )
).astype(int)


# =========================================================
# 3. DELAY FEATURES
# =========================================================

print(
    "Creating delay features..."
)


# Basic delay indicator

df["is_delayed"] = (
    df["completion_delay_days"] > 30
).astype(int)


# Severe delay

df["severe_delay"] = (
    df["completion_delay_days"] > 180
).astype(int)


# Extreme delay

df["extreme_delay"] = (
    df["completion_delay_days"] > 365
).astype(int)


# Delay relative to planned project duration

df["delay_to_duration_ratio"] = np.where(

    df["project_duration_days"] > 0,

    df["completion_delay_days"]
    / df["project_duration_days"],

    0
)


# =========================================================
# 4. EXPENDITURE + TIME FEATURES
# =========================================================

print(
    "Creating expenditure/time features..."
)


# Expenditure per planned project day

df["expenditure_per_duration_day"] = np.where(

    df["project_duration_days"] > 0,

    df["actual_expenditure"]
    / df["project_duration_days"],

    0
)


# ---------------------------------------------------------
# Total elapsed project time
# ---------------------------------------------------------

df["total_elapsed_days"] = (
    df["project_duration_days"]
    +
    df["completion_delay_days"]
)


# Expenditure per elapsed day

df["expenditure_per_elapsed_day"] = np.where(

    df["total_elapsed_days"] > 0,

    df["actual_expenditure"]
    / df["total_elapsed_days"],

    0
)


# =========================================================
# 5. EXPENDITURE RISK INDICATORS
# =========================================================

print(
    "Creating expenditure risk indicators..."
)


# ---------------------------------------------------------
# Excess expenditure
# ---------------------------------------------------------

df["excess_expenditure"] = (
    df["actual_expenditure"]
    >
    df["sanctioned_amount"]
).astype(int)


# ---------------------------------------------------------
# Extreme expenditure
# ---------------------------------------------------------

df["extreme_expenditure"] = (
    df["expenditure_ratio"] > 1.25
).astype(int)


# ---------------------------------------------------------
# Very high expenditure
# ---------------------------------------------------------

df["very_high_expenditure"] = (
    df["expenditure_ratio"] > 1.50
).astype(int)


# =========================================================
# 6. COMBINED RISK INDICATORS
# =========================================================

print(
    "Creating combined risk indicators..."
)


# ---------------------------------------------------------
# Delay + excess expenditure
# ---------------------------------------------------------

df["delay_and_expenditure_risk"] = (

    (
        df["completion_delay_days"]
        > 180
    )

    &

    (
        df["expenditure_ratio"]
        > 1
    )

).astype(int)


# ---------------------------------------------------------
# Missing UC + high expenditure
# ---------------------------------------------------------

df["missing_uc_high_expenditure"] = (

    (
        df["missing_uc"]
        == 1
    )

    &

    (
        df["expenditure_ratio"]
        > 0.90
    )

).astype(int)


# =========================================================
# 7. DATA SAFETY
# =========================================================

print(
    "\nCleaning infinite calculation results..."
)


# Replace infinity generated by calculations

df = df.replace(
    [np.inf, -np.inf],
    np.nan
)


# Only derived numerical features are filled with 0.
#
# Original fields are not intentionally overwritten with
# suspicious replacement values.

derived_features = [
    "expenditure_ratio",
    "expenditure_difference",
    "expenditure_deviation_pct",
    "absolute_expenditure_deviation_pct",
    "uc_expenditure_difference",
    "uc_ratio",
    "uc_discrepancy_pct",
    "delay_to_duration_ratio",
    "expenditure_per_duration_day",
    "total_elapsed_days",
    "expenditure_per_elapsed_day",
]


for feature in derived_features:

    if feature in df.columns:

        df[feature] = (
            df[feature]
            .fillna(0)
        )


# =========================================================
# 8. FEATURE LIST
# =========================================================

feature_columns = [

    # Expenditure
    "expenditure_ratio",
    "expenditure_difference",
    "expenditure_deviation_pct",
    "absolute_expenditure_deviation_pct",

    # UC
    "uc_expenditure_difference",
    "uc_ratio",
    "uc_discrepancy_pct",
    "uc_mismatch",
    "missing_uc",

    # Delay
    "is_delayed",
    "severe_delay",
    "extreme_delay",
    "delay_to_duration_ratio",

    # Time / expenditure
    "expenditure_per_duration_day",
    "total_elapsed_days",
    "expenditure_per_elapsed_day",

    # Risk indicators
    "excess_expenditure",
    "extreme_expenditure",
    "very_high_expenditure",
    "delay_and_expenditure_risk",
    "missing_uc_high_expenditure",
]


# =========================================================
# 9. DISPLAY FEATURES
# =========================================================

print(
    "\nNew engineered features:"
)

for feature in feature_columns:

    print(
        f"  ✓ {feature}"
    )


# =========================================================
# 10. FEATURE SUMMARY
# =========================================================

print(
    "\n" + "-" * 60
)

print(
    "FEATURE SUMMARY"
)

print(
    "-" * 60
)

print(
    f"Projects processed : {len(df)}"
)

print(
    f"Features created   : {len(feature_columns)}"
)


# =========================================================
# 11. RISK SIGNAL SUMMARY
# =========================================================

print(
    "\nRisk signal counts:"
)

signal_features = [

    "excess_expenditure",
    "extreme_expenditure",
    "very_high_expenditure",
    "uc_mismatch",
    "missing_uc",
    "is_delayed",
    "severe_delay",
    "extreme_delay",
    "delay_and_expenditure_risk",
    "missing_uc_high_expenditure",
]


for feature in signal_features:

    count = int(
        df[feature].sum()
    )

    print(
        f"  {feature}: {count}"
    )


# =========================================================
# 12. SAVE PROCESSED DATA
# =========================================================

os.makedirs(
    os.path.dirname(output_path),
    exist_ok=True
)

df.to_csv(
    output_path,
    index=False
)


# =========================================================
# 13. FINAL OUTPUT
# =========================================================

print(
    "\n" + "=" * 60
)

print(
    "FEATURE ENGINEERING COMPLETED"
)

print(
    "=" * 60
)

print(
    f"Processed projects : {len(df)}"
)

print(
    f"Features created   : {len(feature_columns)}"
)

print(
    f"Saved to           : {output_path}"
)

print(
    "\nPipeline:"
)

print(
    "Raw Data"
)

print(
    "   ↓"
)

print(
    "Data Validation"
)

print(
    "   ↓"
)

print(
    "Validated Data"
)

print(
    "   ↓"
)

print(
    "Feature Engineering"
)

print(
    "   ↓"
)

print(
    "Processed ML Data"
)

print(
    "=" * 60
)