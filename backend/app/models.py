from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="clinician")  # clinician / admin
    created_at = Column(DateTime, default=datetime.utcnow)


class SyntheticPatient(Base):
    __tablename__ = "synthetic_patients"

    id = Column(Integer, primary_key=True, index=True)
    profile_code = Column(String(20), unique=True, index=True)  # e.g. SYN-001
    age = Column(Integer, nullable=False)
    sex = Column(String(10))  # M / F / Other

    # Cardiac
    cardiac_diagnosis = Column(String(200))  # e.g. AF, VT, SVT
    lvef = Column(Float)  # Left Ventricular Ejection Fraction %
    heart_rate = Column(Integer)
    qt_interval = Column(Integer)  # ms
    qtc = Column(Integer)  # corrected QT
    qrs_duration = Column(Integer)  # ms

    # Labs
    potassium = Column(Float)  # mmol/L
    magnesium = Column(Float)  # mmol/L
    creatinine = Column(Float)  # µmol/L or mg/dL (we store µmol/L)
    egfr = Column(Float)  # mL/min/1.73m²
    alt = Column(Float)  # U/L
    ast = Column(Float)  # U/L
    tsh = Column(Float)  # mIU/L
    free_t4 = Column(Float)

    # Current medications
    antiarrhythmic_drug = Column(String(50))  # Sotalol / Flecainide / Amiodarone / etc.
    antiarrhythmic_dose = Column(String(50))
    other_medications = Column(Text)  # free text list

    # Monitoring dates
    last_ecg_date = Column(Date)
    last_thyroid_date = Column(Date)
    last_lft_date = Column(Date)
    last_electrolytes_date = Column(Date)
    last_renal_date = Column(Date)

    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    assessments = relationship("SafetyAssessment", back_populates="patient")


class SafetyAssessment(Base):
    __tablename__ = "safety_assessments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("synthetic_patients.id"), nullable=False)
    assessed_at = Column(DateTime, default=datetime.utcnow)
    assessed_by = Column(Integer, ForeignKey("users.id"))
    overall_risk = Column(String(20))  # low / moderate / high / critical
    alerts_json = Column(Text)  # JSON list of alerts
    recommendations = Column(Text)

    patient = relationship("SyntheticPatient", back_populates="assessments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
