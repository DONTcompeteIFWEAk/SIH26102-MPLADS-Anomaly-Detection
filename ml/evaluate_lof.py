import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# =========================================================
# SIH26102 - LOF MODEL EVALUATION
# =========================================================


input_path = "data/lof_results.csv"

df = pd.read_csv(input_path)

print("=" * 60)
print("SIH26102 LOF MODEL EVALUATION")
print("=" * 60)


# ---------------------------------------------------------
# 1. BASIC INFORMATION
# ---------------------------------------------------------

print(f"\nTotal projects: {len(df)}")


# ---------------------------------------------------------
# 2. CHECK REQUIRED COLUMNS
# ---------------------------------------------------------

required_columns = [
    "actual_anomaly",
    "lof_anomaly",
    "lof_score",
    "project_id"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("\nERROR: Required columns are missing:")

    for column in missing_columns:
        print(f"  - {column}")

    raise SystemExit(1)


# ---------------------------------------------------------
# 3. GROUND TRUTH
# ---------------------------------------------------------

y_true = df["actual_anomaly"].astype(int)

y_pred = df["lof_anomaly"].astype(int)


# ---------------------------------------------------------
# 4. ANOMALY COUNTS
# ---------------------------------------------------------

known_anomalies = int(y_true.sum())

detected_anomalies = int(y_pred.sum())

print("\n" + "-" * 60)
print("ANOMALY COUNTS")
print("-" * 60)

print(
    f"Known synthetic anomalies : {known_anomalies}"
)

print(
    f"LOF detected anomalies     : {detected_anomalies}"
)


# ---------------------------------------------------------
# 5. PERFORMANCE METRICS
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


print("\n" + "-" * 60)
print("MODEL PERFORMANCE")
print("-" * 60)

print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")


# ---------------------------------------------------------
# 6. CONFUSION MATRIX
# ---------------------------------------------------------

cm = confusion_matrix(
    y_true,
    y_pred
)

tn, fp, fn, tp = cm.ravel()


print("\n" + "-" * 60)
print("CONFUSION MATRIX")
print("-" * 60)

print(
    "                Predicted Normal   "
    "Predicted Anomaly"
)

print(
    f"Actual Normal        {tn:6d}              {fp:6d}"
)

print(
    f"Actual Anomaly      {fn:6d}              {tp:6d}"
)


# ---------------------------------------------------------
# 7. CLASSIFICATION REPORT
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("CLASSIFICATION REPORT")
print("-" * 60)

print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "Normal",
            "Anomaly"
        ],
        digits=2,
        zero_division=0
    )
)


# ---------------------------------------------------------
# 8. PERFORMANCE BY ANOMALY TYPE
# ---------------------------------------------------------
#
# actual_anomaly_type is expected from the synthetic
# dataset/evaluation pipeline.
#
# If it is not available, we skip this section safely.
#
# ---------------------------------------------------------

if "anomaly_type" in df.columns:

    print("\n" + "-" * 60)
    print("PERFORMANCE BY ANOMALY TYPE")
    print("-" * 60)

    anomaly_types = [
        "Excess Expenditure",
        "Large Delay",
        "Missing UC",
        "UC Mismatch"
    ]

    for anomaly_type in anomaly_types:

        subset = df[
            df["anomaly_type"] == anomaly_type
        ]

        total = len(subset)

        detected = int(
            subset["lof_anomaly"].sum()
        )

        missed = total - detected

        if total > 0:
            detection_rate = (
                detected / total
            ) * 100
        else:
            detection_rate = 0

        print(
            f"{anomaly_type:<24}"
            f"Total: {total:3d}  "
            f"Detected: {detected:3d}  "
            f"Missed: {missed:3d}  "
            f"Detection Rate: "
            f"{detection_rate:6.2f}%"
        )


# ---------------------------------------------------------
# 9. DETECTION BREAKDOWN
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("DETECTION BREAKDOWN")
print("-" * 60)

print(
    f"True positives  : {tp}"
)

print(
    f"False positives : {fp}"
)

print(
    f"Missed anomalies: {fn}"
)


# ---------------------------------------------------------
# 10. MISSED ANOMALIES
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("MISSED ANOMALIES")
print("-" * 60)

missed = df[
    (df["actual_anomaly"] == 1)
    &
    (df["lof_anomaly"] == 0)
].copy()


if len(missed) == 0:

    print("No anomalies were missed.")

else:

    missed = missed.sort_values(
        "lof_score",
        ascending=False
    )

    display_columns = [
        "project_id"
    ]

    if "anomaly_type" in missed.columns:
        display_columns.append(
            "anomaly_type"
        )

    display_columns.extend([
        "lof_score",
        "sanctioned_amount",
        "actual_expenditure",
        "completion_delay_days",
        "missing_uc",
        "uc_available",
        "uc_amount"
    ])

    display_columns = [
        column
        for column in display_columns
        if column in missed.columns
    ]

    print(
        missed[
            display_columns
        ].to_string(index=False)
    )


# ---------------------------------------------------------
# 11. TOP FALSE POSITIVES
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("TOP FALSE POSITIVES")
print("-" * 60)

false_positives = df[
    (df["actual_anomaly"] == 0)
    &
    (df["lof_anomaly"] == 1)
].copy()


if len(false_positives) == 0:

    print("No false positives.")

else:

    false_positives = false_positives.sort_values(
        "lof_score",
        ascending=True
    ).head(10)

    display_columns = [
        "project_id"
    ]

    if "anomaly_type" in false_positives.columns:
        display_columns.append(
            "anomaly_type"
        )

    display_columns.extend([
        "lof_score",
        "sanctioned_amount",
        "actual_expenditure",
        "completion_delay_days",
        "missing_uc",
        "uc_available",
        "uc_amount"
    ])

    display_columns = [
        column
        for column in display_columns
        if column in false_positives.columns
    ]

    print(
        false_positives[
            display_columns
        ].to_string(index=False)
    )


# ---------------------------------------------------------
# 12. TOP LOF ANOMALIES
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("TOP 10 LOF ANOMALIES")
print("-" * 60)

top_anomalies = df.sort_values(
    "lof_score",
    ascending=True
).head(10)


display_columns = [
    "project_id"
]

if "anomaly_type" in top_anomalies.columns:
    display_columns.append(
        "anomaly_type"
    )

display_columns.extend([
    "lof_score",
    "sanctioned_amount",
    "actual_expenditure",
    "completion_delay_days",
    "missing_uc",
    "uc_available",
    "uc_amount"
])

display_columns = [
    column
    for column in display_columns
    if column in top_anomalies.columns
]

print(
    top_anomalies[
        display_columns
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 13. SAVE EVALUATION RESULTS
# ---------------------------------------------------------

evaluation = pd.DataFrame({

    "metric": [
        "total_projects",
        "known_anomalies",
        "detected_anomalies",
        "true_positives",
        "false_positives",
        "missed_anomalies",
        "true_negatives",
        "precision",
        "recall",
        "f1_score"
    ],

    "value": [
        len(df),
        known_anomalies,
        detected_anomalies,
        tp,
        fp,
        fn,
        tn,
        precision,
        recall,
        f1
    ]

})


evaluation.to_csv(
    "data/lof_evaluation_results.csv",
    index=False
)


print("\n" + "-" * 60)
print("Evaluation results saved to:")
print("data/lof_evaluation_results.csv")
print("-" * 60)

print("\nEvaluation completed successfully.")