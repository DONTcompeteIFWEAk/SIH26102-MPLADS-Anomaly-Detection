from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from pathlib import Path

from database import get_db
from db_models import Project, Investigation, WorkInvestigation


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="SIH26102 MPLADS Anomaly Detection API",
    description=(
        "AI-powered system for detecting anomalies, "
        "fraud-risk patterns and inefficiencies in MPLADS implementation."
    ),
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REAL MPLADS FINANCIAL DATA
# =========================================================

REAL_FINANCIAL_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "real_financial_features.csv"
)


def load_real_financial_data():
    """
    Load the real MPLADS financial screening dataset.

    This dataset is aggregate financial data and should be treated
    as financial screening evidence, not project-level fraud labels.
    """

    if not REAL_FINANCIAL_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Real MPLADS financial dataset not found."
        )

    try:
        df = pd.read_csv(REAL_FINANCIAL_FILE)
        df = df.where(pd.notna(df), None)
        return df

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load real MPLADS financial data: {str(e)}"
        )


def clean_value(value):
    """
    Convert pandas/numpy values into JSON-safe Python values.
    """

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


def dataframe_to_records(df):
    """
    Convert DataFrame into JSON-safe dictionaries.
    """

    records = df.to_dict(orient="records")

    cleaned_records = []

    for record in records:
        cleaned_records.append(
            {
                key: clean_value(value)
                for key, value in record.items()
            }
        )

    return cleaned_records


# =========================================================
# INVESTIGATION REQUEST MODEL
# =========================================================

class InvestigationUpdate(BaseModel):
    status: str
    officer_note: str = ""


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "SIH26102 MPLADS Anomaly Detection API",
        "status": "running"
    }


# =========================================================
# GET ALL PROJECTS
# =========================================================

@app.get("/projects")
def get_projects(
    db: Session = Depends(get_db)
):

    projects = (
        db.query(Project)
        .order_by(Project.risk_score.desc())
        .all()
    )

    return [
        {
            "project_id": p.project_id,
            "state": p.state,
            "district": p.district,
            "constituency": p.constituency,

            "sanctioned_amount": p.sanctioned_amount,
            "actual_expenditure": p.actual_expenditure,
            "expenditure_ratio": p.expenditure_ratio,

            "completion_delay_days": p.completion_delay_days,
            "work_status": p.work_status,

            "sector": p.sector,
            "implementing_agency": p.implementing_agency,

            "uc_available": p.uc_available,
            "uc_amount": p.uc_amount,

            "ml_risk_score": p.ml_risk_score,
            "rule_risk_score": p.rule_risk_score,
            "risk_score": p.risk_score,

            "risk_level": p.risk_level,
            "risk_explanation": p.risk_explanation
        }
        for p in projects
    ]


# =========================================================
# GET SINGLE PROJECT
# =========================================================

