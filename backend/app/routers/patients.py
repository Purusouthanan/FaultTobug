from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Patient
from ..auth import require_permission, get_current_user

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/")
def get_patients(
    db: Session = Depends(get_db),
    # Require view permission on patients resource
    authorized: bool = Depends(require_permission("patients", "view"))
):
    patients = db.query(Patient).all()
    return patients

@router.post("/")
def create_patient(
    name: str, dob: str, status: str,
    db: Session = Depends(get_db),
    # Require create permission on patients resource
    authorized: bool = Depends(require_permission("patients", "create"))
):
    new_patient = Patient(name=name, dob=dob, status=status)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient
