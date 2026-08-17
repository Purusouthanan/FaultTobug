import json
import os
import sys

# Add backend dir to path so we can import app
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(base_dir, ".."))
sys.path.append(backend_dir)

from fastapi.testclient import TestClient
from app.main import app

def load_dataset():
    json_path = os.path.join(base_dir, "..", "data", "validation_dataset.json")
    
    with open(json_path, "r") as f:
        incidents = json.load(f)
        
    client = TestClient(app)
    
    success_count = 0
    for incident in incidents:
        payload = {
            "description": incident["description"]
        }
        
        response = client.post("/incidents/", json=payload)
        if response.status_code == 200:
            print(f"Loaded: {incident['description'][:50]}...")
            success_count += 1
        else:
            print(f"Failed: {response.text}")
            
    print(f"\nSuccessfully loaded {success_count} incidents into the database!")

if __name__ == "__main__":
    load_dataset()