@app.get("/projects/{project_id}")
def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):

    project = (
        db.query(Project)
        .filter(Project.project_id == project_id)
        .first()
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return {
        "project_id": project.project_id,
        "state": project.state,
        "district": project.district,
        "constituency": project.constituency,

        "sanctioned_amount": project.sanctioned_amount,
        "actual_expenditure": project.actual_expenditure,
        "expenditure_ratio": project.expenditure_ratio,

        "completion_delay_days": project.completion_delay_days,
        "work_status": project.work_status,

        "sector": project.sector,
        "implementing_agency": project.implementing_agency,

        "uc_available": project.uc_available,
        "uc_amount": project.uc_amount,

        "ml_risk_score": project.ml_risk_score,
        "rule_risk_score": project.rule_risk_score,
        "risk_score": project.risk_score,

        "risk_level": project.risk_level,
        "risk_explanation": project.risk_explanation
    }


# =========================================================
# GET HIGH-RISK PROJECTS
# =========================================================

@app.get("/anomalies")
def get_anomalies(
    db: Session = Depends(get_db)
):

    projects = (
        db.query(Project)
        .filter(Project.risk_score >= 50)
        .order_by(Project.risk_score.desc())
        .all()
    )

    return [
        {
            "project_id": p.project_id,
            "state": p.state,
            "district": p.district,
            "constituency": p.constituency,

            "risk_score": p.risk_score,
            "risk_level": p.risk_level,

            "risk_explanation": p.risk_explanation
        }
        for p in projects
    ]


# =========================================================
# GET CRITICAL PROJECTS
# =========================================================

@app.get("/critical")
def get_critical(
    db: Session = Depends(get_db)
):

    projects = (
        db.query(Project)
        .filter(Project.risk_score >= 75)
        .order_by(Project.risk_score.desc())
        .all()
    )

    return [
        {
            "project_id": p.project_id,
            "state": p.state,
            "district": p.district,
            "constituency": p.constituency,

            "risk_score": p.risk_score,
            "risk_level": p.risk_level,

            "risk_explanation": p.risk_explanation
        }
        for p in projects
    ]


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

@app.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db)
):

    # Total projects
    total_projects = (
        db.query(Project)
        .count()
    )

    # Total expenditure
    total_expenditure = (
        db.query(
            func.coalesce(
                func.sum(Project.actual_expenditure),
                0
            )
        )
        .scalar()
    )

    # High-risk projects
    high_risk = (
        db.query(Project)
        .filter(Project.risk_score >= 50)
        .count()
    )

    # Critical projects
    critical = (
        db.query(Project)
        .filter(Project.risk_score >= 75)
        .count()
    )

    # Delayed projects
    delayed = (
        db.query(Project)
        .filter(Project.completion_delay_days > 30)
        .count()
    )

    # Missing utilization certificates
    #
    # IMPORTANT:
    # uc_available is a PostgreSQL BOOLEAN column.
    # Therefore we use .is_(False), NOT == 0.
    missing_uc = (
        db.query(Project)
        .filter(Project.uc_available.is_(False))
        .count()
    )

    return {
        "total_projects": total_projects,
        "total_expenditure": total_expenditure,
        "high_risk": high_risk,
        "critical": critical,
        "delayed_projects": delayed,
        "missing_uc": missing_uc
    }


# =========================================================
# GET ALL STATES
# =========================================================

@app.get("/states")
def get_states(
    db: Session = Depends(get_db)
):

    states = (
        db.query(Project.state)
        .distinct()
        .order_by(Project.state)
        .all()
    )

    return [
        state[0]
        for state in states
    ]


# =========================================================
# GET PROJECTS BY STATE
# =========================================================

@app.get("/states/{state_name}")
def get_projects_by_state(
    state_name: str,
    db: Session = Depends(get_db)
):

    projects = (
        db.query(Project)
        .filter(Project.state == state_name)
        .order_by(Project.risk_score.desc())
        .all()
    )

    return [
        {
            "project_id": p.project_id,
            "district": p.district,
            "constituency": p.constituency,

            "risk_score": p.risk_score,
            "risk_level": p.risk_level,

            "sanctioned_amount": p.sanctioned_amount,
            "actual_expenditure": p.actual_expenditure
        }
        for p in projects
    ]


# =========================================================
# GET PROJECTS BY CONSTITUENCY
# =========================================================

@app.get("/constituencies/{constituency}")
def get_projects_by_constituency(
    constituency: str,
    db: Session = Depends(get_db)
):

    projects = (
        db.query(Project)
        .filter(Project.constituency == constituency)
        .order_by(Project.risk_score.desc())
        .all()
    )

    return [
        {
            "project_id": p.project_id,
            "state": p.state,
            "district": p.district,

            "risk_score": p.risk_score,
            "risk_level": p.risk_level
        }
        for p in projects
    ]


# =========================================================
# REAL MPLADS — ALL FINANCIAL RECORDS
# =========================================================

@app.get("/real-financial")
def get_real_financial():

    df = load_real_financial_data()

    return dataframe_to_records(df)


