from sqlalchemy import text

from database import engine
from db_models import Base


def add_missing_columns():
    """
    Add columns that were introduced into the SQLAlchemy models
    after the PostgreSQL database was originally created.
    """

    with engine.begin() as connection:

        # -------------------------------------------------
        # PROJECTS TABLE
        # -------------------------------------------------

        connection.execute(
            text(
                """
                ALTER TABLE projects
                ADD COLUMN IF NOT EXISTS project_duration_days INTEGER
                """
            )
        )

        # -------------------------------------------------
        # WORK INVESTIGATIONS TABLE
        # -------------------------------------------------

        # create_all() handles the complete new table.
        Base.metadata.create_all(bind=engine)


if __name__ == "__main__":

    print("Updating database schema...")

    add_missing_columns()

    print("Database schema updated successfully.")
    print("Existing project data was preserved.")
    print("project_duration_days column is ready.")
    print("Work investigation table is ready.")