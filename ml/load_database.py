import os
import sys

import pandas as pd

# ---------------------------------------------------------
# Add project root to Python path
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from database import SessionLocal
from db_models import Project


CSV_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "hybrid_risk_results.csv"
)


def clean_value(value):
    """
    Convert pandas NaN values to None.
    """
    if pd.isna(value):
        return None

    return value


def main():

    print("=" * 60)
    print("SIH26102 DATABASE LOADER")
    print("=" * 60)

    print("\nLoading HYBRID risk data into PostgreSQL...")

    df = pd.read_csv(CSV_FILE)

    print(
        f"Found {len(df)} projects in CSV."
    )

    print("\nCSV columns:")
    print(df.columns.tolist())

    # -----------------------------------------------------
    # Validate required hybrid columns
    # -----------------------------------------------------

    required_columns = [
        "project_id",
        "state_ml",
        "district_ml",
        "constituency_ml",
        "sanctioned_amount_ml",
        "actual_expenditure_ml",
        "expenditure_ratio",
        "completion_delay_days_ml",
        "uc_available_ml",
        "uc_amount_ml",
        "work_status",
        "sector",
        "implementing_agency",
        "ensemble_ml_risk",
        "rule_risk_score",
        "hybrid_risk_score",
        "hybrid_risk_level",
        "hybrid_explanation",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        print("\nERROR: Required columns are missing:")

        for column in missing:
            print(f"  - {column}")

        return

    # -----------------------------------------------------
    # Database session
    # -----------------------------------------------------

    db = SessionLocal()

    try:

        print("\nClearing existing project records...")

        db.query(Project).delete()

        db.commit()

        print("Existing project records cleared.")

        print("\nInserting hybrid risk projects...")

        inserted = 0

        for _, row in df.iterrows():

            project = Project(

                project_id=str(
                    row["project_id"]
                ),

                state=clean_value(
                    row["state_ml"]
                ),

                district=clean_value(
                    row["district_ml"]
                ),

                constituency=clean_value(
                    row["constituency_ml"]
                ),

                sanctioned_amount=clean_value(
                    row["sanctioned_amount_ml"]
                ),

                actual_expenditure=clean_value(
                    row["actual_expenditure_ml"]
                ),

                expenditure_ratio=clean_value(
                    row["expenditure_ratio"]
                ),

                completion_delay_days=clean_value(
                    row["completion_delay_days_ml"]
                ),

                work_status=clean_value(
                    row["work_status"]
                ),

                sector=clean_value(
                    row["sector"]
                ),

                implementing_agency=clean_value(
                    row["implementing_agency"]
                ),

                uc_available=bool(
                    row["uc_available_ml"]
                ),

                uc_amount=clean_value(
                    row["uc_amount_ml"]
                ),

                ml_risk_score=clean_value(
                    row["ensemble_ml_risk"]
                ),

                rule_risk_score=clean_value(
                    row["rule_risk_score"]
                ),

                risk_score=clean_value(
                    row["hybrid_risk_score"]
                ),

                risk_level=clean_value(
                    row["hybrid_risk_level"]
                ),

                risk_explanation=clean_value(
                    row["hybrid_explanation"]
                ),
            )

            db.add(project)

            inserted += 1

        db.commit()

        print(
            f"\nSuccessfully inserted "
            f"{inserted} projects."
        )

        # -------------------------------------------------
        # Verification
        # -------------------------------------------------

        total_projects = db.query(Project).count()

        critical = (
            db.query(Project)
            .filter(Project.risk_score >= 75)
            .count()
        )

        high = (
            db.query(Project)
            .filter(
                Project.risk_score >= 50,
                Project.risk_score < 75
            )
            .count()
        )

        medium = (
            db.query(Project)
            .filter(
                Project.risk_score >= 25,
                Project.risk_score < 50
            )
            .count()
        )

        low = (
            db.query(Project)
            .filter(Project.risk_score < 25)
            .count()
        )

        print("\nDatabase verification")
        print("---------------------")
        print(f"Total projects : {total_projects}")
        print(f"CRITICAL       : {critical}")
        print(f"HIGH           : {high}")
        print(f"MEDIUM         : {medium}")
        print(f"LOW            : {low}")

        print("\nDatabase load completed successfully.")

    except Exception as e:

        db.rollback()

        print("\nERROR while loading database:")
        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    main()