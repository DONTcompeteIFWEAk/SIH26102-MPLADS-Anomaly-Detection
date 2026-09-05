import pandas as pd
import numpy as np


ML_FILE = "data/ensemble_results.csv"
RULE_FILE = "data/rule_results.csv"
OUTPUT_FILE = "data/hybrid_risk_results.csv"


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

ML_WEIGHT = 0.60
RULE_WEIGHT = 0.40


# ---------------------------------------------------------
# Rule weights
# ---------------------------------------------------------

RULE_WEIGHTS = {
    "rule_excess_expenditure": 15,
    "rule_extreme_expenditure": 20,
    "rule_missing_uc": 10,
    "rule_uc_mismatch": 15,
    "rule_delay": 10,
    "rule_severe_delay": 15,
    "rule_not_started": 10,
}


# ---------------------------------------------------------
# Risk level
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


# ---------------------------------------------------------
# Rule risk score
# ---------------------------------------------------------

def calculate_rule_score(row):

    score = 0

    for rule, weight in RULE_WEIGHTS.items():
        if rule in row.index:
            score += int(row[rule]) * weight

    return min(score, 100)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("SIH26102 HYBRID RISK SCORING")
    print("=" * 60)

    print("\nLoading ML results...")
    ml = pd.read_csv(ML_FILE)

    print(f"ML projects: {len(ml)}")

    print("\nLoading CAG rule results...")
    rules = pd.read_csv(RULE_FILE)

    print(f"Rule projects: {len(rules)}")

    # -----------------------------------------------------
    # Preserve synthetic ground truth
    # -----------------------------------------------------

    ground_truth = pd.read_csv("data/processed_mplads.csv")

    truth_columns = ["project_id"]

    if "actual_anomaly" in ground_truth.columns:
        truth_columns.append("actual_anomaly")

    if "anomaly_type" in ground_truth.columns:
        truth_columns.append("anomaly_type")

    ground_truth = ground_truth[truth_columns]

    # -----------------------------------------------------
    # Merge ML + Rules
    # -----------------------------------------------------

    hybrid = ml.merge(
        rules,
        on="project_id",
        how="inner",
        suffixes=("_ml", "_rule")
    )

    print(f"Projects after ML + rule merge: {len(hybrid)}")

    # -----------------------------------------------------
    # Merge ground truth ONLY for evaluation
    # -----------------------------------------------------

    hybrid = hybrid.merge(
        ground_truth,
        on="project_id",
        how="left"
    )

    # -----------------------------------------------------
    # Validate required ML score
    # -----------------------------------------------------

    if "ensemble_ml_risk" not in hybrid.columns:

        print("\nERROR: ensemble_ml_risk is missing.")

        print("\nAvailable columns:")
        print(hybrid.columns.tolist())

        return

    # -----------------------------------------------------
    # Calculate rule score
    # -----------------------------------------------------

    hybrid["rule_risk_score"] = hybrid.apply(
        calculate_rule_score,
        axis=1
    )

    # -----------------------------------------------------
    # Hybrid score
    # -----------------------------------------------------

    hybrid["hybrid_risk_score"] = (
        ML_WEIGHT * hybrid["ensemble_ml_risk"]
        + RULE_WEIGHT * hybrid["rule_risk_score"]
    )

    hybrid["hybrid_risk_score"] = hybrid[
        "hybrid_risk_score"
    ].round(2)

    # -----------------------------------------------------
    # Risk level
    # -----------------------------------------------------

    hybrid["hybrid_risk_level"] = hybrid[
        "hybrid_risk_score"
    ].apply(get_risk_level)

    # -----------------------------------------------------
    # Synthetic benchmark threshold
    #
    # Top 5% are flagged because the synthetic dataset
    # contains exactly 5% injected anomalies.
    # -----------------------------------------------------

    threshold = hybrid[
        "hybrid_risk_score"
    ].quantile(0.95)

    hybrid["hybrid_anomaly"] = (
        hybrid["hybrid_risk_score"] >= threshold
    ).astype(int)

    # -----------------------------------------------------
    # Explanation
    # -----------------------------------------------------

    def create_explanation(row):

        reasons = []

        if row.get("rule_excess_expenditure", 0):
            reasons.append(
                "expenditure exceeds sanction"
            )

        if row.get("rule_extreme_expenditure", 0):
            reasons.append(
                "expenditure >25% above sanction"
            )

        if row.get("rule_missing_uc", 0):
            reasons.append(
                "missing utilization certificate"
            )

        if row.get("rule_uc_mismatch", 0):
            reasons.append(
                "UC amount materially differs from expenditure"
            )

        if row.get("rule_delay", 0):
            reasons.append(
                "significant completion delay"
            )

        if row.get("rule_severe_delay", 0):
            reasons.append(
                "completion delay exceeds one year"
            )

        if row.get("rule_not_started", 0):
            reasons.append(
                "work not started"
            )

        if not reasons:
            reasons.append(
                "ML model identified an unusual project pattern"
            )

        return "; ".join(reasons)

    hybrid["hybrid_explanation"] = hybrid.apply(
        create_explanation,
        axis=1
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    hybrid.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\nHybrid Risk Engine")
    print("------------------")

    print(f"ML weight   : {ML_WEIGHT * 100:.0f}%")
    print(f"Rule weight : {RULE_WEIGHT * 100:.0f}%")

    print(
        f"Hybrid threshold: {threshold:.2f}"
    )

    print(
        f"Projects flagged: "
        f"{hybrid['hybrid_anomaly'].sum()}"
    )

    print("\nRisk distribution:")

    print(
        hybrid["hybrid_risk_level"]
        .value_counts()
        .reindex(
            ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            fill_value=0
        )
    )

    # -----------------------------------------------------
    # Top projects
    # -----------------------------------------------------

    print("\nTop 10 high-risk projects:")

    top = hybrid.sort_values(
        "hybrid_risk_score",
        ascending=False
    ).head(10)

    for _, row in top.iterrows():

        print(
            f"{row['project_id']} | "
            f"ML: {row['ensemble_ml_risk']:.2f} | "
            f"Rule: {row['rule_risk_score']:.2f} | "
            f"Hybrid: {row['hybrid_risk_score']:.2f} | "
            f"{row['hybrid_risk_level']}"
        )

    print(
        f"\nSaved: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()