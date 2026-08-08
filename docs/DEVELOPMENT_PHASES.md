# Development Phases
# Incident-to-Regression Automation Platform

This document is the source of truth for managing the development of the Incident-to-Regression Pipeline project.

**IMPORTANT:**
- We are building this project phase-by-phase.
- Do NOT implement all phases at once.
- Each phase must be completed, tested, verified, and marked complete before moving to the next phase.
- The project is a college project with approximately one week for the first complete working version.

The priority is:
1. Working system
2. Correct end-to-end workflow
3. Measurable results
4. Clear architecture
5. Reliability
6. Innovation
7. Documentation

Do not sacrifice functionality for unnecessary complexity.

---

## PROJECT OBJECTIVE

Build an Incident-to-Regression Pipeline for a hospital management system.

The system should transform:
```text
Production Incident
→ Incident Analysis
→ Failure Classification
→ Workflow Identification
→ Reproduction Steps
→ Regression Test Generation
→ Test Execution
→ Result
→ Regression Repository
→ Metrics
```

The primary evaluation metric is:
**Production incidents successfully converted into passing regression tests.**

---

## DEVELOPMENT MANAGEMENT RULE

For every phase:
1. Define objective
2. Define scope
3. Define implementation tasks
4. Implement
5. Run tests
6. Verify functionality
7. Review code
8. Update documentation
9. Record evidence/results
10. Mark phase complete

**Never mark a phase complete simply because code was written.**
A phase is complete only when its acceptance criteria are satisfied.

---

## PHASE STRUCTURE

### PHASE 0 — Project Foundation
**Set up:**
- Repository
- Project structure
- Environment configuration
- Backend foundation
- Frontend foundation
- Database connection
- Docker configuration if appropriate
- Basic documentation

**Acceptance:**
- Application starts successfully
- Backend health endpoint works
- Database connection works
- Frontend can communicate with backend

---

### PHASE 1 — Hospital Management System Core
Build the minimal hospital simulator.

**Implement:**
- Users
- Roles
- Permissions
- Authentication
- Patients
- Basic workflows

Minimum roles: Admin, Doctor, Nurse. Permissions must be configurable.

**Acceptance:**
- Users can authenticate
- Roles are assigned
- Permissions are evaluated
- Authorized actions succeed
- Unauthorized actions are rejected
- At least two complete workflows work

---

### PHASE 2 — Incident Management
Implement the incident system.

**Implement:**
- Incident model
- Incident creation
- Incident storage
- Incident listing
- Incident details
- Incident lifecycle/status
- Incident traces
- Expected vs actual behavior
- Reproduction information

**Acceptance:**
- Incidents can be created, retrieved, and stored
- Incident status can change
- Realistic incident examples can be stored

---

### PHASE 3 — Incident Analysis Engine
Implement the incident analysis system.

**Extract:**
- Role, Action, Resource, Endpoint, HTTP method, Expected result, Actual result, Failure category, Workflow information

Create configurable rules for failure classification.
Minimum categories: Authentication, Authorization, Validation, Resource access, Duplicate operation, Workflow/state, Unknown.

**Acceptance:**
- Sample incidents are correctly analyzed
- Failure categories are assigned
- Rules are configurable
- Unknown incidents are handled safely

---

### PHASE 4 — Reproduction Engine
Convert incident information into structured reproduction steps.

**Example:**
Incident: "Nurse successfully modified prescription."
Generate:
1. Login as nurse
2. Obtain token
3. Retrieve patient
4. Attempt prescription update
5. Capture response
6. Compare expected vs actual

**Acceptance:**
- Reproduction steps are generated and linked to the incident
- Reproduction information can be reviewed
- At least three incident types can be reproduced

---

### PHASE 5 — Regression Test Generator
Implement automatic generation of executable Pytest tests.

Generated tests must:
- Be valid Python, executable
- Contain incident ID, reproduction steps, assertions, and check expected behavior

**Acceptance:**
- Tests are generated from incidents
- Generated tests execute successfully
- Generated tests fail when the bug exists
- Generated tests pass after the bug is fixed

*(This phase is one of the core project milestones.)*

---

### PHASE 6 — Test Execution Engine
Implement automated execution using Pytest.

**Capture:**
- PASS / FAIL / ERROR
- Execution time
- Error information
- Expected vs Actual result

**Acceptance:**
- Individual generated tests can run
- Complete regression suite can run
- Results are persisted and history is available

---

### PHASE 7 — Regression Repository
Implement storage and management of generated regression tests.

**Support:**
- Test registration, retrieval, version/history, incident linkage, suite execution

**Acceptance:**
- Generated tests remain available after execution
- Tests can be rerun and associated with incidents
- Regression suite can execute multiple tests

---

### PHASE 8 — Baseline Implementation
Create a simple baseline representing a conventional approach.
The baseline should be intentionally simpler than the proposed system.

**Compare:**
- Manual effort, test creation time, conversion success, passing tests, human intervention.
*(Do not fabricate results.)*

**Acceptance:**
- Baseline can process the same validation dataset
- Results can be measured and compared

