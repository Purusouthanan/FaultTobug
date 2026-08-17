from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import datetime

class IncidentBase(BaseModel):
    description: str

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    extracted_role: Optional[str] = None
    extracted_action: Optional[str] = None
    extracted_resource: Optional[str] = None
    extracted_endpoint: Optional[str] = None
    extracted_method: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    failure_category: Optional[str] = None
    reproduction_steps: Optional[str] = None
    generated_test_code: Optional[str] = None
    baseline_test_code: Optional[str] = None

class TestExecutionResponse(BaseModel):
    id: int
    incident_id: int
    status: str
    execution_time: Optional[float] = None
    logs: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class IncidentResponse(IncidentBase):
    id: int
    status: str
    extracted_role: Optional[str] = None
    extracted_action: Optional[str] = None
    extracted_resource: Optional[str] = None
    extracted_endpoint: Optional[str] = None
    extracted_method: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    failure_category: Optional[str] = None
    reproduction_steps: Optional[str] = None
    generated_test_code: Optional[str] = None
    baseline_test_code: Optional[str] = None
    executions: List[TestExecutionResponse] = []

    model_config = ConfigDict(from_attributes=True)

class RegressionTestResponse(BaseModel):
    id: int
    incident_id: int
    test_code: str
    registered_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)

class SuiteExecutionResponse(BaseModel):
    id: int
    total_tests: int
    passed_tests: int
    failed_tests: int
    execution_time: Optional[float] = None
    logs: Optional[str] = None
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)
