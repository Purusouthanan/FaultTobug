import pytest

def test_register_and_fetch_regression_test(client):
    # 1. Setup Incident with code
    response = client.post("/incidents/", json={"description": "Test regression registration"})
    incident_id = response.json()["id"]

    client.patch(f"/incidents/{incident_id}", json={
        "status": "TEST_GENERATED",
        "generated_test_code": "def test_dummy1(client):\n    assert True"
    })
    
    # 2. Register
    response = client.post(f"/regression/register/{incident_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == incident_id
    assert "test_dummy1" in data["test_code"]
    
    # 3. List
    response = client.get("/regression/tests")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert any(t["incident_id"] == incident_id for t in response.json())

def test_execute_regression_suite(client):
    # 1. Register multiple tests
    response1 = client.post("/incidents/", json={"description": "Test 1"})
    incident1_id = response1.json()["id"]
    client.patch(f"/incidents/{incident1_id}", json={
        "status": "TEST_GENERATED",
        "generated_test_code": "def test_pass_1(client):\n    assert True"
    })
    client.post(f"/regression/register/{incident1_id}")
    
    response2 = client.post("/incidents/", json={"description": "Test 2"})
    incident2_id = response2.json()["id"]
    client.patch(f"/incidents/{incident2_id}", json={
        "status": "TEST_GENERATED",
        "generated_test_code": "def test_fail_1(client):\n    assert False"
    })
    client.post(f"/regression/register/{incident2_id}")

    # 2. Execute suite
    response = client.post("/regression/suite/execute")
    assert response.status_code == 200
    data = response.json()
    
    # Our suite will have all registered tests, including the one from the previous test function.
    assert data["total_tests"] >= 3
    assert data["passed_tests"] >= 2
    assert data["failed_tests"] >= 1
    
    # 3. Fetch history
    response = client.get("/regression/suite/executions")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 1
    assert history[0]["id"] == data["id"]
