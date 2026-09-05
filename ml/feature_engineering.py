import pandas as pd
import numpy as np


INPUT_FILE = "data/validated_mplads.csv"
OUTPUT_FILE = "data/processed_mplads.csv"


def main():

    print("=" * 60)
    print("SIH26102 FEATURE ENGINEERING")
    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    print(f"\nLoaded records: {len(df)}")

    # ---------------------------------------------------------
    # Preserve synthetic ground truth
    # ---------------------------------------------------------
    #
    # These columns are ONLY for evaluation.
    # They are NOT used as ML features.
    #

    ground_truth_columns = []

    if "actual_anomaly" in df.columns:
        ground_truth_columns.append("actual_anomaly")

    if "anomaly_type" in df.columns:
        ground_truth_columns.append("anomaly_type")

    # ---------------------------------------------------------
    # Basic numerical features
    # ---------------------------------------------------------

    df["expenditure_ratio"] = (
        df["actual_expenditure"]
        / df["sanctioned_amount"].replace(0, np.nan)
    ).fillna(0)

    df["expenditure_difference"] = (
        df["actual_expenditure"]
        - df["sanctioned_amount"]
    )

    df["expenditure_deviation_pct"] = (
        df["expenditure_difference"]
        / df["sanctioned_amount"].replace(0, np.nan)
        * 100
    ).fillna(0)

    df["absolute_expenditure_deviation_pct"] = (
        df["expenditure_deviation_pct"].abs()
    )

    # ---------------------------------------------------------
    # UC features
    # ---------------------------------------------------------

    df["uc_expenditure_difference"] = (
        df["uc_amount"]
        - df["actual_expenditure"]
    )

    df["uc_ratio"] = (
        df["uc_amount"]
        / df["actual_expenditure"].replace(0, np.nan)
    ).fillna(0)

    df["uc_discrepancy_pct"] = (
        (
            df["uc_amount"]
            - df["actual_expenditure"]
        ).abs()
        / df["actual_expenditure"].replace(0, np.nan)
        * 100
    ).fillna(0)

    df["uc_mismatch"] = (
        (
            df["uc_available"] == True
        )
        &
        (
            df["actual_expenditure"] > 0
        )
        &
        (
            df["uc_discrepancy_pct"] > 25
        )
    ).astype(int)

    df["missing_uc"] = (
        df["uc_available"] == False
    ).astype(int)

    # ---------------------------------------------------------
    # Delay features
    # ---------------------------------------------------------

    df["is_delayed"] = (
        df["completion_delay_days"] > 180
    ).astype(int)

    df["severe_delay"] = (
        df["completion_delay_days"] > 365
    ).astype(int)

    df["extreme_delay"] = (
        df["completion_delay_days"] > 730
    ).astype(int)

    df["delay_to_duration_ratio"] = (
        df["completion_delay_days"]
        / df["project_duration_days"].replace(0, np.nan)
    ).fillna(0)

    # ---------------------------------------------------------
    # Financial velocity features
    # ---------------------------------------------------------

    df["expenditure_per_duration_day"] = (
        df["actual_expenditure"]
        / df["project_duration_days"].replace(0, np.nan)
    ).fillna(0)

    df["total_elapsed_days"] = (
        df["project_duration_days"]
        + df["completion_delay_days"]
    )

    df["expenditure_per_elapsed_day"] = (
        df["actual_expenditure"]
        / df["total_elapsed_days"].replace(0, np.nan)
    ).fillna(0)

    # ---------------------------------------------------------
    # Rule-oriented derived signals
    # ---------------------------------------------------------

    df["excess_expenditure"] = (
        df["actual_expenditure"]
        > df["sanctioned_amount"]
    ).astype(int)

    df["extreme_expenditure"] = (
        df["actual_expenditure"]
        > df["sanctioned_amount"] * 1.25
    ).astype(int)

    df["very_high_expenditure"] = (
        df["actual_expenditure"]
        > df["sanctioned_amount"] * 1.50
    ).astype(int)

    df["delay_and_expenditure_risk"] = (
        (
            df["completion_delay_days"] > 180
        )
        &
        (
            df["actual_expenditure"]
            > df["sanctioned_amount"]
        )
    ).astype(int)

    df["missing_uc_high_expenditure"] = (
        (
            df["uc_available"] == False
        )
        &
        (
            df["actual_expenditure"]
            > df["sanctioned_amount"]
        )
    ).astype(int)

    # ---------------------------------------------------------
    # Save processed dataset
    # ---------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("\nFeature engineering completed.")

    print(
        f"Total columns: {len(df.columns)}"
    )

    print("\nCreated features:")

    feature_columns = [
        "expenditure_ratio",
        "expenditure_difference",
        "expenditure_deviation_pct",
        "absolute_expenditure_deviation_pct",
        "uc_expenditure_difference",
        "uc_ratio",
        "uc_discrepancy_pct",
        "uc_mismatch",
        "missing_uc",
        "is_delayed",
        "severe_delay",
        "extreme_delay",
        "delay_to_duration_ratio",
        "expenditure_per_duration_day",
        "total_elapsed_days",
        "expenditure_per_elapsed_day",
        "excess_expenditure",
        "extreme_expenditure",
        "very_high_expenditure",
        "delay_and_expenditure_risk",
        "missing_uc_high_expenditure",
    ]

    for feature in feature_columns:
        if feature in df.columns:
            print(
                f"{feature}: {df[feature].sum()}"
                if df[feature].dtype != "float64"
                else f"{feature}: created"
            )

    # ---------------------------------------------------------
    # Ground truth confirmation
    # ---------------------------------------------------------

    print("\nEvaluation columns preserved:")

    for column in ground_truth_columns:
        print(f"- {column}")

    print(
        f"\nSaved: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()