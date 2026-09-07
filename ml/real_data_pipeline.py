import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

INPUT_WORKS_FILE = RAW_DIR / "MPLADS.csv"
INPUT_FINANCIAL_FILE = RAW_DIR / "mplads_real.csv"

OUTPUT_WORKS_FILE = DATA_DIR / "real_mplads_works_processed.csv"
OUTPUT_FINANCIAL_FILE = DATA_DIR / "real_financial_features.csv"

print("=" * 75)
print("SIH26102 — REAL MPLADS COMPREHENSIVE DATA PIPELINE")
print("=" * 75)

# =========================================================
# 1. PROCESS REAL WORKS (60,000+ RECORDS)
# =========================================================
print(f"\n[1/2] Loading raw MPLADS works from {INPUT_WORKS_FILE.name}...")

if not INPUT_WORKS_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_WORKS_FILE}")

# Read raw CSV (semicolon delimited)
df_works = pd.read_csv(
    INPUT_WORKS_FILE,
    sep=";",
    quotechar='"',
    encoding="utf-8",
    low_memory=False
)
print(f"  Raw works loaded: {len(df_works):,}")

# Standardize column names
df_works.columns = [
    c.strip().lower().replace(" ", "_").replace("/", "_")
    for c in df_works.columns
]

# String columns cleanup
string_cols = [
    "mp_name", "work", "category", "state", "constituency",
    "ida", "city", "ward", "block", "village", "ida_approval", "status", "house"
]
for col in string_cols:
    if col in df_works.columns:
        df_works[col] = df_works[col].astype("string").str.strip()
        df_works[col] = df_works[col].replace({"": pd.NA, "NA": pd.NA, "N/A": pd.NA})

# Date and allocation parsing
df_works["recommended_date"] = pd.to_datetime(df_works["recommended_date"], errors="coerce")
df_works["allocation_amount"] = pd.to_numeric(
    df_works["allocation_amount"].astype("string")
    .str.replace(",", "", regex=False)
    .str.replace("₹", "", regex=False)
    .str.strip(),
    errors="coerce"
)

# Deduplicate
df_works = df_works.drop_duplicates().reset_index(drop=True)
df_works.insert(0, "work_id", [f"REAL-WORK-{i:06d}" for i in range(1, len(df_works) + 1)])

# Temporal features
reference_date = df_works["recommended_date"].max()
if pd.isna(reference_date):
    reference_date = pd.to_datetime("2024-03-31")

df_works["recommendation_year"] = df_works["recommended_date"].dt.year
df_works["recommendation_month"] = df_works["recommended_date"].dt.month
df_works["recommendation_quarter"] = df_works["recommended_date"].dt.quarter
df_works["days_since_recommendation"] = (reference_date - df_works["recommended_date"]).dt.days.clip(lower=0).fillna(365)

# Missing field indicators
for col in ["status", "constituency", "city", "ward", "block", "village", "ida"]:
    if col in df_works.columns:
        df_works[f"missing_{col}"] = df_works[col].isna().astype(int)
    else:
        df_works[f"missing_{col}"] = 0

# Status flags
status_norm = df_works["status"].fillna("").astype(str).str.strip().str.lower()
df_works["is_unsanctioned"] = status_norm.eq("unsanctioned").astype(int)
df_works["is_sanctioned"] = status_norm.eq("sanctioned").astype(int)
df_works["is_ongoing"] = status_norm.eq("ongoing").astype(int)
df_works["is_completed"] = status_norm.eq("completed").astype(int)

# Approval status
approval_norm = df_works["ida_approval"].fillna("").astype(str).str.strip().str.lower()
df_works["approval_pending"] = approval_norm.str.contains("pending", na=False).astype(int)

# Financial & Log amount
df_works["allocation_amount_log"] = np.log1p(df_works["allocation_amount"].clip(lower=0).fillna(0))

# Benchmark medians
state_median = df_works.groupby("state")["allocation_amount"].transform("median")
constituency_median = df_works.groupby("constituency")["allocation_amount"].transform("median")
category_median = df_works.groupby("category")["allocation_amount"].transform("median")

df_works["allocation_vs_state_median"] = (df_works["allocation_amount"] / state_median.replace(0, np.nan)).fillna(1.0).clip(0, 50)
df_works["allocation_vs_constituency_median"] = (df_works["allocation_amount"] / constituency_median.replace(0, np.nan)).fillna(1.0).clip(0, 50)
df_works["allocation_vs_category_median"] = (df_works["allocation_amount"] / category_median.replace(0, np.nan)).fillna(1.0).clip(0, 50)

