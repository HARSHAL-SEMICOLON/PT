from datetime import date, datetime, time
from typing import Literal, Optional
from pydantic import BaseModel, field_validator


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id: Optional[str] = None


# ── Users ─────────────────────────────────────────────────────────────────────

RoleType = Literal["patient", "doctor", "admin"]


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: RoleType
    specialization: Optional[str] = None  # used if role == "doctor"
    phone: Optional[str] = None           # used if role == "patient"

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        return v.lower().strip()


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: RoleType
    created_at: Optional[datetime] = None


# ── Doctors & Patients ────────────────────────────────────────────────────────

class DoctorOut(BaseModel):
    id: str
    user_id: str
    specialization: Optional[str] = None
    created_at: Optional[datetime] = None
    user: Optional[UserOut] = None


class PatientOut(BaseModel):
    id: str
    user_id: str
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    user: Optional[UserOut] = None


# ── Appointments ──────────────────────────────────────────────────────────────

class AppointmentBase(BaseModel):
    doctor_id: str
    appointment_date: date
    appointment_time: time


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    status: Optional[str] = None


class AppointmentOut(AppointmentBase):
    id: str
    patient_id: str
    status: str
    created_at: Optional[datetime] = None
    patient: Optional[PatientOut] = None
    doctor: Optional[DoctorOut] = None


# ── Medical Records ───────────────────────────────────────────────────────────

class MedicalRecordCreate(BaseModel):
    patient_id: str
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None


class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None


class MedicalRecordOut(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    created_at: Optional[datetime] = None
    patient: Optional[PatientOut] = None
    doctor: Optional[DoctorOut] = None
