from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Prescription
from ..auth import require_permission

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])

@router.get("/{id}")
def get_prescription(
    id: int,
    db: Session = Depends(get_db),
    authorized: bool = Depends(require_permission("prescriptions", "view"))
):
    prescription = db.query(Prescription).filter(Prescription.id == id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@router.patch("/{id}")
def modify_prescription(
    id: int,
    instructions: str,
    db: Session = Depends(get_db),
    # Crucial permission check that our pipeline will evaluate
    authorized: bool = Depends(require_permission("prescriptions", "modify"))
):
    prescription = db.query(Prescription).filter(Prescription.id == id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    prescription.instructions = instructions
    db.commit()
    db.refresh(prescription)
    return prescription
