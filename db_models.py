from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


# =========================================================
# PROJECT
# =========================================================

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    constituency = Column(String, nullable=True)

    sanctioned_amount = Column(Float, nullable=True)
    project_duration_days = Column(Integer, nullable=True)
    completion_delay_days = Column(Integer, nullable=True)

    uc_available = Column(Boolean, nullable=True)
    work_status = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    implementing_agency = Column(String, nullable=True)

    actual_expenditure = Column(Float, nullable=True)
    uc_amount = Column(Float, nullable=True)
    expenditure_ratio = Column(Float, nullable=True)

    ml_risk_score = Column(Float, nullable=True)
    rule_risk_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)

    risk_level = Column(String, nullable=True)
    risk_explanation = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# =========================================================
# PROJECT INVESTIGATION
# =========================================================

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    status = Column(
        String,
        default="NEW",
        nullable=False
    )

    officer_note = Column(
        String,
        default="",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


# =========================================================
# REAL MPLADS WORK INVESTIGATION
# =========================================================

class WorkInvestigation(Base):
    __tablename__ = "work_investigations"

    id = Column(Integer, primary_key=True, index=True)

    work_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    status = Column(
        String,
        default="NEW",
        nullable=False
    )

    officer_note = Column(
        String,
        default="",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )