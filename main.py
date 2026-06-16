from datetime import date, time
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    register_user,
)
from database import supabase
from model import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentUpdate,
    DoctorOut,
    MedicalRecordCreate,
    MedicalRecordOut,
    MedicalRecordUpdate,
    PatientOut,
    Token,
    UserCreate,
    UserOut,
)

app = FastAPI(title="Clinic Appointment Management System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(payload: UserCreate):
    user = register_user(payload)
    return user


@app.post("/auth/login", response_model=Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user["id"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserOut, tags=["Auth"])
def me(current_user: dict = Depends(get_current_active_user)):
    return current_user


# ── Doctors ───────────────────────────────────────────────────────────────────

@app.get("/doctors", response_model=list[DoctorOut], tags=["Doctors"])
def list_doctors(current_user: dict = Depends(get_current_active_user)):
    resp = supabase.table("doctors").select("*, user:users(*)").execute()
    return resp.data


# ── Patients ──────────────────────────────────────────────────────────────────

@app.get("/patients", response_model=list[PatientOut], tags=["Patients"])
def list_patients(current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors or admins can view patient lists",
        )
    resp = supabase.table("patients").select("*, user:users(*)").execute()
    return resp.data


# ── Appointments ──────────────────────────────────────────────────────────────

@app.post("/appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED, tags=["Appointments"])
def book_appointment(payload: AppointmentCreate, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can book appointments",
        )
    patient_id = current_user.get("patient_id")
    if not patient_id:
        raise HTTPException(status_code=500, detail="Patient profile not found")

    data = payload.model_dump()
    data["appointment_date"] = str(data["appointment_date"])
    data["appointment_time"] = str(data["appointment_time"])
    data["patient_id"] = patient_id

    resp = supabase.table("appointments").insert(data).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create appointment")

    # Retrieve nested representation for response_model
    appt_id = resp.data[0]["id"]
    nested_resp = (
        supabase.table("appointments")
        .select("*, patient:patients(*, user:users(*)), doctor:doctors(*, user:users(*))")
        .eq("id", appt_id)
        .execute()
    )
    return nested_resp.data[0]


@app.get("/appointments", response_model=list[AppointmentOut], tags=["Appointments"])
def list_appointments(current_user: dict = Depends(get_current_active_user)):
    query = supabase.table("appointments").select("*, patient:patients(*, user:users(*)), doctor:doctors(*, user:users(*))")
    
    if current_user["role"] == "patient":
        patient_id = current_user.get("patient_id")
        if not patient_id:
            return []
        query = query.eq("patient_id", patient_id)
    elif current_user["role"] == "doctor":
        doctor_id = current_user.get("doctor_id")
        if not doctor_id:
            return []
        query = query.eq("doctor_id", doctor_id)
        
    resp = query.execute()
    return resp.data


@app.get("/appointments/{appointment_id}", response_model=AppointmentOut, tags=["Appointments"])
def get_appointment(appointment_id: str, current_user: dict = Depends(get_current_active_user)):
    resp = (
        supabase.table("appointments")
        .select("*, patient:patients(*, user:users(*)), doctor:doctors(*, user:users(*))")
        .eq("id", appointment_id)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt = resp.data[0]

    # Authorization Check
    if current_user["role"] == "patient" and appt["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user["role"] == "doctor" and appt["doctor_id"] != current_user.get("doctor_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    return appt


@app.patch("/appointments/{appointment_id}", response_model=AppointmentOut, tags=["Appointments"])
def update_appointment(appointment_id: str, payload: AppointmentUpdate, current_user: dict = Depends(get_current_active_user)):
    # Retrieve appointment to check permissions
    appt_resp = supabase.table("appointments").select("*").eq("id", appointment_id).execute()
    if not appt_resp.data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt = appt_resp.data[0]

    # Authorization Check
    if current_user["role"] == "patient" and appt["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user["role"] == "doctor" and appt["doctor_id"] != current_user.get("doctor_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    changes = {k: v for k, v in payload.model_dump().items() if v is not None}
    if "appointment_date" in changes:
        changes["appointment_date"] = str(changes["appointment_date"])
    if "appointment_time" in changes:
        changes["appointment_time"] = str(changes["appointment_time"])

    if not changes:
        raise HTTPException(status_code=400, detail="No fields to update")

    resp = supabase.table("appointments").update(changes).eq("id", appointment_id).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to update appointment")

    # Fetch nested representation
    nested_resp = (
        supabase.table("appointments")
        .select("*, patient:patients(*, user:users(*)), doctor:doctors(*, user:users(*))")
        .eq("id", appointment_id)
        .execute()
    )
    return nested_resp.data[0]


@app.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Appointments"])
def delete_appointment(appointment_id: str, current_user: dict = Depends(get_current_active_user)):
    appt_resp = supabase.table("appointments").select("*").eq("id", appointment_id).execute()
    if not appt_resp.data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt = appt_resp.data[0]

    # Authorization Check
    if current_user["role"] == "patient" and appt["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user["role"] == "doctor" and appt["doctor_id"] != current_user.get("doctor_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    supabase.table("appointments").delete().eq("id", appointment_id).execute()


# ── Medical Records ───────────────────────────────────────────────────────────

@app.post("/medical-records", response_model=MedicalRecordOut, status_code=status.HTTP_201_CREATED, tags=["Medical Records"])
def create_medical_record(payload: MedicalRecordCreate, current_user: dict = Depends(get_current_active_user)):
    if current_user["role"] != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create medical records",
        )
    doctor_id = current_user.get("doctor_id")
    if not doctor_id:
        raise HTTPException(status_code=500, detail="Doctor profile not found")

    data = payload.model_dump()
    data["doctor_id"] = doctor_id

    resp = supabase.table("medical_records").insert(data).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create medical record")

    # Fetch nested representation
    nested_resp = (
        supabase.table("medical_records")
        .select("*, patient:patients(*, user:users(*)), doctor:doctors(*, user:users(*))")
        .eq("id", resp.data[0]["id"])
        .execute()
    )
    return nested_resp.data[0]


@app.get("/medical-records", response_model=list[MedicalRecordOut], tags=["Medical Records"])
def list_medical_records(current_user: dict = Depends(get_current_active_user)):
    query = supabase.table("medical_records").select("*, patient:patients(*, user:users(*)), doctor:doctors(*, user:users(*))")
    
    if current_user["role"] == "patient":
        patient_id = current_user.get("patient_id")
        if not patient_id:
            return []
        query = query.eq("patient_id", patient_id)
    elif current_user["role"] == "doctor":
        doctor_id = current_user.get("doctor_id")
        if not doctor_id:
            return []
        query = query.eq("doctor_id", doctor_id)
        
    resp = query.execute()
    return resp.data


@app.get("/medical-records/{record_id}", response_model=MedicalRecordOut, tags=["Medical Records"])
def get_medical_record(record_id: str, current_user: dict = Depends(get_current_active_user)):
    resp = (
        supabase.table("medical_records")
        .select("*, patient:patients(*, user:users(*)), doctor:doctors(*, user:users(*))")
        .eq("id", record_id)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Medical record not found")
    rec = resp.data[0]

    # Authorization Check
    if current_user["role"] == "patient" and rec["patient_id"] != current_user.get("patient_id"):
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user["role"] == "doctor" and rec["doctor_id"] != current_user.get("doctor_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    return rec
