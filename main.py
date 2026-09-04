from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from db_models import Project, Investigation


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