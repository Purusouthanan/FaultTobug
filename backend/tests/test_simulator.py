import pytest
# Note: `client` fixture is provided by conftest.py (session-scoped, in-memory DB)

def test_nurse_cannot_modify_prescription(client):
    # Login as nurse to get token
    response = client.post("/auth/login", data={"username": "nurse_joy", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Attempt to modify prescription 1
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch("/prescriptions/1?instructions=take daily", headers=headers)
    
    # Assert Nurse is denied (403)
    assert response.status_code == 403
    # Hardened: check that the detail contains the key role and action info
    detail = response.json()["detail"]
    assert "Nurse" in detail
    assert "modify" in detail.lower() or "prescriptions" in detail.lower()

def test_doctor_can_modify_prescription(client):
    # Login as doctor to get token
    response = client.post("/auth/login", data={"username": "dr_smith", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Attempt to modify prescription 1
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch("/prescriptions/1?instructions=take daily", headers=headers)
    
    # Assert Doctor is allowed (200)
    assert response.status_code == 200
    assert response.json()["instructions"] == "take daily"

def test_admin_can_access_anything(client):
    # Login as admin to get token
    response = client.post("/auth/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Attempt to view patients
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/patients/", headers=headers)
    
    # Assert Admin is allowed (200)
    assert response.status_code == 200

