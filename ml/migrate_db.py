import sys
from pathlib import Path
import sqlalchemy as sa

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import database

def migrate():
    conn = database.engine.connect()
    queries = [
        "ALTER TABLE work_investigations ADD COLUMN IF NOT EXISTS priority VARCHAR(50) DEFAULT 'ROUTINE'",
        "ALTER TABLE work_investigations ADD COLUMN IF NOT EXISTS officer_name VARCHAR(100) DEFAULT 'Lead Auditor'",
        "ALTER TABLE work_investigations ADD COLUMN IF NOT EXISTS checklist_verified BOOLEAN DEFAULT FALSE",
        "ALTER TABLE work_investigations ADD COLUMN IF NOT EXISTS site_inspection_date TIMESTAMP NULL"
    ]
    for q in queries:
        conn.execute(sa.text(q))
    conn.commit()
    conn.close()
    print("[OK] work_investigations schema migration successful!")

if __name__ == "__main__":
    migrate()