# =========================================================
# REAL MPLADS — HIGH-RISK FINANCIAL RECORDS
# =========================================================

@app.get("/real-financial/high-risk")
def get_real_financial_high_risk():

    df = load_real_financial_data()

    df = df[
        df["financial_rule_score"] >= 50
    ].copy()

    df = df.sort_values(
        by="financial_rule_score",
        ascending=False
    )

    return dataframe_to_records(df)


# =========================================================
# REAL MPLADS — FINANCIAL STATISTICS
# =========================================================

@app.get("/real-financial/statistics")
def get_real_financial_statistics():

    df = load_real_financial_data()

    risk_counts = (
        df["financial_risk_level"]
        .value_counts()
        .to_dict()
    )

    signal_counts = {}

    signal_columns = [
        "signal_excess_expenditure",
        "signal_extreme_expenditure",
        "signal_severe_expenditure_deviation",
        "signal_expenditure_above_available",
        "signal_sanction_gap",
        "signal_high_unspent_balance"
    ]

    for column in signal_columns:

        if column in df.columns:
            signal_counts[column] = int(
                df[column].fillna(0).sum()
            )

    high_risk_count = int(
        (df["financial_rule_score"] >= 50).sum()
    )

    medium_or_above_count = int(
        (df["financial_rule_score"] >= 25).sum()
    )

    return {
        "data_source": "REAL_MPLADS",
        "total_records": int(len(df)),

        "risk_distribution": {
            "CRITICAL": int(risk_counts.get("CRITICAL", 0)),
            "HIGH": int(risk_counts.get("HIGH", 0)),
            "MEDIUM": int(risk_counts.get("MEDIUM", 0)),
            "LOW": int(risk_counts.get("LOW", 0))
        },

        "high_risk_records": high_risk_count,
        "medium_or_above_records": medium_or_above_count,

        "signal_counts": signal_counts,

        "ground_truth_available": False,

        "interpretation": (
            "Financial screening signals from real MPLADS data. "
            "These signals are not confirmed fraud findings and "
            "require human verification."
        )
    }


# =========================================================
# REAL MPLADS — SINGLE FINANCIAL RECORD
# =========================================================

@app.get("/real-financial/{project_id}")
def get_real_financial_record(
    project_id: str
):

    df = load_real_financial_data()

    record = df[
        df["project_id"].astype(str) == str(project_id)
    ]

    if record.empty:

        raise HTTPException(
            status_code=404,
            detail="Real MPLADS financial record not found"
        )

    return dataframe_to_records(record)[0]


# =========================================================
# REAL MPLADS WORK-LEVEL DATA
# =========================================================

REAL_WORK_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "real_mplads_works_hybrid_risk.csv"
)


def load_real_work_data():
    """
    Load the real MPLADS work-level hybrid-risk dataset.

    This dataset is based on real MPLADS work records. The anomaly
    scores are screening signals produced by the hybrid ML + rule
    engine and are NOT confirmed fraud findings.
    """

    if not REAL_WORK_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Real MPLADS work-level dataset not found."
        )

    try:
        df = pd.read_csv(REAL_WORK_FILE)

        # The hybrid-risk pipeline stores work-level fields with "work_"
        # prefixes. Normalize them here so the API has stable names.
        aliases = {
            "work_hybrid_risk_score": "hybrid_risk_score",
            "work_hybrid_risk_level": "hybrid_risk_level",
            "work_hybrid_explanation": "hybrid_risk_explanation",
            "ml_risk_score": "real_ml_risk_score",
            "data_quality_score_v2": "data_quality_score",
        }

        for source_column, api_column in aliases.items():
            if source_column in df.columns and api_column not in df.columns:
                df[api_column] = df[source_column]

        if "hybrid_risk_score" in df.columns:
            df["hybrid_risk_score"] = pd.to_numeric(
                df["hybrid_risk_score"], errors="coerce"
            )

        # The hybrid engine uses the 95th-percentile screening threshold.
        # For this generated hybrid dataset the threshold is 77.85.
        # This is deliberately separate from risk-level boundaries:
        # MEDIUM starts at 50, HIGH at 75, and CRITICAL at 90.
        if "hybrid_risk_flag" not in df.columns:
            if "hybrid_risk_score" in df.columns:
                df["hybrid_risk_flag"] = (
                    df["hybrid_risk_score"] >= 77.85
                ).astype(int)
            else:
                df["hybrid_risk_flag"] = 0

        # Prefer the hybrid pipeline's v2 data-quality field.
        if "data_quality_score_v2" in df.columns:
            df["data_quality_score"] = pd.to_numeric(
                df["data_quality_score_v2"], errors="coerce"
            )

        df = df.where(pd.notna(df), None)
        return df

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load real MPLADS work-level data: {str(e)}"
        )