# Work description features
work_text = df_works["work"].fillna("").astype(str).str.lower()
df_works["work_description_length"] = work_text.str.len()
df_works["work_word_count"] = work_text.str.split().str.len()

# Work text repetition / cluster detection
normalized_work = work_text.str.replace(r"\s+", " ", regex=True).str.strip()
work_freq = normalized_work.value_counts()
df_works["same_work_description_count"] = normalized_work.map(work_freq).fillna(1)

# ADVANCED CAG DOMAIN FEATURES:
# 1. Tender-splitting detection (allocations within 95-99.9% of common procurement thresholds: 5 Lakh, 10 Lakh, 25 Lakh)
# In public procurement, works are frequently split just below 5 Lakhs (e.g. ₹4,80,000 to ₹4,99,999) to avoid e-tender mandates
alloc = df_works["allocation_amount"].fillna(0)
is_near_5l = (alloc >= 475000) & (alloc <= 499999)
is_near_10l = (alloc >= 950000) & (alloc <= 999999)
is_near_25l = (alloc >= 2400000) & (alloc <= 2499999)
df_works["split_tender_flag"] = (is_near_5l | is_near_10l | is_near_25l).astype(int)

# 2. Local Cluster Anomaly: Same work description repeated in the exact same Village / Block
village_block = df_works["village"].fillna("").astype(str) + "___" + df_works["block"].fillna("").astype(str)
work_loc_combo = normalized_work + "___" + village_block
work_loc_freq = work_loc_combo.value_counts()
df_works["same_work_location_count"] = work_loc_combo.map(work_loc_freq).fillna(1)
# If repeated 3+ times in same village, high cluster flag
df_works["cluster_work_flag"] = ((df_works["same_work_location_count"] >= 3) & (village_block != "___")).astype(int)

# 3. Dormancy / Prolonged Inaction Flag (recommended > 180 days ago but still unsanctioned or action pending)
df_works["prolonged_inaction_flag"] = (
    (df_works["days_since_recommendation"] > 180) & 
    (df_works["is_unsanctioned"] == 1)
).astype(int)

# 4. Data Quality Score
data_quality = pd.Series(100, index=df_works.index)
data_quality -= df_works["missing_status"] * 15
data_quality -= df_works["missing_constituency"] * 10
data_quality -= df_works["missing_block"] * 5
data_quality -= df_works["missing_village"] * 5
data_quality -= df_works["missing_city"] * 5
df_works["data_quality_score"] = data_quality.clip(0, 100)

df_works["data_source"] = "REAL_MPLADS_WORKS"
df_works["ground_truth_available"] = False

# Save processed works
OUTPUT_WORKS_FILE.parent.mkdir(parents=True, exist_ok=True)
df_works.to_csv(OUTPUT_WORKS_FILE, index=False)
print(f"  [OK] Saved processed works: {OUTPUT_WORKS_FILE} ({len(df_works):,} rows, {len(df_works.columns)} cols)")

# =========================================================
# 2. PROCESS REAL FINANCIAL DATA (559 MPS)
# =========================================================
print(f"\n[2/2] Loading raw MPLADS financial data from {INPUT_FINANCIAL_FILE.name}...")

