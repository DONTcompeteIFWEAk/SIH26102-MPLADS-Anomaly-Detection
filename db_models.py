from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime
)

from sqlalchemy.sql import func

from database import Base


# =====================================================
# PROJECT TABLE
# =====================================================

class Project(Base):

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)

    project_id = Column(
        String,
        unique=True,
        nullable=False
    )

    state = Column(String)

    district = Column(String)

    constituency = Column(String)

    sanctioned_amount = Column(Float)

    actual_expenditure = Column(Float)

    expenditure_ratio = Column(Float)

    completion_delay_days = Column(Integer)

    work_status = Column(String)

    sector = Column(String)

    implementing_agency = Column(String)

    uc_available = Column(Boolean)

    uc_amount = Column(Float)

    ml_risk_score = Column(Float)

    rule_risk_score = Column(Float)

    risk_score = Column(Float)

    risk_level = Column(String)

    risk_explanation = Column(Text)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )


# =====================================================
# INVESTIGATION TABLE
# =====================================================

class Investigation(Base):

    __tablename__ = "investigations"

    id = Column(
        Integer,
        primary_key=True
    )

    project_id = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="NEW"
    )

    officer_note = Column(
        Text,
        default=""
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )