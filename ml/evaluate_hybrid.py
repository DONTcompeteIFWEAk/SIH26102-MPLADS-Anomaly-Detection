import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# =========================================================
# SIH26102 - HYBRID MODEL EVALUATION
# ML Ensemble + CAG Rule Engine
# =========================================================


HYBRID_PATH = "data/hybrid_risk_results.csv"
GROUND_TRUTH_PATH = "data/processed_mplads.csv"
OUTPUT_PATH = "data/hybrid_evaluation_results.csv"


print("=" * 60)
print("SIH26102 HYBRID MODEL EVALUATION")
print("=" * 60)


# ---------------------------------------------------------
# 1. LOAD HYBRID RESULTS
# ---------------------------------------------------------

hybrid_df = pd.read_csv(
    HYBRID_PATH
)

print(
    f"\nHybrid projects: {len(hybrid_df)}"
)


# ---------------------------------------------------------
# 2. LOAD SYNTHETIC GROUND TRUTH
# ---------------------------------------------------------
#
# actual_anomaly is synthetic ground truth.
#
# IMPORTANT:
# This column is NOT used by the ML models or the hybrid
# risk calculation.
#
# It is used here ONLY to benchmark the system.
#
# ---------------------------------------------------------

truth_df = pd.read_csv(
    GROUND_TRUTH_PATH
)


if "actual_anomaly" not in truth_df.columns:

    print(
        "\nERROR: actual_anomaly not found in:"
    )

    print(
        GROUND_TRUTH_PATH
    )

    raise SystemExit(1)


# ---------------------------------------------------------
# 3. MERGE GROUND TRUTH
# ---------------------------------------------------------

truth_columns = [
    "project_id",
    "actual_anomaly"
]


if "anomaly_type" in truth_df.columns:

    truth_columns.append(
        "anomaly_type"
    )


truth = truth_df[
    truth_columns
].copy()


df = hybrid_df.merge(
    truth,
    on="project_id",
    how="inner"
)


print(
    f"Projects after ground-truth merge: {len(df)}"
)


# ---------------------------------------------------------
# 4. CHECK HYBRID COLUMNS
# ---------------------------------------------------------

required_columns = [

    "project_id",

    "actual_anomaly",

    "hybrid_anomaly",

    "hybrid_risk_score",

    "hybrid_risk_level",

    "ensemble_ml_risk",

    "rule_risk_score",

]


missing_columns = [

    column

    for column in required_columns

    if column not in df.columns

]


if missing_columns:

    print(
        "\nERROR: Required hybrid columns are missing:"
    )

    for column in missing_columns:

        print(
            f"  - {column}"
        )

    raise SystemExit(1)


# ---------------------------------------------------------
# 5. GROUND TRUTH / PREDICTIONS
# ---------------------------------------------------------

y_true = (
    df["actual_anomaly"]
    .astype(int)
)


y_pred = (
    df["hybrid_anomaly"]
    .astype(int)
)


# ---------------------------------------------------------
# 6. ANOMALY COUNTS
# ---------------------------------------------------------

actual_anomalies = int(
    y_true.sum()
)


predicted_anomalies = int(
    y_pred.sum()
)


print("\n" + "-" * 60)
print("ANOMALY COUNTS")
print("-" * 60)


print(
    f"Known synthetic anomalies : "
    f"{actual_anomalies}"
)


print(
    f"Hybrid flagged anomalies  : "
    f"{predicted_anomalies}"
)


# ---------------------------------------------------------
# 7. PERFORMANCE METRICS
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
print("HYBRID MODEL PERFORMANCE")
print("-" * 60)


print(
    f"Precision : {precision:.4f}"
)


print(
    f"Recall    : {recall:.4f}"
)


print(
    f"F1 Score  : {f1:.4f}"
)


# ---------------------------------------------------------
# 8. CONFUSION MATRIX
# ---------------------------------------------------------

tn, fp, fn, tp = confusion_matrix(
    y_true,
    y_pred
).ravel()


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
# 9. CLASSIFICATION REPORT
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
# 10. ANOMALY TYPE DETECTION
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("ANOMALY TYPE DETECTION")
print("-" * 60)


if "anomaly_type" in df.columns:

    anomaly_types = [

        "Excess Expenditure",

        "Large Delay",

        "Missing UC",

        "UC Mismatch",

    ]


    for anomaly_type in anomaly_types:

        subset = df[
            df["anomaly_type"]
            == anomaly_type
        ]


        total = len(subset)


        detected = int(
            subset["hybrid_anomaly"]
            .sum()
        )


        missed = (
            total
            - detected
        )


        detection_rate = (

            detected
            / total
            * 100

            if total > 0

            else 0

        )


        print(

            f"{anomaly_type:<20} : "
            f"{detected}/{total} "
            f"({detection_rate:.2f}%)"

        )


