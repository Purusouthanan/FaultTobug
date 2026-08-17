from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Incident, RegressionTest, SuiteExecution
from ..schemas import RegressionTestResponse, SuiteExecutionResponse
from ..execution_engine import execute_suite

router = APIRouter(prefix="/regression", tags=["Regression Repository"])

@router.post("/register/{incident_id}", response_model=RegressionTestResponse)
def register_test(incident_id: int, db: Session = Depends(get_db)):
    """
    Register an incident's generated test into the regression repository.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    if not incident.generated_test_code:
        raise HTTPException(status_code=400, detail="Incident has no generated test code to register")
        
    # Check if already registered
    existing = db.query(RegressionTest).filter(RegressionTest.incident_id == incident_id).first()
    if existing:
        # Update existing
        existing.test_code = incident.generated_test_code
        db.commit()
        db.refresh(existing)
        return existing

    new_test = RegressionTest(
        incident_id=incident_id,
        test_code=incident.generated_test_code
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)
    return new_test

@router.get("/tests", response_model=List[RegressionTestResponse])
def get_registered_tests(db: Session = Depends(get_db)):
    """
    Retrieve all registered regression tests.
    """
    return db.query(RegressionTest).all()

@router.post("/suite/execute", response_model=SuiteExecutionResponse)
def execute_regression_suite(db: Session = Depends(get_db)):
    """
    Execute all registered regression tests as a suite.
    """
    tests = db.query(RegressionTest).all()
    if not tests:
        raise HTTPException(status_code=400, detail="No registered regression tests found in the repository")
        
    # Execute suite
    result = execute_suite(tests)
    
    suite_execution = SuiteExecution(
        total_tests=result["total_tests"],
        passed_tests=result["passed_tests"],
        failed_tests=result["failed_tests"],
        execution_time=result["execution_time"],
        logs=result["logs"]
    )
    db.add(suite_execution)
    db.commit()
    db.refresh(suite_execution)
    
    return suite_execution

@router.get("/suite/executions", response_model=List[SuiteExecutionResponse])
def get_suite_executions(db: Session = Depends(get_db)):
    """
    Retrieve suite execution history.
    """
    return db.query(SuiteExecution).order_by(SuiteExecution.created_at.desc()).all()
