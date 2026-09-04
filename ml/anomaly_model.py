import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

# -----------------------------------------
# 1. Load processed data
# -----------------------------------------

df = pd.read_csv("data/processed_mplads.csv")


# -----------------------------------------
# 2. Select ML features
# -----------------------------------------

features = [
    "sanctioned_amount",
    "actual_expenditure",
    "expenditure_ratio",
    "expenditure_difference",
    "completion_delay_days",
    "is_delayed",
    "severe_delay",
    "uc_available",
    "uc_amount",
    "uc_ratio",
    "uc_expenditure_difference",
    "missing_uc",
    "excess_expenditure",
    "extreme_expenditure"
]

X = df[features].copy()


# -----------------------------------------
# 3. Scale numerical features
# -----------------------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# -----------------------------------------
# 4. Create Isolation Forest
# -----------------------------------------

model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)


# -----------------------------------------
# 5. Train model
# -----------------------------------------

model.fit(X_scaled)


# -----------------------------------------
# 6. Predict anomalies
# -----------------------------------------

df["ml_prediction"] = model.predict(X_scaled)

df["ml_anomaly_score"] = model.decision_function(X_scaled)


# Isolation Forest:
# -1 = anomaly
#  1 = normal

df["ml_anomaly"] = (
    df["ml_prediction"] == -1
).astype(int)


# -----------------------------------------
# 7. Display results
# -----------------------------------------

print("\nML Model Results")
print("================")

print("\nTotal projects:", len(df))

print(
    "Anomalies detected:",
    df["ml_anomaly"].sum()
)

print(
    "Normal projects:",
    len(df) - df["ml_anomaly"].sum()
)


# Show most suspicious projects
print("\nTop 10 suspicious projects:")

result = df.sort_values(
    "ml_anomaly_score"
).head(10)

print(
    result[
        [
            "project_id",
            "sanctioned_amount",
            "actual_expenditure",
            "completion_delay_days",
            "missing_uc",
            "ml_anomaly_score",
            "ml_anomaly"
        ]
    ].to_string(index=False)
)


# -----------------------------------------
# 8. Save results
# -----------------------------------------

df.to_csv(
    "data/ml_results.csv",
    index=False
)


# -----------------------------------------
# 9. Save model and scaler
# -----------------------------------------
os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/isolation_forest.pkl"
)

joblib.dump(
    scaler,
    "models/scaler.pkl"
)


print("\nModel saved successfully!")
print("Results saved to: data/ml_results.csv")