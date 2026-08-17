def generate_baseline_test(incident_id: int, description: str) -> str:
    """
    A naive baseline engine that attempts to generate Pytest code directly
    from an unstructured text description using keyword heuristics.
    
    This deliberately lacks the structured analysis and reproduction steps 
    of the main prototype to serve as a point of comparison.
    """
    desc_lower = description.lower()
    
    # 1. Guess Role (default to unauthenticated if not mentioned)
    headers_code = "headers = {}"
    if "admin" in desc_lower:
        headers_code = "headers = {'Authorization': 'Bearer mock_admin_token'}"
    elif "doctor" in desc_lower:
        headers_code = "headers = {'Authorization': 'Bearer mock_doctor_token'}"
    elif "nurse" in desc_lower:
        headers_code = "headers = {'Authorization': 'Bearer mock_nurse_token'}"

    # 2. Guess Method
    method = "get"
    if "create" in desc_lower or "post" in desc_lower:
        method = "post"
    elif "update" in desc_lower or "modify" in desc_lower or "patch" in desc_lower:
        method = "patch"
    elif "delete" in desc_lower or "remove" in desc_lower:
        method = "delete"

    # 3. Guess Endpoint
    endpoint = "/"
    if "patient" in desc_lower:
        endpoint = "/patients/" if method == "post" else "/patients/1"
    elif "prescription" in desc_lower:
        endpoint = "/prescriptions/" if method == "post" else "/prescriptions/1"
    elif "incident" in desc_lower:
        endpoint = "/incidents/" if method == "post" else "/incidents/1"

    # 4. Guess Expected Outcome
    expected_status = 200
    if "fail" in desc_lower or "unauthorized" in desc_lower or "deny" in desc_lower or "cannot" in desc_lower:
        # The naive baseline assumes a failure means 403 Forbidden. It won't know if it's 401 or 404.
        expected_status = 403
        
    if method == "post" and expected_status == 200:
        expected_status = 201

    json_payload = "json={}" if method in ["post", "patch", "put"] else ""
    comma = ", " if json_payload else ""
    
    # Generate the naive test code
    code = f"""import pytest

def test_incident_{incident_id}_baseline(client):
    \"\"\"Generated Baseline Test for Incident {incident_id}\"\"\"
    # Naive assumptions based on keywords:
    {headers_code}
    
    response = client.{method}('{endpoint}', headers=headers{comma}{json_payload})
    
    assert response.status_code == {expected_status}
"""
    
    return code
