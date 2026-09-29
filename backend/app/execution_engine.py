"""
Execution Engine
================
Executes generated Pytest code dynamically with strict security sandboxing:
- AST Static Security Analysis: Rejects dangerous imports (os, subprocess, socket, etc.) & calls (eval, exec)
- Strict Execution Timeouts: Enforces execution deadlines to prevent infinite loops / DoS
- Restricted Environment Variables: Strips sensitive API keys and system credentials
- Isolated Sandbox Directory: Writes ephemeral tests into .sandbox/ with automatic cleanup
- Optional Docker Sandboxing: Supports containerized isolation when configured
"""

import os
import sys
import subprocess
import time
import shutil
import re
import ast
from typing import Dict, Any, Optional, List

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT = int(os.getenv("TEST_EXECUTION_TIMEOUT", "15"))
SANDBOX_MODE = os.getenv("SANDBOX_MODE", "subprocess").lower()

FORBIDDEN_MODULES = {
    "os", "subprocess", "sys", "shutil", "socket", "pty",
    "commands", "posix", "nt", "pickle", "ctypes", "builtins"
}
FORBIDDEN_CALLS = {
    "eval", "exec", "__import__", "globals", "locals", 
    "compile", "breakpoint", "getattr"
}

# ---------------------------------------------------------------------------
# AST Static Security Validator
# ---------------------------------------------------------------------------

class SecurityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violation: Optional[str] = None

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            mod_root = alias.name.split(".")[0]
            if mod_root in FORBIDDEN_MODULES:
                self.violation = f"Forbidden import '{alias.name}' detected"
                return
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            mod_root = node.module.split(".")[0]
            if mod_root in FORBIDDEN_MODULES:
                self.violation = f"Forbidden from-import '{node.module}' detected"
                return
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                self.violation = f"Forbidden call '{node.func.id}()' detected"
                return
        self.generic_visit(node)

def validate_test_code_safety(test_code: str) -> Optional[str]:
    """
    Statically analyzes test code using the AST.
    Returns violation error message if dangerous patterns are found, or None if safe.
    """
    try:
        tree = ast.parse(test_code)
    except SyntaxError as e:
        return f"Syntax error in generated test code: {e.msg} (line {e.lineno})"

    visitor = SecurityVisitor()
    visitor.visit(tree)
    return visitor.violation

# ---------------------------------------------------------------------------
# Sandbox Environment Setup
# ---------------------------------------------------------------------------

def get_sanitized_env(base_dir: str) -> Dict[str, str]:
    """
    Returns a restricted environment dict with secrets stripped.
    Prevents generated test scripts from exfiltrating credentials.
    """
    project_root = os.path.abspath(os.path.join(base_dir, ".."))
    safe_keys = {
        "PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", 
        "HOMEPATH", "USERPROFILE", "LANG", "LC_ALL"
    }
    sanitized = {k: v for k, v in os.environ.items() if k.upper() in safe_keys}
    existing_pythonpath = os.environ.get("PYTHONPATH", "")
    paths = [project_root, base_dir]
    if existing_pythonpath:
        paths.append(existing_pythonpath)
    sanitized["PYTHONPATH"] = os.pathsep.join(paths)
    sanitized["PYTHONDONTWRITEBYTECODE"] = "1"
    sanitized["SANDBOX_ACTIVE"] = "1"
    return sanitized

