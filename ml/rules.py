import pandas as pd


def apply_rules(df):
    """
    Apply domain-specific MPLADS anomaly rules.

    Each rule produces:
    1. A binary flag (0/1)
    2. A human-readable explanation
    """

    # --------------------------------------------------
    # Rule 1: Excess expenditure
    # --------------------------------------------------

    df["rule_excess_expenditure"] = (
        df["actual_expenditure"] >
        df["sanctioned_amount"]
    ).astype(int)

    # --------------------------------------------------
    # Rule 2: Extreme expenditure
    # --------------------------------------------------

    df["rule_extreme_expenditure"] = (
        df["expenditure_ratio"] > 1.25
    ).astype(int)

    # --------------------------------------------------
    # Rule 3: Missing Utilization Certificate
    # --------------------------------------------------

    df["rule_missing_uc"] = (
        (df["uc_available"] == 0) &
        (df["actual_expenditure"] > 0)
    ).astype(int)

    # --------------------------------------------------
    # Rule 4: UC / expenditure mismatch
    # --------------------------------------------------

    df["rule_uc_mismatch"] = (
        (
            df["uc_expenditure_difference"] >
            df["actual_expenditure"] * 0.20
        ) &
        (df["uc_available"] == 1)
    ).astype(int)

    # --------------------------------------------------
    # Rule 5: Significant delay
    # --------------------------------------------------

    df["rule_delay"] = (
        df["completion_delay_days"] > 180
    ).astype(int)

    # --------------------------------------------------
    # Rule 6: Severe delay
    # --------------------------------------------------

    df["rule_severe_delay"] = (
        df["completion_delay_days"] > 365
    ).astype(int)

    # --------------------------------------------------
    # Rule 7: Not Started despite elapsed duration
    # --------------------------------------------------

    df["rule_not_started"] = (
        df["work_status"] == "Not Started"
    ).astype(int)

    # --------------------------------------------------
    # Count total rule violations
    # --------------------------------------------------

    rule_columns = [
        "rule_excess_expenditure",
        "rule_extreme_expenditure",
        "rule_missing_uc",
        "rule_uc_mismatch",
        "rule_delay",
        "rule_severe_delay",
        "rule_not_started"
    ]

    df["total_rule_violations"] = df[rule_columns].sum(axis=1)

    return df


# ------------------------------------------------------
# Generate explanations
# ------------------------------------------------------

def generate_explanation(row):

    reasons = []

    if row["rule_excess_expenditure"] == 1:
        reasons.append(
            "Expenditure exceeds sanctioned amount"
        )

    if row["rule_extreme_expenditure"] == 1:
        reasons.append(
            "Expenditure is more than 25% above sanction"
        )

    if row["rule_missing_uc"] == 1:
        reasons.append(
            "Utilization Certificate is missing"
        )

    if row["rule_uc_mismatch"] == 1:
        reasons.append(
            "UC amount differs significantly from expenditure"
        )

    if row["rule_delay"] == 1:
        reasons.append(
            "Project completion is significantly delayed"
        )

    if row["rule_severe_delay"] == 1:
        reasons.append(
            "Project delay exceeds one year"
        )

    if row["rule_not_started"] == 1:
        reasons.append(
            "Project has not started"
        )

    if not reasons:
        return "No rule-based anomaly detected"

    return "; ".join(reasons)


# ------------------------------------------------------
# Main
# ------------------------------------------------------

if __name__ == "__main__":

    # Load processed dataset
    df = pd.read_csv(
        "data/processed_mplads.csv"
    )

    # Apply rules
    df = apply_rules(df)

    # Generate explanations
    df["rule_explanation"] = df.apply(
        generate_explanation,
        axis=1
    )

    # Display summary
    print("\nCAG Rule Engine Results")
    print("=======================")

    print(
        "\nTotal projects:",
        len(df)
    )

    print(
        "Projects with rule violations:",
        (df["total_rule_violations"] > 0).sum()
    )

    print("\nRule violation counts:")

    for column in [
        "rule_excess_expenditure",
        "rule_extreme_expenditure",
        "rule_missing_uc",
        "rule_uc_mismatch",
        "rule_delay",
        "rule_severe_delay",
        "rule_not_started"
    ]:
        print(
            f"{column}: {df[column].sum()}"
        )

    # Show projects with violations
    print("\nSample flagged projects:")

    flagged = df[
        df["total_rule_violations"] > 0
    ].sort_values(
        "total_rule_violations",
        ascending=False
    ).head(10)

    print(
        flagged[
            [
                "project_id",
                "total_rule_violations",
                "rule_explanation"
            ]
        ].to_string(index=False)
    )

    # Save results
    df.to_csv(
        "data/rule_results.csv",
        index=False
    )

    print(
        "\nRule results saved to: "
        "data/rule_results.csv"
    )