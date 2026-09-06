import os
import sys
import pandas as pd
import numpy as np


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


RAW_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "mplads_real.csv"
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "real_mplads_normalized.csv"
)


def clean_number(value):
    """
    Convert financial values into numeric values.
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


def find_column(df, candidates):
    """
    Find the first matching source column.
    Matching is case-insensitive and whitespace-insensitive.
    """

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for candidate in candidates:

        key = candidate.strip().lower()

        if key in normalized:
            return normalized[key]

    return None


def clean_text_series(series):
    """
    Convert empty/string-null values to pandas NA.
    """

    result = (
        series
        .astype("string")
        .str.strip()
    )

    result = result.replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            "null": pd.NA
        }
    )

    return result


def main():

    print("=" * 60)
    print("SIH26102 REAL MPLADS DATA ADAPTER")
    print("=" * 60)

    if not os.path.exists(RAW_FILE):

        print("\nERROR:")
        print(
            f"Real data file not found:\n{RAW_FILE}"
        )

        print(
            "\nPlace the real MPLADS CSV inside:"
        )

        print(
            "data/raw/mplads_real.csv"
        )

        return

    print(
        f"\nLoading:\n{RAW_FILE}"
    )

    df = pd.read_csv(RAW_FILE)

    print(
        f"\nRows loaded: {len(df)}"
    )

    print("\nOriginal columns:")

    for column in df.columns:
        print(f"- {column}")

    # ---------------------------------------------------------
    # Detect source columns
    # ---------------------------------------------------------

    mappings = {

        "state": [
            "state"
        ],

        "district": [
            "district"
        ],

        "constituency": [
            "constituency"
        ],

        "actual_expenditure": [
            "actual_expenditure",
            "ActualExpenditureIncurred",
            "Actual Expenditure Incurred"
        ],

        "sanctioned_amount": [
            "sanctioned_amount",
            "WSCost",
            "WS Cost",
            "work sanctioned cost",
            "sanctioned cost"
        ],

        "work_status": [
            "work_status",
            "WorkStatus",
            "status",
            "Status"
        ],

        "implementing_agency": [
            "implementing_agency",
            "ImplementingAgency",
            "implementing agency"
        ],

        "uc_amount": [
            "uc_amount",
            "UCAmount",
            "utilization certificate amount",
            "utilization amount"
        ],

        "uc_available": [
            "uc_available",
            "UCAvailable",
            "utilization certificate available"
        ],

        "completion_delay_days": [
            "completion_delay_days",
            "CompletionDelayDays"
        ],

        "project_duration_days": [
            "project_duration_days",
            "ProjectDurationDays"
        ],

        "sector": [
            "sector",
            "Sector"
        ]
    }

    detected = {}

    print("\nColumn mapping:")

    for target, candidates in mappings.items():

        source = find_column(
            df,
            candidates
        )

        detected[target] = source

        if source:

            print(
                f"{target:25} <- {source}"
            )

        else:

            print(
                f"{target:25} <- NOT AVAILABLE"
            )

    # ---------------------------------------------------------
    # Create normalized dataframe
    # ---------------------------------------------------------

    normalized = pd.DataFrame(
        index=df.index
    )

    # ---------------------------------------------------------
    # Project ID
    # ---------------------------------------------------------

    normalized["project_id"] = [
        f"REAL-{i:06d}"
        for i in range(1, len(df) + 1)
    ]

    # ---------------------------------------------------------
    # Constituency/location fields
    # ---------------------------------------------------------

    for target in [
        "state",
        "district",
        "constituency"
    ]:

        source = detected[target]

        if source:

            normalized[target] = clean_text_series(
                df[source]
            )

        else:

            normalized[target] = pd.Series(
                pd.NA,
                index=df.index,
                dtype="string"
            )

    # ---------------------------------------------------------
    # Financial fields
    # ---------------------------------------------------------

    for target in [
        "sanctioned_amount",
        "actual_expenditure",
        "uc_amount"
    ]:

        source = detected[target]

        if source:

            normalized[target] = (
                df[source]
                .apply(clean_number)
            )

        else:

            normalized[target] = np.nan

    # ---------------------------------------------------------
    # UC availability
    # ---------------------------------------------------------

    source = detected["uc_available"]

    if source:

        values = (
            df[source]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        normalized["uc_available"] = (
            values.map(
                {
                    "true": True,
                    "yes": True,
                    "y": True,
                    "1": True,
                    "available": True,
                    "false": False,
                    "no": False,
                    "n": False,
                    "0": False,
                    "unavailable": False
                }
            )
        )

    else:

        # IMPORTANT:
        # Unknown is different from False.
        normalized["uc_available"] = pd.Series(
            pd.NA,
            index=df.index,
            dtype="boolean"
        )

    # ---------------------------------------------------------
    # Work status
    # ---------------------------------------------------------

    source = detected["work_status"]

    if source:

        normalized["work_status"] = clean_text_series(
            df[source]
        )

    else:

        normalized["work_status"] = pd.Series(
            pd.NA,
            index=df.index,
            dtype="string"
        )

    # ---------------------------------------------------------
    # Implementing agency
    # ---------------------------------------------------------

    source = detected["implementing_agency"]

    if source:

        normalized["implementing_agency"] = (
            clean_text_series(df[source])
        )

    else:

        normalized["implementing_agency"] = pd.Series(
            pd.NA,
            index=df.index,
            dtype="string"
        )

    # ---------------------------------------------------------
    # Sector
    # ---------------------------------------------------------

    source = detected["sector"]

    if source:

        normalized["sector"] = clean_text_series(
            df[source]
        )

    else:

        normalized["sector"] = pd.Series(
            pd.NA,
            index=df.index,
            dtype="string"
        )

    # ---------------------------------------------------------
    # Project duration
    # ---------------------------------------------------------

    source = detected["project_duration_days"]

    if source:

        normalized["project_duration_days"] = (
            df[source]
            .apply(clean_number)
        )

    else:

        normalized["project_duration_days"] = np.nan

    # ---------------------------------------------------------
    # Completion delay
    # ---------------------------------------------------------

    source = detected["completion_delay_days"]

    if source:

        normalized["completion_delay_days"] = (
            df[source]
            .apply(clean_number)
        )

    else:

        normalized["completion_delay_days"] = np.nan

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    normalized["data_source"] = "REAL_MPLADS"

    # Real data has no confirmed anomaly labels.
    normalized["ground_truth_available"] = False

    # ---------------------------------------------------------
    # Save normalized dataset
    # ---------------------------------------------------------

    normalized.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("NORMALIZATION COMPLETE")
    print("=" * 60)

    print(
        f"\nOutput rows: {len(normalized)}"
    )

    print(
        f"Output columns: {len(normalized.columns)}"
    )

    print("\nNormalized columns:")

    for column in normalized.columns:
        print(f"- {column}")

    print(
        f"\nSaved:\n{OUTPUT_FILE}"
    )

    # ---------------------------------------------------------
    # Accurate availability summary
    # ---------------------------------------------------------

    print("\nData availability:")

    for column in normalized.columns:

        if column in [
            "project_id",
            "data_source",
            "ground_truth_available"
        ]:
            continue

        available = normalized[column].notna().sum()

        print(
            f"{column:25} "
            f"{available}/{len(normalized)}"
        )

    # ---------------------------------------------------------
    # Real-data limitations
    # ---------------------------------------------------------

    print("\nReal-data limitations:")

    unavailable = [
        column
        for column in [
            "state",
            "district",
            "uc_amount",
            "uc_available",
            "work_status",
            "implementing_agency",
            "sector",
            "project_duration_days",
            "completion_delay_days"
        ]
        if normalized[column].notna().sum() == 0
    ]

    if unavailable:

        for column in unavailable:
            print(
                f"- {column}: unavailable in source"
            )

    print(
        "\nGround truth available: NO"
    )

    print(
        "Real records will be screened, "
        "not benchmarked against synthetic labels."
    )


if __name__ == "__main__":
    main()