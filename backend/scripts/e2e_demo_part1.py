import requests
import time
import json

BASE_URL = "http://localhost:8000"

def run_demo():
    print("=== Phase 12: End-to-End Demo (Part 1) ===")
    
    # 0. Register and login to get admin token
    print("\n[+] Getting admin token...")
    requests.post(f"{BASE_URL}/auth/register", json={"username": "e2eadmin", "password": "pw", "role": "Admin"})
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "e2eadmin", "password": "pw"})
    token = login_res.json().get("token")
    
    # 1. Create a patient to delete
    print("\n[+] Creating a dummy patient record for the demo...")
    res = requests.post(f"{BASE_URL}/patients/", json={
        "name": "Jane Doe (Demo)",
        "dob": "1990-01-01",
        "status": "admitted"
    }, headers={"Authorization": f"Bearer {token}"})
    
    patient_id = res.json().get("id", 1)
    print(f"    -> Patient created with ID: {patient_id}")
    
    # 2. Create the Incident
    incident_desc = f"Nurse logged in and sent a DELETE request to /patients/{patient_id}. The patient was successfully deleted. Expected this action to be forbidden (403)."
    print(f"\n[+] Reporting Incident:\n    '{incident_desc}'")
    
    res = requests.post(f"{BASE_URL}/incidents/", json={"description": incident_desc})
    incident_id = res.json()["id"]
    print(f"    -> Incident created with ID: {incident_id}")
    
    # 3. Analyze
    print("\n[+] Triggering Analysis Engine...")
    res = requests.post(f"{BASE_URL}/incidents/{incident_id}/analyze")
    data = res.json()
    print(f"    -> Status: {data['status']}")
    print(f"    -> Role: {data['extracted_role']}, Endpoint: {data['extracted_endpoint']}, Expected: {data['expected_result']}")
    
    # 4. Reproduce
    print("\n[+] Triggering Reproduction Engine...")
    res = requests.post(f"{BASE_URL}/incidents/{incident_id}/reproduce")
    print(f"    -> Status: {res.json()['status']}")
    
    # 5. Generate Test
    print("\n[+] Triggering Test Generator...")
    res = requests.post(f"{BASE_URL}/incidents/{incident_id}/generate-test")
    print(f"    -> Status: {res.json()['status']}")
    
    # 6. Execute Test (Should Fail)
    print("\n[+] Executing Generated Test (Expecting FAIL because bug exists)...")
    res = requests.post(f"{BASE_URL}/incidents/{incident_id}/execute")
    exec_data = res.json()
    
    print(f"\n=== EXECUTION RESULT: {exec_data['status']} ===")
    print("Logs snippet:")
    lines = exec_data['logs'].split('\n')
    for line in lines[-10:]:
        print("  " + line)
        
    # Save incident ID for part 2
    with open("e2e_demo_state.txt", "w") as f:
        f.write(str(incident_id))

if __name__ == "__main__":
    run_demo()
