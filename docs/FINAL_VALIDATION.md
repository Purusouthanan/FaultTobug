# Final Validation & Limitations Report

This document outlines the final validation checks performed on the Incident-to-Regression Automation Platform (Phase 13), along with an analysis of its limitations and error states.

## Sanity Checks

### API Health
- **Check:** `GET /health` and `GET /db-health`
- **Result:** `PASS`. Endpoints are reachable and correctly return operational status.

### End-to-End Edge Cases
- **Check:** Submit a highly vague, non-actionable incident ("A user did a random thing and the system crashed").
- **Result:** `PASS`. The Analysis Engine correctly identified the `failure_category` as `Unknown` instead of hallucinating parameters.

### Role-Based Access Control (RBAC)
- **Check:** Verify that users without the `delete` permission (e.g., `Nurse`) cannot delete a patient.
- **Result:** `PASS`. The backend returns `403 Forbidden` correctly (as verified during Phase 12's bug-fix demonstration).

---

## Known Limitations

While the prototype successfully demonstrated the ability to convert simple bug reports into regression tests, several limitations exist that must be addressed before production deployment:

### 1. Complex State Setup (Multi-step tests)
- **Limitation:** The current `test_generator.py` only handles single-step requests (e.g., Login -> Request -> Assert).
- **Impact:** If an incident requires complex pre-requisite state (e.g., "Create a patient, discharge them, then attempt to prescribe medication"), the pipeline cannot currently generate the setup steps unless explicitly guided by the LLM in the `reproduce` phase.

### 2. LLM Hallucinations on Vague Input
- **Limitation:** Although we added a check for "Unknown", if an incident mentions words that look like endpoints (e.g., "failed to get user info"), the LLM might guess the endpoint is `/users/info` even if the real endpoint is `/api/v1/profile`.
- **Mitigation:** Future iterations should provide the LLM with an OpenAPI schema (Swagger JSON) to constrain its endpoint extraction strictly to valid routes.

### 3. Static Test Accounts
- **Limitation:** The `test_generator.py` relies on hardcoded user aliases (e.g., `nurse_joy`) mapped to `mock_nurse_token`.
- **Impact:** If the authentication system changes or tests require specific data topologies linked to specific users, static accounts will cause test flakiness.

### 4. Dynamic Code Execution Risks
- **Limitation:** Running `pytest` dynamically inside a subprocess (`execution_engine.py`) requires a carefully sandboxed in-memory SQLite database (`test_engine`) to prevent tests from wiping production data.
- **Impact:** In a real distributed microservice environment, setting up an isolated ephemeral database for every test execution is complex and resource-intensive.

## Conclusion

The platform effectively meets its MVP goals. It accurately translates natural language bugs into passing tests for straightforward endpoints. To scale to complex, stateful enterprise applications, the reproduction engine will need OpenAPI awareness and the test generator will need a multi-step DSL.
