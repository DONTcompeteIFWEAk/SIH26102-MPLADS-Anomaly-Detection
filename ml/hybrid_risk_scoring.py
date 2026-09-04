import pandas as pd
import os


# =========================================================
# SIH26102 - HYBRID RISK SCORING ENGINE
# ML Ensemble + CAG Rule Engine
# =========================================================


ML_PATH = "data/ensemble_results.csv"
RULE_PATH = "data/rule_results.csv"
OUTPUT_PATH = "data/hybrid_risk_results.csv"


ML_WEIGHT = 0.60
RULE_WEIGHT = 0.40


print("=" * 60)
print("SIH26102 HYBRID RISK ENGINE")
print("=" * 60)


# ---------------------------------------------------------
# 1. LOAD ML RESULTS
# ---------------------------------------------------------

if not os.path.exists(ML_PATH):

    print(f"\nERROR: {ML_PATH} not found.")

    print("\nRun:")
    print("python ml/ensemble_model.py")

    raise SystemExit(1)


ml_df = pd.read_csv(
    ML_PATH
)


# ---------------------------------------------------------
# 2. LOAD RULE RESULTS
# ---------------------------------------------------------

if not os.path.exists(RULE_PATH):

    print(f"\nERROR: {RULE_PATH} not found.")

    print("\nRun:")
    print("python ml/rules.py")

    raise SystemExit(1)


rule_df = pd.read_csv(
    RULE_PATH
)


print(
    f"\nML projects    : {len(ml_df)}"
)

print(
    f"Rule projects  : {len(rule_df)}"
)


# ---------------------------------------------------------
# 3. CHECK PROJECT IDS
# ---------------------------------------------------------

ml_ids = set(
    ml_df["project_id"]
)

rule_ids = set(
    rule_df["project_id"]
)


if ml_ids != rule_ids:

    print(
        "\nERROR: Project IDs do not match."
    )

    print(
        "Missing in rules:",
        list(ml_ids - rule_ids)[:10]
    )

    print(
        "Missing in ML:",
        list(rule_ids - ml_ids)[:10]
    )

    raise SystemExit(1)


# ---------------------------------------------------------
# 4. MERGE RESULTS
# ---------------------------------------------------------

df = ml_df.merge(
    rule_df,
    on="project_id",
    how="inner",
    suffixes=("_ml", "_rule")
)


print(
    f"\nProjects after merge: {len(df)}"
)


# ---------------------------------------------------------
# 5. VALIDATE ML RISK COLUMN
# ---------------------------------------------------------

if "ensemble_ml_risk" not in df.columns:

    print(
        "\nERROR: ensemble_ml_risk not found."
    )

    print(
        "Run:"
    )

    print(
        "python ml/ensemble_model.py"
    )

    raise SystemExit(1)


# ---------------------------------------------------------
# 6. CALCULATE RULE RISK
# ---------------------------------------------------------
#
# Rule risk is based on the number and severity of
# detected domain/audit signals.
#
# Current rule signals:
#
#   Excess expenditure
#   Extreme expenditure
#   Missing UC
#   Delay
#   Severe delay
#   Not started
#
# Each rule contributes a defined amount.
#
# The score is capped at 100.
#
# ---------------------------------------------------------


rule_weights = {

    "rule_excess_expenditure": 15,

    "rule_extreme_expenditure": 20,

    "rule_missing_uc": 10,

    "rule_uc_mismatch": 15,

    "rule_delay": 10,

    "rule_severe_delay": 15,

    "rule_not_started": 10,
}


df["rule_risk_score"] = 0.0


for column, weight in rule_weights.items():

    if column in df.columns:

        df["rule_risk_score"] += (
            df[column].astype(int)
            * weight
        )


# Cap rule risk at 100.

df["rule_risk_score"] = (
    df["rule_risk_score"]
    .clip(0, 100)
)


# ---------------------------------------------------------
# 7. HYBRID RISK SCORE
# ---------------------------------------------------------
#
# Final score:
#
#     60% ML
#     40% Rules
#
# ---------------------------------------------------------

df["hybrid_risk_score"] = (

    ML_WEIGHT
    * df["ensemble_ml_risk"]

    +

    RULE_WEIGHT
    * df["rule_risk_score"]

)


# ---------------------------------------------------------
# 8. RISK LEVEL
# ---------------------------------------------------------

def get_risk_level(score):

    if score >= 75:

        return "CRITICAL"

    elif score >= 50:

        return "HIGH"

    elif score >= 25:

        return "MEDIUM"

    else:

        return "LOW"


df["hybrid_risk_level"] = (
    df["hybrid_risk_score"]
    .apply(get_risk_level)
)


# ---------------------------------------------------------
# 9. HYBRID EXPLANATION
# ---------------------------------------------------------

