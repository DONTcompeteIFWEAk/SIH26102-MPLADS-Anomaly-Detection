import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

print("=" * 60)
print("SIH26102 ML ENSEMBLE EVALUATION")
print("=" * 60)

# ---------------------------------------------------------
# LOAD RESULTS
# ---------------------------------------------------------

df = pd.read_csv("data/ensemble_results.csv")

print(f"\nTotal projects: {len(df)}")

# ---------------------------------------------------------
# GROUND TRUTH
# ---------------------------------------------------------

y_true = df["actual_anomaly"].astype(int)

# ---------------------------------------------------------
# ENSEMBLE PREDICTION
# ---------------------------------------------------------

y_pred = df["ensemble_anomaly"].astype(int)

# ---------------------------------------------------------
# COUNTS
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("ANOMALY COUNTS")
print("-" * 60)

print(f"Known synthetic anomalies : {y_true.sum()}")
print(f"Ensemble detected anomalies: {y_pred.sum()}")

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

print("                Predicted Normal   Predicted Anomaly")

print(
    f"Actual Normal       {cm[0][0]:>6}"
    f"              {cm[0][1]:>6}"
)

print(
    f"Actual Anomaly      {cm[1][0]:>6}"
    f"              {cm[1][1]:>6}"
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
        target_names=[
            "Normal",
            "Anomaly"
        ],
        zero_division=0
    )
)

# ---------------------------------------------------------
# ANOMALY TYPE
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
        ) > 0.20 *
        row["actual_expenditure"]
    ):
        return "UC Mismatch"

    return "Other Anomaly"


df["anomaly_type"] = df.apply(
    get_anomaly_type,
    axis=1
)

# ---------------------------------------------------------
# PERFORMANCE BY TYPE
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
        subset["ensemble_anomaly"] == 1
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
# DETECTION BREAKDOWN
# ---------------------------------------------------------

true_positives = df[
    (df["actual_anomaly"] == 1) &
    (df["ensemble_anomaly"] == 1)
]

false_positives = df[
    (df["actual_anomaly"] == 0) &
    (df["ensemble_anomaly"] == 1)
]

missed_anomalies = df[
    (df["actual_anomaly"] == 1) &
    (df["ensemble_anomaly"] == 0)
]

print("\n" + "-" * 60)
print("DETECTION BREAKDOWN")
print("-" * 60)

print(f"True positives  : {len(true_positives)}")
print(f"False positives : {len(false_positives)}")
print(f"Missed anomalies: {len(missed_anomalies)}")

# ---------------------------------------------------------
# TOP ENSEMBLE ANOMALIES
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("TOP 10 ENSEMBLE ANOMALIES")
print("-" * 60)

columns = [
    "project_id",
    "actual_anomaly",
    "anomaly_type",
    "iforest_risk",
    "lof_risk",
    "ensemble_ml_risk",
    "ensemble_risk_level"
]

columns = [
    col for col in columns
    if col in df.columns
]

print(
    df.sort_values(
        "ensemble_ml_risk",
        ascending=False
    )
    .head(10)[columns]
    .to_string(index=False)
)

# ---------------------------------------------------------
# SAVE EVALUATION
# ---------------------------------------------------------

df["ensemble_prediction_correct"] = (
    y_true == y_pred
)

df["ensemble_true_positive"] = (
    (y_true == 1) &
    (y_pred == 1)
).astype(int)

df["ensemble_false_positive"] = (
    (y_true == 0) &
    (y_pred == 1)
).astype(int)

df["ensemble_missed_anomaly"] = (
    (y_true == 1) &
    (y_pred == 0)
).astype(int)

output_path = "data/ensemble_evaluation_results.csv"

df.to_csv(
    output_path,
    index=False
)

print("\n" + "-" * 60)
print("Evaluation results saved to:")
print(output_path)
print("-" * 60)

print("\nEnsemble evaluation completed successfully.")