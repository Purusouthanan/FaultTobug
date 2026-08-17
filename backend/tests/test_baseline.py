import pytest
from app.baseline_engine import generate_baseline_test

def test_generate_baseline_test_unit():
    desc = "Admin tries to create a new patient and it fails."
    code = generate_baseline_test(100, desc)
    
    assert "mock_admin_token" in code
    assert "client.post" in code
    assert "/patients/" in code
    assert "status_code == 403" in code

def test_generate_baseline_test_endpoint(client):
    # 1. Create incident
    response = client.post("/incidents/", json={"description": "Doctor update prescription"})
    incident_id = response.json()["id"]

    # 2. Call Baseline generator
    response = client.post(f"/baseline/incidents/{incident_id}/generate-test")
    assert response.status_code == 200
    
    data = response.json()
    code = data["baseline_test_code"]
    
    assert code is not None
    assert "mock_doctor_token" in code
    assert "client.patch" in code
    assert "status_code == 200" in code
