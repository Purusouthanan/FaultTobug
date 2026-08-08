# Product Requirements Document (PRD)
# Incident-to-Regression Pipeline

| Field         | Value                                      |
|---------------|--------------------------------------------|
| Project       | Incident-to-Regression Pipeline            |
| Domain        | Hospital Management System (Simulated)     |
| Version       | 1.0                                        |
| Status        | Draft                                      |
| Date          | August 2026                                |

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Problem Context](#2-problem-context)
3. [Existing / Current Workflow](#3-existing--current-workflow)
4. [Problems with the Current Workflow](#4-problems-with-the-current-workflow)
5. [Proposed Solution](#5-proposed-solution)
6. [Goals and Objectives](#6-goals-and-objectives)
7. [Target Users and Stakeholders](#7-target-users-and-stakeholders)
8. [Core User Workflows](#8-core-user-workflows)
9. [Functional Requirements](#9-functional-requirements)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Incident-to-Regression Workflow](#11-incident-to-regression-workflow)
12. [Role and Permission Requirements](#12-role-and-permission-requirements)
13. [Incident Lifecycle](#13-incident-lifecycle)
14. [Regression Test Lifecycle](#14-regression-test-lifecycle)
15. [Baseline Approach vs. Proposed Approach](#15-baseline-approach-vs-proposed-approach)
16. [Success Metrics and KPIs](#16-success-metrics-and-kpis)
17. [Edge and Failure Cases](#17-edge-and-failure-cases)
18. [Validation and Experiment Requirements](#18-validation-and-experiment-requirements)
19. [Constraints](#19-constraints)
20. [Assumptions](#20-assumptions)
21. [Limitations](#21-limitations)
22. [Out-of-Scope Items](#22-out-of-scope-items)
23. [Expected Final Deliverables](#23-expected-final-deliverables)

---

## 1. Problem Statement

A hospital management system has complex, permission-dependent workflows. When a production incident occurs, the engineering organisation struggles to quickly convert the real-world failure into a reliable, automated regression test. As a result, bugs that were previously fixed can silently reappear in production — because the knowledge captured during incident investigation is never systematically turned into a permanent, executable test.

**The central problem is not a lack of testing. It is a broken knowledge-transfer loop between production incidents and the regression test suite.**

---

## 2. Problem Context

Hospital management systems enforce strict role-based access control (RBAC). Different staff roles — such as doctors, nurses, receptionists, and administrators — are permitted to perform different actions on patient data, prescriptions, and clinical records. A failure in these permission rules can have serious consequences: unauthorized data modification, privacy violations, or dangerous clinical actions.

Permission rules are also complex and contextual. A nurse may be allowed to view a prescription but not modify it. A doctor may be allowed to modify a prescription for their own patients but not those of another department. These rules may change over time as organizational policies evolve.

When a permission-related bug surfaces in production, the incident is typically recorded in a ticket describing what happened — the role involved, the action taken, and what the system allowed or denied incorrectly. This information exists in natural language. It is then investigated manually, and if a fix is applied, no formal automated test is written to verify that the same failure cannot recur. The knowledge from the incident is therefore lost as institutional memory rather than embedded as a test.

---

## 3. Existing / Current Workflow

The current approach when a production incident is reported follows this pattern:

```
1. Incident Reported (e.g., via ticket, alert, or user complaint)
        ↓
2. Engineer Reads the Incident Description
        ↓
3. Engineer Manually Investigates the System
        ↓
4. Root Cause Identified (if possible)
        ↓
5. Fix Applied
        ↓
6. Fix Manually Verified (ad-hoc, often in staging)
        ↓
7. Incident Closed
        ↓
8. [No automated regression test written — knowledge is lost]
```

There is no structured step that converts the incident into an automated, replayable test. Any regression test that does get written depends entirely on the initiative of the individual engineer, and it is not systematically stored or maintained.

---

## 4. Problems with the Current Workflow

| ID   | Problem                                                                                                      |
|------|--------------------------------------------------------------------------------------------------------------|
| P-01 | Incidents are recorded in natural language but never translated into structured, executable test cases.       |
| P-02 | Fixes are verified ad-hoc. There is no guarantee the same failure will be caught in the future.              |
| P-03 | Regression test suites do not grow from production incidents, so they do not reflect real-world failure modes. |
| P-04 | Each incident requires significant manual effort to investigate, reproduce, and fix, with no reuse of that effort. |
| P-05 | Permission-related bugs are especially subtle and easy to miss in manual testing because they are role-specific. |
| P-06 | Without a structured reproduction step, it is difficult to verify that a fix is correct before closing the incident. |

---

## 5. Proposed Solution

The proposed solution is an **Incident-to-Regression Pipeline** — an automated or semi-automated system that takes a production incident as input and produces an executable, passing regression test as output. Once the test passes (i.e., the bug is fixed), the test is persisted in a regression suite to prevent future recurrence.

The pipeline bridges the gap between:
- **Incident knowledge** (what went wrong, who, what action, what was expected, what happened)
- **Regression test artefacts** (a repeatable, automated test that enforces the correct behavior)

The system operates on a simulated hospital application that exposes permission-dependent workflows, enabling the pipeline to be demonstrated and evaluated against realistic scenarios.

### Illustrative Example

**Incident Report (natural language):**
> A nurse was able to modify a patient's prescription even though nurses are not allowed to modify prescriptions.

**Structured Understanding the Pipeline Should Produce:**

| Field             | Value                          |
|-------------------|--------------------------------|
| Role              | Nurse                          |
| Action            | Modify Prescription            |
| Expected Behavior | Access Denied (HTTP 403)       |
| Actual Behavior   | Success (HTTP 200)             |
| Failure Category  | Authorization / Permission Bug |

**Regression Test the Pipeline Should Generate:**
```
1. Authenticate as a user with the Nurse role
2. Navigate to a patient record
3. Attempt to modify the patient's prescription
4. Assert that the system returns an Access Denied response
5. Assert that the prescription record remains unmodified
```

After the fix is applied, this test passes and is stored permanently in the regression suite.

---

## 6. Goals and Objectives

### Primary Goal
Convert production incidents into executable, passing regression tests reliably and systematically.

### Objectives

| ID   | Objective                                                                                                             |
|------|-----------------------------------------------------------------------------------------------------------------------|
| O-01 | Build a pipeline that accepts incident descriptions and produces structured, executable regression tests.              |
| O-02 | Build a simulated hospital system with configurable roles and permission-dependent workflows for the pipeline to test against. |
| O-03 | Demonstrate that the pipeline correctly converts a set of representative incidents into passing regression tests.      |
| O-04 | Evaluate the pipeline against a simple baseline approach and measure the difference in conversion success rate.       |
| O-05 | Ensure the system handles failure cases, ambiguous inputs, and edge cases gracefully.                                 |
| O-06 | Produce a regression suite that grows with each successfully processed incident.                                      |

---

## 7. Target Users and Stakeholders

### Primary Users (for the prototype / demonstration)

| Role                        | Description                                                                                   |
|-----------------------------|-----------------------------------------------------------------------------------------------|
| Project Evaluator           | Academic audience assessing whether the pipeline achieves its stated objectives.              |
| System Demonstrator         | The student(s) running the pipeline and presenting results.                                   |

### Represented Stakeholders (real-world equivalents the project models)

| Role                        | Description                                                                                   |
|-----------------------------|-----------------------------------------------------------------------------------------------|
| DevOps / On-Call Engineer   | The person who receives and investigates production incidents.                                |
| QA Engineer                 | The person responsible for maintaining and expanding the regression test suite.               |
| Hospital IT Admin           | The person who manages role definitions and permission configurations.                        |
| Clinical Staff (end users)  | Nurses, Doctors, Receptionists — users whose actions are tested through the pipeline.         |

---

## 8. Core User Workflows

### Workflow 1 — Incident Submission and Test Generation

```
User submits an incident description (natural language or structured format)
        ↓
System parses and analyzes the incident
        ↓
System identifies: Role, Action, Expected Behavior, Actual Behavior
        ↓
System generates reproduction steps
        ↓
System generates an executable regression test
        ↓
System executes the test against the hospital system
        ↓
System reports: PASS / FAIL / ERROR (with reasoning)
        ↓
If PASS: test is stored in the regression suite
```

### Workflow 2 — Regression Suite Execution

```
User triggers the regression suite
        ↓
All previously stored tests are executed against the current hospital system
        ↓
Results are reported per test: PASS / FAIL
        ↓
Any regressions (previously passing tests that now fail) are flagged
```

### Workflow 3 — Permission Configuration

```
Admin modifies a role's permissions (e.g., grants nurses write access to prescriptions)
        ↓
The hospital system enforces the updated permissions
        ↓
Existing regression tests that depend on those permissions reflect the change in their results
```

---

## 9. Functional Requirements

Requirements are categorized by component.

### 9.1 — Incident Ingestion

| ID     | Requirement                                                                                                    | Priority  | Acceptance Criteria                                                                  |
|--------|----------------------------------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------|
| FR-01  | The system shall accept incident descriptions as free-form natural language text.                              | Must Have | A user can submit a paragraph describing an incident; the system does not reject it. |
| FR-02  | The system shall also accept incidents in a structured format (e.g., JSON or form fields).                     | Must Have | A structured incident with defined fields can be submitted and processed.            |
| FR-03  | The system shall extract the following fields from any valid incident: Role, Action, Expected Behavior, Actual Behavior. | Must Have | Given a valid incident, these four fields are present in the parsed output.          |
| FR-04  | The system shall classify the failure category (e.g., permission failure, data failure, workflow failure).     | Should Have | A failure category label is assigned to each parsed incident.                        |

### 9.2 — Incident Analysis

| ID     | Requirement                                                                                                    | Priority  | Acceptance Criteria                                                                  |
|--------|----------------------------------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------|
| FR-05  | The system shall map the identified action to a specific operation in the hospital system (e.g., "modify prescription" → `PATCH /prescriptions/{id}`). | Must Have | The mapped operation is valid and executable against the hospital system.            |
| FR-06  | The system shall map the identified role to a valid role defined in the hospital system's role configuration.  | Must Have | The mapped role exists in the configuration; an error is raised if it does not.      |
| FR-07  | The system shall determine the expected HTTP response or system state based on current permission configuration. | Must Have | The expected behavior reflects what the permission rules say should happen.          |

### 9.3 — Test Generation

| ID     | Requirement                                                                                                    | Priority  | Acceptance Criteria                                                                  |
|--------|----------------------------------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------|
| FR-08  | The system shall generate a sequence of reproduction steps from the parsed incident.                           | Must Have | Reproduction steps are logically ordered and map to executable actions.              |
| FR-09  | The system shall generate an executable regression test from the reproduction steps.                           | Must Have | The generated test can be executed without manual modification.                      |
| FR-10  | The generated test shall include an assertion that verifies expected vs. actual behavior.                      | Must Have | The test explicitly asserts the expected outcome; it does not merely run the action. |
| FR-11  | The system shall assign a unique identifier to each generated test.                                            | Must Have | No two tests in the suite share the same identifier.                                 |

### 9.4 — Test Execution

| ID     | Requirement                                                                                                    | Priority  | Acceptance Criteria                                                                  |
|--------|----------------------------------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------|
| FR-12  | The system shall execute the generated test against the simulated hospital system.                             | Must Have | Execution is automated; no manual step is required to run the test.                  |
| FR-13  | The system shall report a result of PASS, FAIL, or ERROR for each executed test.                               | Must Have | The result is accompanied by a reason (what assertion failed or what error occurred). |
| FR-14  | A test result of PASS means the hospital system is currently behaving correctly with respect to the incident.  | Must Have | A PASS is only reported when the assertion holds against the live system.             |

### 9.5 — Regression Suite Management

| ID     | Requirement                                                                                                    | Priority  | Acceptance Criteria                                                                  |
|--------|----------------------------------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------|
| FR-15  | The system shall persist a passing test to the regression suite after it passes execution.                     | Must Have | The test is stored and retrievable after the pipeline run ends.                      |
| FR-16  | The system shall support re-running all tests in the regression suite at any time.                             | Must Have | All stored tests execute successfully on re-run without configuration changes.       |
| FR-17  | The regression suite shall report which tests pass and which fail on each run.                                 | Must Have | A per-test result is produced for every suite execution.                             |
| FR-18  | The system shall flag a test that previously passed but now fails (regression detection).                      | Should Have | A regression is clearly identified and distinguishable from a new failure.           |

### 9.6 — Hospital System (Simulated Target Application)

| ID     | Requirement                                                                                                    | Priority  | Acceptance Criteria                                                                  |
|--------|----------------------------------------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------|
| FR-19  | The hospital system shall expose permission-dependent operations that the pipeline tests against.               | Must Have | At least 5 distinct operations are available (e.g., view, create, modify, delete records). |
| FR-20  | The hospital system shall enforce role-based access control on all exposed operations.                          | Must Have | An unauthorized role attempting an operation receives a denial response.             |
| FR-21  | The hospital system shall support at least two distinct organizational roles with different permission sets.    | Must Have | The two roles differ in at least one permission.                                     |
| FR-22  | Role definitions and permission mappings shall be configurable, not hard-coded.                                | Must Have | Changing a permission in the configuration file is reflected in the system's behavior without code changes. |
| FR-23  | The hospital system shall support authenticated sessions so tests can operate as specific roles.               | Must Have | A test can authenticate as a given role and all subsequent requests use that role's permissions. |

---

## 10. Non-Functional Requirements

| ID     | Requirement                                                                                                    | Priority  |
|--------|----------------------------------------------------------------------------------------------------------------|-----------|
| NFR-01 | The pipeline must be runnable end-to-end on a single local machine without external service dependencies.      | Must Have |
| NFR-02 | Configuration (roles, permissions, workflow mappings) must be editable via plain-text files.                   | Must Have |
| NFR-03 | The system must produce human-readable output for each pipeline stage to support inspection and debugging.     | Must Have |
| NFR-04 | The regression suite must be stored in a durable format that persists between runs.                            | Must Have |
| NFR-05 | The pipeline must complete a single incident-to-test cycle in a reasonable time for demonstration purposes.    | Should Have |
| NFR-06 | The hospital system must behave deterministically — the same request with the same role must always return the same result. | Must Have |
| NFR-07 | The system must be structured so that the hospital system can be replaced or extended without rewriting the pipeline. | Should Have |

---

## 11. Incident-to-Regression Workflow

The following is the end-to-end workflow the system must implement. Each stage is a distinct processing step with defined inputs and outputs.

```
┌───────────────────────────────────────────────────────────────┐
│  STAGE 1 — Incident Ingestion                                 │
│  Input:  Raw incident description (text or structured)        │
│  Output: Ingested incident record                             │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│  STAGE 2 — Incident Analysis                                  │
│  Input:  Ingested incident record                             │
│  Output: Structured incident model                            │
│          { Role, Action, Expected, Actual, Failure Type }     │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│  STAGE 3 — Reproduction Step Extraction                       │
│  Input:  Structured incident model                            │
│  Output: Ordered list of reproduction steps                   │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│  STAGE 4 — Test Generation                                    │
│  Input:  Reproduction steps + expected behavior               │
│  Output: Executable regression test with assertion            │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│  STAGE 5 — Test Execution                                     │
│  Input:  Generated test                                       │
│  Output: Execution result (PASS / FAIL / ERROR)               │
└───────────────────────────────────────────────────────────────┘
                            ↓
┌───────────────────────────────────────────────────────────────┐
│  STAGE 6 — Regression Suite Storage                           │
│  Input:  Passing test + metadata                              │
│  Output: Test persisted in regression suite                   │
└───────────────────────────────────────────────────────────────┘
```

---

## 12. Role and Permission Requirements

### 12.1 Role Requirements

- The hospital system must support a minimum of **two distinct roles** (e.g., Doctor and Nurse).
- A role defines what actions a user holding that role is permitted or denied to perform.
- Roles must be defined in a configuration file, not in application code.
- Adding or modifying a role must not require changes to the application code.

### 12.2 Permission Requirements

- Each permission must map a **Role** to an **Action** and a **Decision** (Allow / Deny).
- Permission decisions must be enforced consistently by the hospital system.
- The pipeline must be able to read the permission configuration to determine what the expected behavior for any role-action combination should be.
- Permission rules must support at minimum: **Allow** and **Deny**. Conditional rules (e.g., allow only for own patients) are desirable but not required.

### 12.3 Example Permission Configuration (Illustrative)

| Role          | Action                    | Decision |
|---------------|---------------------------|----------|
| Doctor        | View Prescription         | Allow    |
| Doctor        | Modify Prescription       | Allow    |
| Nurse         | View Prescription         | Allow    |
| Nurse         | Modify Prescription       | Deny     |
| Receptionist  | View Patient Record       | Allow    |
| Receptionist  | Modify Patient Record     | Deny     |
| Receptionist  | View Prescription         | Deny     |
| Admin         | All Actions               | Allow    |

---

## 13. Incident Lifecycle

An incident moves through the following states from the moment it is reported until a regression test is committed to the suite.

```
[OPEN]
  The incident has been reported and ingested but not yet analyzed.
        ↓
[ANALYZED]
  The incident has been parsed into a structured model: Role, Action, Expected, Actual.
        ↓
[TEST GENERATED]
  A regression test has been generated from the incident model.
        ↓
[TEST EXECUTED]
  The test has been run against the hospital system and a result is available.
        ↓
[COMMITTED]  <--- The test PASSED. It is now part of the regression suite.
   -- or --
[FAILED]     <--- The test FAILED. The bug may not yet be fixed, or generation was incorrect.
   -- or --
[ERROR]      <--- The test could not be executed (e.g., missing role, unmapped action).
```

For incidents that result in FAILED or ERROR, the system must surface the reason so that the issue can be diagnosed.

---

## 14. Regression Test Lifecycle

Each generated test has its own lifecycle within the regression suite.

```
[GENERATED]
  Test created from incident analysis.
        ↓
[EXECUTED -- NEW]
  Test runs for the first time against the hospital system.
        ↓
[PASSING]   <--- Assertion holds. Test is committed to the suite.
   -- or --
[FAILING]   <--- Assertion fails. Test is not committed until it passes.
        ↓ (if committed)
[IN SUITE]
  Test is part of the permanent regression suite. Runs on every suite execution.
        ↓
[REGRESSED]  <--- Test was previously PASSING but now FAILS in a suite run.
   -- or --
[STABLE]     <--- Test continues to PASS on every suite run.
```

---

## 15. Baseline Approach vs. Proposed Approach

To evaluate the value of the pipeline, the system must be compared against a simple baseline. This comparison is a project requirement, not an optional enhancement.

### 15.1 Baseline Approach

The baseline represents the current, naive approach:

- Incidents are processed using a **template-based** or **keyword-matching** system.
- The baseline reads an incident and applies a fixed template to generate a test (e.g., if the keyword "prescription" is present and the role is "nurse", generate test template T-03).
- The baseline does not perform semantic understanding of the incident.
- The baseline does not consult the permission configuration to determine expected behavior.
- The baseline generates tests mechanically from predefined mappings.

### 15.2 Proposed Approach

The proposed pipeline performs structured analysis:

- It understands the incident semantically (not just keyword-matches).
- It cross-references the role-action pair against the live permission configuration to determine correct expected behavior.
- It generates reproduction steps that reflect the actual workflow, not a template.
- It executes and verifies the test before committing it to the suite.

### 15.3 Comparison Dimensions

| Dimension                                     | Baseline              | Proposed Pipeline       |
|-----------------------------------------------|-----------------------|-------------------------|
| Incident understanding                        | Keyword / template    | Structured analysis     |
| Permission awareness                          | None                  | Configuration-aware     |
| Test generation method                        | Fixed templates       | Dynamic, workflow-based |
| Assertion quality                             | Partial / generic     | Specific, role-aware    |
| Handling of ambiguous or novel incidents      | Fails or misclassifies | Detects and reports    |
| Passing test conversion rate                  | Measured              | Measured (primary KPI)  |

---

## 16. Success Metrics and KPIs

The **primary success criterion** is:

> **How many production incidents are successfully converted into executable, passing regression tests?**

### 16.1 Primary KPI

| KPI                              | Definition                                                                                  | Target (Prototype)   |
|----------------------------------|---------------------------------------------------------------------------------------------|----------------------|
| Incident Conversion Rate         | (Number of incidents that produce a passing regression test) / (Total incidents processed) × 100% | >= 70%           |

### 16.2 Supporting Metrics

| Metric                           | Definition                                                                                  |
|----------------------------------|---------------------------------------------------------------------------------------------|
| Structured Extraction Accuracy   | % of incidents where Role, Action, Expected, and Actual are all correctly extracted.        |
| Test Executability Rate          | % of generated tests that can be executed without errors (regardless of PASS/FAIL result).  |
| Regression Detection Rate        | % of reintroduced bugs that are caught by the regression suite on re-run.                   |
| Baseline vs. Pipeline Delta      | Difference in Incident Conversion Rate between the baseline and the proposed pipeline.      |
| False Positive Rate              | % of tests that PASS but assert the wrong behavior.                                         |

### 16.3 Evaluation Protocol

- A fixed set of **representative incidents** will be prepared in advance.
- Both the baseline and the pipeline will be run against this same incident set.
- Results will be recorded and compared on all metrics above.
- At least one incident set will include edge cases and ambiguous descriptions.

---

## 17. Edge and Failure Cases

The system must handle the following non-happy-path scenarios. Each must produce a meaningful output rather than silently failing or crashing.

| ID     | Scenario                                                                                          | Expected System Behavior                                                      |
|--------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| EC-01  | Incident description is too vague to extract role or action.                                      | System reports that the incident could not be parsed; does not generate a test. |
| EC-02  | The role mentioned in the incident does not exist in the current configuration.                   | System reports an unmapped role error; does not execute the test.             |
| EC-03  | The action mentioned in the incident is not mapped to any hospital system operation.              | System reports an unmapped action error; does not execute the test.           |
| EC-04  | The expected behavior in the incident contradicts the current permission configuration.           | System flags the discrepancy and reports it; still generates and runs the test. |
| EC-05  | The hospital system is unavailable during test execution.                                         | System reports a test execution error with a connection failure message.      |
| EC-06  | A duplicate incident (same role, same action, same expected/actual) is submitted.                 | System detects the duplicate and does not create a duplicate test.            |
| EC-07  | The generated test passes, but a later permission configuration change causes it to fail.         | System flags the test as REGRESSED on the next suite run.                    |
| EC-08  | An incident has internally contradictory information (e.g., both success and denial are claimed). | System reports an inconsistency and requests clarification; does not generate a test. |
| EC-09  | The bug described in the incident has not yet been fixed when the test is run.                    | Test result is FAIL; system does not commit the test to the suite.            |
| EC-10  | An incident involves a role-action combination that is conditionally permitted.                   | System notes that the rule is conditional; flags limited confidence in the assertion. |

---

## 18. Validation and Experiment Requirements

### 18.1 Incident Dataset

- A set of **at least 10 representative incidents** must be prepared for evaluation.
- The set must include:
  - Permission denial failures (e.g., unauthorized action succeeded).
  - Permission grant failures (e.g., authorized action was blocked).
  - Ambiguous or incomplete incident descriptions.
  - Edge cases from Section 17.
- Incidents must be written in realistic, production-like language — not artificially simple.

### 18.2 Experiment Design

| Experiment | Description                                                                                      |
|------------|--------------------------------------------------------------------------------------------------|
| EXP-01     | Run all 10+ incidents through the baseline. Record conversion rate and supporting metrics.       |
| EXP-02     | Run all 10+ incidents through the proposed pipeline. Record conversion rate and supporting metrics. |
| EXP-03     | Reintroduce a bug into the hospital system (revert a permission to the broken state). Run the regression suite. Verify that the relevant test is now flagged as REGRESSED. |
| EXP-04     | Modify a role's permission configuration. Re-run the regression suite. Observe that tests dependent on the changed permission reflect the new expected behavior. |

### 18.3 Reporting Requirements

- Results for each experiment must be recorded in a structured format.
- A comparison table of baseline vs. pipeline performance must be produced.
- Any cases where the pipeline fails must be documented with a root cause.

---

## 19. Constraints

| ID     | Constraint                                                                                                              |
|--------|-------------------------------------------------------------------------------------------------------------------------|
| C-01   | The project must be completable within approximately one week of development time (college prototype).                   |
| C-02   | The hospital system is simulated — it does not need to be a real hospital application.                                  |
| C-03   | The system must run on a single local machine without requiring a cloud deployment.                                     |
| C-04   | The pipeline must not require real patient data.                                                                        |
| C-05   | Configuration files (roles, permissions) must be human-readable and editable without technical expertise.               |

---

## 20. Assumptions

| ID     | Assumption                                                                                                              |
|--------|-------------------------------------------------------------------------------------------------------------------------|
| A-01   | Incidents will be provided as text (natural language) or simple structured data. Complex log files or telemetry are not the input format. |
| A-02   | The hospital system's roles and permissions are the primary subject of incidents; general application bugs are not in scope. |
| A-03   | The permission configuration accurately reflects the intended system behavior at the time of evaluation.                |
| A-04   | A test that passes when the hospital system is in a known-correct state can be trusted as a valid regression test.      |
| A-05   | The set of operations in the hospital system is finite and known in advance; the pipeline does not need to discover operations dynamically. |

---

## 21. Limitations

| ID     | Limitation                                                                                                              |
|--------|-------------------------------------------------------------------------------------------------------------------------|
| L-01   | The pipeline is designed for permission-related incidents. It is not a general-purpose test generator for all bug types. |
| L-02   | The quality of test generation depends on the quality and clarity of the incident description.                          |
| L-03   | Conditional or context-dependent permissions (e.g., "doctor may modify only their own patient's records") may not be fully testable within the current scope. |
| L-04   | The simulated hospital system may not capture all the complexity of a real-world hospital application.                  |
| L-05   | Regression tests generated from incidents only cover the scenarios described in those incidents; they are not comprehensive test suites. |

---

## 22. Out-of-Scope Items

The following items are explicitly **not** part of this project:

| Item                                                                                          | Reason Out of Scope                                                               |
|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| Integration with real hospital software or EHR systems                                       | The hospital system is simulated for demonstration purposes.                      |
| Monitoring or alerting infrastructure for production incidents                                | Incidents are submitted manually or from a prepared dataset.                      |
| Performance or load testing                                                                   | The focus is correctness of permission enforcement, not system performance.       |
| UI/UX testing (e.g., browser automation)                                                     | Tests target application logic (APIs/endpoints), not graphical interfaces.        |
| General-purpose bug tracking or ticket management                                             | This is not a ticketing system replacement.                                       |
| Machine learning model training or fine-tuning                                                | Any AI/LLM used is treated as an external component; the project does not train models. |
| Multi-tenant or multi-hospital configurations                                                 | A single simulated hospital is sufficient for the project's objectives.           |
| Security testing beyond permission enforcement (e.g., SQL injection, XSS)                    | Permission-based RBAC is the only security concern in scope.                      |

---

## 23. Expected Final Deliverables

| Deliverable                        | Description                                                                                                    |
|------------------------------------|----------------------------------------------------------------------------------------------------------------|
| Simulated Hospital System          | A runnable application with at least two roles, permission-dependent operations, and configurable RBAC rules.  |
| Incident-to-Regression Pipeline    | The end-to-end pipeline that takes an incident and produces a stored, passing regression test.                 |
| Baseline System                    | A simpler, template/keyword-based system that performs the same task for comparison.                           |
| Incident Dataset                   | A curated set of at least 10 realistic incidents, including happy-path, edge, and failure cases.               |
| Regression Test Suite              | The persistent collection of tests generated and committed by the pipeline across all processed incidents.     |
| Experiment Results                 | Structured results comparing baseline vs. pipeline across all defined metrics and experiments.                 |
| Project Report / Documentation     | A write-up covering the design, implementation, results, and analysis of the project.                         |

---

*End of PRD — Version 1.0*
