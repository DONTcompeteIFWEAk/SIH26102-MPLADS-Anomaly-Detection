import os
import json
import argparse
import pandas as pd


# ============================================================
# SIH26102 - MPLADS DATA VALIDATION
# ============================================================

REQUIRED_COLUMNS = [
    "project_id",
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

OPTIONAL_COLUMNS = [
    "project_duration_days",
]

NUMERIC_COLUMNS = [
    "sanctioned_amount",
    "actual_expenditure",
    "completion_delay_days",
    "uc_amount",
    "project_duration_days",
]

BOOLEAN_COLUMNS = [
    "uc_available",
]


# ============================================================
# COLUMN VALIDATION
# ============================================================

def validate_columns(df):
    """
    Check whether all required columns are present.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    return missing_columns


# ============================================================
# DUPLICATE VALIDATION
# ============================================================

def validate_duplicates(df):
    """
    Check duplicate project IDs.
    """

    duplicate_count = int(
        df["project_id"].duplicated().sum()
    )

    duplicate_ids = (
        df.loc[
            df["project_id"].duplicated(keep=False),
            "project_id"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return duplicate_count, duplicate_ids


# ============================================================
# MISSING VALUE VALIDATION
# ============================================================

def validate_missing_values(df):
    """
    Count missing values in important columns.
    """

    missing_values = {}

    for column in REQUIRED_COLUMNS:

        if column in df.columns:

            count = int(
                df[column].isna().sum()
            )

            if count > 0:
                missing_values[column] = count

    return missing_values


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def validate_numeric_columns(df):
    """
    Convert numeric fields to numeric values and detect
    invalid/non-numeric entries.
    """

    invalid_numeric = {}

    cleaned_df = df.copy()

    for column in NUMERIC_COLUMNS:

        if column not in cleaned_df.columns:
            continue

        original_values = cleaned_df[column].copy()

        cleaned_df[column] = pd.to_numeric(
            cleaned_df[column],
            errors="coerce"
        )

        invalid_mask = (
            original_values.notna()
            & cleaned_df[column].isna()
        )

        invalid_count = int(
            invalid_mask.sum()
        )

        if invalid_count > 0:

            invalid_numeric[column] = invalid_count

    return cleaned_df, invalid_numeric


# ============================================================
# NEGATIVE VALUE VALIDATION
# ============================================================

def validate_negative_values(df):
    """
    Negative financial or duration values are generally invalid.

    IMPORTANT:
    Expenditure greater than sanctioned amount is NOT treated
    as a validation error because it may represent a genuine
    anomaly that our risk engine should detect.
    """

    negative_values = {}

    for column in NUMERIC_COLUMNS:

        if column not in df.columns:
            continue

        count = int(
            (df[column] < 0).sum()
        )

        if count > 0:

            negative_values[column] = count

    return negative_values


# ============================================================
# BOOLEAN VALIDATION
# ============================================================

def validate_boolean_column(df):
    """
    Validate uc_available values.

    Accepted values:

    True / False
    1 / 0
    yes / no
    y / n
    true / false
    """

    if "uc_available" not in df.columns:

        return df, {}

    cleaned_df = df.copy()

    valid_true = {
        True,
        1,
        "1",
        "true",
        "True",
        "TRUE",
        "yes",
        "Yes",
        "YES",
        "y",
        "Y",
    }

    valid_false = {
        False,
        0,
        "0",
        "false",
        "False",
        "FALSE",
        "no",
        "No",
        "NO",
        "n",
        "N",
    }

    invalid_count = 0

    converted_values = []

    for value in cleaned_df["uc_available"]:

        if pd.isna(value):

            converted_values.append(pd.NA)

            continue

        if value in valid_true:

            converted_values.append(True)

        elif value in valid_false:

            converted_values.append(False)

        else:

            converted_values.append(pd.NA)

            invalid_count += 1

    cleaned_df["uc_available"] = pd.array(
        converted_values,
        dtype="boolean"
    )

    result = {}

    if invalid_count > 0:

        result["uc_available"] = int(
            invalid_count
        )

    return cleaned_df, result


# ============================================================
# WARNING GENERATION
# ============================================================

def generate_warnings(df):
    """
    Generate warnings for unusual but potentially valid records.

    These records are NOT rejected because they may represent
    anomalies that our ML/rule engine is designed to detect.
    """

    warnings = {}

    # --------------------------------------------------------
    # 1. EXPENDITURE ABOVE SANCTIONED AMOUNT
    # --------------------------------------------------------

    if {
        "sanctioned_amount",
        "actual_expenditure"
    }.issubset(df.columns):

        count = int(
            (
                df["actual_expenditure"]
                > df["sanctioned_amount"]
            ).sum()
        )

        if count > 0:

            warnings[
                "expenditure_above_sanctioned"
            ] = count

    # --------------------------------------------------------
    # 2. MATERIAL UC / EXPENDITURE DISCREPANCY
    # --------------------------------------------------------

    if {
        "uc_amount",
        "actual_expenditure"
    }.issubset(df.columns):

        valid_mask = (
            df["uc_amount"].notna()
            & df["actual_expenditure"].notna()
            & (df["actual_expenditure"] > 0)
        )

        discrepancy_pct = (
            (
                df["uc_amount"]
                - df["actual_expenditure"]
            ).abs()
            / df["actual_expenditure"]
        )

        # Only flag material discrepancies.
        # Prototype threshold = 20%.

        mismatch_count = int(
            (
                valid_mask
                & (discrepancy_pct > 0.20)
            ).sum()
        )

        if mismatch_count > 0:

            warnings[
                "material_uc_expenditure_mismatch"
            ] = mismatch_count

    # --------------------------------------------------------
    # 3. UC UNAVAILABLE BUT AMOUNT PRESENT
    # --------------------------------------------------------

    if {
        "uc_available",
        "uc_amount"
    }.issubset(df.columns):

        count = int(
            (
                (df["uc_available"] == False)
                & df["uc_amount"].notna()
                & (df["uc_amount"] != 0)
            ).sum()
        )

        if count > 0:

            warnings[
                "uc_unavailable_but_amount_present"
            ] = count

    # --------------------------------------------------------
    # 4. UC AVAILABLE BUT AMOUNT MISSING
    # --------------------------------------------------------

    if {
        "uc_available",
        "uc_amount"
    }.issubset(df.columns):

        count = int(
            (
                (df["uc_available"] == True)
                & df["uc_amount"].isna()
            ).sum()
        )

        if count > 0:

            warnings[
                "uc_available_but_amount_missing"
            ] = count

    # --------------------------------------------------------
    # 5. LONG PROJECT DELAY
    # --------------------------------------------------------

    if "completion_delay_days" in df.columns:

        count = int(
            (
                df["completion_delay_days"] > 180
            ).sum()
        )

        if count > 0:

            warnings[
                "delay_over_180_days"
            ] = count

    # --------------------------------------------------------
    # 6. MISSING PROJECT DURATION
    # --------------------------------------------------------

    if "project_duration_days" in df.columns:

        count = int(
            df["project_duration_days"].isna().sum()
        )

        if count > 0:

            warnings[
                "project_duration_missing"
            ] = count

    return warnings


# ============================================================
# JSON TYPE CONVERSION
# ============================================================

def convert_to_python(value):
    """
    Convert NumPy/Pandas values into native Python values
    so they can safely be saved as JSON.
    """

    if isinstance(value, dict):

        return {
            str(key): convert_to_python(val)
            for key, val in value.items()
        }

    if isinstance(value, list):

        return [
            convert_to_python(item)
            for item in value
        ]

    if hasattr(value, "item"):

        try:

            return value.item()

        except (ValueError, TypeError):

            pass

    return value


# ============================================================
# VALIDATION REPORT
# ============================================================

def create_validation_report(
    df,
    missing_columns,
    duplicate_count,
    duplicate_ids,
    missing_values,
    invalid_numeric,
    negative_values,
    invalid_boolean,
    warnings,
):
    """
    Create a structured validation report.
    """

    errors = []

    if missing_columns:

        errors.append(
            "Required columns are missing."
        )

    if duplicate_count > 0:

        errors.append(
            "Duplicate project IDs found."
        )

    if invalid_numeric:

        errors.append(
            "Invalid numeric values found."
        )

    if negative_values:

        errors.append(
            "Negative numeric values found."
        )

    if invalid_boolean:

        errors.append(
            "Invalid boolean values found."
        )

    report = {

        "validation_status": (
            "PASS"
            if len(errors) == 0
            else "REVIEW_REQUIRED"
        ),

        "total_records": int(
            len(df)
        ),

        "total_columns": int(
            len(df.columns)
        ),

        "required_columns": REQUIRED_COLUMNS,

        "optional_columns": OPTIONAL_COLUMNS,

        "missing_required_columns":
            missing_columns,

        "duplicate_project_count":
            int(duplicate_count),

        "duplicate_project_ids":
            duplicate_ids,

        "missing_values":
            missing_values,

        "invalid_numeric_values":
            invalid_numeric,

        "negative_values":
            negative_values,

        "invalid_boolean_values":
            invalid_boolean,

        "warnings":
            warnings,

        "errors":
            errors,

        "notes": [

            "Expenditure above sanctioned amount is treated as a warning, not a validation failure.",

            "Material UC mismatch is treated as a warning, not a validation failure.",

            "actual_anomaly is not required for production data.",

            "actual_anomaly is a synthetic ground-truth field used only for prototype evaluation.",

        ],
    }

    # Fix NumPy/Pandas values before JSON serialization.

    report = convert_to_python(
        report
    )

    return report


# ============================================================
# MAIN VALIDATION PIPELINE
# ============================================================

def validate_dataset(
    input_file,
    output_file,
    report_file
):

    print("=" * 60)
    print("SIH26102 MPLADS DATA VALIDATION")
    print("=" * 60)

    print(
        f"\nInput file : {input_file}"
    )

    print(
        f"Output file: {output_file}"
    )

    # --------------------------------------------------------
    # CHECK INPUT FILE
    # --------------------------------------------------------

    if not os.path.exists(input_file):

        print(
            "\nERROR: Input file does not exist."
        )

        return False

    # --------------------------------------------------------
    # LOAD DATASET
    # --------------------------------------------------------

    print(
        "\nLoading dataset..."
    )

    df = pd.read_csv(
        input_file
    )

    print(
        f"Loaded {len(df)} records "
        f"with {len(df.columns)} columns."
    )

    # --------------------------------------------------------
    # COLUMN VALIDATION
    # --------------------------------------------------------

    print(
        "\nChecking required columns..."
    )

    missing_columns = validate_columns(
        df
    )

    if missing_columns:

        print(
            "Missing columns:",
            missing_columns
        )

    else:

        print(
            "All required columns are present."
        )

    # --------------------------------------------------------
    # DUPLICATE VALIDATION
    # --------------------------------------------------------

    print(
        "\nChecking duplicate project IDs..."
    )

    if "project_id" in df.columns:

        (
            duplicate_count,
            duplicate_ids
        ) = validate_duplicates(
            df
        )

        print(
            f"Duplicate project records: "
            f"{duplicate_count}"
        )

    else:

        duplicate_count = 0

        duplicate_ids = []

    # --------------------------------------------------------
    # MISSING VALUE VALIDATION
    # --------------------------------------------------------

    print(
        "\nChecking missing values..."
    )

    missing_values = validate_missing_values(
        df
    )

    if missing_values:

        for column, count in missing_values.items():

            print(
                f"  {column}: {count}"
            )

    else:

        print(
            "No missing values found."
        )

    # --------------------------------------------------------
    # NUMERIC VALIDATION
    # --------------------------------------------------------

    print(
        "\nChecking numeric fields..."
    )

    (
        df,
        invalid_numeric
    ) = validate_numeric_columns(
        df
    )

    if invalid_numeric:

        for column, count in invalid_numeric.items():

            print(
                f"  {column}: "
                f"{count} invalid values"
            )

    else:

        print(
            "Numeric fields look valid."
        )

    # --------------------------------------------------------
    # NEGATIVE VALUE VALIDATION
    # --------------------------------------------------------

    print(
        "\nChecking negative values..."
    )

    negative_values = validate_negative_values(
        df
    )

    if negative_values:

        for column, count in negative_values.items():

            print(
                f"  {column}: "
                f"{count} negative values"
            )

    else:

        print(
            "No negative numeric values found."
        )

    # --------------------------------------------------------
    # BOOLEAN VALIDATION
    # --------------------------------------------------------

    print(
        "\nChecking UC boolean field..."
    )

    (
        df,
        invalid_boolean
    ) = validate_boolean_column(
        df
    )

    if invalid_boolean:

        for column, count in invalid_boolean.items():

            print(
                f"  {column}: "
                f"{count} invalid values"
            )

    else:

        print(
            "UC boolean values look valid."
        )

    # --------------------------------------------------------
    # GENERATE WARNINGS
    # --------------------------------------------------------

    print(
        "\nGenerating data-quality warnings..."
    )

    warnings = generate_warnings(
        df
    )

    if warnings:

        for warning, count in warnings.items():

            print(
                f"  {warning}: {count}"
            )

    else:

        print(
            "No unusual patterns found."
        )

    # --------------------------------------------------------
    # CREATE REPORT
    # --------------------------------------------------------

    report = create_validation_report(
        df=df,
        missing_columns=missing_columns,
        duplicate_count=duplicate_count,
        duplicate_ids=duplicate_ids,
        missing_values=missing_values,
        invalid_numeric=invalid_numeric,
        negative_values=negative_values,
        invalid_boolean=invalid_boolean,
        warnings=warnings,
    )

    # --------------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    output_directory = os.path.dirname(
        output_file
    )

    if output_directory:

        os.makedirs(
            output_directory,
            exist_ok=True
        )

    report_directory = os.path.dirname(
        report_file
    )

    if report_directory:

        os.makedirs(
            report_directory,
            exist_ok=True
        )

    # --------------------------------------------------------
    # SAVE VALIDATED DATASET
    # --------------------------------------------------------

    df.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # SAVE JSON REPORT
    # --------------------------------------------------------

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "VALIDATION SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        f"Status        : "
        f"{report['validation_status']}"
    )

    print(
        f"Records       : "
        f"{report['total_records']}"
    )

    print(
        f"Columns       : "
        f"{report['total_columns']}"
    )

    print(
        f"Duplicates    : "
        f"{duplicate_count}"
    )

    print(
        f"Warnings      : "
        f"{len(warnings)}"
    )

    print(
        "\nValidated data saved to:"
        f"\n{output_file}"
    )

    print(
        "\nValidation report saved to:"
        f"\n{report_file}"
    )

    print(
        "=" * 60
    )

    return True


# ============================================================
# COMMAND LINE ENTRY POINT
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Validate MPLADS project data "
            "before ML processing."
        )
    )

    parser.add_argument(
        "--input",
        default="data/synthetic_mplads.csv",
        help="Input CSV file",
    )

    parser.add_argument(
        "--output",
        default="data/validated_mplads.csv",
        help="Validated output CSV",
    )

    parser.add_argument(
        "--report",
        default="data/data_validation_report.json",
        help="Validation report JSON",
    )

    args = parser.parse_args()

    validate_dataset(
        input_file=args.input,
        output_file=args.output,
        report_file=args.report,
    )