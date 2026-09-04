import pandas as pd
import numpy as np


# =========================================================
# 1. Convert ML anomaly score into 0-100 risk score
# =========================================================

def calculate_ml_risk(df):

    # Isolation Forest decision_function:
    # Higher = more normal
    # Lower  = more anomalous

    min_score = df["ml_anomaly_score"].min()
    max_score = df["ml_anomaly_score"].max()

    # Convert so that:
    # Most anomalous -> 100
    # Most normal    -> 0

    df["ml_risk_score"] = (
        (max_score - df["ml_anomaly_score"]) /
        (max_score - min_score)
    ) * 100

    return df


# =========================================================
# 2. Calculate rule-based risk
# =========================================================

def calculate_rule_risk(df):

    # Individual rule weights
    #
    # These are prototype weights.
    # They will be calibrated later using real MPLADS data
    # and official guidelines/audit evidence.

    df["rule_risk_score"] = (

        df["rule_excess_expenditure"] * 20 +

        df["rule_extreme_expenditure"] * 15 +

        df["rule_missing_uc"] * 15 +

        df["rule_uc_mismatch"] * 15 +

        df["rule_delay"] * 10 +

        df["rule_severe_delay"] * 15 +

        df["rule_not_started"] * 10
    )

    # Maximum possible score = 100

    df["rule_risk_score"] = df[
        "rule_risk_score"
    ].clip(upper=100)

    return df


# =========================================================
# 3. Hybrid risk score
# =========================================================

def calculate_hybrid_score(df):

    # ML contributes 50%
    # Rules contribute 50%

    df["risk_score"] = (
        0.50 * df["ml_risk_score"] +
        0.50 * df["rule_risk_score"]
    )

    # Keep between 0 and 100
    df["risk_score"] = df[
        "risk_score"
    ].clip(0, 100)

    return df


# =========================================================
# 4. Risk category
# =========================================================

def assign_risk_level(score):

    if score >= 75:
        return "CRITICAL"

    elif score >= 50:
        return "HIGH"

    elif score >= 25:
        return "MEDIUM"

    else:
        return "LOW"


# =========================================================
# 5. Generate explanation
# =========================================================

def generate_final_explanation(row):

    reasons = []

    # Financial
    if row["rule_extreme_expenditure"] == 1:
        reasons.append(
            "Expenditure is significantly above sanctioned amount"
        )

    elif row["rule_excess_expenditure"] == 1:
        reasons.append(
            "Expenditure exceeds sanctioned amount"
        )

    # UC
    if row["rule_missing_uc"] == 1:
        reasons.append(
            "Utilization Certificate is missing"
        )

    if row["rule_uc_mismatch"] == 1:
        reasons.append(
            "UC amount is inconsistent with expenditure"
        )

    # Delay
    if row["rule_severe_delay"] == 1:
        reasons.append(
            "Project has a severe completion delay"
        )

    elif row["rule_delay"] == 1:
        reasons.append(
            "Project has a significant completion delay"
        )

    # Project status
    if row["rule_not_started"] == 1:
        reasons.append(
            "Project has not started"
        )

    # ML
    if row["ml_risk_score"] >= 75:
        reasons.append(
            "ML model identifies the project as highly unusual"
        )

    if not reasons:
        return "No significant anomaly detected"

    return "; ".join(reasons)


# =========================================================
# 6. Main
# =========================================================

if __name__ == "__main__":

    print("\nLoading model results...")

    df = pd.read_csv(
        "data/ml_results.csv"
    )

    # -----------------------------------------------------
    # ML risk
    # -----------------------------------------------------

    df = calculate_ml_risk(df)

    # -----------------------------------------------------
    # Rule risk
    # -----------------------------------------------------

    # Load rule results
    rules_df = pd.read_csv(
        "data/rule_results.csv"
    )

    # Copy rule columns into main dataframe

    rule_columns = [
        "rule_excess_expenditure",
        "rule_extreme_expenditure",
        "rule_missing_uc",
        "rule_uc_mismatch",
        "rule_delay",
        "rule_severe_delay",
        "rule_not_started"
    ]

    for column in rule_columns:
        df[column] = rules_df[column]

    # -----------------------------------------------------
    # Calculate rule risk
    # -----------------------------------------------------

    df = calculate_rule_risk(df)

    # -----------------------------------------------------
    # Hybrid score
    # -----------------------------------------------------

    df = calculate_hybrid_score(df)

    # -----------------------------------------------------
    # Risk level
    # -----------------------------------------------------

    df["risk_level"] = df[
        "risk_score"
    ].apply(assign_risk_level)

    # -----------------------------------------------------
    # Explanation
    # -----------------------------------------------------

    df["risk_explanation"] = df.apply(
        generate_final_explanation,
        axis=1
    )

    # -----------------------------------------------------
    # Sort by highest risk
    # -----------------------------------------------------

    df = df.sort_values(
        "risk_score",
        ascending=False
    )

    # -----------------------------------------------------
    # Display
    # -----------------------------------------------------

    print("\n======================================")
    print("      MPLADS HYBRID RISK MODEL")
    print("======================================")

    print(
        "\nTotal Projects:",
        len(df)
    )

    print("\nRisk Distribution:")

    print(
        df["risk_level"]
        .value_counts()
        .to_string()
    )

    print("\nTop 15 High-Risk Projects:")

    display_columns = [
        "project_id",
        "ml_risk_score",
        "rule_risk_score",
        "risk_score",
        "risk_level",
        "risk_explanation"
    ]

    print(
        df[display_columns]
        .head(15)
        .to_string(index=False)
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    df.to_csv(
        "data/final_risk_results.csv",
        index=False
    )

    print(
        "\nFinal results saved to:"
        " data/final_risk_results.csv"
    )