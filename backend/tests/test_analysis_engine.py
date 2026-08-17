"""
Tests for the Incident Analysis Engine.
Verifies entity extraction, RBAC-aware expected behavior resolution,
failure classification, and safe handling of unknown/vague incidents.
"""
import pytest
import sys
import os

# Add workspace root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from backend.app.analysis_engine import analyze_incident
# Note: `client` fixture is provided by conftest.py (session-scoped, in-memory DB)


# ---------------------------------------------------------------------------
# Unit tests for the analysis engine logic
# ---------------------------------------------------------------------------

def test_clear_nurse_prescription_incident():
    """Classic permission bug: Nurse successfully modifying a prescription."""
    result = analyze_incident(
        "A nurse was able to modify a patient's prescription even though nurses "
        "are not allowed to modify prescriptions."
    )
    assert result.role == "Nurse"
    assert result.action == "modify"
    assert result.resource == "prescriptions"
    assert result.expected_result == "Deny (HTTP 403)"     # from rbac.yaml
    assert result.actual_result == "Success (HTTP 200)"    # "was able to" signals success
    assert result.failure_category == "Authorization"
    assert result.confidence == "high"


def test_doctor_allowed_to_modify_prescription():
    """Doctor has correct permission — engine should reflect Allow expectation."""
    result = analyze_incident(
        "Doctor successfully modified a patient's prescription."
    )
    assert result.role == "Doctor"
    assert result.action == "modify"
    assert result.resource == "prescriptions"
    assert result.expected_result == "Allow (HTTP 200)"    # Doctor can modify
    assert result.actual_result == "Success (HTTP 200)"


def test_nurse_denied_access_detection():
    """Engine correctly detects an unexpected denial incident."""
    result = analyze_incident(
        "Nurse received 403 when trying to view patient records."
    )
    assert result.role == "Nurse"
    assert result.action == "view"
    assert result.resource == "patients"
    # Nurse CAN view patients — so denial is unexpected
    assert result.expected_result == "Allow (HTTP 200)"
    assert result.actual_result == "Denied (HTTP 403)"


def test_unknown_vague_incident():
    """Vague incident with no identifiable entities should return Unknown category and low confidence."""
    result = analyze_incident(
        "Something went wrong in the system yesterday."
    )
    assert result.role is None
    assert result.action is None
    assert result.failure_category == "Unknown"
    assert result.confidence == "low"


def test_endpoint_and_method_mapping():
    """Verifies that the correct HTTP method and endpoint are mapped."""
    result = analyze_incident(
        "Nurse was able to modify a prescription."
    )
    assert result.http_method == "PATCH"
    assert result.endpoint == "/prescriptions/{id}"


# ---------------------------------------------------------------------------
# Integration tests — analysis via the API endpoint
# ---------------------------------------------------------------------------

def test_api_analyze_endpoint_full_flow(client):
    """Create an incident, run /analyze, verify the DB record is updated."""
    # Create incident
    create_resp = client.post(
        "/incidents/",
        json={"description": "Nurse successfully modified a patient's prescription."}
    )
    assert create_resp.status_code == 200
    incident_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "OPEN"

    # Trigger analysis
    analyze_resp = client.post(f"/incidents/{incident_id}/analyze")
    assert analyze_resp.status_code == 200
    data = analyze_resp.json()

    assert data["status"] == "ANALYZED"
    assert data["extracted_role"] == "Nurse"
    assert data["extracted_action"] == "modify"
    assert data["extracted_resource"] == "prescriptions"
    assert data["failure_category"] == "Authorization"


def test_api_analyze_unknown_incident_marks_error(client):
    """Vague incident that cannot be analyzed should be marked ERROR."""
    create_resp = client.post(
        "/incidents/",
        json={"description": "Something broke."}
    )
    incident_id = create_resp.json()["id"]

    analyze_resp = client.post(f"/incidents/{incident_id}/analyze")
    assert analyze_resp.status_code == 200
    assert analyze_resp.json()["status"] == "ERROR"
