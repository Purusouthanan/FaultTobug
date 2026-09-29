"""
Incident Analysis Engine
========================
Extracts structured information from a natural-language incident description.

Pipeline:
  raw text
    -> extract role, action, resource
    -> lookup expected behavior from rbac.yaml
    -> determine actual behavior from text signals
    -> classify failure category
    -> return AnalysisResult

All rules are driven by analysis_rules.yaml and rbac.yaml.
No hard-coded logic. Unknown incidents are handled safely.
"""

import os
import re
import yaml
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Config loading helpers
# ---------------------------------------------------------------------------

def _load_yaml(filename: str) -> dict:
    config_dir = os.path.join(os.path.dirname(__file__), "../config")
    path = os.path.join(config_dir, filename)
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def load_analysis_rules() -> dict:
    return _load_yaml("analysis_rules.yaml")


def load_rbac_config() -> dict:
    return _load_yaml("rbac.yaml")


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class AnalysisResult:
    role: Optional[str] = None
    action: Optional[str] = None
    resource: Optional[str] = None
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    failure_category: str = "Unknown"
    confidence: str = "low"       # low | medium | high
    notes: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Resource -> endpoint / HTTP method mapping
# ---------------------------------------------------------------------------

RESOURCE_ENDPOINT_MAP = {
    "prescriptions": {
        "view":   ("GET",   "/prescriptions/{id}"),
        "modify": ("PATCH", "/prescriptions/{id}"),
        "create": ("POST",  "/prescriptions/"),
        "delete": ("DELETE","/prescriptions/{id}"),
    },
    "patients": {
        "view":   ("GET",  "/patients/"),
        "create": ("POST", "/patients/"),
        "delete": ("DELETE","/patients/{id}"),
    },
    "appointments": {
        "view":   ("GET",  "/appointments/"),
        "create": ("POST", "/appointments/"),
        "delete": ("DELETE","/appointments/{id}"),
    },
    "billing": {
        "view":   ("GET",  "/billing/"),
        "create": ("POST", "/billing/"),
        "delete": ("DELETE","/billing/{id}"),
    },
}


# ---------------------------------------------------------------------------
# Core extraction functions
# ---------------------------------------------------------------------------

def _extract_role(text_lower: str, rules: dict) -> Optional[str]:
    for role in rules.get("role_keywords", []):
        if role.lower() in text_lower:
            if "clerk" in role.lower() or "billing" in role.lower():
                return "Billing Clerk"
            return role.capitalize()
    return None


def _extract_action(text_lower: str, rules: dict) -> Optional[str]:
    action_map = rules.get("action_keywords", {})
    for action, keywords in action_map.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return action
    return None


def _extract_resource(text_lower: str, rules: dict) -> Optional[str]:
    resource_map = rules.get("resource_keywords", {})
    for resource, keywords in resource_map.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return resource
    return None


def _resolve_expected_behavior(role: str, action: str, resource: str, rbac: dict) -> str:
    """
    Cross-reference rbac.yaml to determine what SHOULD happen.
    Returns a human-readable string like 'Allow (HTTP 200)' or 'Deny (HTTP 403)'.
    """
    if not (role and action and resource):
        return "Unknown (insufficient context)"

    role_rules = rbac.get("roles", {}).get(role, [])
    decision = "Deny"  # default to deny if no rule matches

    for rule in role_rules:
        r_resource = rule.get("resource", "")
        r_action   = rule.get("action", "")
        if (r_resource == resource or r_resource == "*") and \
           (r_action   == action   or r_action   == "*"):
            decision = rule.get("decision", "Deny")
            break

    if decision == "Allow":
        return "Allow (HTTP 200)"
    return "Deny (HTTP 403)"


def _detect_actual_result(text_lower: str, rules: dict) -> str:
    """
    Detect whether the incident describes an unexpected success or unexpected denial.
    """
    success_signals = rules.get("failure_indicators", {}).get("unexpected_success", [])
    denial_signals  = rules.get("failure_indicators", {}).get("unexpected_denial", [])

    for sig in success_signals:
        if sig.lower() in text_lower:
            return "Success (HTTP 200)"

    for sig in denial_signals:
        if sig.lower() in text_lower:
            return "Denied (HTTP 403)"

    return "Unknown"


def _classify_failure(text_lower: str, expected: str, actual: str, rules: dict) -> str:
    """
    Classify the failure category from incident text and expected/actual mismatch.
    Checks category keywords in order — first match wins.
    Falls back to 'Authorization' when there is an Allow/Deny mismatch with no other match.
    """
    categories = rules.get("failure_categories", {})
    for category, keywords in categories.items():
        for kw in keywords:
            if str(kw).lower() in text_lower:
                return category

    # Structural inference: if expected and actual mismatch on Allow/Deny
    if expected and actual and expected != actual:
        if "Allow" in expected and "Success" not in actual:
            return "Authorization"
        if "Deny" in expected and "Denied" not in actual:
            return "Authorization"

    return "Unknown"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_incident(description: str) -> AnalysisResult:
    """
    Analyze a raw incident description and return a structured AnalysisResult.
    This function is the single entry point for the Analysis Engine.
    """
    result = AnalysisResult()
    rules  = load_analysis_rules()
    rbac   = load_rbac_config()

    text_lower = description.lower()

    # 1. Extract entities
    result.role     = _extract_role(text_lower, rules)
    result.action   = _extract_action(text_lower, rules)
    result.resource = _extract_resource(text_lower, rules)

    if not result.role:
        result.notes.append("Could not identify a role in the incident description.")
    if not result.action:
        result.notes.append("Could not identify an action in the incident description.")
    if not result.resource:
        result.notes.append("Could not identify a resource in the incident description.")

    # 2. Map resource + action to endpoint
    if result.resource and result.action:
        endpoint_map = RESOURCE_ENDPOINT_MAP.get(result.resource, {})
        mapping = endpoint_map.get(result.action)
        if mapping:
            result.http_method, result.endpoint = mapping
        else:
            result.notes.append(f"No endpoint mapping found for {result.action} on {result.resource}.")

    # 3. Resolve expected behavior from RBAC config
    result.expected_result = _resolve_expected_behavior(
        result.role, result.action, result.resource, rbac
    )

    # 4. Detect actual behavior from text signals
    result.actual_result = _detect_actual_result(text_lower, rules)

    # 5. Classify failure category
    result.failure_category = _classify_failure(
        text_lower, result.expected_result, result.actual_result, rules
    )

    # 6. Set confidence level
    extracted_count = sum([
        result.role is not None,
        result.action is not None,
        result.resource is not None,
        result.actual_result not in ("Unknown", None),
    ])
    if extracted_count >= 4:
        result.confidence = "high"
    elif extracted_count >= 2:
        result.confidence = "medium"
    else:
        result.confidence = "low"

    return result
