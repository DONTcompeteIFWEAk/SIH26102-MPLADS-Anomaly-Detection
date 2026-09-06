import pandas as pd
import numpy as np
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

V2_FILE = DATA_DIR / "real_mplads_works_anomaly_v2.csv"
OUTPUT_FILE = DATA_DIR / "real_work_model_comparison.csv"


print("=" * 75)
print("REAL MPLADS WORK-LEVEL MODEL COMPARISON")
print("=" * 75)


# =========================================================
# 1. FIND V1 OUTPUT
# =========================================================

print("\nSearching for V1 model output...")

csv_files = list(DATA_DIR.glob("*.csv"))

possible_v1_files = []

for file in csv_files:

    name = file.name.lower()

    if (
        "anomaly" in name
        and "v2" not in name
        and "comparison" not in name
    ):
        possible_v1_files.append(file)


if not possible_v1_files:

    print("\nNo V1 anomaly-result CSV found.")

    print("\nCSV files currently present:")

    for file in sorted(csv_files):
        print(f"  - {file.name}")

    raise FileNotFoundError(
        "\nCould not find the V1 anomaly output."
    )


print("\nPossible V1 files found:")

for file in possible_v1_files:
    print(f"  - {file.name}")


# Prefer the known V1 filename if present
preferred_v1 = DATA_DIR / "real_work_anomaly_results.csv"

if preferred_v1.exists():

    V1_FILE = preferred_v1

elif len(possible_v1_files) == 1:

    V1_FILE = possible_v1_files[0]

else:

    v1_candidates = [
        file
        for file in possible_v1_files
        if "v1" in file.name.lower()
    ]

    if len(v1_candidates) == 1:
        V1_FILE = v1_candidates[0]
    else:
        raise RuntimeError(
            "\nMultiple possible V1 files found."
        )


print(f"\nUsing V1 file: {V1_FILE.name}")


# =========================================================
# 2. CHECK V2
# =========================================================

if not V2_FILE.exists():

    raise FileNotFoundError(
        f"\nV2 output not found:\n{V2_FILE}"
    )


# =========================================================
# 3. LOAD DATA
# =========================================================

print("\nLoading V1...")

v1 = pd.read_csv(
    V1_FILE,
    low_memory=False
)

print("Loading V2...")

v2 = pd.read_csv(
    V2_FILE,
    low_memory=False
)

print(f"\nV1 records: {len(v1):,}")
print(f"V2 records: {len(v2):,}")


# =========================================================
# 4. DETECT ACTUAL V1/V2 COLUMNS
# =========================================================

# Your actual V1:
#
# real_ml_risk_score
# real_ml_flag
# real_ml_risk_level
#
# Your V2:
#
# ml_risk_score
# ml_anomaly_flag
# ml_risk_level


v1_score_col = None

for column in [
    "real_ml_risk_score",
    "ml_risk_score",
    "ensemble_risk_score",
    "risk_score",
]:

    if column in v1.columns:
        v1_score_col = column
        break


v1_flag_col = None

for column in [
    "real_ml_flag",
    "ml_anomaly_flag",
    "ensemble_anomaly_flag",
    "anomaly_flag",
]:

    if column in v1.columns:
        v1_flag_col = column
        break


v2_score_col = None

for column in [
    "ml_risk_score",
    "real_ml_risk_score",
    "ensemble_risk_score",
    "risk_score",
]:

    if column in v2.columns:
        v2_score_col = column
        break


v2_flag_col = None

for column in [
    "ml_anomaly_flag",
    "real_ml_flag",
    "ensemble_anomaly_flag",
    "anomaly_flag",
]:

    if column in v2.columns:
        v2_flag_col = column
        break


print("\nDetected columns:")

print(f"V1 score : {v1_score_col}")
print(f"V1 flag  : {v1_flag_col}")
print(f"V2 score : {v2_score_col}")
print(f"V2 flag  : {v2_flag_col}")


if v1_score_col is None:

    print("\nV1 columns:")
    print(v1.columns.tolist())

    raise ValueError(
        "\nCould not identify V1 risk score."
    )


if v1_flag_col is None:

    print("\nV1 columns:")
    print(v1.columns.tolist())

    raise ValueError(
        "\nCould not identify V1 anomaly flag."
    )


if v2_score_col is None:

    print("\nV2 columns:")
    print(v2.columns.tolist())

    raise ValueError(
        "\nCould not identify V2 risk score."
    )


