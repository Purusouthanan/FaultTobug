import pytest
import os
from app.execution_engine import execute_test

def test_execution_engine_pass():
    test_code = """
import pytest

def test_dummy_pass(client):
    assert True
"""
    result = execute_test(999, test_code)
    
    assert result["status"] == "PASS"
    assert result["execution_time"] > 0
    assert "test_dummy_pass PASSED" in result["logs"] or "1 passed" in result["logs"]

def test_execution_engine_fail():
    test_code = """
import pytest

def test_dummy_fail(client):
    assert False
"""
    result = execute_test(998, test_code)
    
    assert result["status"] == "FAIL"
    assert "1 failed" in result["logs"]

def test_execution_endpoints(client):
    # 1. Create incident and push it to TEST_GENERATED state
    response = client.post("/incidents/", json={"description": "Execution test"})
    incident_id = response.json()["id"]

    # We skip analysis/reproduction and just patch generated code directly for the test
    client.patch(f"/incidents/{incident_id}", json={
        "status": "TEST_GENERATED",
        "generated_test_code": "def test_api(client):\n    assert client.get('/incidents/').status_code == 200\n"
    })
    
    # 2. Call Execute endpoint
    response = client.post(f"/incidents/{incident_id}/execute")
    assert response.status_code == 200
    
    data = response.json()
    assert data["incident_id"] == incident_id
    assert data["status"] == "PASS"
    assert "1 passed" in data["logs"]
    
    # 3. Verify status updated
    response = client.get(f"/incidents/{incident_id}")
    assert response.json()["status"] == "TEST_EXECUTED"
    
    # 4. Fetch executions
    response = client.get(f"/incidents/{incident_id}/executions")
    executions = response.json()
    assert len(executions) == 1
    assert executions[0]["status"] == "PASS"

def test_execute_fails_without_code(client):
    response = client.post("/incidents/", json={"description": "Empty"})
    incident_id = response.json()["id"]
    
    response = client.post(f"/incidents/{incident_id}/execute")
    assert response.status_code == 400
    assert "no generated test code" in response.json()["detail"]
