import pandas as pd
import numpy as np

print("=" * 60)
print("SIH26102 HYBRID RISK ENGINE")
print("=" * 60)

# ---------------------------------------------------------
# LOAD RESULTS
# ---------------------------------------------------------

ensemble_path = "data/ensemble_results.csv"
rules_path = "data/rule_results.csv"

ml = pd.read_csv(ensemble_path)
rules = pd.read_csv(rules_path)

print(f"\nML projects   : {len(ml)}")
print(f"Rule projects : {len(rules)}")

# ---------------------------------------------------------
# ALIGN PROJECTS
# ---------------------------------------------------------

ml = ml.sort_values("project_id").reset_index(drop=True)
rules = rules.sort_values("project_id").reset_index(drop=True)

if not ml["project_id"].equals(rules["project_id"]):
    raise ValueError(
        "Project IDs do not match between ensemble and rule results."
    )

df = ml.copy()

# ---------------------------------------------------------
# RULE RISK
# ---------------------------------------------------------

rule_columns = [
    "excess_expenditure",
    "extreme_expenditure",
    "missing_uc",
    "uc_mismatch",
    "delay_over_180",
    "severe_delay",
    "not_started"
]

available_rule_columns = [
    col
    for col in rule_columns
    if col in rules.columns
]

df["rule_risk_score"] = 0.0

# ---------------------------------------------------------
# RULE WEIGHTS
# ---------------------------------------------------------

rule_weights = {
    "excess_expenditure": 20,
    "extreme_expenditure": 15,
    "missing_uc": 15,
    "uc_mismatch": 15,
    "delay_over_180": 10,
    "severe_delay": 15,
    "not_started": 10
}

for rule in available_rule_columns:

    weight = rule_weights.get(rule, 0)

    df["rule_risk_score"] += (
        rules[rule].astype(int) * weight
    )

df["rule_risk_score"] = (
    df["rule_risk_score"].clip(0, 100)
)

# ---------------------------------------------------------
# HYBRID SCORE
# ---------------------------------------------------------

ML_WEIGHT = 0.60
RULE_WEIGHT = 0.40

df["hybrid_risk_score"] = (
    ML_WEIGHT * df["ensemble_ml_risk"]
    +
    RULE_WEIGHT * df["rule_risk_score"]
)

df["hybrid_risk_score"] = (
    df["hybrid_risk_score"].clip(0, 100)
)

# ---------------------------------------------------------
# RISK LEVEL
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
    df["hybrid_risk_score"].apply(get_risk_level)
)

# ---------------------------------------------------------
# ADD RULE COLUMNS
# ---------------------------------------------------------

for rule in available_rule_columns:
    df[rule] = rules[rule]

# ---------------------------------------------------------
# EXPLANATION
# ---------------------------------------------------------

def generate_explanation(row):

    reasons = []

    # ML signals
    if row["iforest_risk"] >= 75:
        reasons.append(
            "Isolation Forest identified a strong outlier pattern"
        )

    if row["lof_risk"] >= 75:
        reasons.append(
            "LOF identified a strong local outlier pattern"
        )

    # Rule signals
    if row.get("excess_expenditure", 0) == 1:
        reasons.append(
            "Actual expenditure exceeds sanctioned amount"
        )

    if row.get("extreme_expenditure", 0) == 1:
        reasons.append(
            "Expenditure is substantially above sanctioned amount"
        )

    if row.get("missing_uc", 0) == 1:
        reasons.append(
            "Utilization Certificate is missing"
        )

    if row.get("uc_mismatch", 0) == 1:
        reasons.append(
            "UC amount differs significantly from expenditure"
        )

    if row.get("delay_over_180", 0) == 1:
        reasons.append(
            "Project has a significant completion delay"
        )

    if row.get("severe_delay", 0) == 1:
        reasons.append(
            "Project has a severe completion delay"
        )

    if row.get("not_started", 0) == 1:
        reasons.append(
            "Project has not started"
        )

    if not reasons:
        reasons.append(
            "No major anomaly signal identified"
        )

    return "; ".join(reasons)


df["hybrid_explanation"] = df.apply(
    generate_explanation,
    axis=1
)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

output_path = "data/hybrid_risk_results.csv"

df.to_csv(
    output_path,
    index=False
)

# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

critical_count = (
    df["hybrid_risk_score"] >= 75
).sum()

high_count = (
    df["hybrid_risk_score"] >= 50
).sum()

medium_count = (
    (
        df["hybrid_risk_score"] >= 25
    )
    &
    (
        df["hybrid_risk_score"] < 50
    )
).sum()

low_count = (
    df["hybrid_risk_score"] < 25
).sum()

print("\n" + "-" * 60)
print("HYBRID RISK RESULTS")
print("-" * 60)

print(f"ML weight          : {ML_WEIGHT:.0%}")
print(f"Rule weight        : {RULE_WEIGHT:.0%}")

print(f"\nCritical projects  : {critical_count}")
print(f"High-risk projects : {high_count}")
print(f"Medium-risk projects: {medium_count}")
print(f"Low-risk projects  : {low_count}")

# ---------------------------------------------------------
# TOP HIGH-RISK PROJECTS
# ---------------------------------------------------------

print("\nTop 10 high-risk projects:")

display_columns = [
    "project_id",
    "ensemble_ml_risk",
    "rule_risk_score",
    "hybrid_risk_score",
    "hybrid_risk_level",
    "hybrid_explanation"
]

print(
    df.sort_values(
        "hybrid_risk_score",
        ascending=False
    )
    .head(10)[display_columns]
    .to_string(index=False)
)

# ---------------------------------------------------------
# FINISHED
# ---------------------------------------------------------

print("\n" + "-" * 60)
print(f"Results saved to: {output_path}")
print("-" * 60)

print("\nHybrid risk engine completed successfully.")