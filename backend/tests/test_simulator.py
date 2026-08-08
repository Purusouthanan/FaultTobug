from fastapi.testclient import TestClient
from backend.app.main import app
import pytest

client = TestClient(app)

def test_nurse_cannot_modify_prescription():
    # Login as nurse to get token
    response = client.post("/auth/login", data={"username": "nurse_joy", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Attempt to modify prescription 1
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch("/prescriptions/1?instructions=take daily", headers=headers)
    
    # Assert Nurse is denied (403)
    assert response.status_code == 403
    assert "cannot modify prescriptions" in response.json()["detail"]

def test_doctor_can_modify_prescription():
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

def test_admin_can_access_anything():
    # Login as admin to get token
    response = client.post("/auth/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Attempt to view patients
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/patients/", headers=headers)
    
    # Assert Admin is allowed (200)
    assert response.status_code == 200
