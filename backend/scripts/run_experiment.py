import os
import sys
import time

# Add backend dir to path so we can import app
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(base_dir, ".."))
sys.path.append(backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import Incident
from app.execution_engine import execute_test

def run_experiment():
    client = TestClient(app)
    
    # Get all incidents using context manager to avoid unclosed sessions (SQLite locks)
    db_gen = get_db()
    db = next(db_gen)
    try:
        incidents = db.query(Incident).all()
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass
    
    total = len(incidents)
    print(f"Starting experiment on {total} incidents...\n", flush=True)
    
    baseline_passes = 0
    prototype_passes = 0
    
    baseline_time = 0.0
    prototype_time = 0.0
    
    results = []

    for incident in incidents:
        iid = incident.id
        print(f"--- Processing Incident #{iid} ---", flush=True)
        
        # --- BASELINE PIPELINE ---
        b_start = time.time()
        # 1. Generate Baseline Test
        res = client.post(f"/baseline/incidents/{iid}/generate-test")
        baseline_code = res.json().get("baseline_test_code")
        
        # 2. Execute Baseline Test (using the engine directly for simplicity)
        b_status = "ERROR"
        if baseline_code:
            exec_res = execute_test(iid, baseline_code)
            b_status = exec_res["status"]
            
        b_end = time.time()
        b_dur = b_end - b_start
        baseline_time += b_dur
        
        if b_status == "PASS":
            baseline_passes += 1
            
        print(f"Baseline Result: {b_status} ({b_dur:.2f}s)", flush=True)
            
        # --- PROTOTYPE PIPELINE ---
        p_start = time.time()
        # 1. Analyze
        client.post(f"/incidents/{iid}/analyze")
        # 2. Reproduce
        client.post(f"/incidents/{iid}/reproduce")
        # 3. Generate Test
        client.post(f"/incidents/{iid}/generate-test")
        # 4. Execute Test
        res = client.post(f"/incidents/{iid}/execute")
        p_status = "ERROR"
        if res.status_code == 200:
            p_status = res.json().get("status", "ERROR")
            
        p_end = time.time()
        p_dur = p_end - p_start
        prototype_time += p_dur
        
        if p_status == "PASS":
            prototype_passes += 1
            
        print(f"Prototype Result: {p_status} ({p_dur:.2f}s)\n", flush=True)
        
        results.append({
            "id": iid,
            "description": incident.description,
            "baseline": b_status,
            "prototype": p_status
        })

    print("====================================", flush=True)
    print("        EXPERIMENT RESULTS          ", flush=True)
    print("====================================", flush=True)
    print(f"Total Incidents Processed: {total}", flush=True)
    print(f"Baseline Passes:  {baseline_passes} / {total} ({(baseline_passes/total)*100:.1f}%)", flush=True)
    print(f"Prototype Passes: {prototype_passes} / {total} ({(prototype_passes/total)*100:.1f}%)", flush=True)
    print(f"Baseline Total Time:  {baseline_time:.2f}s", flush=True)
    print(f"Prototype Total Time: {prototype_time:.2f}s", flush=True)
    print("====================================", flush=True)
    
    # Save detailed report
    report_path = os.path.join(backend_dir, "..", "docs", "EXPERIMENT_RESULTS.md")
    with open(report_path, "w") as f:
        f.write("# Experiment Metrics & Results\n\n")
        f.write("## Overview\n")
        f.write(f"- **Total Incidents Evaluated:** {total}\n")
        f.write(f"- **Baseline Success Rate:** {baseline_passes} / {total} ({(baseline_passes/total)*100:.1f}%)\n")
        f.write(f"- **Prototype Success Rate:** {prototype_passes} / {total} ({(prototype_passes/total)*100:.1f}%)\n")
        f.write(f"- **Baseline Execution Time:** {baseline_time:.2f}s\n")
        f.write(f"- **Prototype Execution Time:** {prototype_time:.2f}s\n\n")
        
        f.write("## Detailed Breakdown\n")
        f.write("| ID | Baseline | Prototype | Description |\n")
        f.write("|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['id']} | {r['baseline']} | {r['prototype']} | {r['description']} |\n")

if __name__ == "__main__":
    run_experiment()
