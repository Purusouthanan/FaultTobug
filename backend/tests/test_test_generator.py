import pytest
from app.test_generator import generate_pytest_code

def test_generate_pytest_code_unit():
    steps = [
        {"step": 1, "type": "login", "role": "Nurse"},
        {"step": 2, "type": "request", "method": "PATCH", "endpoint": "/prescriptions/{id}"},
        {"step": 3, "type": "assert", "expected_result": "Allow (HTTP 200)"}
    ]
    
    code = generate_pytest_code(123, steps)
    
    assert "def test_incident_123_regression(client):" in code
    assert "headers = {'Authorization': 'Bearer nurse_joy'}" in code
    assert "response = client.patch('/prescriptions/1', headers=headers, json={})" in code
    assert "assert response.status_code == 200" in code
    
    # Very basic validation that it executes
    # We create a dummy client to pass to the exec scope
    class DummyClient:
        def patch(self, url, headers, json):
            class DummyResponse:
                status_code = 200
            return DummyResponse()
            
    exec_scope = {"pytest": pytest, "client": DummyClient()}
    exec(code, exec_scope)
    exec_scope["test_incident_123_regression"](exec_scope["client"])

def test_generate_test_endpoint(client):
    # 1. Create incident
    response = client.post("/incidents/", json={"description": "Nurse modifies prescription"})
    incident_id = response.json()["id"]

    # Analyze it
    client.patch(f"/incidents/{incident_id}", json={
        "status": "ANALYZED",
        "extracted_role": "Nurse",
        "extracted_method": "PATCH",
        "extracted_endpoint": "/prescriptions/{id}",
        "expected_result": "Allow (HTTP 200)"
    })
    
    # Reproduce it
    client.post(f"/incidents/{incident_id}/reproduce")
    
    # 2. Generate test
    response = client.post(f"/incidents/{incident_id}/generate-test")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "TEST_GENERATED"
    assert data["generated_test_code"] is not None
    assert "test_incident_" in data["generated_test_code"]

def test_generate_test_fails_if_not_reproduced(client):
    response = client.post("/incidents/", json={"description": "Just opened"})
    incident_id = response.json()["id"]

    response = client.post(f"/incidents/{incident_id}/generate-test")
    assert response.status_code == 400
    assert "REPRODUCED before generating test" in response.json()["detail"]

def test_generate_pytest_code_multi_role_rbac_matrix():
    steps = [
        {"step": 1, "type": "login", "role": "Nurse"},
        {"step": 2, "type": "request", "method": "PATCH", "endpoint": "/prescriptions/1"},
        {"step": 3, "type": "assert", "expected_result": "Deny (HTTP 403)"},
        {"step": 4, "type": "login", "role": "Doctor", "is_boundary_check": True},
        {"step": 5, "type": "request", "method": "PATCH", "endpoint": "/prescriptions/1", "is_boundary_check": True},
        {"step": 6, "type": "assert", "expected_result": "Allow (HTTP 200)", "is_boundary_check": True},
        {"step": 7, "type": "login", "role": "Billing Clerk", "is_boundary_check": True},
        {"step": 8, "type": "request", "method": "PATCH", "endpoint": "/prescriptions/1", "is_boundary_check": True},
        {"step": 9, "type": "assert", "expected_result": "Deny (HTTP 403)", "is_boundary_check": True},
    ]
    
    code = generate_pytest_code(99, steps)
    
    assert "def test_incident_99_regression(client):" in code
    # Nurse primary
    assert "Bearer nurse_joy" in code
    assert "assert response.status_code == 403" in code
    # Doctor boundary
    assert "Bearer dr_smith" in code
    assert "assert response.status_code == 200" in code
    # Billing Clerk boundary
    assert "Bearer clerk_bob" in code

