from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Incident, TestExecution
from ..schemas import IncidentCreate, IncidentUpdate, IncidentResponse, TestExecutionResponse
from ..analysis_engine import analyze_incident
from ..reproduction_engine import generate_reproduction_steps
from ..test_generator import generate_pytest_code
from ..execution_engine import execute_test
import json
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

@router.post("/{id}/reproduce", response_model=IncidentResponse)
def reproduce_incident_endpoint(id: int, include_boundaries: bool = False, db: Session = Depends(get_db)):
    """
    Trigger the Reproduction Engine on an incident.
    Generates structured reproduction steps based on extracted data.
    When include_boundaries=True, adds multi-role RBAC boundary checks (Doctor vs Nurse vs Billing Clerk).
    Transitions the incident status to REPRODUCED.
    """
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status not in ["ANALYZED", "REPRODUCED"]:
        raise HTTPException(status_code=400, detail="Incident must be ANALYZED before reproducing")

    incident_data = {
        "extracted_role": incident.extracted_role,
        "extracted_action": incident.extracted_action,
        "extracted_resource": incident.extracted_resource,
        "extracted_method": incident.extracted_method,
        "extracted_endpoint": incident.extracted_endpoint,
        "expected_result": incident.expected_result,
    }

    steps = generate_reproduction_steps(incident_data, include_boundaries=include_boundaries)
    incident.reproduction_steps = json.dumps(steps)
    incident.status = "REPRODUCED"

    db.commit()
    db.refresh(incident)
    return incident

@router.post("/{id}/generate-test", response_model=IncidentResponse)
def generate_test_endpoint(id: int, db: Session = Depends(get_db)):
    """
    Trigger the Regression Test Generator on an incident.
    Reads reproduction steps and generates valid Pytest code.
    Transitions the incident status to TEST_GENERATED.
    """
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status not in ["REPRODUCED", "TEST_GENERATED"]:
        raise HTTPException(status_code=400, detail="Incident must be REPRODUCED before generating test")
        
    if not incident.reproduction_steps:
        raise HTTPException(status_code=400, detail="Incident has no reproduction steps")

    steps = json.loads(incident.reproduction_steps)
    code = generate_pytest_code(incident.id, steps)
    
    incident.generated_test_code = code
    incident.status = "TEST_GENERATED"

    db.commit()
    db.refresh(incident)
    return incident

@router.post("/{id}/execute", response_model=TestExecutionResponse)
def execute_incident_test_endpoint(id: int, db: Session = Depends(get_db)):
    """
    Trigger the Execution Engine on an incident.
    Runs the generated test code and persists the result.
    Transitions incident status to TEST_EXECUTED.
    """
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if not incident.generated_test_code:
        raise HTTPException(status_code=400, detail="Incident has no generated test code")

    # Run the test
    exec_result = execute_test(incident.id, incident.generated_test_code)

    # Save execution record
    test_execution = TestExecution(
        incident_id=incident.id,
        status=exec_result["status"],
        execution_time=exec_result["execution_time"],
        logs=exec_result["logs"]
    )
    db.add(test_execution)
    
    incident.status = "TEST_EXECUTED"
    db.commit()
    db.refresh(test_execution)
    
    return test_execution

@router.get("/{id}/executions", response_model=List[TestExecutionResponse])
def get_incident_executions(id: int, db: Session = Depends(get_db)):
    """
    Retrieve execution history for an incident.
    """
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    return db.query(TestExecution).filter(TestExecution.incident_id == id).order_by(TestExecution.created_at.desc()).all()
