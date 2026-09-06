import os
import pandas as pd
import numpy as np


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "mplads_real.csv"
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "real_financial_features.csv"
)


def clean_number(value):
    """
    Convert financial values to numeric.
    Handles commas, rupee symbols and blank values.
    """

    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    if value == "":
        return np.nan

    value = (
        value
        .replace(",", "")
        .replace("₹", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .strip()
    )

    try:
        return float(value)
    except ValueError:
        return np.nan


def main():

    print("=" * 60)
    print("SIH26102 REAL MPLADS FINANCIAL FEATURES")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load real data
    # ---------------------------------------------------------

    print("\nLoading real MPLADS data...")

    df = pd.read_csv(INPUT_FILE)

    print(
        f"Rows loaded: {len(df)}"
    )

    # ---------------------------------------------------------
    # Clean column names
    # ---------------------------------------------------------

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # ---------------------------------------------------------
    # Required source fields
    # ---------------------------------------------------------

    required_columns = [
        "MP Name",
        "Constituency",
        "Entitlement",
        "FundReceivedGOI",
        "AmountAvailable",
        "WorksRecommCost",
        "WSCost",
        "ActualExpenditureIncurred",
        "UtilizationOverRelease",
        "UnspentBalance",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        print("\nERROR: Required source columns missing:")

        for column in missing:
            print(f"- {column}")

        return

    # ---------------------------------------------------------
    # Clean financial columns
    # ---------------------------------------------------------

    financial_columns = [
        "Entitlement",
        "FundReceivedGOI",
        "AmountAvailable",
        "WorksRecommCost",
        "WSCost",
        "ActualExpenditureIncurred",
        "UtilizationOverRelease",
        "UnspentBalance",
    ]

    for column in financial_columns:

        df[column] = (
            df[column]
            .apply(clean_number)
        )

    # ---------------------------------------------------------
    # Create normalized output
    # ---------------------------------------------------------

    result = pd.DataFrame()

    result["project_id"] = [
        f"REAL-{i:06d}"
        for i in range(1, len(df) + 1)
    ]

    result["mp_name"] = (
        df["MP Name"]
        .astype("string")
        .str.strip()
    )

    result["constituency"] = (
        df["Constituency"]
        .astype("string")
        .str.strip()
    )

    result["entitlement"] = df["Entitlement"]

    result["fund_received"] = df["FundReceivedGOI"]

    result["amount_available"] = df["AmountAvailable"]

    result["works_recommended_cost"] = (
        df["WorksRecommCost"]
    )

    result["work_sanctioned_cost"] = (
        df["WSCost"]
    )

    result["actual_expenditure"] = (
        df["ActualExpenditureIncurred"]
    )

    result["utilization_over_release"] = (
        df["UtilizationOverRelease"]
    )

    result["unspent_balance"] = (
        df["UnspentBalance"]
    )

    # ---------------------------------------------------------
    # Financial derived features
    # ---------------------------------------------------------

    # Actual expenditure relative to sanctioned work cost
    result["expenditure_to_sanction_ratio"] = (
        result["actual_expenditure"]
        / result["work_sanctioned_cost"].replace(
            0,
            np.nan
        )
    )

    # Difference between actual expenditure and sanctioned cost
    result["expenditure_sanction_difference"] = (
        result["actual_expenditure"]
        - result["work_sanctioned_cost"]
    )

    # Percentage deviation from sanctioned work cost
    result["expenditure_deviation_pct"] = (
        result["expenditure_sanction_difference"]
        / result["work_sanctioned_cost"].replace(
            0,
            np.nan
        )
        * 100
    )

    # Actual expenditure relative to available funds
    result["expenditure_to_available_ratio"] = (
        result["actual_expenditure"]
        / result["amount_available"].replace(
            0,
            np.nan
        )
    )

    # Recommended cost vs sanctioned cost
    result["sanction_gap"] = (
        result["works_recommended_cost"]
        - result["work_sanctioned_cost"]
    )

    result["sanction_gap_pct"] = (
        result["sanction_gap"]
        / result["works_recommended_cost"].replace(
            0,
            np.nan
        )
        * 100
    )

    # Funds received vs entitlement
    result["fund_receipt_ratio"] = (
        result["fund_received"]
        / result["entitlement"].replace(
            0,
            np.nan
        )
    )

    # Available funds vs received funds
    result["available_to_received_ratio"] = (
        result["amount_available"]
        / result["fund_received"].replace(
            0,
            np.nan
        )
    )

    # Unspent funds relative to available amount
    result["unspent_ratio"] = (
        result["unspent_balance"]
        / result["amount_available"].replace(
            0,
            np.nan
        )
    )

    # Unspent percentage
    result["unspent_pct"] = (
        result["unspent_ratio"] * 100
    )

    # ---------------------------------------------------------
    # Financial screening signals
    # ---------------------------------------------------------

    # Expenditure greater than sanctioned work cost
    result["signal_excess_expenditure"] = (
        result["actual_expenditure"]
        > result["work_sanctioned_cost"]
    ).astype(int)

    # Expenditure more than 25% above sanctioned cost
    result["signal_extreme_expenditure"] = (
        result["actual_expenditure"]
        >
        result["work_sanctioned_cost"] * 1.25
    ).astype(int)

    # Very large expenditure deviation
    result["signal_severe_expenditure_deviation"] = (
        result["expenditure_deviation_pct"] > 50
    ).astype(int)

    # Actual expenditure exceeds currently available funds
    result["signal_expenditure_above_available"] = (
        result["actual_expenditure"]
        >
        result["amount_available"]
    ).astype(int)

    # Recommended work cost differs substantially
    # from sanctioned work cost
    result["signal_sanction_gap"] = (
        result["sanction_gap_pct"].abs() > 25
    ).astype(int)

    # High unspent balance
    result["signal_high_unspent_balance"] = (
        result["unspent_pct"] > 25
    ).astype(int)

    # ---------------------------------------------------------
    # Financial risk score
    # ---------------------------------------------------------

    result["financial_rule_score"] = (
        result["signal_excess_expenditure"] * 20
        +
        result["signal_extreme_expenditure"] * 20
        +
        result["signal_severe_expenditure_deviation"] * 20
        +
        result["signal_expenditure_above_available"] * 15
        +
        result["signal_sanction_gap"] * 10
        +
        result["signal_high_unspent_balance"] * 15
    )

    result["financial_rule_score"] = (
        result["financial_rule_score"]
        .clip(upper=100)
    )

    # ---------------------------------------------------------
    # Risk level
    # ---------------------------------------------------------

    def risk_level(score):

        if score >= 75:
            return "CRITICAL"

        elif score >= 50:
            return "HIGH"

        elif score >= 25:
            return "MEDIUM"

        return "LOW"

    result["financial_risk_level"] = (
        result["financial_rule_score"]
        .apply(risk_level)
    )

    # ---------------------------------------------------------
    # Explanation
    # ---------------------------------------------------------

    def explanation(row):

        reasons = []

        if row["signal_excess_expenditure"]:
            reasons.append(
                "actual expenditure exceeds sanctioned work cost"
            )

        if row["signal_extreme_expenditure"]:
            reasons.append(
                "expenditure >25% above sanctioned cost"
            )

        if row["signal_severe_expenditure_deviation"]:
            reasons.append(
                "expenditure deviation >50%"
            )

        if row["signal_expenditure_above_available"]:
            reasons.append(
                "expenditure exceeds available funds"
            )

        if row["signal_sanction_gap"]:
            reasons.append(
                "large gap between recommended and sanctioned cost"
            )

        if row["signal_high_unspent_balance"]:
            reasons.append(
                "high unspent balance"
            )

        if not reasons:
            reasons.append(
                "no major financial screening rule triggered"
            )

        return "; ".join(reasons)

    result["financial_explanation"] = (
        result.apply(
            explanation,
            axis=1
        )
    )

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    result["data_source"] = "REAL_MPLADS"
    result["ground_truth_available"] = False

    # ---------------------------------------------------------
    # Replace infinite values
    # ---------------------------------------------------------

    result = result.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINANCIAL FEATURE ENGINEERING COMPLETE")
    print("=" * 60)

    print(
        f"\nRecords: {len(result)}"
    )

    print(
        f"Columns: {len(result.columns)}"
    )

    print("\nFinancial screening signals:")

    signals = [
        "signal_excess_expenditure",
        "signal_extreme_expenditure",
        "signal_severe_expenditure_deviation",
        "signal_expenditure_above_available",
        "signal_sanction_gap",
        "signal_high_unspent_balance",
    ]

    for signal in signals:

        print(
            f"{signal:45} "
            f"{result[signal].sum()}"
        )

    print("\nFinancial risk distribution:")

    print(
        result["financial_risk_level"]
        .value_counts()
        .reindex(
            [
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW"
            ],
            fill_value=0
        )
    )

    print("\nTop 10 financially high-risk records:")

    top = (
        result
        .sort_values(
            "financial_rule_score",
            ascending=False
        )
        .head(10)
    )

    for _, row in top.iterrows():

        print(
            f"{row['project_id']} | "
            f"{row['constituency']} | "
            f"Score: {row['financial_rule_score']:.0f} | "
            f"{row['financial_risk_level']}"
        )

    print(
        f"\nSaved:\n{OUTPUT_FILE}"
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "These are financial screening signals "
        "from real MPLADS data."
    )

    print(
        "They are NOT confirmed fraud findings."
    )


if __name__ == "__main__":
    main()