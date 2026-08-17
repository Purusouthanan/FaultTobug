import os
import subprocess
import time
import shutil
import re
from typing import Dict, Any

def execute_test(incident_id: int, test_code: str) -> Dict[str, Any]:
    """
    Executes the generated Pytest code dynamically.
    Writes it to a temporary file in the tests/ directory so it has access
    to the client fixture, runs pytest as a subprocess, captures output,
    and returns the result.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tests_dir = os.path.join(base_dir, "tests")
    
    # Create temp filename
    timestamp = int(time.time())
    temp_filename = f"test_dynamic_exec_inc_{incident_id}_{timestamp}.py"
    temp_filepath = os.path.join(tests_dir, temp_filename)
    
    # Write code to temp file
    with open(temp_filepath, "w") as f:
        f.write(test_code)
        
    start_time = time.time()
    
    result = {
        "status": "ERROR",
        "execution_time": 0.0,
        "logs": ""
    }
    
    try:
        # Execute pytest on this specific file
        # Running as python -m pytest ensures it uses the current venv/path
        cmd = ["python", "-m", "pytest", f"tests/{temp_filename}", "-v"]
        
        process = subprocess.run(
            cmd, 
            cwd=base_dir,
            capture_output=True, 
            text=True
        )
        
        end_time = time.time()
        result["execution_time"] = round(end_time - start_time, 2)
        
        stdout = process.stdout
        stderr = process.stderr
        combined_logs = f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}"
        result["logs"] = combined_logs
        
        if process.returncode == 0:
            result["status"] = "PASS"
        elif process.returncode == 1:
            result["status"] = "FAIL"
        else:
            result["status"] = "ERROR"
            
    except Exception as e:
        result["logs"] = f"Failed to execute subprocess: {str(e)}"
        result["status"] = "ERROR"
    finally:
        # Cleanup
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except:
                pass
                
    return result

def execute_suite(tests: list) -> Dict[str, Any]:
    """
    Executes multiple tests as a suite in a temporary directory.
    tests: List of RegressionTest objects (with test_code, id, incident_id)
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tests_dir = os.path.join(base_dir, "tests")
    
    timestamp = int(time.time())
    temp_suite_dir = os.path.join(tests_dir, f"temp_suite_{timestamp}")
    
    os.makedirs(temp_suite_dir, exist_ok=True)
    
    # create __init__.py so pytest finds it
    with open(os.path.join(temp_suite_dir, "__init__.py"), "w") as f:
        f.write("")
        
    for t in tests:
        test_filepath = os.path.join(temp_suite_dir, f"test_regression_{t.id}.py")
        with open(test_filepath, "w") as f:
            f.write(t.test_code)
            
    start_time = time.time()
    
    result = {
        "total_tests": len(tests),
        "passed_tests": 0,
        "failed_tests": 0,
        "execution_time": 0.0,
        "logs": ""
    }
    
    try:
        # Execute pytest on the suite dir
        cmd = ["python", "-m", "pytest", f"tests/temp_suite_{timestamp}", "-v"]
        
        process = subprocess.run(
            cmd, 
            cwd=base_dir,
            capture_output=True, 
            text=True
        )
        
        end_time = time.time()
        result["execution_time"] = round(end_time - start_time, 2)
        
        stdout = process.stdout
        stderr = process.stderr
        combined_logs = f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}"
        result["logs"] = combined_logs
        
        # Parse pass/fail from pytest output
        # E.g. "==== 2 passed, 1 failed in 0.12s ===="
        # Or "==== 3 passed in 0.12s ===="
        
        passed = 0
        failed = 0
        
        passed_match = re.search(r"(\d+) passed", stdout)
        if passed_match:
            passed = int(passed_match.group(1))
            
        failed_match = re.search(r"(\d+) failed", stdout)
        if failed_match:
            failed = int(failed_match.group(1))
            
        result["passed_tests"] = passed
        result["failed_tests"] = failed
        
    except Exception as e:
        result["logs"] = f"Failed to execute subprocess: {str(e)}"
    finally:
        # Cleanup
        if os.path.exists(temp_suite_dir):
            try:
                shutil.rmtree(temp_suite_dir)
            except:
                pass
                
    return result
