import sys
import os

# Add project root to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from database import engine, Base
import db_models


print("Creating database tables...")

Base.metadata.create_all(
    bind=engine
)

print("Database tables created successfully!")