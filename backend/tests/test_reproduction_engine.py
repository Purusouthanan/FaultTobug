import pytest
import json
from app.reproduction_engine import generate_reproduction_steps

def test_generate_reproduction_steps_unit():
    incident_data = {
        "extracted_role": "Nurse",
        "extracted_method": "PATCH",
        "extracted_endpoint": "/prescriptions/{id}",
        "expected_result": "Allow (HTTP 200)"
    }
    
    steps = generate_reproduction_steps(incident_data)
    
    assert len(steps) == 3
    assert steps[0]["type"] == "login"
    assert steps[0]["role"] == "Nurse"
    
    assert steps[1]["type"] == "request"
    assert steps[1]["method"] == "PATCH"
    assert steps[1]["endpoint"] == "/prescriptions/{id}"
    
    assert steps[2]["type"] == "assert"
    assert steps[2]["expected_result"] == "Allow (HTTP 200)"

def test_generate_reproduction_steps_missing_data():
    incident_data = {}
    
    steps = generate_reproduction_steps(incident_data)
    
    assert len(steps) == 3
    assert steps[0]["role"] == "Unknown"
    assert steps[1]["method"] == "UNKNOWN"
    assert steps[2]["expected_result"] == "Unknown"

def test_reproduce_incident_endpoint(client):
    # 1. Create incident
    response = client.post("/incidents/", json={"description": "Nurse modifies prescription"})
    incident_id = response.json()["id"]

    # Analyze it (to set it to ANALYZED state and populate data)
    client.patch(f"/incidents/{incident_id}", json={
        "status": "ANALYZED",
        "extracted_role": "Nurse",
        "extracted_method": "PATCH",
        "extracted_endpoint": "/prescriptions/{id}",
        "expected_result": "Allow (HTTP 200)"
    })

    # 2. Call reproduce endpoint
    response = client.post(f"/incidents/{incident_id}/reproduce")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "REPRODUCED"
    assert data["reproduction_steps"] is not None
    
    # 3. Verify parsed JSON
    steps = json.loads(data["reproduction_steps"])
    assert len(steps) == 3
    assert steps[0]["role"] == "Nurse"

def test_reproduce_unassayed_incident_fails(client):
    # 1. Create incident with OPEN status
    response = client.post("/incidents/", json={"description": "Just opened"})
    incident_id = response.json()["id"]

    # 2. Call reproduce endpoint
    response = client.post(f"/incidents/{incident_id}/reproduce")
    assert response.status_code == 400
    assert "ANALYZED before reproducing" in response.json()["detail"]

def test_reproduction_multi_role_rbac_boundary_steps():
    incident_data = {
        "extracted_role": "Nurse",
        "extracted_action": "modify",
        "extracted_resource": "prescriptions",
        "extracted_method": "PATCH",
        "extracted_endpoint": "/prescriptions/{id}",
        "expected_result": "Deny (HTTP 403)"
    }
    
    steps = generate_reproduction_steps(incident_data, include_boundaries=True)
    
    # 3 primary steps + 2 boundary roles (Doctor, Billing Clerk) * 3 steps = 9 steps
    assert len(steps) == 9
    
    # Primary role check
    assert steps[0]["role"] == "Nurse"
    assert steps[2]["expected_result"] == "Deny (HTTP 403)"
    
    # Doctor boundary check (Doctor CAN modify prescriptions -> Allow 200)
    doctor_login = [s for s in steps if s.get("role") == "Doctor"][0]
    assert doctor_login["is_boundary_check"] is True
    doctor_assert = [s for s in steps if s.get("type") == "assert" and "Doctor" in s.get("description", "")][0]
    assert doctor_assert["expected_result"] == "Allow (HTTP 200)"
    
    # Billing Clerk boundary check (Billing Clerk CANNOT modify prescriptions -> Deny 403)
    clerk_login = [s for s in steps if s.get("role") == "Billing Clerk"][0]
    assert clerk_login["is_boundary_check"] is True
    clerk_assert = [s for s in steps if s.get("type") == "assert" and "Billing Clerk" in s.get("description", "")][0]
    assert clerk_assert["expected_result"] == "Deny (HTTP 403)"