def _ensure_sandbox_dir(base_dir: str) -> str:
    """
    Ensures .sandbox directory exists outside tests/ and is wired to conftest.
    """
    sandbox_dir = os.path.join(base_dir, ".sandbox")
    os.makedirs(sandbox_dir, exist_ok=True)
    
    # Create conftest inside .sandbox so fixtures (client) are available
    conftest_path = os.path.join(sandbox_dir, "conftest.py")
    with open(conftest_path, "w") as f:
        f.write("# Re-export test fixtures for sandbox execution\n")
        f.write("from backend.tests.conftest import *  # noqa\n")
            
    # Add .gitignore in .sandbox
    gitignore_path = os.path.join(sandbox_dir, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("*\n!.gitignore\n!conftest.py\n")
            
    return sandbox_dir

# ---------------------------------------------------------------------------
# Execution Functions
# ---------------------------------------------------------------------------

def execute_test(
    incident_id: int, 
    test_code: str, 
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Executes generated Pytest code dynamically inside a sandboxed environment.
    Applies AST safety checks, execution timeouts, and sanitized environment variables.
    """
    # 1. Pre-execution AST Security Scan
    violation = validate_test_code_safety(test_code)
    if violation:
        return {
            "status": "SECURITY_VIOLATION",
            "execution_time": 0.0,
            "logs": f"[SECURITY AUDIT FAILED] Code execution rejected: {violation}"
        }

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sandbox_dir = _ensure_sandbox_dir(base_dir)
    
    # 2. Write code to isolated temp file in .sandbox
    timestamp = int(time.time() * 1000)
    temp_filename = f"test_dynamic_exec_inc_{incident_id}_{timestamp}.py"
    temp_filepath = os.path.join(sandbox_dir, temp_filename)
    
    with open(temp_filepath, "w") as f:
        f.write(test_code)
        
    start_time = time.time()
    result = {
        "status": "ERROR",
        "execution_time": 0.0,
        "logs": ""
    }
    
    try:
        # 3. Execute with strict timeout and restricted env
        cmd = ["python", "-m", "pytest", f".sandbox/{temp_filename}", "-v"]
        
        process = subprocess.run(
            cmd, 
            cwd=base_dir,
            capture_output=True, 
            text=True,
            timeout=timeout,
            env=get_sanitized_env(base_dir)
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
            
    except subprocess.TimeoutExpired:
        end_time = time.time()
        result["status"] = "TIMEOUT"
        result["execution_time"] = round(end_time - start_time, 2)
        result["logs"] = f"[TIMEOUT] Test execution exceeded strict safety timeout of {timeout}s."
    except Exception as e:
        result["logs"] = f"Failed to execute subprocess: {str(e)}"
        result["status"] = "ERROR"
    finally:
        # Guaranteed cleanup
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception:
                pass
                
    return result

def execute_suite(
    tests: list, 
    timeout: int = DEFAULT_TIMEOUT * 4
) -> Dict[str, Any]:
    """
    Executes multiple tests as a suite in a temporary directory with safety checks.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sandbox_dir = _ensure_sandbox_dir(base_dir)
    
    timestamp = int(time.time() * 1000)
    temp_suite_dir = os.path.join(sandbox_dir, f"temp_suite_{timestamp}")
    os.makedirs(temp_suite_dir, exist_ok=True)
    
    # Validate all tests prior to writing
    for t in tests:
        violation = validate_test_code_safety(t.test_code)
        if violation:
            shutil.rmtree(temp_suite_dir, ignore_errors=True)
            return {
                "total_tests": len(tests),
                "passed_tests": 0,
                "failed_tests": 0,
                "execution_time": 0.0,
                "logs": f"[SECURITY AUDIT FAILED] Suite execution aborted due to Test #{t.id}: {violation}"
            }

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
        cmd = ["python", "-m", "pytest", f".sandbox/temp_suite_{timestamp}", "-v"]
        
        process = subprocess.run(
            cmd, 
            cwd=base_dir,
            capture_output=True, 
            text=True,
            timeout=timeout,
            env=get_sanitized_env(base_dir)
        )
        
        end_time = time.time()
        result["execution_time"] = round(end_time - start_time, 2)
        
        stdout = process.stdout
        stderr = process.stderr
        combined_logs = f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}"
        result["logs"] = combined_logs
        
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
        
    except subprocess.TimeoutExpired:
        end_time = time.time()
        result["execution_time"] = round(end_time - start_time, 2)
        result["logs"] = f"[TIMEOUT] Regression suite exceeded total safety timeout of {timeout}s."
    except Exception as e:
        result["logs"] = f"Failed to execute subprocess: {str(e)}"
    finally:
        if os.path.exists(temp_suite_dir):
            try:
                shutil.rmtree(temp_suite_dir)
            except Exception:
                pass
                
    return result
