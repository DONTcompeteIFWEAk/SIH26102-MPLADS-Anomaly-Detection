import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)

import pandas as pd

from database import SessionLocal
from db_models import Project


# CSV containing the new hybrid ML + rule risk results
CSV_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "hybrid_risk_results.csv"
)


def load_projects():

    print("Loading HYBRID risk data into PostgreSQL...")

    # Check if CSV exists
    if not os.path.exists(CSV_PATH):
        print("ERROR: CSV file not found:")
        print(CSV_PATH)
        return

    # Read CSV
    df = pd.read_csv(CSV_PATH)

    print(f"Found {len(df)} projects in CSV.")

    # Show columns for verification
    print("\nCSV columns:")
    print(list(df.columns))

    db = SessionLocal()

    try:

        # --------------------------------------------------
        # CLEAR OLD PROJECT DATA
        # --------------------------------------------------

        print("\nClearing existing project records...")

        db.query(Project).delete()

        # --------------------------------------------------
        # INSERT NEW HYBRID RESULTS
        # --------------------------------------------------

        print("Inserting hybrid risk projects...")

        for _, row in df.iterrows():

            project = Project(

                project_id=str(
                    row["project_id"]
                ),

                state=str(
                    row["state"]
                ),

                district=str(
                    row["district"]
                ),

                constituency=str(
                    row["constituency"]
                ),

                sanctioned_amount=float(
                    row["sanctioned_amount"]
                ),

                actual_expenditure=float(
                    row["actual_expenditure"]
                ),

                expenditure_ratio=float(
                    row["expenditure_ratio"]
                ),

                completion_delay_days=int(
                    row["completion_delay_days"]
                ),

                work_status=str(
                    row["work_status"]
                ),

                sector=str(
                    row["sector"]
                ),

                implementing_agency=str(
                    row["implementing_agency"]
                ),

                # PostgreSQL column is BOOLEAN
                uc_available=bool(
                    row["uc_available"]
                ),

                uc_amount=float(
                    row["uc_amount"]
                ),

                # --------------------------------------------------
                # NEW HYBRID RISK VALUES
                # --------------------------------------------------

                ml_risk_score=float(
                    row["ensemble_ml_risk"]
                ),

                rule_risk_score=float(
                    row["rule_risk_score"]
                ),

                risk_score=float(
                    row["hybrid_risk_score"]
                ),

                risk_level=str(
                    row["hybrid_risk_level"]
                ),

                risk_explanation=str(
                    row["hybrid_explanation"]
                )
            )

            db.add(project)

        # --------------------------------------------------
        # COMMIT
        # --------------------------------------------------

        db.commit()

        print()
        print("==============================================")
        print("HYBRID DATABASE LOADING COMPLETED!")
        print("==============================================")
        print(f"Successfully loaded {len(df)} projects.")
        print("Source:")
        print("data/hybrid_risk_results.csv")
        print("==============================================")

    except Exception as e:

        db.rollback()

        print()
        print("ERROR while loading database:")
        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    load_projects()