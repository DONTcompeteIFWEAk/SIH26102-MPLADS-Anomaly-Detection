import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import engine, SessionLocal
from db_models import Base, RealWork, ConstituencyFinance, WorkInvestigation

WORKS_CSV = PROJECT_ROOT / "data" / "real_mplads_works_hybrid_risk.csv"
FINANCIAL_CSV = PROJECT_ROOT / "data" / "real_financial_features.csv"

def clean_val(v):
    if pd.isna(v):
        return None
    if hasattr(v, "item"):
        return v.item()
    return v

def seed():
    print("=" * 75)
    print("SIH26102 — POSTGRESQL REAL DATA SEEDER")
    print("=" * 75)

    print("\nCreating/Verifying tables in PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables verified.")

    db = SessionLocal()

    try:
        # 1. Seed Constituency Finances
        if FINANCIAL_CSV.exists():
            print(f"\n[1/2] Seeding Constituency Finances from {FINANCIAL_CSV.name}...")
            df_fin = pd.read_csv(FINANCIAL_CSV)
            existing_fin = {row[0] for row in db.query(ConstituencyFinance.project_id).all()}
            print(f"  Existing records in DB: {len(existing_fin):,}")

            new_fin = []
            for _, r in df_fin.iterrows():
                pid = str(r["project_id"])
                if pid in existing_fin:
                    continue
                obj = ConstituencyFinance(
                    project_id=pid,
                    mp_name=clean_val(r.get("mp_name")),
                    constituency=clean_val(r.get("constituency")),
                    entitlement=float(clean_val(r.get("entitlement")) or 0.0),
                    fund_received=float(clean_val(r.get("fund_received")) or 0.0),
                    amount_available=float(clean_val(r.get("amount_available")) or 0.0),
                    works_recommended_cost=float(clean_val(r.get("works_recommended_cost")) or 0.0),
                    work_sanctioned_cost=float(clean_val(r.get("work_sanctioned_cost")) or 0.0),
                    actual_expenditure=float(clean_val(r.get("actual_expenditure")) or 0.0),
                    unspent_balance=float(clean_val(r.get("unspent_balance")) or 0.0),
                    expenditure_to_sanction_ratio=float(clean_val(r.get("expenditure_to_sanction_ratio")) or 0.0),
                    expenditure_deviation_pct=float(clean_val(r.get("expenditure_deviation_pct")) or 0.0),
                    sanction_gap_pct=float(clean_val(r.get("sanction_gap_pct")) or 0.0),
                    unspent_pct=float(clean_val(r.get("unspent_pct")) or 0.0),
                    financial_rule_score=float(clean_val(r.get("financial_rule_score")) or 0.0),
                    financial_risk_level=str(clean_val(r.get("financial_risk_level")) or "LOW"),
                    financial_explanation=clean_val(r.get("financial_explanation"))
                )
                new_fin.append(obj)

            if new_fin:
                db.bulk_save_objects(new_fin)
                db.commit()
                print(f"  [OK] Successfully inserted {len(new_fin):,} new constituency financial records.")
            else:
                print("  Constituency finances already up to date.")

        # 2. Seed Real Works
        if WORKS_CSV.exists():
            print(f"\n[2/2] Seeding Real Works from {WORKS_CSV.name}...")
            df_works = pd.read_csv(WORKS_CSV, low_memory=False)
            existing_works = {row[0] for row in db.query(RealWork.work_id).all()}
            print(f"  Existing works in DB: {len(existing_works):,}")

            to_insert = []
            chunk_size = 3000
            total_inserted = 0

            for idx, r in df_works.iterrows():
                wid = str(r["work_id"])
                if wid in existing_works:
                    continue

                rec_date = None
                if pd.notna(r.get("recommended_date")):
                    try:
                        rec_date = pd.to_datetime(r["recommended_date"]).to_pydatetime()
                    except Exception:
                        pass

                obj = RealWork(
                    work_id=wid,
                    mp_name=clean_val(r.get("mp_name")),
                    work=clean_val(r.get("work")),
                    category=clean_val(r.get("category")),
                    state=clean_val(r.get("state")),
                    constituency=clean_val(r.get("constituency")),
                    ida=clean_val(r.get("ida")),
                    city=clean_val(r.get("city")),
                    ward=clean_val(r.get("ward")),
                    block=clean_val(r.get("block")),
                    village=clean_val(r.get("village")),
                    recommended_date=rec_date,
                    allocation_amount=float(clean_val(r.get("allocation_amount")) or 0.0),
                    ida_approval=clean_val(r.get("ida_approval")),
                    status=clean_val(r.get("status")),
                    house=clean_val(r.get("house")),
                    data_quality_score=float(clean_val(r.get("data_quality_score")) or 100.0),
                    real_ml_risk_score=float(clean_val(r.get("real_ml_risk_score")) or 0.0),
                    work_rule_score=float(clean_val(r.get("work_rule_score")) or 0.0),
                    hybrid_risk_score=float(clean_val(r.get("hybrid_risk_score")) or 0.0),
                    hybrid_risk_level=str(clean_val(r.get("hybrid_risk_level")) or "LOW"),
                    hybrid_risk_flag=int(clean_val(r.get("hybrid_risk_flag")) or 0),
                    hybrid_risk_explanation=clean_val(r.get("hybrid_risk_explanation")),
                    recommended_action=clean_val(r.get("recommended_action")),
                    split_tender_flag=int(clean_val(r.get("split_tender_flag")) or 0),
                    cluster_work_flag=int(clean_val(r.get("cluster_work_flag")) or 0),
                    prolonged_inaction_flag=int(clean_val(r.get("prolonged_inaction_flag")) or 0)
                )
                to_insert.append(obj)

                if len(to_insert) >= chunk_size:
                    db.bulk_save_objects(to_insert)
                    db.commit()
                    total_inserted += len(to_insert)
                    print(f"  Inserted chunk... Total inserted: {total_inserted:,}")
                    to_insert = []

            if to_insert:
                db.bulk_save_objects(to_insert)
                db.commit()
                total_inserted += len(to_insert)

            print(f"  [OK] Real works seeding complete. Added: {total_inserted:,}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

    print("\n" + "=" * 75)
    print("DATABASE SEEDING COMPLETE")
    print("=" * 75)

if __name__ == "__main__":
    seed()
