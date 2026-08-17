"""
Reproduction Engine
===================
Converts analyzed incident information into structured reproduction steps.
These steps can be stored and later used to generate actual regression tests.
"""

def generate_reproduction_steps(incident_data: dict) -> list[dict]:
    """
    Generate sequential reproduction steps from incident data.
    
    Expected incident_data keys:
    - extracted_role
    - extracted_method
    - extracted_endpoint
    - expected_result
    """
    role = incident_data.get("extracted_role")
    method = incident_data.get("extracted_method")
    endpoint = incident_data.get("extracted_endpoint")
    expected = incident_data.get("expected_result")

    steps = []

    # Step 1: Login
    if role:
        steps.append({
            "step": 1,
            "type": "login",
            "role": role,
            "description": f"Login as {role} and obtain token"
        })
    else:
        steps.append({
            "step": 1,
            "type": "login",
            "role": "Unknown",
            "description": "Attempt login without specific role"
        })

    # Step 2: Make Request
    if method and endpoint:
        steps.append({
            "step": 2,
            "type": "request",
            "method": method,
            "endpoint": endpoint,
            "description": f"Attempt {method} request to {endpoint}"
        })
    else:
        steps.append({
            "step": 2,
            "type": "request",
            "method": "UNKNOWN",
            "endpoint": "UNKNOWN",
            "description": "Attempt request to unknown endpoint"
        })

    # Step 3: Assert expected response
    if expected:
        steps.append({
            "step": 3,
            "type": "assert",
            "expected_result": expected,
            "description": f"Verify response matches expected behavior: {expected}"
        })
    else:
        steps.append({
            "step": 3,
            "type": "assert",
            "expected_result": "Unknown",
            "description": "Verify response matches unknown behavior"
        })

    return steps
