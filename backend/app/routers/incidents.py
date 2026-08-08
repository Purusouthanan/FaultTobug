from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Incident
from ..schemas import IncidentCreate, IncidentUpdate, IncidentResponse
from ..analysis_engine import analyze_incident

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("/", response_model=IncidentResponse)
def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(description=incident.description, status="OPEN")
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

@router.get("/", response_model=List[IncidentResponse])
def get_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()

@router.get("/{id}", response_model=IncidentResponse)
def get_incident(id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/{id}", response_model=IncidentResponse)
def update_incident(id: int, update_data: IncidentUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(incident, key, value)
        
    db.commit()
    db.refresh(incident)
    return incident

@router.post("/{id}/analyze", response_model=IncidentResponse)
def analyze_incident_endpoint(id: int, db: Session = Depends(get_db)):
    """
    Trigger the Analysis Engine on an incident.
    Extracts role, action, resource, expected/actual behavior, and failure category.
    Transitions the incident status to ANALYZED.
    """
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    result = analyze_incident(incident.description)

    # Persist extracted data back to the incident record
    incident.extracted_role     = result.role
    incident.extracted_action   = result.action
    incident.extracted_resource = result.resource
    incident.extracted_endpoint = result.endpoint
    incident.extracted_method   = result.http_method
    incident.expected_result    = result.expected_result
    incident.actual_result      = result.actual_result
    incident.failure_category   = result.failure_category

    if result.failure_category == "Unknown" and result.confidence == "low":
        incident.status = "ERROR"
    else:
        incident.status = "ANALYZED"

    db.commit()
    db.refresh(incident)
    return incident
