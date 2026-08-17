import pytest

def test_incident_23_baseline(client):
    """Generated Baseline Test for Incident 23"""
    # Naive assumptions based on keywords:
    headers = {'Authorization': 'Bearer mock_nurse_token'}
    
    response = client.get('/patients/1', headers=headers)
    
    assert response.status_code == 200
