from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, ConfigDict
from ..database import get_db
from ..models import Patient
from ..auth import require_permission

router = APIRouter(prefix="/patients", tags=["Patients"])


# ---------------------------------------------------------------------------
# Schemas (local to avoid circular imports)
# ---------------------------------------------------------------------------

class PatientCreate(BaseModel):
    name: str
    dob: date          # Pydantic parses "YYYY-MM-DD" → datetime.date automatically
    status: str

class PatientResponse(BaseModel):
    id: int
    name: str
    dob: date
    status: str

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[PatientResponse])
def get_patients(
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_permission("patients", "view"))
):
    return db.query(Patient).all()


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_permission("patients", "view"))
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/", response_model=PatientResponse, status_code=201)
def create_patient(
    body: PatientCreate,
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_permission("patients", "create"))
):
    new_patient = Patient(name=body.name, dob=body.dob, status=body.status)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.delete("/{patient_id}", status_code=204)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_permission("patients", "delete"))
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(patient)
    db.commit()
    return None