def generate_explanation(row):

    reasons = []


    # -------------------------------
    # ML signals
    # -------------------------------

    if row["ensemble_ml_risk"] >= 90:

        reasons.append(
            "Strong statistical anomaly pattern detected by ML"
        )

    elif row["ensemble_ml_risk"] >= 75:

        reasons.append(
            "Elevated statistical anomaly pattern detected by ML"
        )


    # -------------------------------
    # Financial rules
    # -------------------------------

    if (
        "rule_excess_expenditure" in row.index
        and row["rule_excess_expenditure"] == 1
    ):

        reasons.append(
            "Expenditure exceeds sanctioned amount"
        )


    if (
        "rule_extreme_expenditure" in row.index
        and row["rule_extreme_expenditure"] == 1
    ):

        reasons.append(
            "Expenditure is substantially above sanction"
        )


    # -------------------------------
    # UC rules
    # -------------------------------

    if (
        "rule_missing_uc" in row.index
        and row["rule_missing_uc"] == 1
    ):

        reasons.append(
            "Utilization Certificate is missing"
        )


    if (
        "rule_uc_mismatch" in row.index
        and row["rule_uc_mismatch"] == 1
    ):

        reasons.append(
            "UC and expenditure values are inconsistent"
        )


    # -------------------------------
    # Delay rules
    # -------------------------------

    if (
        "rule_delay" in row.index
        and row["rule_delay"] == 1
    ):

        reasons.append(
            "Project completion is delayed"
        )


    if (
        "rule_severe_delay" in row.index
        and row["rule_severe_delay"] == 1
    ):

        reasons.append(
            "Project delay exceeds one year"
        )


    # -------------------------------
    # Project status
    # -------------------------------

    if (
        "rule_not_started" in row.index
        and row["rule_not_started"] == 1
    ):

        reasons.append(
            "Project has not started"
        )


    # -------------------------------
    # Fallback
    # -------------------------------

    if not reasons:

        reasons.append(
            "No major rule violation; statistical risk requires review"
        )


    return "; ".join(reasons)


df["hybrid_explanation"] = (
    df.apply(
        generate_explanation,
        axis=1
    )
)


# ---------------------------------------------------------
# 10. HYBRID FLAG
# ---------------------------------------------------------
#
# For the synthetic benchmark, use the top 5% of
# hybrid-risk projects.
#
# In production this threshold should be calibrated using
# historical audit outcomes and operational capacity.
#
# ---------------------------------------------------------

hybrid_threshold = (
    df["hybrid_risk_score"]
    .quantile(0.95)
)


df["hybrid_anomaly"] = (
    df["hybrid_risk_score"]
    >= hybrid_threshold
).astype(int)


# ---------------------------------------------------------
# 11. DISPLAY SUMMARY
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("HYBRID MODEL RESULTS")
print("-" * 60)

print(
    f"ML weight          : {ML_WEIGHT:.0%}"
)

print(
    f"Rule weight        : {RULE_WEIGHT:.0%}"
)

print(
    f"Hybrid threshold   : "
    f"{hybrid_threshold:.2f}"
)

print(
    f"Projects flagged   : "
    f"{int(df['hybrid_anomaly'].sum())}"
)


# ---------------------------------------------------------
# 12. RISK DISTRIBUTION
# ---------------------------------------------------------

print("\nRisk distribution:")

distribution = (
    df["hybrid_risk_level"]
    .value_counts()
)


for level in [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW"
]:

    print(
        f"{level:<10}: "
        f"{int(distribution.get(level, 0))}"
    )


# ---------------------------------------------------------
# 13. TOP HIGH-RISK PROJECTS
# ---------------------------------------------------------

print("\nTop 15 high-risk projects:")

top_projects = (
    df.sort_values(
        "hybrid_risk_score",
        ascending=False
    )
    .head(15)
)


display_columns = [

    "project_id",

    "ensemble_ml_risk",

    "rule_risk_score",

    "hybrid_risk_score",

    "hybrid_risk_level",

    "hybrid_anomaly",

    "hybrid_explanation",

]


print(
    top_projects[
        display_columns
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 14. SAVE RESULTS
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
# 15. FINAL OUTPUT
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("HYBRID RISK ENGINE COMPLETED")
print("=" * 60)

print(
    f"Projects processed : {len(df)}"
)

print(
    f"ML weight           : {ML_WEIGHT:.0%}"
)

print(
    f"Rule weight         : {RULE_WEIGHT:.0%}"
)

print(
    f"Hybrid threshold    : "
    f"{hybrid_threshold:.2f}"
)

print(
    f"Flagged projects    : "
    f"{int(df['hybrid_anomaly'].sum())}"
)

print(
    "\nResults saved to:"
    "\ndata/hybrid_risk_results.csv"
)

print("=" * 60)