"""
Regression Test Generator
=========================
Converts structured reproduction steps into executable Pytest python code.
"""

def generate_pytest_code(incident_id: int, steps: list[dict]) -> str:
    """
    Generate executable Pytest code from reproduction steps.
    """
    lines = [
        "import pytest",
        "",
        f"def test_incident_{incident_id}_regression(client):",
        f"    \"\"\"Generated Regression Test for Incident {incident_id}\"\"\""
    ]
    
    has_request = False

    for step in steps:
        step_num = step.get("step", "?")
        stype = step.get("type")
        
        if stype == "login":
            role = step.get("role", "Unknown").lower()
            lines.append(f"    # Step {step_num}: Login as {role.capitalize()}")
            
            token_map = {
                "admin": "admin",
                "doctor": "dr_smith",
                "nurse": "nurse_joy"
            }
            token = token_map.get(role, "unknown_token")
            
            if role != "unknown":
                lines.append(f"    headers = {{'Authorization': 'Bearer {token}'}}")
            else:
                lines.append(f"    headers = {{}}")
                
        elif stype == "request":
            has_request = True
            method = step.get("method", "GET").lower()
            endpoint = step.get("endpoint", "/").replace("{id}", "1")
            
            lines.append(f"    # Step {step_num}: Make {method.upper()} request to {endpoint}")
            if method != "unknown":
                if method in ["post", "patch", "put"]:
                    lines.append(f"    response = client.{method}('{endpoint}', headers=headers, json={{}})")
                else:
                    lines.append(f"    response = client.{method}('{endpoint}', headers=headers)")
            else:
                lines.append(f"    response = client.get('/', headers=headers)")
                
        elif stype == "assert":
            expected = step.get("expected_result", "")
            lines.append(f"    # Step {step_num}: Assert {expected}")
            if not has_request:
                lines.append(f"    # No request made, skipping assertion")
                continue
                
            if "200" in expected:
                lines.append(f"    assert response.status_code == 200")
            elif "403" in expected:
                lines.append(f"    assert response.status_code == 403")
            else:
                lines.append(f"    # Unknown expected result, generic assert")
                lines.append(f"    assert response.status_code is not None")

    return "\n".join(lines) + "\n"
