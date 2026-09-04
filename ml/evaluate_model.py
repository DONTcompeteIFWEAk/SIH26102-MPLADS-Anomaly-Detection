import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

print("=" * 60)
print("SIH26102 ML MODEL EVALUATION")
print("=" * 60)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

df = pd.read_csv("data/ml_results.csv")

print(f"\nTotal projects: {len(df)}")

# ---------------------------------------------------------
# GROUND TRUTH
# ---------------------------------------------------------

if "actual_anomaly" not in df.columns:
    raise ValueError(
        "actual_anomaly column not found."
    )

y_true = df["actual_anomaly"].astype(int)

# ---------------------------------------------------------
# ML PREDICTION
# ---------------------------------------------------------

if "ml_anomaly" not in df.columns:
    raise ValueError(
        "ml_anomaly column not found."
    )

y_pred = df["ml_anomaly"].astype(int)

# ---------------------------------------------------------
# ANOMALY COUNTS
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("ANOMALY COUNTS")
print("-" * 60)

print(
    f"Known synthetic anomalies : {y_true.sum()}"
)

print(
    f"ML detected anomalies     : {y_pred.sum()}"
)

# ---------------------------------------------------------
# PERFORMANCE
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
# CONFUSION MATRIX
# ---------------------------------------------------------

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1]
)

print("\n" + "-" * 60)
print("CONFUSION MATRIX")
print("-" * 60)

print(
    "                Predicted Normal   Predicted Anomaly"
)

print(
    f"Actual Normal       {cm[0][0]:>6}              {cm[0][1]:>6}"
)

print(
    f"Actual Anomaly      {cm[1][0]:>6}              {cm[1][1]:>6}"
)

# ---------------------------------------------------------
# CLASSIFICATION REPORT
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("CLASSIFICATION REPORT")
print("-" * 60)

print(
    classification_report(
        y_true,
        y_pred,
        target_names=["Normal", "Anomaly"],
        zero_division=0
    )
)

# ---------------------------------------------------------
# CREATE ANOMALY TYPE
# ---------------------------------------------------------

def get_anomaly_type(row):

    if row["actual_anomaly"] == 0:
        return "Normal"

    if (
        row["actual_expenditure"]
        > row["sanctioned_amount"]
    ):
        return "Excess Expenditure"

    if row["completion_delay_days"] >= 300:
        return "Large Delay"

    if row["missing_uc"] == 1:
        return "Missing UC"

    if (
        row["uc_available"] == 1
        and abs(
            row["uc_expenditure_difference"]
        ) > 0.20 * row["actual_expenditure"]
    ):
        return "UC Mismatch"

    return "Other Anomaly"


df["anomaly_type"] = df.apply(
    get_anomaly_type,
    axis=1
)

# ---------------------------------------------------------
# PERFORMANCE BY ANOMALY TYPE
# ---------------------------------------------------------

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

    detected = (
        subset["ml_anomaly"] == 1
    ).sum()

    missed = total - detected

    detection_rate = (
        detected / total
        if total > 0
        else 0
    )

    print(
        f"{anomaly_type:<22}"
        f" Total: {total:>3}"
        f"  Detected: {detected:>3}"
        f"  Missed: {missed:>3}"
        f"  Detection Rate: {detection_rate:.2%}"
    )

# ---------------------------------------------------------
# TRUE POSITIVES
# ---------------------------------------------------------

true_positives = df[
    (df["actual_anomaly"] == 1) &
    (df["ml_anomaly"] == 1)
]

# ---------------------------------------------------------
# FALSE POSITIVES
# ---------------------------------------------------------

false_positives = df[
    (df["actual_anomaly"] == 0) &
    (df["ml_anomaly"] == 1)
]

# ---------------------------------------------------------
# MISSED ANOMALIES
# ---------------------------------------------------------

missed_anomalies = df[
    (df["actual_anomaly"] == 1) &
    (df["ml_anomaly"] == 0)
]

print("\n" + "-" * 60)
print("DETECTION BREAKDOWN")
print("-" * 60)

print(
    f"True positives  : {len(true_positives)}"
)

print(
    f"False positives : {len(false_positives)}"
)

print(
    f"Missed anomalies: {len(missed_anomalies)}"
)

# ---------------------------------------------------------
# MISSED ANOMALIES
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("MISSED ANOMALIES")
print("-" * 60)

missed_columns = [
    "project_id",
    "anomaly_type",
    "ml_anomaly_score",
    "sanctioned_amount",
    "actual_expenditure",
    "completion_delay_days",
    "missing_uc",
    "uc_available",
    "uc_amount"
]

missed_columns = [
    col for col in missed_columns
    if col in df.columns
]

print(
    missed_anomalies[
        missed_columns
    ]
    .sort_values(
        "ml_anomaly_score",
        ascending=True
    )
    .to_string(index=False)
)

# ---------------------------------------------------------
# FALSE POSITIVES
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("TOP FALSE POSITIVES")
print("-" * 60)

print(
    false_positives[
        missed_columns
    ]
    .sort_values(
        "ml_anomaly_score",
        ascending=True
    )
    .head(10)
    .to_string(index=False)
)

# ---------------------------------------------------------
# TOP ANOMALIES
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("TOP 10 ML ANOMALIES")
print("-" * 60)

top_anomalies = (
    df
    .sort_values(
        "ml_anomaly_score",
        ascending=True
    )
    .head(10)
)

print(
    top_anomalies[
        missed_columns
    ]
    .to_string(index=False)
)

# ---------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------

evaluation_df = df.copy()

evaluation_df["evaluation_prediction"] = y_pred

evaluation_df["prediction_correct"] = (
    y_true == y_pred
)

evaluation_df["true_positive"] = (
    (y_true == 1) &
    (y_pred == 1)
).astype(int)

evaluation_df["false_positive"] = (
    (y_true == 0) &
    (y_pred == 1)
).astype(int)

evaluation_df["missed_anomaly"] = (
    (y_true == 1) &
    (y_pred == 0)
).astype(int)

output_path = "data/ml_evaluation_results.csv"

evaluation_df.to_csv(
    output_path,
    index=False
)

print("\n" + "-" * 60)
print("Evaluation results saved to:")
print(output_path)
print("-" * 60)

print("\nEvaluation completed successfully.")