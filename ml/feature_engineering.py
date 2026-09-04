import pandas as pd

# -----------------------------------------
# 1. Load data
# -----------------------------------------

df = pd.read_csv("data/synthetic_mplads.csv")


# -----------------------------------------
# 2. Financial features
# -----------------------------------------

# How much of the sanctioned amount was spent?
df["expenditure_ratio"] = (
    df["actual_expenditure"] /
    df["sanctioned_amount"]
)

# Amount spent above/below sanction
df["expenditure_difference"] = (
    df["actual_expenditure"] -
    df["sanctioned_amount"]
)


# -----------------------------------------
# 3. UC-related features
# -----------------------------------------

# Difference between expenditure and UC amount
df["uc_expenditure_difference"] = (
    df["actual_expenditure"] -
    df["uc_amount"]
)

# UC utilization ratio
df["uc_ratio"] = 0.0

mask = df["actual_expenditure"] > 0

df.loc[mask, "uc_ratio"] = (
    df.loc[mask, "uc_amount"] /
    df.loc[mask, "actual_expenditure"]
)


# -----------------------------------------
# 4. Delay features
# -----------------------------------------

df["is_delayed"] = (
    df["completion_delay_days"] > 30
).astype(int)


df["severe_delay"] = (
    df["completion_delay_days"] > 180
).astype(int)


# -----------------------------------------
# 5. UC missing flag
# -----------------------------------------

df["missing_uc"] = (
    df["uc_available"] == 0
).astype(int)


# -----------------------------------------
# 6. Financial anomaly indicators
# -----------------------------------------

df["excess_expenditure"] = (
    df["expenditure_ratio"] > 1.0
).astype(int)


df["extreme_expenditure"] = (
    df["expenditure_ratio"] > 1.25
).astype(int)


# -----------------------------------------
# 7. Display features
# -----------------------------------------

print("\nNew features created:\n")

feature_columns = [
    "project_id",
    "sanctioned_amount",
    "actual_expenditure",
    "expenditure_ratio",
    "expenditure_difference",
    "completion_delay_days",
    "is_delayed",
    "severe_delay",
    "uc_available",
    "uc_amount",
    "uc_ratio",
    "uc_expenditure_difference",
    "missing_uc",
    "excess_expenditure",
    "extreme_expenditure"
]

print(df[feature_columns].head(10))


# -----------------------------------------
# 8. Save processed dataset
# -----------------------------------------

df.to_csv(
    "data/processed_mplads.csv",
    index=False
)

print("\nProcessed dataset saved successfully!")