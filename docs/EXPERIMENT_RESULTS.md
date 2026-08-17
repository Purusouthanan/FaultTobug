# Experiment Metrics & Results

## Overview
- **Total Incidents Evaluated:** 26
- **Baseline Success Rate:** 0 / 26 (0.0%)
- **Prototype Success Rate:** 6 / 26 (23.1%)
- **Baseline Execution Time:** 104.52s
- **Prototype Execution Time:** 97.25s

## Detailed Breakdown
| ID | Baseline | Prototype | Description |
|---|---|---|---|
| 1 | FAIL | FAIL | Doctor attempted to view a patient they are not assigned to and it allowed them. |
| 2 | FAIL | FAIL | Doctor attempted to view a patient they are not assigned to and it allowed them. |
| 3 | FAIL | FAIL | Nurse tried to delete a prescription record which should be forbidden. |
| 4 | FAIL | PASS | Anonymous user tried to list all patients without logging in. |
| 5 | FAIL | FAIL | Admin successfully created a new patient. |
| 6 | FAIL | PASS | Doctor requested a prescription with a completely invalid ID format like 'abc'. |
| 7 | FAIL | FAIL | Nurse fetched patient ID 99999 which does not exist. |
| 8 | FAIL | FAIL | Doctor successfully modified the dosage on a prescription assigned to them. |
| 9 | FAIL | PASS | User logged in with expired mock token. |
| 10 | FAIL | FAIL | Nurse attempted to create a new patient. |
| 11 | FAIL | FAIL | Doctor tried to delete patient ID 1. |
| 12 | FAIL | FAIL | Admin deleted a prescription successfully. |
| 13 | FAIL | PASS | Anonymous user attempted to create a prescription. |
| 14 | FAIL | FAIL | Nurse updated patient status successfully. |
| 15 | FAIL | FAIL | Doctor created a prescription with missing medication field. |
| 16 | FAIL | FAIL | Admin fetched a prescription that was already deleted (ID 999). |
| 17 | FAIL | PASS | Doctor requested patient data using an invalid JWT format. |
| 18 | FAIL | FAIL | Nurse modified prescription but left the dosage field entirely empty. |
| 19 | FAIL | FAIL | Admin tried to create a patient with a duplicate name. |
| 20 | FAIL | PASS | Doctor tried to view incident logs. |
| 21 | FAIL | ERROR | Anonymous user fetched public hospital information endpoint. |
| 22 | FAIL | FAIL | Admin patched a patient with invalid state transition. |
| 23 | FAIL | FAIL | Nurse viewed a patient they are assigned to successfully. |
| 24 | FAIL | FAIL | Doctor attempted to modify a prescription that belongs to another doctor. |
| 25 | FAIL | FAIL | Nurse deleted a patient record by accident. |
| 26 | FAIL | FAIL | Admin created a prescription successfully. |
