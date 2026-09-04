import pandas as pd


# =========================================================
# Generate investigation recommendation
# =========================================================

def generate_action(row):

    actions = []

    # Financial verification
    if (
        row["rule_excess_expenditure"] == 1
        or row["rule_extreme_expenditure"] == 1
    ):
        actions.append(
            "Verify sanction, bills, vouchers and expenditure records"
        )

    # UC verification
    if (
        row["rule_missing_uc"] == 1
        or row["rule_uc_mismatch"] == 1
    ):
        actions.append(
            "Verify Utilization Certificate and supporting documents"
        )

    # Delay verification
    if (
        row["rule_delay"] == 1
        or row["rule_severe_delay"] == 1
    ):
        actions.append(
            "Verify project timeline and reasons for delay"
        )

    # Not started
    if row["rule_not_started"] == 1:
        actions.append(
            "Verify project commencement status through field records"
        )

    # ML anomaly
    if row["ml_risk_score"] >= 75:
        actions.append(
            "Perform additional verification because the project is statistically unusual"
        )

    if not actions:
        actions.append(
            "No immediate investigation action required"
        )

    return actions


# =========================================================
# Generate complete investigation report
# =========================================================

def generate_report(row):

    report = {
        "project_id": row["project_id"],
        "risk_score": round(row["risk_score"], 2),
        "risk_level": row["risk_level"],

        "ml_risk_score": round(
            row["ml_risk_score"], 2
        ),

        "rule_risk_score": round(
            row["rule_risk_score"], 2
        ),

        "anomaly_explanation":
            row["risk_explanation"],

        "recommended_actions":
            generate_action(row)
    }

    return report


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":

    # Load final risk results
    df = pd.read_csv(
        "data/final_risk_results.csv"
    )

    # Generate reports for high-risk projects
    high_risk = df[
        df["risk_score"] >= 50
    ].copy()

    print("\n======================================")
    print("       INVESTIGATION REPORTS")
    print("======================================")

    print(
        "\nProjects requiring attention:",
        len(high_risk)
    )

    # Generate reports
    reports = []

    for _, row in high_risk.iterrows():

        report = generate_report(row)

        reports.append(report)

    # -----------------------------------------------------
    # Display first 5 reports
    # -----------------------------------------------------

    for report in reports[:5]:

        print("\n--------------------------------------")

        print(
            f"Project: {report['project_id']}"
        )

        print(
            f"Risk Score: {report['risk_score']}"
        )

        print(
            f"Risk Level: {report['risk_level']}"
        )

        print(
            f"ML Risk: {report['ml_risk_score']}"
        )

        print(
            f"Rule Risk: {report['rule_risk_score']}"
        )

        print("\nWhy flagged:")

        print(
            report["anomaly_explanation"]
        )

        print("\nRecommended actions:")

        for action in report["recommended_actions"]:
            print(f"→ {action}")

    # -----------------------------------------------------
    # Save investigation data
    # -----------------------------------------------------

    investigation_df = pd.DataFrame({

        "project_id":
            [r["project_id"] for r in reports],

        "risk_score":
            [r["risk_score"] for r in reports],

        "risk_level":
            [r["risk_level"] for r in reports],

        "ml_risk_score":
            [r["ml_risk_score"] for r in reports],

        "rule_risk_score":
            [r["rule_risk_score"] for r in reports],

        "anomaly_explanation":
            [r["anomaly_explanation"] for r in reports],

        "recommended_actions":
            [
                " | ".join(r["recommended_actions"])
                for r in reports
            ]
    })

    investigation_df.to_csv(
        "data/investigation_queue.csv",
        index=False
    )

    print(
        "\nInvestigation queue saved to:"
        " data/investigation_queue.csv"
    )