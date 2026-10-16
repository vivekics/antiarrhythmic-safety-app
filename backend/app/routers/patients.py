from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime

from ..database import get_db
from ..models import SyntheticPatient, SafetyAssessment, AuditLog, User
from ..schemas import (
    PatientCreate, PatientUpdate, PatientOut,
    AssessmentResult, AssessmentOut, Alert
)
from ..auth import get_current_user
from ..rules_engine import assess_patient

router = APIRouter(prefix="/api/patients", tags=["Patients"])


def log_action(db: Session, user_id: int, action: str, entity_type: str, entity_id: int, details: str = ""):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.add(entry)
    db.commit()


@router.post("/", response_model=PatientOut)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Auto-generate profile code if not provided
    if not patient_in.profile_code:
        count = db.query(SyntheticPatient).count()
        patient_in.profile_code = f"SYN-{count + 1:04d}"

    patient = SyntheticPatient(**patient_in.model_dump(), created_by=current_user.id)
    db.add(patient)
    db.commit()
    db.refresh(patient)

    log_action(db, current_user.id, "CREATE", "patient", patient.id, f"Created {patient.profile_code}")
    return patient


@router.get("/", response_model=List[PatientOut])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(SyntheticPatient).offset(skip).limit(limit).all()


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(SyntheticPatient).filter(SyntheticPatient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return patient


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    patient_in: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(SyntheticPatient).filter(SyntheticPatient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    update_data = patient_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(patient)

    log_action(db, current_user.id, "UPDATE", "patient", patient.id)
    return patient


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(SyntheticPatient).filter(SyntheticPatient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    db.delete(patient)
    db.commit()
    log_action(db, current_user.id, "DELETE", "patient", patient_id)
    return {"message": "Profile deleted"}


@router.post("/{patient_id}/assess", response_model=AssessmentResult)
def run_safety_assessment(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(SyntheticPatient).filter(SyntheticPatient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    result = assess_patient(patient)

    # Save assessment
    assessment = SafetyAssessment(
        patient_id=patient.id,
        assessed_by=current_user.id,
        overall_risk=result["overall_risk"],
        alerts_json=json.dumps([a.model_dump() for a in result["alerts"]]),
        recommendations="\n".join(result["recommendations"])
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    log_action(
        db, current_user.id, "ASSESS", "patient", patient.id,
        f"Risk: {result['overall_risk']} | Alerts: {len(result['alerts'])}"
    )

    return AssessmentResult(
        patient_id=patient.id,
        overall_risk=result["overall_risk"],
        alerts=result["alerts"],
        recommendations=result["recommendations"],
        assessed_at=assessment.assessed_at
    )


@router.get("/{patient_id}/assessments", response_model=List[AssessmentOut])
def get_patient_assessments(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(SafetyAssessment).filter(
        SafetyAssessment.patient_id == patient_id
    ).order_by(SafetyAssessment.assessed_at.desc()).all()
