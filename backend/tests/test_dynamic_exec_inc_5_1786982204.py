import pytest

def test_incident_5_baseline(client):
    """Generated Baseline Test for Incident 5"""
    # Naive assumptions based on keywords:
    headers = {'Authorization': 'Bearer mock_admin_token'}
    
    response = client.post('/patients/', headers=headers, json={})
    
    assert response.status_code == 201
