import pandas as pd
import numpy as np
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

V2_FILE = DATA_DIR / "real_mplads_works_anomaly_v2.csv"
V3_FILE = DATA_DIR / "real_mplads_works_anomaly_v3.csv"

OUTPUT_FILE = DATA_DIR / "real_work_v2_v3_comparison.csv"


print("=" * 75)
print("REAL MPLADS WORK-LEVEL V2 vs V3 COMPARISON")
print("=" * 75)


# =========================================================
# 1. LOAD
# =========================================================

print("\nLoading V2...")

v2 = pd.read_csv(
    V2_FILE,
    low_memory=False
)

print("Loading V3...")

v3 = pd.read_csv(
    V3_FILE,
    low_memory=False
)

print(f"\nV2 records: {len(v2):,}")
print(f"V3 records: {len(v3):,}")


if len(v2) != len(v3):

    raise ValueError(
        "V2 and V3 contain different numbers of records."
    )


# =========================================================
# 2. IDENTIFY COLUMNS
# =========================================================

v2_score = "ml_risk_score"
v2_flag = "ml_anomaly_flag"

v3_score = "real_ml_v3_risk_score"
v3_flag = "real_ml_v3_flag"


for column in [
    v2_score,
    v2_flag,
]:

    if column not in v2.columns:

        raise ValueError(
            f"Missing V2 column: {column}"
        )


for column in [
    v3_score,
    v3_flag,
]:

    if column not in v3.columns:

        raise ValueError(
            f"Missing V3 column: {column}"
        )


print("\nDetected columns:")

print(f"V2 score : {v2_score}")
print(f"V2 flag  : {v2_flag}")
print(f"V3 score : {v3_score}")
print(f"V3 flag  : {v3_flag}")


# =========================================================
# 3. ALIGN USING WORK ID
# =========================================================

if (
    "work_id" not in v2.columns
    or "work_id" not in v3.columns
):

    raise ValueError(
        "work_id is required for V2/V3 comparison."
    )


comparison = pd.DataFrame({

    "work_id": v2["work_id"].astype(str),

    "v2_score": pd.to_numeric(
        v2[v2_score],
        errors="coerce"
    ),

    "v3_score": pd.to_numeric(
        v3[v3_score],
        errors="coerce"
    ),

    "v2_flag": (
        v2[v2_flag]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    ),

    "v3_flag": (
        v3[v3_flag]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    ),
})


comparison = comparison.dropna(
    subset=[
        "v2_score",
        "v3_score"
    ]
).reset_index(drop=True)


# =========================================================
# 4. FLAG OVERLAP
# =========================================================

v2_flags = comparison["v2_flag"]
v3_flags = comparison["v3_flag"]

both = v2_flags & v3_flags
v2_only = v2_flags & ~v3_flags
v3_only = ~v2_flags & v3_flags
neither = ~v2_flags & ~v3_flags


print("\n" + "=" * 75)
print("FLAG OVERLAP")
print("=" * 75)

print(f"V2 flagged       : {v2_flags.sum():,}")
print(f"V3 flagged       : {v3_flags.sum():,}")
print(f"Both             : {both.sum():,}")
print(f"V2 only          : {v2_only.sum():,}")
print(f"V3 only          : {v3_only.sum():,}")
print(f"Neither          : {neither.sum():,}")


v2_overlap = (
    both.sum() / v2_flags.sum() * 100
    if v2_flags.sum() > 0
    else 0
)

v3_overlap = (
    both.sum() / v3_flags.sum() * 100
    if v3_flags.sum() > 0
    else 0
)


print(
    f"\nV2 -> V3 overlap: {v2_overlap:.2f}%"
)

print(
    f"V3 -> V2 overlap: {v3_overlap:.2f}%"
)


# =========================================================
# 5. SCORE CORRELATION
# =========================================================

correlation = comparison[
    [
        "v2_score",
        "v3_score"
    ]
].corr().iloc[0, 1]


