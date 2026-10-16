from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime


# ---------- Auth ----------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# ---------- Patient ----------
class PatientBase(BaseModel):
    profile_code: Optional[str] = None
    age: int
    sex: Optional[str] = None
    cardiac_diagnosis: Optional[str] = None
    lvef: Optional[float] = None
    heart_rate: Optional[int] = None
    qt_interval: Optional[int] = None
    qtc: Optional[int] = None
    qrs_duration: Optional[int] = None
    potassium: Optional[float] = None
    magnesium: Optional[float] = None
    creatinine: Optional[float] = None
    egfr: Optional[float] = None
    alt: Optional[float] = None
    ast: Optional[float] = None
    tsh: Optional[float] = None
    free_t4: Optional[float] = None
    antiarrhythmic_drug: Optional[str] = None
    antiarrhythmic_dose: Optional[str] = None
    other_medications: Optional[str] = None
    last_ecg_date: Optional[date] = None
    last_thyroid_date: Optional[date] = None
    last_lft_date: Optional[date] = None
    last_electrolytes_date: Optional[date] = None
    last_renal_date: Optional[date] = None
    notes: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    age: Optional[int] = None


class PatientOut(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Safety ----------
class Alert(BaseModel):
    severity: str          # info / warning / high / critical
    code: str
    message: str
    recommendation: str


class AssessmentResult(BaseModel):
    patient_id: int
    overall_risk: str
    alerts: List[Alert]
    recommendations: List[str]
    assessed_at: datetime


class AssessmentOut(BaseModel):
    id: int
    patient_id: int
    assessed_at: datetime
    overall_risk: str
    alerts_json: str
    recommendations: Optional[str]

    class Config:
        from_attributes = True
