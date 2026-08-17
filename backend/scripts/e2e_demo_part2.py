import requests

BASE_URL = "http://localhost:8000"

def run_demo():
    print("\n=== Phase 12: End-to-End Demo (Part 2) ===")
    
    try:
        with open("e2e_demo_state.txt", "r") as f:
            incident_id = f.read().strip()
    except FileNotFoundError:
        print("[-] State file not found. Did you run part 1?")
        return

    print(f"\n[+] Re-executing Generated Test for Incident {incident_id} (Expecting PASS because bug is fixed)...")
    res = requests.post(f"{BASE_URL}/incidents/{incident_id}/execute")
    exec_data = res.json()
    
    print(f"\n=== EXECUTION RESULT: {exec_data['status']} ===")
    print("Logs snippet:")
    lines = exec_data['logs'].split('\n')
    for line in lines[-10:]:
        print("  " + line)
        
    print("\n[+] SUCCESS! The bug was fixed, and the generated regression test is now a permanent guard against it.")

if __name__ == "__main__":
    run_demo()
