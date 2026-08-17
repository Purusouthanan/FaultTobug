from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Incident
from ..schemas import IncidentResponse
from ..baseline_engine import generate_baseline_test

router = APIRouter(prefix="/baseline", tags=["Baseline Comparison"])

@router.post("/incidents/{id}/generate-test", response_model=IncidentResponse)
def generate_baseline_test_endpoint(id: int, db: Session = Depends(get_db)):
    """
    Trigger the naive baseline test generator.
    Reads the raw incident description and generates a test using basic heuristics.
    """
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if not incident.description:
        raise HTTPException(status_code=400, detail="Incident has no description")

    # Generate baseline code directly from raw description
    code = generate_baseline_test(incident.id, incident.description)
    
    incident.baseline_test_code = code

    db.commit()
    db.refresh(incident)
    
    return incident
