import pandas as pd
import numpy as np
import os

np.random.seed(42)

# Make sure data directory exists
os.makedirs("data", exist_ok=True)

# Number of projects
n = 1000

# ---------------------------------------------------------
# BASIC PROJECT DATA
# ---------------------------------------------------------

data = {
    "project_id": [f"P{i:04d}" for i in range(1, n + 1)],

    "state": np.random.choice(
        [
            "State A",
            "State B",
            "State C",
            "State D",
            "State E",
            "State F",
            "State G",
            "State H",
            "State I",
            "State J"
        ],
        n
    ),

    "district": np.random.choice(
        [f"District {chr(65+i)}" for i in range(5)],
        n
    ),

    "constituency": np.random.choice(
        [f"CON-{i:03d}" for i in range(1, 101)],
        n
    ),

    "sanctioned_amount": np.random.randint(
        100000,
        2500000,
        n
    ),

    "project_duration_days": np.random.randint(
        30,
        365,
        n
    ),

    "completion_delay_days": np.random.randint(
        0,
        60,
        n
    ),

    "uc_available": np.random.choice(
        [0, 1],
        n,
        p=[0.1, 0.9]
    ),

    "work_status": np.random.choice(
        [
            "Completed",
            "Ongoing",
            "Not Started"
        ],
        n,
        p=[0.65, 0.30, 0.05]
    ),

    "sector": np.random.choice(
        [
            "Education",
            "Health",
            "Road",
            "Water",
            "Sanitation",
            "Other"
        ],
        n
    ),

    "implementing_agency": np.random.choice(
        [
            "Municipality",
            "PWD",
            "Panchayat",
            "NGO",
            "Other"
        ],
        n
    )
}

df = pd.DataFrame(data)

# ---------------------------------------------------------
# NORMAL EXPENDITURE
# ---------------------------------------------------------

df["actual_expenditure"] = (
    df["sanctioned_amount"] *
    np.random.uniform(0.50, 0.95, n)
).astype(int)

df["uc_amount"] = np.where(
    df["uc_available"] == 1,
    df["actual_expenditure"] *
    np.random.uniform(0.90, 1.05, n),
    0
).astype(int)

# ---------------------------------------------------------
# MARK ALL PROJECTS AS NORMAL INITIALLY
# ---------------------------------------------------------

df["actual_anomaly"] = 0

# ---------------------------------------------------------
# INJECT SYNTHETIC ANOMALIES
# ---------------------------------------------------------

# Select exactly 50 unique projects
anomaly_indices = np.random.choice(
    df.index,
    size=50,
    replace=False
)

# Mark them as actual synthetic anomalies
df.loc[anomaly_indices, "actual_anomaly"] = 1

# Split the 50 anomalies into groups
expenditure_indices = anomaly_indices[:15]
delay_indices = anomaly_indices[15:30]
missing_uc_indices = anomaly_indices[30:40]
uc_mismatch_indices = anomaly_indices[40:50]

# ---------------------------------------------------------
# 1. EXCESS EXPENDITURE ANOMALIES
# ---------------------------------------------------------

df.loc[
    expenditure_indices,
    "actual_expenditure"
] = (
    df.loc[
        expenditure_indices,
        "sanctioned_amount"
    ] * 1.5
).astype(int)

# ---------------------------------------------------------
# 2. LARGE DELAY ANOMALIES
# ---------------------------------------------------------

df.loc[
    delay_indices,
    "completion_delay_days"
] = np.random.randint(
    300,
    801,
    len(delay_indices)
)

# ---------------------------------------------------------
# 3. MISSING UC ANOMALIES
# ---------------------------------------------------------

df.loc[
    missing_uc_indices,
    "uc_available"
] = 0

df.loc[
    missing_uc_indices,
    "uc_amount"
] = 0

# ---------------------------------------------------------
# 4. UC MISMATCH ANOMALIES
# ---------------------------------------------------------

df.loc[
    uc_mismatch_indices,
    "uc_available"
] = 1

df.loc[
    uc_mismatch_indices,
    "uc_amount"
] = (
    df.loc[
        uc_mismatch_indices,
        "actual_expenditure"
    ] * 0.30
).astype(int)

# ---------------------------------------------------------
# SAVE DATASET
# ---------------------------------------------------------

output_path = "data/synthetic_mplads.csv"

df.to_csv(
    output_path,
    index=False
)

print("=" * 60)
print("Synthetic MPLADS dataset generated")
print("=" * 60)

print(f"Total projects     : {len(df)}")
print(f"Synthetic anomalies: {df['actual_anomaly'].sum()}")
print(f"Normal projects    : {(df['actual_anomaly'] == 0).sum()}")

print("\nAnomaly breakdown:")
print(f"Excess expenditure : {len(expenditure_indices)}")
print(f"Large delay        : {len(delay_indices)}")
print(f"Missing UC         : {len(missing_uc_indices)}")
print(f"UC mismatch        : {len(uc_mismatch_indices)}")

print(f"\nSaved to: {output_path}")