print("\n" + "=" * 75)
print("SCORE CORRELATION")
print("=" * 75)

print(
    f"V2 range: "
    f"{comparison['v2_score'].min():.2f} - "
    f"{comparison['v2_score'].max():.2f}"
)

print(
    f"V3 range: "
    f"{comparison['v3_score'].min():.2f} - "
    f"{comparison['v3_score'].max():.2f}"
)

print(
    f"V2/V3 correlation: "
    f"{correlation:.4f}"
)


# =========================================================
# 6. TOP 20
# =========================================================

TOP_N = 20


v2_top = set(
    comparison
    .sort_values(
        "v2_score",
        ascending=False
    )
    .head(TOP_N)["work_id"]
)


v3_top = set(
    comparison
    .sort_values(
        "v3_score",
        ascending=False
    )
    .head(TOP_N)["work_id"]
)


top_overlap = len(
    v2_top & v3_top
)


print("\n" + "=" * 75)
print("TOP 20 OVERLAP")
print("=" * 75)

print(
    f"Common top-20 records: "
    f"{top_overlap}/20"
)


# =========================================================
# 7. SCORE CHANGE
# =========================================================

comparison["score_change"] = (
    comparison["v3_score"]
    - comparison["v2_score"]
)

comparison["absolute_score_change"] = (
    comparison["score_change"].abs()
)


print("\n" + "=" * 75)
print("LARGEST V3 SCORE INCREASES")
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
print("LARGEST V3 SCORE DECREASES")
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
# 8. V2 ONLY
# =========================================================

print("\n" + "=" * 75)
print("V2-ONLY FLAGGED RECORDS")
print("=" * 75)

print(
    comparison[v2_only]
    .sort_values(
        "v2_score",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)


# =========================================================
# 9. V3 ONLY
# =========================================================

print("\n" + "=" * 75)
print("V3-ONLY FLAGGED RECORDS")
print("=" * 75)

print(
    comparison[v3_only]
    .sort_values(
        "v3_score",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)


# =========================================================
# 10. RISK DISTRIBUTION
# =========================================================

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


v2_distribution = risk_distribution(
    comparison["v2_score"]
)

v3_distribution = risk_distribution(
    comparison["v3_score"]
)


print("\n" + "=" * 75)
print("RISK DISTRIBUTION")
print("=" * 75)

print("\nV2:")

for level, count in v2_distribution.items():

    print(
        f"  {level:<10}: {count:,}"
    )


print("\nV3:")

for level, count in v3_distribution.items():

    print(
        f"  {level:<10}: {count:,}"
    )


# =========================================================
# 11. ADD RECORD DETAILS
# =========================================================

detail_columns = [
    "work_id",
    "mp_name",
    "state",
    "constituency",
    "category",
    "allocation_amount",
    "work",
    "status",
]


available_details = [
    column
    for column in detail_columns
    if column in v3.columns
]


details = v3[
    available_details
].copy()


details["work_id"] = (
    details["work_id"].astype(str)
)


comparison = comparison.merge(
    details,
    on="work_id",
    how="left"
)


# =========================================================
# 12. SAVE
# =========================================================

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# 13. FINAL SUMMARY
# =========================================================

print("\n" + "=" * 75)
print("FINAL SUMMARY")
print("=" * 75)

print(
    f"""
V2 flagged records       : {v2_flags.sum():,}
V3 flagged records       : {v3_flags.sum():,}

Common flagged           : {both.sum():,}

V2-only                  : {v2_only.sum():,}
V3-only                  : {v3_only.sum():,}

V2 -> V3 overlap         : {v2_overlap:.2f}%
V3 -> V2 overlap         : {v3_overlap:.2f}%

Score correlation        : {correlation:.4f}

Top-20 overlap            : {top_overlap}/20
"""
)

print(
    "Saved:"
)

print(
    OUTPUT_FILE
)

print(
    "\nThis comparison evaluates unsupervised screening behavior."
)

print(
    "It does not establish fraud or confirmed irregularity."
)