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


# CSV file containing final ML + rule risk results
CSV_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "final_risk_results.csv"
)


def load_projects():
    print("Loading data into PostgreSQL...")

    # Check if CSV exists
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: CSV file not found:")
        print(CSV_PATH)
        return

    # Read CSV
    df = pd.read_csv(CSV_PATH)

    print(f"Found {len(df)} projects in CSV.")

    db = SessionLocal()

    try:
        # Clear existing projects
        print("Clearing existing project records...")

        db.query(Project).delete()

        # Insert projects
        print("Inserting projects...")

        for _, row in df.iterrows():

            project = Project(
                project_id=str(row["project_id"]),
                state=str(row["state"]),
                district=str(row["district"]),
                constituency=str(row["constituency"]),

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

                uc_available=int(
                    row["uc_available"]
                ),

                uc_amount=float(
                    row["uc_amount"]
                ),

                ml_risk_score=float(
                    row["ml_risk_score"]
                ),

                rule_risk_score=float(
                    row["rule_risk_score"]
                ),

                risk_score=float(
                    row["risk_score"]
                ),

                risk_level=str(
                    row["risk_level"]
                ),

                risk_explanation=str(
                    row["risk_explanation"]
                )
            )

            db.add(project)

        # Save everything
        db.commit()

        print()
        print("===================================")
        print("Database loading completed!")
        print(f"Successfully loaded {len(df)} projects.")
        print("===================================")

    except Exception as e:

        db.rollback()

        print()
        print("ERROR while loading database:")
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    load_projects()