# =========================================================
# REAL MPLADS WORKS — ALL RECORDS
# =========================================================

@app.get("/real-work")
def get_real_work():
    df = load_real_work_data()

    return dataframe_to_records(df)


# =========================================================
# REAL MPLADS WORKS — HIGH-RISK RECORDS
# =========================================================

@app.get("/real-work/high-risk")
def get_real_work_high_risk(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Return a paginated subset of high-risk real MPLADS works.

    The underlying dataset contains 56,138 work records and thousands of
    screening flags. Returning every flagged record to Swagger or the
    frontend at once can create a very large JSON response and make the
    browser unresponsive.

    Default: top 100 records. Maximum: 500 records per request.
    """

    df = load_real_work_data()

    if "hybrid_risk_score" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="hybrid_risk_score column missing from real work dataset."
        )

    high_risk_df = df[
        df["hybrid_risk_score"] >= 75
    ].copy()

    high_risk_df = high_risk_df.sort_values(
        by="hybrid_risk_score",
        ascending=False
    )

    # Paginate BEFORE converting to dictionaries/JSON.
    paged_df = high_risk_df.iloc[offset:offset + limit]

    return dataframe_to_records(paged_df)


# =========================================================
# REAL MPLADS WORKS — STATISTICS
# =========================================================

@app.get("/real-work/statistics")
def get_real_work_statistics():
    df = load_real_work_data()

    if "hybrid_risk_score" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="hybrid_risk_score column missing from real work dataset."
        )

    risk_counts = (
        df["hybrid_risk_level"]
        .value_counts()
        .to_dict()
        if "hybrid_risk_level" in df.columns
        else {}
    )

    signal_columns = {
        "high_state_allocation": "rule_high_state_allocation",
        "high_constituency_allocation": "rule_high_constituency_allocation",
        "high_category_allocation": "rule_high_category_allocation",
        "repeated_description": "rule_repeated_description",
        "long_description": "rule_long_description",
    }

    signal_counts = {}

    for output_name, column in signal_columns.items():
        if column in df.columns:
            signal_counts[output_name] = int(
                pd.to_numeric(df[column], errors="coerce")
                .fillna(0)
                .sum()
            )
        else:
            signal_counts[output_name] = 0

    high_risk_count = int(
        (pd.to_numeric(df["hybrid_risk_score"], errors="coerce") >= 50).sum()
    )

    medium_or_above_count = int(
        (pd.to_numeric(df["hybrid_risk_score"], errors="coerce") >= 25).sum()
    )

    flagged_count = (
        int(df["hybrid_risk_flag"].sum())
        if "hybrid_risk_flag" in df.columns
        else high_risk_count
    )

    data_quality_average = None
    records_below_70 = 0

    if "data_quality_score" in df.columns:
        quality = pd.to_numeric(
            df["data_quality_score"],
            errors="coerce"
        )

        if quality.notna().any():
            data_quality_average = round(float(quality.mean()), 2)
            records_below_70 = int((quality < 70).sum())

    return {
        "data_source": "REAL_MPLADS_WORKS",
        "total_records": int(len(df)),

        "risk_distribution": {
            "CRITICAL": int(risk_counts.get("CRITICAL", 0)),
            "HIGH": int(risk_counts.get("HIGH", 0)),
            "MEDIUM": int(risk_counts.get("MEDIUM", 0)),
            "LOW": int(risk_counts.get("LOW", 0)),
        },

        "hybrid_screening_threshold": 77.85,
        "flagged_records": flagged_count,
        "high_risk_records": high_risk_count,
        "medium_or_above_records": medium_or_above_count,

        "signal_counts": signal_counts,

        "data_quality": {
            "average_score": data_quality_average,
            "records_below_70": records_below_70,
        },

        "ground_truth_available": False,

        "interpretation": (
            "Work-level anomaly screening signals from real MPLADS data "
            "using a hybrid ML and behavioral-rule engine. "
            "These signals are not confirmed fraud findings and "
            "require human verification."
        ),
    }


# =========================================================
# REAL MPLADS WORKS — SINGLE WORK RECORD
# =========================================================

@app.get("/real-work/{work_id}")
def get_real_work_record(
    work_id: str
):
    df = load_real_work_data()

    if "work_id" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="work_id column missing from real work dataset."
        )

    record = df[
        df["work_id"].astype(str) == str(work_id)
    ]

    if record.empty:
        raise HTTPException(
            status_code=404,
            detail="Real MPLADS work record not found"
        )

    return dataframe_to_records(record)[0]



# =========================================================
# CREATE INVESTIGATION
# =========================================================

@app.post("/investigations/{project_id}")
def create_investigation(
    project_id: str,
    db: Session = Depends(get_db)
):

    # Check project
    project = (
        db.query(Project)
        .filter(Project.project_id == project_id)
        .first()
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Check whether investigation already exists
    existing = (
        db.query(Investigation)
        .filter(
            Investigation.project_id == project_id
        )
        .first()
    )

    if existing:

        return {
            "message": "Investigation already exists",
            "investigation_id": existing.id,
            "project_id": existing.project_id,
            "status": existing.status,
            "officer_note": existing.officer_note
        }

    # Create investigation
    investigation = Investigation(
        project_id=project_id,
        status="NEW",
        officer_note=""
    )

    db.add(investigation)

    db.commit()

    db.refresh(investigation)

    return {
        "message": "Investigation created successfully",
        "investigation_id": investigation.id,
        "project_id": investigation.project_id,
        "status": investigation.status,
        "officer_note": investigation.officer_note
    }


# =========================================================
# GET INVESTIGATION
# =========================================================

@app.get("/investigations/{project_id}")
def get_investigation(
    project_id: str,
    db: Session = Depends(get_db)
):

    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.project_id == project_id
        )
        .first()
    )

    if not investigation:

        raise HTTPException(
            status_code=404,
            detail="Investigation not found"
        )

    return {
        "id": investigation.id,
        "project_id": investigation.project_id,
        "status": investigation.status,
        "officer_note": investigation.officer_note,
        "created_at": investigation.created_at,
        "updated_at": investigation.updated_at
    }


# =========================================================
# UPDATE INVESTIGATION
# =========================================================

@app.put("/investigations/{project_id}")
def update_investigation(
    project_id: str,
    data: InvestigationUpdate,
    db: Session = Depends(get_db)
):

    # Check project
    project = (
        db.query(Project)
        .filter(Project.project_id == project_id)
        .first()
    )

    if not project:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    # Find existing investigation
    investigation = (
        db.query(Investigation)
        .filter(
            Investigation.project_id == project_id
        )
        .first()
    )

    # If no investigation exists,
    # create one automatically.
    if not investigation:

        investigation = Investigation(
            project_id=project_id,
            status=data.status,
            officer_note=data.officer_note
        )

        db.add(investigation)

    else:

        investigation.status = data.status
        investigation.officer_note = data.officer_note

    db.commit()

    db.refresh(investigation)

    return {
        "message": "Investigation updated successfully",
        "id": investigation.id,
        "project_id": investigation.project_id,
        "status": investigation.status,
        "officer_note": investigation.officer_note
    }

# =========================================================
# REAL MPLADS WORK — INVESTIGATION QUEUE
# =========================================================

@app.get("/work-investigations/queue")
def get_work_investigation_queue(
    db: Session = Depends(get_db)
):
    investigations = (
        db.query(WorkInvestigation)
        .order_by(WorkInvestigation.updated_at.desc())
        .all()
    )

    return [
        {
            "id": investigation.id,
            "work_id": investigation.work_id,
            "status": investigation.status,
            "officer_note": investigation.officer_note,
            "created_at": investigation.created_at,
            "updated_at": investigation.updated_at
        }
        for investigation in investigations
    ]


# =========================================================
# CREATE WORK INVESTIGATION
# =========================================================

@app.post("/work-investigations/{work_id}")
def create_work_investigation(
    work_id: str,
    db: Session = Depends(get_db)
):
    df = load_real_work_data()

    if "work_id" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="work_id column missing from real work dataset."
        )

    work_exists = (
        df["work_id"].astype(str) == str(work_id)
    ).any()

    if not work_exists:
        raise HTTPException(
            status_code=404,
            detail="Real MPLADS work not found."
        )

    existing = (
        db.query(WorkInvestigation)
        .filter(WorkInvestigation.work_id == work_id)
        .first()
    )

    if existing:
        return {
            "message": "Work investigation already exists",
            "investigation_id": existing.id,
            "work_id": existing.work_id,
            "status": existing.status,
            "officer_note": existing.officer_note
        }

    investigation = WorkInvestigation(
        work_id=work_id,
        status="NEW",
        officer_note=""
    )

    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    return {
        "message": "Work investigation created successfully",
        "investigation_id": investigation.id,
        "work_id": investigation.work_id,
        "status": investigation.status,
        "officer_note": investigation.officer_note
    }


# =========================================================
# GET WORK INVESTIGATION
# =========================================================

@app.get("/work-investigations/{work_id}")
def get_work_investigation(
    work_id: str,
    db: Session = Depends(get_db)
):
    investigation = (
        db.query(WorkInvestigation)
        .filter(WorkInvestigation.work_id == work_id)
        .first()
    )

    if not investigation:
        raise HTTPException(
            status_code=404,
            detail="Work investigation not found"
        )

    return {
        "id": investigation.id,
        "work_id": investigation.work_id,
        "status": investigation.status,
        "officer_note": investigation.officer_note,
        "created_at": investigation.created_at,
        "updated_at": investigation.updated_at
    }


# =========================================================
# UPDATE WORK INVESTIGATION
# =========================================================

@app.put("/work-investigations/{work_id}")
def update_work_investigation(
    work_id: str,
    data: InvestigationUpdate,
    db: Session = Depends(get_db)
):
    investigation = (
        db.query(WorkInvestigation)
        .filter(WorkInvestigation.work_id == work_id)
        .first()
    )

    if not investigation:
        df = load_real_work_data()

        if "work_id" not in df.columns:
            raise HTTPException(
                status_code=500,
                detail="work_id column missing from real work dataset."
            )

        work_exists = (
            df["work_id"].astype(str) == str(work_id)
        ).any()

        if not work_exists:
            raise HTTPException(
                status_code=404,
                detail="Real MPLADS work not found."
            )

        investigation = WorkInvestigation(
            work_id=work_id,
            status=data.status,
            officer_note=data.officer_note
        )

        db.add(investigation)
    else:
        investigation.status = data.status
        investigation.officer_note = data.officer_note

    db.commit()
    db.refresh(investigation)

    return {
        "message": "Work investigation updated successfully",
        "id": investigation.id,
        "work_id": investigation.work_id,
        "status": investigation.status,
        "officer_note": investigation.officer_note
    }

