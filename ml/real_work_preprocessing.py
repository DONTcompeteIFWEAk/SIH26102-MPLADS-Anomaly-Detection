from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "data" / "raw" / "MPLADS.csv"
OUTPUT_FILE = BASE_DIR / "data" / "real_mplads_works_processed.csv"

df = pd.read_csv(INPUT_FILE, sep=";", quotechar='"', encoding="utf-8", low_memory=False)
df.columns = [c.strip().lower().replace(" ", "_").replace("/", "_") for c in df.columns]

string_cols = ["mp_name","work","category","state","constituency","ida","city","ward","block","village","ida_approval","status","house"]
for col in string_cols:
    df[col] = df[col].astype("string").str.strip()
    df[col] = df[col].replace({"": pd.NA, "NA": pd.NA, "N/A": pd.NA})

df["recommended_date"] = pd.to_datetime(df["recommended_date"], errors="coerce")
df["allocation_amount"] = pd.to_numeric(
    df["allocation_amount"].astype("string").str.replace(",","",regex=False).str.replace("₹","",regex=False).str.strip(),
    errors="coerce"
)
df = df.drop_duplicates().reset_index(drop=True)
df.insert(0, "work_id", [f"REAL-WORK-{i:06d}" for i in range(1, len(df)+1)])

reference_date = df["recommended_date"].max()
df["recommendation_year"] = df["recommended_date"].dt.year
df["recommendation_month"] = df["recommended_date"].dt.month
df["recommendation_quarter"] = df["recommended_date"].dt.quarter
df["days_since_recommendation"] = (reference_date - df["recommended_date"]).dt.days

for col in ["status","constituency","city","ward","block","village"]:
    df[f"missing_{col}"] = df[col].isna().astype(int)

status_norm = df["status"].fillna("").astype(str).str.strip().str.lower()
df["is_unsanctioned"] = status_norm.eq("unsanctioned").astype(int)
df["is_sanctioned"] = status_norm.eq("sanctioned").astype(int)
df["is_ongoing"] = status_norm.eq("ongoing").astype(int)
df["is_completed"] = status_norm.eq("completed").astype(int)

approval_norm = df["ida_approval"].fillna("").astype(str).str.strip().str.lower()
df["approval_pending"] = approval_norm.str.contains("pending", na=False).astype(int)

df["allocation_amount_log"] = np.log1p(df["allocation_amount"].clip(lower=0))

state_median = df.groupby("state")["allocation_amount"].transform("median")
constituency_median = df.groupby("constituency")["allocation_amount"].transform("median")
category_median = df.groupby("category")["allocation_amount"].transform("median")

df["allocation_vs_state_median"] = df["allocation_amount"] / state_median.replace(0, np.nan)
df["allocation_vs_constituency_median"] = df["allocation_amount"] / constituency_median.replace(0, np.nan)
df["allocation_vs_category_median"] = df["allocation_amount"] / category_median.replace(0, np.nan)

work_text = df["work"].fillna("").astype(str).str.lower()
df["work_description_length"] = work_text.str.len()
df["work_word_count"] = work_text.str.split().str.len()

normalized_work = work_text.str.replace(r"\s+", " ", regex=True).str.strip()
work_frequency = normalized_work.value_counts()
df["same_work_description_count"] = normalized_work.map(work_frequency).fillna(1)

df["data_quality_score"] = 100
df.loc[df["missing_status"] == 1, "data_quality_score"] -= 15
df.loc[df["missing_constituency"] == 1, "data_quality_score"] -= 10
df.loc[df["missing_block"] == 1, "data_quality_score"] -= 5
df.loc[df["missing_village"] == 1, "data_quality_score"] -= 5
df["data_quality_score"] = df["data_quality_score"].clip(0, 100)

df["data_source"] = "REAL_MPLADS_WORKS"
df["ground_truth_available"] = False

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns):,}")
print(f"Output: {OUTPUT_FILE}")
