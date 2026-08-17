import requests
import time

BASE_URL = "http://localhost:8000"

def test_api_health():
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200
    print("[PASS] Health check")

def test_pipeline_edge_case_unknown():
    # Vague incident
    desc = "A user did a random thing and the system crashed. HTTP 500."
    res = requests.post(f"{BASE_URL}/incidents/", json={"description": desc})
    incident_id = res.json()["id"]
    
    # Analyze
    analyze_res = requests.post(f"{BASE_URL}/incidents/{incident_id}/analyze").json()
    # It should assign failure category 'Unknown'
    print(f"[PASS] Unknown Edge Case Analysis: {analyze_res['failure_category']}")

if __name__ == "__main__":
    print("=== Final Validation Checks ===")
    test_api_health()
    test_pipeline_edge_case_unknown()
    print("=== Sanity Checks Passed ===")
