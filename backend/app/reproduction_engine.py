"""
Reproduction Engine
===================
Converts analyzed incident information into structured reproduction steps.
These steps can be stored and later used to generate actual regression tests.

Supports:
- Single-role primary incident reproduction
- Multi-role RBAC boundary matrix testing (Doctor vs. Nurse vs. Billing Clerk)
"""
import os
import yaml
from typing import Optional, List, Dict, Any

def _load_rbac_config() -> dict:
    config_dir = os.path.join(os.path.dirname(__file__), "../config")
    path = os.path.join(config_dir, "rbac.yaml")
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}

def resolve_role_permission(role: str, resource: str, action: str, rbac: dict) -> str:
    """Resolve expected behavior for a given role from rbac.yaml."""
    if not (role and resource and action):
        return "Unknown"
    
    role_rules = rbac.get("roles", {}).get(role, [])
    decision = "Deny"
    for rule in role_rules:
        r_resource = rule.get("resource", "")
        r_action = rule.get("action", "")
        if (r_resource == resource or r_resource == "*") and \
           (r_action == action or r_action == "*"):
            decision = rule.get("decision", "Deny")
            break
            
    return "Allow (HTTP 200)" if decision == "Allow" else "Deny (HTTP 403)"

def generate_rbac_boundary_steps(
    incident_data: dict, 
    roles_to_compare: Optional[List[str]] = None,
    starting_step: int = 4
) -> List[Dict[str, Any]]:
    """
    Generate RBAC boundary assertions across multi-role scenarios
    (e.g., Doctor vs. Nurse vs. Billing Clerk).
    
    Verifies that while the incident role's behavior is asserted,
    neighboring roles in the RBAC matrix strictly adhere to their boundaries.
    """
    primary_role = (incident_data.get("extracted_role") or "").strip()
    resource = incident_data.get("extracted_resource")
    action = incident_data.get("extracted_action")
    method = incident_data.get("extracted_method", "GET")
    endpoint = incident_data.get("extracted_endpoint", "/")
    
    if not resource or not action:
        return []
        
    rbac = _load_rbac_config()
    all_known_roles = roles_to_compare or ["Doctor", "Nurse", "Billing Clerk"]
    
    boundary_steps = []
    current_step = starting_step
    
    for role in all_known_roles:
        # Don't duplicate the primary incident role
        if role.lower() == primary_role.lower():
            continue
            
        expected = resolve_role_permission(role, resource, action, rbac)
        
        # Step: Login as boundary role
        boundary_steps.append({
            "step": current_step,
            "type": "login",
            "role": role,
            "is_boundary_check": True,
            "description": f"RBAC Boundary Check: Login as {role}"
        })
        current_step += 1
        
        # Step: Attempt the same action on the endpoint
        boundary_steps.append({
            "step": current_step,
            "type": "request",
            "method": method,
            "endpoint": endpoint,
            "is_boundary_check": True,
            "description": f"RBAC Boundary Check: Attempt {method} {endpoint} as {role}"
        })
        current_step += 1
        
        # Step: Assert role's RBAC boundary
        boundary_steps.append({
            "step": current_step,
            "type": "assert",
            "expected_result": expected,
            "is_boundary_check": True,
            "description": f"RBAC Boundary Check: Assert {role} behavior is {expected}"
        })
        current_step += 1
        
    return boundary_steps

def generate_reproduction_steps(
    incident_data: dict, 
    include_boundaries: bool = False,
    boundary_roles: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Generate sequential reproduction steps from incident data.
    
    Expected incident_data keys:
    - extracted_role
    - extracted_method
    - extracted_endpoint
    - expected_result
    - extracted_resource (optional, used for RBAC boundary matrix)
    - extracted_action (optional, used for RBAC boundary matrix)
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

    # RBAC Boundary Matrix expansion if requested
    if include_boundaries:
        boundary_steps = generate_rbac_boundary_steps(
            incident_data, 
            roles_to_compare=boundary_roles,
            starting_step=len(steps) + 1
        )
        steps.extend(boundary_steps)

    return steps
