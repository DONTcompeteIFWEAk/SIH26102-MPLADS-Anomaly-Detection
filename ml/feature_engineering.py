import pandas as pd
import numpy as np
import os

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

input_path = "data/synthetic_mplads.csv"
output_path = "data/processed_mplads.csv"

df = pd.read_csv(input_path)

print("=" * 60)
print("SIH26102 FEATURE ENGINEERING")
print("=" * 60)

print(f"\nInput projects: {len(df)}")

# ---------------------------------------------------------
# BASIC SAFETY
# ---------------------------------------------------------

# Prevent division by zero
df["sanctioned_amount"] = df["sanctioned_amount"].replace(0, np.nan)
df["actual_expenditure"] = df["actual_expenditure"].replace(0, np.nan)

# ---------------------------------------------------------
# 1. EXPENDITURE FEATURES
# ---------------------------------------------------------

# Actual expenditure as a fraction of sanctioned amount
df["expenditure_ratio"] = (
    df["actual_expenditure"] /
    df["sanctioned_amount"]
)

# Difference between actual and sanctioned expenditure
df["expenditure_difference"] = (
    df["actual_expenditure"] -
    df["sanctioned_amount"]
)

# Percentage deviation from sanctioned amount
df["expenditure_deviation_pct"] = (
    df["expenditure_difference"] /
    df["sanctioned_amount"]
) * 100

# Absolute deviation
df["absolute_expenditure_deviation_pct"] = (
    abs(df["expenditure_deviation_pct"])
)

# ---------------------------------------------------------
# 2. UC FEATURES
# ---------------------------------------------------------

# Difference between UC amount and actual expenditure
df["uc_expenditure_difference"] = (
    df["uc_amount"] -
    df["actual_expenditure"]
)

# UC amount as percentage of actual expenditure
df["uc_ratio"] = np.where(
    df["actual_expenditure"] > 0,
    df["uc_amount"] /
    df["actual_expenditure"],
    0
)

# UC discrepancy percentage
df["uc_discrepancy_pct"] = np.where(
    df["actual_expenditure"] > 0,
    (
        abs(
            df["uc_expenditure_difference"]
        ) /
        df["actual_expenditure"]
    ) * 100,
    0
)

# Large UC mismatch indicator
df["uc_mismatch"] = (
    (df["uc_available"] == 1) &
    (df["uc_discrepancy_pct"] > 20)
).astype(int)

# Missing UC indicator
df["missing_uc"] = (
    (df["uc_available"] == 0) &
    (df["actual_expenditure"] > 0)
).astype(int)

# ---------------------------------------------------------
# 3. DELAY FEATURES
# ---------------------------------------------------------

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

# Normalized delay relative to planned duration
df["delay_to_duration_ratio"] = np.where(
    df["project_duration_days"] > 0,
    df["completion_delay_days"] /
    df["project_duration_days"],
    0
)

# ---------------------------------------------------------
# 4. EXPENDITURE + TIME RELATIONSHIP
# ---------------------------------------------------------

# Expenditure per planned project day
df["expenditure_per_duration_day"] = np.where(
    df["project_duration_days"] > 0,
    df["actual_expenditure"] /
    df["project_duration_days"],
    0
)

# Expenditure per total elapsed time
df["expenditure_per_elapsed_day"] = np.where(
    (
        df["project_duration_days"] +
        df["completion_delay_days"]
    ) > 0,
    df["actual_expenditure"] /
    (
        df["project_duration_days"] +
        df["completion_delay_days"]
    ),
    0
)

# ---------------------------------------------------------
# 5. RISK INDICATORS
# ---------------------------------------------------------

# Excess expenditure
df["excess_expenditure"] = (
    df["actual_expenditure"] >
    df["sanctioned_amount"]
).astype(int)

# Extreme expenditure
df["extreme_expenditure"] = (
    df["expenditure_ratio"] > 1.25
).astype(int)

# Very high expenditure
df["very_high_expenditure"] = (
    df["expenditure_ratio"] > 1.50
).astype(int)

# Delay + expenditure combination
df["delay_and_expenditure_risk"] = (
    (
        df["completion_delay_days"] > 180
    ) &
    (
        df["expenditure_ratio"] > 1
    )
).astype(int)

# Missing UC + high expenditure combination
df["missing_uc_high_expenditure"] = (
    (
        df["missing_uc"] == 1
    ) &
    (
        df["expenditure_ratio"] > 0.90
    )
).astype(int)

# ---------------------------------------------------------
# RESTORE SAFE NUMBERS
# ---------------------------------------------------------

df = df.replace(
    [np.inf, -np.inf],
    np.nan
)

df = df.fillna(0)

# ---------------------------------------------------------
# DISPLAY FEATURES
# ---------------------------------------------------------

feature_columns = [
    "expenditure_ratio",
    "expenditure_difference",
    "expenditure_deviation_pct",
    "absolute_expenditure_deviation_pct",
    "uc_expenditure_difference",
    "uc_ratio",
    "uc_discrepancy_pct",
    "uc_mismatch",
    "missing_uc",
    "is_delayed",
    "severe_delay",
    "extreme_delay",
    "delay_to_duration_ratio",
    "expenditure_per_duration_day",
    "expenditure_per_elapsed_day",
    "excess_expenditure",
    "extreme_expenditure",
    "very_high_expenditure",
    "delay_and_expenditure_risk",
    "missing_uc_high_expenditure"
]

print("\nNew engineered features:")

for feature in feature_columns:
    print(f"  ✓ {feature}")

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

df.to_csv(
    output_path,
    index=False
)

print("\n" + "-" * 60)
print(f"Processed projects: {len(df)}")
print(f"Features created  : {len(feature_columns)}")
print(f"Saved to          : {output_path}")
print("-" * 60)

print("\nFeature engineering completed successfully.")