if INPUT_FINANCIAL_FILE.exists():
    df_fin = pd.read_csv(INPUT_FINANCIAL_FILE)
    df_fin.columns = [c.strip().lower().replace(" ", "_") for c in df_fin.columns]

    # Map column names if needed
    col_map = {
        "sl_no": "sl_no",
        "mp_name": "mp_name",
        "constituency": "constituency",
        "entitlement": "entitlement",
        "fundreceivedgoi": "fund_received",
        "amountavailable": "amount_available",
        "worksrecommcost": "works_recommended_cost",
        "wscost": "work_sanctioned_cost",
        "actualexpenditureincurred": "actual_expenditure",
        "utilizationoverrelease": "utilization_over_release",
        "unspentbalance": "unspent_balance"
    }
    df_fin = df_fin.rename(columns=col_map)
    df_fin.insert(0, "project_id", [f"REAL-FIN-{i:04d}" for i in range(1, len(df_fin) + 1)])

    # Numeric conversions
    num_cols = [
        "entitlement", "fund_received", "amount_available", "works_recommended_cost",
        "work_sanctioned_cost", "actual_expenditure", "utilization_over_release", "unspent_balance"
    ]
    for c in num_cols:
        if c in df_fin.columns:
            df_fin[c] = pd.to_numeric(df_fin[c], errors="coerce").fillna(0)

    # Financial ratios
    sanctioned = df_fin["work_sanctioned_cost"].replace(0, np.nan)
    available = df_fin["amount_available"].replace(0, np.nan)
    received = df_fin["fund_received"].replace(0, np.nan)
    recomm = df_fin["works_recommended_cost"].replace(0, np.nan)

    df_fin["expenditure_to_sanction_ratio"] = (df_fin["actual_expenditure"] / sanctioned).fillna(0)
    df_fin["expenditure_sanction_difference"] = df_fin["actual_expenditure"] - df_fin["work_sanctioned_cost"]
    df_fin["expenditure_deviation_pct"] = ((df_fin["expenditure_sanction_difference"] / sanctioned) * 100).fillna(0)
    df_fin["expenditure_to_available_ratio"] = (df_fin["actual_expenditure"] / available).fillna(0)
    df_fin["sanction_gap"] = df_fin["works_recommended_cost"] - df_fin["work_sanctioned_cost"]
    df_fin["sanction_gap_pct"] = ((df_fin["sanction_gap"] / recomm) * 100).fillna(0)
    df_fin["unspent_ratio"] = (df_fin["unspent_balance"] / available).fillna(0)
    df_fin["unspent_pct"] = df_fin["unspent_ratio"] * 100

    # Screening signals
    df_fin["signal_excess_expenditure"] = (df_fin["actual_expenditure"] > df_fin["work_sanctioned_cost"]).astype(int)
    df_fin["signal_extreme_expenditure"] = (df_fin["expenditure_deviation_pct"] > 25).astype(int)
    df_fin["signal_expenditure_above_available"] = (df_fin["actual_expenditure"] > df_fin["amount_available"]).astype(int)
    df_fin["signal_sanction_gap"] = (df_fin["sanction_gap_pct"] > 30).astype(int)
    df_fin["signal_high_unspent_balance"] = (df_fin["unspent_pct"] > 40).astype(int)

    # Financial rule score (0-100)
    fin_score = (
        df_fin["signal_excess_expenditure"] * 25 +
        df_fin["signal_extreme_expenditure"] * 25 +
        df_fin["signal_expenditure_above_available"] * 25 +
        df_fin["signal_sanction_gap"] * 15 +
        df_fin["signal_high_unspent_balance"] * 10
    ).clip(0, 100)
    df_fin["financial_rule_score"] = fin_score

    def get_fin_risk_level(s):
        if s >= 75: return "CRITICAL"
        if s >= 50: return "HIGH"
        if s >= 25: return "MEDIUM"
        return "LOW"

    df_fin["financial_risk_level"] = df_fin["financial_rule_score"].apply(get_fin_risk_level)

    def get_fin_explanation(r):
        reasons = []
        if r["signal_extreme_expenditure"]:
            reasons.append("Actual expenditure exceeds sanctioned cost by >25%")
        elif r["signal_excess_expenditure"]:
            reasons.append("Actual expenditure exceeds sanctioned cost")
        if r["signal_expenditure_above_available"]:
            reasons.append("Expenditure exceeds total available funds")
        if r["signal_sanction_gap"]:
            reasons.append("High gap (>30%) between recommended and sanctioned cost")
        if r["signal_high_unspent_balance"]:
            reasons.append("High unspent balance (>40% of available funds)")
        return "; ".join(reasons) if reasons else "No major financial irregularity detected"

    df_fin["financial_explanation"] = df_fin.apply(get_fin_explanation, axis=1)
    df_fin["data_source"] = "REAL_MPLADS"
    df_fin["ground_truth_available"] = False

    df_fin.to_csv(OUTPUT_FINANCIAL_FILE, index=False)
    print(f"  [OK] Saved processed financials: {OUTPUT_FINANCIAL_FILE} ({len(df_fin):,} rows)")
else:
    print(f"  ! Warning: {INPUT_FINANCIAL_FILE} not found.")

print("\n" + "=" * 75)
print("PREPROCESSING COMPLETE")
print("=" * 75)