if v2_flag_col is None:

    print("\nV2 columns:")
    print(v2.columns.tolist())

    raise ValueError(
        "\nCould not identify V2 anomaly flag."
    )


# =========================================================
# 5. IDENTIFY COMMON RECORD ID
# =========================================================

id_candidates = [
    "work_id",
    "WORK ID",
    "workId",
    "project_id",
    "ID",
    "IDA",
]


id_col = None

for candidate in id_candidates:

    if (
        candidate in v1.columns
        and candidate in v2.columns
    ):
        id_col = candidate
        break


if id_col:

    print(
        f"\nUsing stable record identifier: {id_col}"
    )

    comparison = pd.DataFrame({
        "record_id": v1[id_col].astype(str),

        "v1_score": pd.to_numeric(
            v1[v1_score_col],
            errors="coerce"
        ),

        "v2_score": pd.to_numeric(
            v2[v2_score_col],
            errors="coerce"
        ),

        "v1_flag": (
            v1[v1_flag_col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
        ),

        "v2_flag": (
            v2[v2_flag_col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
        ),
    })


else:

    print(
        "\nNo common ID found."
    )

    print(
        "Using row position because both models "
        "were generated from the same processed dataset."
    )

    if len(v1) != len(v2):

        raise ValueError(
            "V1 and V2 record counts differ."
        )

    comparison = pd.DataFrame({
        "record_id": np.arange(len(v1)),

        "v1_score": pd.to_numeric(
            v1[v1_score_col],
            errors="coerce"
        ),

        "v2_score": pd.to_numeric(
            v2[v2_score_col],
            errors="coerce"
        ),

        "v1_flag": (
            v1[v1_flag_col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
        ),

        "v2_flag": (
            v2[v2_flag_col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
        ),
    })


# =========================================================
# 6. CLEAN INVALID SCORES
# =========================================================

comparison = comparison.dropna(
    subset=[
        "v1_score",
        "v2_score"
    ]
).reset_index(drop=True)


# =========================================================
# 7. FLAG OVERLAP
# =========================================================

v1_flags = comparison["v1_flag"]
v2_flags = comparison["v2_flag"]

both_flagged = (
    v1_flags & v2_flags
)

v1_only = (
    v1_flags & ~v2_flags
)

v2_only = (
    ~v1_flags & v2_flags
)

neither = (
    ~v1_flags & ~v2_flags
)


print("\n" + "=" * 75)
print("FLAG OVERLAP")
print("=" * 75)

print(
    f"V1 flagged          : {v1_flags.sum():,}"
)

print(
    f"V2 flagged          : {v2_flags.sum():,}"
)

print(
    f"Both V1 + V2        : {both_flagged.sum():,}"
)

print(
    f"V1 only             : {v1_only.sum():,}"
)

print(
    f"V2 only             : {v2_only.sum():,}"
)

print(
    f"Neither             : {neither.sum():,}"
)


if v1_flags.sum() > 0:

    v1_overlap = (
        both_flagged.sum()
        / v1_flags.sum()
    ) * 100

else:

    v1_overlap = 0


if v2_flags.sum() > 0:

    v2_overlap = (
        both_flagged.sum()
        / v2_flags.sum()
    ) * 100

else:

    v2_overlap = 0


print(
    f"\nV1 -> V2 overlap: "
    f"{v1_overlap:.2f}%"
)

print(
    f"V2 -> V1 overlap: "
    f"{v2_overlap:.2f}%"
)


# =========================================================
# 8. SCORE CORRELATION
# =========================================================

score_correlation = comparison[
    [
        "v1_score",
        "v2_score"
    ]
].corr().iloc[0, 1]


print("\n" + "=" * 75)
print("SCORE COMPARISON")
print("=" * 75)

print(
    f"V1 score range: "
    f"{comparison['v1_score'].min():.2f} - "
    f"{comparison['v1_score'].max():.2f}"
)

print(
    f"V2 score range: "
    f"{comparison['v2_score'].min():.2f} - "
    f"{comparison['v2_score'].max():.2f}"
)

print(
    f"V1/V2 score correlation: "
    f"{score_correlation:.4f}"
)


# =========================================================
# 9. TOP 20 OVERLAP
# =========================================================

TOP_N = 20


v1_top_ids = set(
    comparison
    .sort_values(
        "v1_score",
        ascending=False
    )
    .head(TOP_N)["record_id"]
)


v2_top_ids = set(
    comparison
    .sort_values(
        "v2_score",
        ascending=False
    )
    .head(TOP_N)["record_id"]
)


top_overlap = len(
    v1_top_ids & v2_top_ids
)


print("\n" + "=" * 75)
print("TOP 20 COMPARISON")
print("=" * 75)

print(
    f"Common top-20 records: "
    f"{top_overlap}/20"
)


# =========================================================
# 10. RISK DISTRIBUTION
# =========================================================

print("\n" + "=" * 75)
print("RISK DISTRIBUTION")
print("=" * 75)


def risk_distribution(scores):

    return {
        "CRITICAL": int(
            (scores >= 90).sum()
        ),

        "HIGH": int(
            (
                (scores >= 75)
                & (scores < 90)
            ).sum()
        ),

        "MEDIUM": int(
            (
                (scores >= 50)
                & (scores < 75)
            ).sum()
        ),

        "LOW": int(
            (scores < 50).sum()
        ),
    }


v1_distribution = risk_distribution(
    comparison["v1_score"]
)

v2_distribution = risk_distribution(
    comparison["v2_score"]
)


print("\nV1:")

for level, count in v1_distribution.items():

    print(
        f"  {level:<10}: {count:,}"
    )


print("\nV2:")

for level, count in v2_distribution.items():

    print(
        f"  {level:<10}: {count:,}"
    )


# =========================================================
# 11. SCORE CHANGES
# =========================================================

comparison["score_change"] = (
    comparison["v2_score"]
    - comparison["v1_score"]
)

comparison["absolute_score_change"] = (
    comparison["score_change"].abs()
)


print("\n" + "=" * 75)
print("LARGEST V2 SCORE INCREASES")
print("=" * 75)

print(
    comparison
    .sort_values(
        "score_change",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


print("\n" + "=" * 75)
print("LARGEST V2 SCORE DECREASES")
print("=" * 75)

print(
    comparison
    .sort_values(
        "score_change"
    )
    .head(10)
    .to_string(index=False)
)


# =========================================================
# 12. V1-ONLY
# =========================================================

print("\n" + "=" * 75)
print("V1-ONLY HIGH-RISK RECORDS")
print("=" * 75)

print(
    comparison[v1_only]
    .sort_values(
        "v1_score",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# =========================================================
# 13. V2-ONLY
# =========================================================

print("\n" + "=" * 75)
print("V2-ONLY HIGH-RISK RECORDS")
print("=" * 75)

print(
    comparison[v2_only]
    .sort_values(
        "v2_score",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# =========================================================
# 14. ADD SOURCE INFORMATION
# =========================================================

source_columns = [
    "work_id",
    "mp_name",
    "MP NAME",
    "state",
    "STATE",
    "constituency",
    "CONSTITUENCY",
    "work",
    "WORK",
    "category",
    "CATEGORY",
    "allocation_amount",
    "ALLOCATION AMOUNT",
    "status",
    "STATUS",
]


available_source_columns = [
    column
    for column in source_columns
    if column in v2.columns
]


if id_col and available_source_columns:

    source = v2[
        [id_col] + available_source_columns
    ].copy()

    source = source.loc[
        :,
        ~source.columns.duplicated()
    ]

    source = source.rename(
        columns={
            id_col: "record_id"
        }
    )

    source["record_id"] = (
        source["record_id"].astype(str)
    )

    comparison["record_id"] = (
        comparison["record_id"].astype(str)
    )

    # Avoid duplicate record_id merge columns
    source = source.drop_duplicates(
        subset=["record_id"]
    )

    comparison = comparison.merge(
        source,
        on="record_id",
        how="left"
    )


# =========================================================
# 15. SAVE
# =========================================================

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# 16. FINAL SUMMARY
# =========================================================

print("\n" + "=" * 75)
print("FINAL COMPARISON SUMMARY")
print("=" * 75)

print(
    f"""
V1 flagged records        : {v1_flags.sum():,}
V2 flagged records        : {v2_flags.sum():,}

Common flagged records    : {both_flagged.sum():,}
V1-only records           : {v1_only.sum():,}
V2-only records           : {v2_only.sum():,}

Flag overlap V1 -> V2     : {v1_overlap:.2f}%
Flag overlap V2 -> V1     : {v2_overlap:.2f}%

Score correlation         : {score_correlation:.4f}

Top-20 overlap            : {top_overlap}/20
"""
)


print(
    "Comparison saved to:"
)

print(
    OUTPUT_FILE
)


print(
    "\nThese are unsupervised ML screening results."
)

print(
    "They do NOT establish fraud or confirmed irregularity."
)

print(
    "Human/audit verification is required."
)