import pandas as pd


INPUT_FILE = "data/processed_mplads.csv"
OUTPUT_FILE = "data/rule_results.csv"


def apply_rules(df):
    results = pd.DataFrame()
    results["project_id"] = df["project_id"]

    # ---------------------------------------------------------
    # CAG-inspired rule engine
    # ---------------------------------------------------------

    # 1. Expenditure exceeds sanctioned amount
    results["rule_excess_expenditure"] = (
        df["actual_expenditure"] > df["sanctioned_amount"]
    ).astype(int)

    # 2. Extreme expenditure deviation
    results["rule_extreme_expenditure"] = (
        df["actual_expenditure"]
        > df["sanctioned_amount"] * 1.25
    ).astype(int)

    # 3. Missing Utilization Certificate
    results["rule_missing_uc"] = (
        df["uc_available"] == False
    ).astype(int)

    # 4. UC amount does not reasonably match expenditure
    #
    # A UC is considered materially mismatched when:
    # - UC is available
    # - expenditure is greater than zero
    # - UC amount differs from expenditure by more than 25%
    #
    # This is a screening rule, NOT proof of irregularity.
    uc_difference_pct = (
        (df["uc_amount"] - df["actual_expenditure"]).abs()
        / df["actual_expenditure"].replace(0, pd.NA)
    )

    results["rule_uc_mismatch"] = (
        (df["uc_available"] == True)
        & (df["actual_expenditure"] > 0)
        & (uc_difference_pct > 0.25)
    ).astype(int)

    # 5. Significant delay
    results["rule_delay"] = (
        df["completion_delay_days"] > 180
    ).astype(int)

    # 6. Severe delay
    results["rule_severe_delay"] = (
        df["completion_delay_days"] > 365
    ).astype(int)

    # 7. Work not started
    results["rule_not_started"] = (
        df["work_status"]
        .astype(str)
        .str.lower()
        .isin(["not started", "not_started", "not-started"])
    ).astype(int)

    # ---------------------------------------------------------
    # Rule descriptions
    # ---------------------------------------------------------

    def get_rule_reasons(row):
        reasons = []

        if row["rule_excess_expenditure"]:
            reasons.append("expenditure exceeds sanction")

        if row["rule_extreme_expenditure"]:
            reasons.append(">25% above sanction")

        if row["rule_missing_uc"]:
            reasons.append("missing UC")

        if row["rule_uc_mismatch"]:
            reasons.append("UC amount materially differs from expenditure")

        if row["rule_delay"]:
            reasons.append("significant delay")

        if row["rule_severe_delay"]:
            reasons.append("delay > one year")

        if row["rule_not_started"]:
            reasons.append("work not started")

        return "; ".join(reasons)

    results["rule_violation_count"] = results[
        [
            "rule_excess_expenditure",
            "rule_extreme_expenditure",
            "rule_missing_uc",
            "rule_uc_mismatch",
            "rule_delay",
            "rule_severe_delay",
            "rule_not_started",
        ]
    ].sum(axis=1)

    results["rule_explanation"] = results.apply(
        get_rule_reasons,
        axis=1
    )

    # ---------------------------------------------------------
    # Preserve useful project metadata
    # ---------------------------------------------------------

    metadata_columns = [
        "state",
        "district",
        "constituency",
        "sanctioned_amount",
        "actual_expenditure",
        "completion_delay_days",
        "uc_available",
        "uc_amount",
        "work_status",
        "sector",
        "implementing_agency",
    ]

    for column in metadata_columns:
        if column in df.columns:
            results[column] = df[column].values

    return results


def main():
    print("Loading processed MPLADS data...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Total projects: {len(df)}")

    results = apply_rules(df)

    results.to_csv(OUTPUT_FILE, index=False)

    flagged = results[
        results["rule_violation_count"] > 0
    ]

    print("\nCAG Rule Engine Results")
    print("-----------------------")
    print(f"Total projects: {len(results)}")
    print(f"Projects with rule violations: {len(flagged)}")

    print("\nRule violation counts:")

    rule_columns = [
        "rule_excess_expenditure",
        "rule_extreme_expenditure",
        "rule_missing_uc",
        "rule_uc_mismatch",
        "rule_delay",
        "rule_severe_delay",
        "rule_not_started",
    ]

    for column in rule_columns:
        print(
            f"{column}: "
            f"{results[column].sum()}"
        )

    print("\nSample flagged projects:")

    sample = flagged.sort_values(
        "rule_violation_count",
        ascending=False
    ).head(10)

    for _, row in sample.iterrows():
        print(
            row["project_id"],
            row["rule_violation_count"],
            ":",
            row["rule_explanation"]
        )

    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()