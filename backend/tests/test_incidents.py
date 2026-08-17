import pytest
# Note: `client` fixture is provided by conftest.py (session-scoped, in-memory DB)

def test_create_and_retrieve_incident(client):
    # Create incident
    response = client.post("/incidents/", json={"description": "Nurse modified prescription"})
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Nurse modified prescription"
    assert data["status"] == "OPEN"
    incident_id = data["id"]
    
    # Retrieve incident
    response = client.get(f"/incidents/{incident_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == incident_id
    assert data["status"] == "OPEN"

def test_update_incident_status_and_data(client):
    # Create incident
    response = client.post("/incidents/", json={"description": "Doctor created patient"})
    incident_id = response.json()["id"]
    
    # Update incident with extracted data
    update_data = {
        "status": "ANALYZED",
        "extracted_role": "Doctor",
        "extracted_action": "create",
        "extracted_resource": "patients"
    }
    response = client.patch(f"/incidents/{incident_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ANALYZED"
    assert data["extracted_role"] == "Doctor"
    assert data["extracted_action"] == "create"
    assert data["extracted_resource"] == "patients"
    
    # Verify persistence
    response = client.get(f"/incidents/{incident_id}")
    assert response.json()["status"] == "ANALYZED"
    assert response.json()["extracted_role"] == "Doctor"