else:

    print(
        "anomaly_type unavailable."
    )


# ---------------------------------------------------------
# 11. DETECTION BREAKDOWN
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("DETECTION BREAKDOWN")
print("-" * 60)


print(
    f"True Positives  : {tp}"
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


# ---------------------------------------------------------
# 12. RISK DISTRIBUTION
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("HYBRID RISK DISTRIBUTION")
print("-" * 60)


distribution = (
    df["hybrid_risk_level"]
    .value_counts()
)


for level in [

    "CRITICAL",

    "HIGH",

    "MEDIUM",

    "LOW",

]:

    print(

        f"{level:<10}: "
        f"{int(distribution.get(level, 0))}"

    )


# ---------------------------------------------------------
# 13. TOP HIGH-RISK PROJECTS
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("TOP 15 HIGH-RISK PROJECTS")
print("-" * 60)


top_projects = (

    df.sort_values(

        "hybrid_risk_score",

        ascending=False

    )

    .head(15)

)


display_columns = [

    "project_id",

    "actual_anomaly",

]


if "anomaly_type" in df.columns:

    display_columns.append(
        "anomaly_type"
    )


display_columns.extend([

    "ensemble_ml_risk",

    "rule_risk_score",

    "hybrid_risk_score",

    "hybrid_risk_level",

    "hybrid_anomaly",

    "hybrid_explanation",

])


display_columns = [

    column

    for column in display_columns

    if column in df.columns

]


print(

    top_projects[
        display_columns
    ]

    .to_string(
        index=False
    )

)


# ---------------------------------------------------------
# 14. TOP FALSE POSITIVES
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("TOP FALSE POSITIVES")
print("-" * 60)


false_positives = df[

    (df["actual_anomaly"] == 0)

    &

    (df["hybrid_anomaly"] == 1)

].copy()


if len(false_positives) == 0:

    print(
        "No false positives."
    )

else:

    false_positives = (

        false_positives

        .sort_values(

            "hybrid_risk_score",

            ascending=False

        )

        .head(10)

    )


    print(

        false_positives[

            [

                "project_id",

                "ensemble_ml_risk",

                "rule_risk_score",

                "hybrid_risk_score",

                "hybrid_risk_level",

                "hybrid_explanation",

            ]

        ]

        .to_string(
            index=False
        )

    )


# ---------------------------------------------------------
# 15. MISSED ANOMALIES
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("MISSED ANOMALIES")
print("-" * 60)


missed = df[

    (df["actual_anomaly"] == 1)

    &

    (df["hybrid_anomaly"] == 0)

].copy()


if len(missed) == 0:

    print(
        "No anomalies were missed."
    )

else:

    missed = (

        missed

        .sort_values(

            "hybrid_risk_score",

            ascending=False

        )

    )


    display_columns = [

        "project_id",

    ]


    if "anomaly_type" in missed.columns:

        display_columns.append(
            "anomaly_type"
        )


    display_columns.extend([

        "ensemble_ml_risk",

        "rule_risk_score",

        "hybrid_risk_score",

        "hybrid_risk_level",

    ])


    print(

        missed[
            display_columns
        ]

        .to_string(
            index=False
        )

    )


# ---------------------------------------------------------
# 16. SAVE EVALUATION
# ---------------------------------------------------------

evaluation = pd.DataFrame({

    "metric": [

        "total_projects",

        "actual_anomalies",

        "predicted_anomalies",

        "true_positives",

        "false_positives",

        "false_negatives",

        "true_negatives",

        "precision",

        "recall",

        "f1_score",

    ],

    "value": [

        len(df),

        actual_anomalies,

        predicted_anomalies,

        tp,

        fp,

        fn,

        tn,

        precision,

        recall,

        f1,

    ]

})


evaluation.to_csv(
    OUTPUT_PATH,
    index=False
)


# ---------------------------------------------------------
# 17. FINAL OUTPUT
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("HYBRID MODEL EVALUATION COMPLETED")
print("=" * 60)


print(
    f"\nEvaluation results saved to:"
    f"\n{OUTPUT_PATH}"
)


print(
    "\nIMPORTANT:"
)


print(
    "These metrics are based ONLY on "
    "synthetic ground-truth labels."
)


print(
    "They must NOT be presented as "
    "real-world MPLADS fraud-detection accuracy."
)


print(
    "\nA high-risk score indicates a "
    "potential anomaly pattern requiring "
    "human/audit verification."
)


print("=" * 60)