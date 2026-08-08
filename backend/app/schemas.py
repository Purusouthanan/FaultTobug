from pydantic import BaseModel
from typing import Optional

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

    class Config:
        from_attributes = True