---

### PHASE 9 — Validation Dataset
Create a realistic synthetic production incident dataset.
Target: 20–30 incidents.

**Include:**
- Authentication, authorization, validation, resource access, and workflow failures
- Duplicate operations, edge cases, incomplete incidents, unsupported scenarios

**Acceptance:**
- Dataset is version controlled with structured information
- Ground-truth expected behavior exists
- Dataset can be processed automatically

---

### PHASE 10 — Experiment and Metrics
Run the baseline and proposed system against the same dataset.

**Primary metric:** Incident-to-Passing-Regression Rate
**Also measure:** Processing time, human intervention, false positives/invalid tests.

**Acceptance:**
- Actual experimental results exist (Baseline vs Prototype)
- Failed cases are explained
- No fabricated metrics

---

### PHASE 11 — Dashboard and UI
Implement the final usable interface.

**Screens:**
- Dashboard, Incident list, Incident details
- Analysis result, Reproduction steps, Generated test
- Test execution, Regression suite, Experiment metrics

**Acceptance:**
- Complete workflow can be demonstrated through UI
- Metrics are based on real data
- Incident-to-test lifecycle is visible

---

### PHASE 12 — End-to-End Integration
Connect everything.

**Final workflow:**
Incident → Analyze → Reproduce → Generate Test → Execute → Fix Application → Execute Again → PASS → Store Regression Test → Update Metrics

**Acceptance:**
- Complete workflow works without manual code editing of generated tests
- Multiple incidents can be processed and passing tests stored

---

### PHASE 13 — Final Validation
Perform functional, edge-case, regression, API, permission, failure testing, and performance sanity checks.

**Document:**
- Passed cases, failed cases, limitations, error analysis.

---

### PHASE 14 — Documentation and Demonstration
Complete: README, PRD, System Architecture, API docs, Experiment report, Metrics, Error analysis, Setup instructions, Demo workflow.

---

## PHASE TRACKING

| Phase | Status | Completion % | Tests | Evidence | Blockers |
|-------|--------|--------------|-------|----------|----------|
| 0 | COMPLETED | 100% | - | - | - |
| 1 | NOT_STARTED | 0% | - | - | - |
| 2 | NOT_STARTED | 0% | - | - | - |
| 3 | NOT_STARTED | 0% | - | - | - |
| 4 | NOT_STARTED | 0% | - | - | - |
| 5 | NOT_STARTED | 0% | - | - | - |
| 6 | NOT_STARTED | 0% | - | - | - |
| 7 | NOT_STARTED | 0% | - | - | - |
| 8 | NOT_STARTED | 0% | - | - | - |
| 9 | NOT_STARTED | 0% | - | - | - |
| 10 | NOT_STARTED | 0% | - | - | - |
| 11 | NOT_STARTED | 0% | - | - | - |
| 12 | NOT_STARTED | 0% | - | - | - |
| 13 | NOT_STARTED | 0% | - | - | - |
| 14 | NOT_STARTED | 0% | - | - | - |

*(Allowed statuses: NOT_STARTED, IN_PROGRESS, BLOCKED, TESTING, COMPLETED. Do not mark COMPLETED without satisfying acceptance criteria.)*

---

## IMPLEMENTATION RULES

1. Work on one phase at a time.
2. Never silently skip a phase.
3. Never start a dependent phase while the previous phase is broken.
4. Keep the project runnable after every phase.
5. Write tests for important functionality.
6. Do not fabricate successful test results.
7. Do not introduce unnecessary technologies.
8. Keep permissions configurable.
9. Keep incident analysis explainable.
10. Keep generated tests executable.
11. Preserve traceability: Incident → Analysis → Reproduction → Generated Test → Execution Result.
12. Maintain documentation as development progresses.
13. If a requirement is ambiguous, flag it rather than inventing unnecessary functionality.
14. Prefer a modular monolith over microservices.
15. The final system must work on modest hardware.

---

## DEFINITION OF DONE

The project is considered complete only when a real end-to-end demonstration can show:

```text
Production-like Incident
        ↓
Incident Analysis
        ↓
Reproduction
        ↓
Generated Regression Test
        ↓
Test Execution
        ↓
Bug Detection
        ↓
Application Fix
        ↓
Regression Test PASS
        ↓
Stored Regression Test
        ↓
Metrics Updated
```

The final measurable result must include Baseline, Target, Actual measured result, Error analysis, and Limitations. 
The primary outcome remains: **"Production incidents converted into passing regression tests."**

---

## IMPORTANT FOR THE DEVELOPMENT AGENT

Do not attempt to implement the entire project in one step.

At the beginning of each development session:
1. Read this file.
2. Identify the current phase.
3. Check the previous phase's acceptance criteria.
4. Inspect the existing implementation.
5. Continue only with the current phase.
6. Run relevant tests.
7. Update this file with progress.
8. Clearly report:
   - What was implemented
   - What was tested
   - What passed
   - What remains
   - Current phase status

The development agent must treat this file as the project's development control document.
