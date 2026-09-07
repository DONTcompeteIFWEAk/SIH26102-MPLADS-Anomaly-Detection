from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# =========================================================
# LEGACY PROJECT (SYNTHETIC BENCHMARK)
# =========================================================

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True, nullable=False)
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

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# =========================================================
# LEGACY PROJECT INVESTIGATION
# =========================================================

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="NEW", nullable=False)
    officer_note = Column(String, default="", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# =========================================================
# REAL MPLADS WORK (60,000+ WORKS FROM PORTAL)
# =========================================================

class RealWork(Base):
    __tablename__ = "real_works"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(String, unique=True, index=True, nullable=False)
    mp_name = Column(String, index=True, nullable=True)
    work = Column(String, nullable=True)
    category = Column(String, index=True, nullable=True)
    state = Column(String, index=True, nullable=True)
    constituency = Column(String, index=True, nullable=True)
    ida = Column(String, nullable=True)
    city = Column(String, nullable=True)
    ward = Column(String, nullable=True)
    block = Column(String, nullable=True)
    village = Column(String, nullable=True)
    recommended_date = Column(DateTime, nullable=True)
    allocation_amount = Column(Float, index=True, nullable=True)
    ida_approval = Column(String, nullable=True)
    status = Column(String, index=True, nullable=True)
    house = Column(String, nullable=True)

    # Risk & Behavioral scores
    data_quality_score = Column(Float, nullable=True)
    real_ml_risk_score = Column(Float, nullable=True)
    work_rule_score = Column(Float, nullable=True)
    hybrid_risk_score = Column(Float, index=True, nullable=True)
    hybrid_risk_level = Column(String, index=True, nullable=True)
    hybrid_risk_flag = Column(Integer, default=0, index=True)
    hybrid_risk_explanation = Column(String, nullable=True)
    recommended_action = Column(String, nullable=True)

    # Detected signal flags
    split_tender_flag = Column(Integer, default=0)
    cluster_work_flag = Column(Integer, default=0)
    prolonged_inaction_flag = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# =========================================================
# REAL CONSTITUENCY FINANCIALS (559 MPS)
# =========================================================

class ConstituencyFinance(Base):
    __tablename__ = "constituency_finances"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True, nullable=False)
    mp_name = Column(String, index=True, nullable=True)
    constituency = Column(String, index=True, nullable=True)

    entitlement = Column(Float, default=0.0)
    fund_received = Column(Float, default=0.0)
    amount_available = Column(Float, default=0.0)
    works_recommended_cost = Column(Float, default=0.0)
    work_sanctioned_cost = Column(Float, default=0.0)
    actual_expenditure = Column(Float, default=0.0)
    unspent_balance = Column(Float, default=0.0)

    expenditure_to_sanction_ratio = Column(Float, default=0.0)
    expenditure_deviation_pct = Column(Float, default=0.0)
    sanction_gap_pct = Column(Float, default=0.0)
    unspent_pct = Column(Float, default=0.0)

    financial_rule_score = Column(Float, default=0.0, index=True)
    financial_risk_level = Column(String, default="LOW", index=True)
    financial_explanation = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# =========================================================
# REAL MPLADS WORK INVESTIGATION
# =========================================================

class WorkInvestigation(Base):
    __tablename__ = "work_investigations"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(String(60), unique=True, index=True, nullable=False)
    status = Column(String(50), default="NEW", nullable=False)
    priority = Column(String(50), default="ROUTINE", nullable=False)
    officer_name = Column(String(100), default="Lead CAG Auditor", nullable=False)
    officer_note = Column(String(4000), default="", nullable=False)
    checklist_verified = Column(Boolean, default=False)
    site_inspection_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)