import pandas as pd
import numpy as np
import os


# =========================================================
# SIH26102 - ENSEMBLE MODEL EVALUATION
# =========================================================

print("=" * 60)
print("SIH26102 ENSEMBLE MODEL EVALUATION")
print("=" * 60)


# ---------------------------------------------------------
# 1. LOAD RESULTS
# ---------------------------------------------------------

input_path = "data/ensemble_results.csv"

if not os.path.exists(input_path):

    print(
        f"\nERROR: Ensemble results not found:"
        f"\n{input_path}"
    )

    print(
        "\nRun:"
    )

    print(
        "python ml/ensemble_model.py"
    )

    raise SystemExit(1)


df = pd.read_csv(
    input_path
)


# ---------------------------------------------------------
# 2. CHECK GROUND TRUTH
# ---------------------------------------------------------

if "actual_anomaly" not in df.columns:

    print(
        "\nERROR: actual_anomaly column not found."
    )

    print(
        "\nThis evaluation requires the synthetic "
        "ground-truth labels."
    )

    raise SystemExit(1)


# ---------------------------------------------------------
# 3. IMPORT METRICS
# ---------------------------------------------------------

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ---------------------------------------------------------
# 4. ACTUAL + PREDICTED
# ---------------------------------------------------------

y_true = (
    df["actual_anomaly"]
    .astype(int)
)

y_pred = (
    df["ensemble_anomaly"]
    .astype(int)
)


# ---------------------------------------------------------
# 5. CALCULATE METRICS
# ---------------------------------------------------------

precision = precision_score(
    y_true,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0
)


# ---------------------------------------------------------
# 6. CONFUSION MATRIX
# ---------------------------------------------------------

tn, fp, fn, tp = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1]
).ravel()


# ---------------------------------------------------------
# 7. DISPLAY MAIN RESULTS
# ---------------------------------------------------------

print(
    "\n" + "-" * 60
)

print(
    "OVERALL PERFORMANCE"
)

print(
    "-" * 60
)

print(
    f"Total projects : {len(df)}"
)

print(
    f"Actual anomalies : {int(y_true.sum())}"
)

print(
    f"Predicted anomalies: {int(y_pred.sum())}"
)

print(
    f"\nTrue Positives  : {tp}"
)

print(
    f"False Positives : {fp}"
)

print(
    f"False Negatives : {fn}"
)

print(
    f"True Negatives  : {tn}"
)

print(
    f"\nPrecision : {precision:.4f}"
)

print(
    f"Recall    : {recall:.4f}"
)

print(
    f"F1 Score  : {f1:.4f}"
)


# ---------------------------------------------------------
# 8. CLASSIFICATION REPORT
# ---------------------------------------------------------

print(
    "\n" + "-" * 60
)

print(
    "CLASSIFICATION REPORT"
)

print(
    "-" * 60
)

print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "Normal",
            "Anomaly"
        ],
        zero_division=0
    )
)


# =========================================================
# 9. ANOMALY TYPE ANALYSIS
# =========================================================

print(
    "-" * 60
)

print(
    "ANOMALY TYPE DETECTION"
)

print(
    "-" * 60
)


# ---------------------------------------------------------
# Excess expenditure
# ---------------------------------------------------------

excess_mask = (
    df["actual_expenditure"]
    >
    df["sanctioned_amount"]
)

if excess_mask.sum() > 0:

    detected = int(
        (
            excess_mask
            &
            (df["ensemble_anomaly"] == 1)
        ).sum()
    )

    total = int(
        excess_mask.sum()
    )

    percentage = (
        detected / total
    ) * 100

    print(
        f"Excess expenditure : "
        f"{detected}/{total} "
        f"({percentage:.2f}%)"
    )


# ---------------------------------------------------------
# Large delay
# ---------------------------------------------------------

delay_mask = (
    df["completion_delay_days"]
    >= 300
)

if delay_mask.sum() > 0:

    detected = int(
        (
            delay_mask
            &
            (df["ensemble_anomaly"] == 1)
        ).sum()
    )

    total = int(
        delay_mask.sum()
    )

    percentage = (
        detected / total
    ) * 100

    print(
        f"Large delay        : "
        f"{detected}/{total} "
        f"({percentage:.2f}%)"
    )


# ---------------------------------------------------------
# Missing UC
# ---------------------------------------------------------

missing_uc_mask = (
    (
        df["uc_available"] == 0
    )
    &
    (
        df["actual_expenditure"] > 0
    )
)

if missing_uc_mask.sum() > 0:

    detected = int(
        (
            missing_uc_mask
            &
            (df["ensemble_anomaly"] == 1)
        ).sum()
    )

    total = int(
        missing_uc_mask.sum()
    )

    percentage = (
        detected / total
    ) * 100

    print(
        f"Missing UC         : "
        f"{detected}/{total} "
        f"({percentage:.2f}%)"
    )


# ---------------------------------------------------------
# UC mismatch
# ---------------------------------------------------------

uc_mismatch_mask = (
    (
        df["uc_available"] == 1
    )
    &
    (
        df["actual_expenditure"] > 0
    )
    &
    (
        (
            df["uc_amount"]
            -
            df["actual_expenditure"]
        ).abs()
        >
        (
            0.20
            *
            df["actual_expenditure"]
        )
    )
)

if uc_mismatch_mask.sum() > 0:

    detected = int(
        (
            uc_mismatch_mask
            &
            (df["ensemble_anomaly"] == 1)
        ).sum()
    )

    total = int(
        uc_mismatch_mask.sum()
    )

    percentage = (
        detected / total
    ) * 100

    print(
        f"UC mismatch       : "
        f"{detected}/{total} "
        f"({percentage:.2f}%)"
    )


# =========================================================
# 10. RISK LEVEL DISTRIBUTION
# =========================================================

print(
    "\n" + "-" * 60
)

print(
    "ENSEMBLE RISK DISTRIBUTION"
)

print(
    "-" * 60
)

risk_counts = (
    df["ensemble_risk_level"]
    .value_counts()
)

for level in [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW"
]:

    count = int(
        risk_counts.get(
            level,
            0
        )
    )

    print(
        f"{level:<10}: {count}"
    )


# =========================================================
# 11. TOP HIGH-RISK PROJECTS
# =========================================================

print(
    "\n" + "-" * 60
)

print(
    "TOP 10 HIGH-RISK PROJECTS"
)

print(
    "-" * 60
)


top_projects = (
    df.sort_values(
        "ensemble_ml_risk",
        ascending=False
    )
    .head(10)
)


display_columns = [
    "project_id",
    "actual_anomaly",
    "iforest_risk",
    "lof_risk",
    "ensemble_ml_risk",
    "ensemble_risk_level",
]


print(
    top_projects[
        display_columns
    ].to_string(
        index=False
    )
)


# =========================================================
# 12. INTERPRETATION
# =========================================================

print(
    "\n" + "=" * 60
)

print(
    "EVALUATION INTERPRETATION"
)

print(
    "=" * 60
)

print(
    "\nThese metrics are based ONLY on the synthetic"
    " ground-truth labels."
)

print(
    "They must NOT be presented as real-world MPLADS"
    " fraud-detection accuracy."
)

print(
    "\nThe ensemble combines:"
)

print(
    "  • Isolation Forest : 40%"
)

print(
    "  • LOF              : 60%"
)

print(
    "\nHigher ensemble risk means a stronger statistical"
    " anomaly pattern."
)

print(
    "It does NOT prove fraud or misconduct."
)

print(
    "=" * 60
)