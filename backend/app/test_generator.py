"""
Regression Test Generator
=========================
Converts structured reproduction steps into executable Pytest python code.
Supports multi-role RBAC boundary assertions across Doctor, Nurse, Billing Clerk, etc.
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
    
    token_map = {
        "admin": "admin",
        "doctor": "dr_smith",
        "nurse": "nurse_joy",
        "receptionist": "receptionist_amy",
        "billing clerk": "clerk_bob",
        "clerk": "clerk_bob",
        "billing": "clerk_bob",
    }

    for step in steps:
        step_num = step.get("step", "?")
        stype = step.get("type")
        is_boundary = step.get("is_boundary_check", False)
        desc = step.get("description", "")
        
        if stype == "login":
            role_raw = step.get("role", "Unknown")
            role_key = role_raw.lower().strip()
            
            # Match tokens
            token = token_map.get(role_key)
            if not token:
                if "clerk" in role_key or "billing" in role_key:
                    token = "clerk_bob"
                elif "reception" in role_key:
                    token = "receptionist_amy"
                else:
                    token = "unknown_token"
                    
            prefix = "    # RBAC Boundary Check: " if is_boundary else "    # "
            lines.append(f"{prefix}Step {step_num}: Login as {role_raw}")
            
            if role_key != "unknown":
                lines.append(f"    headers = {{'Authorization': 'Bearer {token}'}}")
            else:
                lines.append(f"    headers = {{}}")
                
        elif stype == "request":
            has_request = True
            method = step.get("method", "GET").lower()
            endpoint = step.get("endpoint", "/").replace("{id}", "1")
            
            prefix = "    # RBAC Boundary Check: " if is_boundary else "    # "
            lines.append(f"{prefix}Step {step_num}: Make {method.upper()} request to {endpoint}")
            if method != "unknown":
                if method in ["post", "patch", "put"]:
                    lines.append(f"    response = client.{method}('{endpoint}', headers=headers, json={{}})")
                else:
                    lines.append(f"    response = client.{method}('{endpoint}', headers=headers)")
            else:
                lines.append(f"    response = client.get('/', headers=headers)")
                
        elif stype == "assert":
            expected = step.get("expected_result", "")
            prefix = "    # RBAC Boundary Check: " if is_boundary else "    # "
            lines.append(f"{prefix}Step {step_num}: Assert {expected}")
            if not has_request:
                lines.append(f"    # No request made, skipping assertion")
                continue
                
            if "200" in expected or "Allow" in expected:
                lines.append(f"    assert response.status_code == 200")
            elif "403" in expected or "Deny" in expected:
                lines.append(f"    assert response.status_code == 403")
            elif "401" in expected:
                lines.append(f"    assert response.status_code == 401")
            elif "404" in expected:
                lines.append(f"    assert response.status_code == 404")
            elif "422" in expected:
                lines.append(f"    assert response.status_code == 422")
            else:
                lines.append(f"    assert response.status_code is not None")

    return "\n".join(lines) + "\n"
