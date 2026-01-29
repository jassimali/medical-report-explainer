# backend/parsed_report_utils.py

import re
from typing import Dict, Any


# Simple patterns for some common tests (you can add more)
TEST_PATTERNS = {
    "Hemoglobin": [r"\bHb\b", r"\bHemoglobin\b"],
    "RBC": [r"\bRBC\b"],
    "WBC": [r"\bWBC\b", r"\bTotal Leukocyte Count\b"],
    "Platelets": [r"\bPlatelet[s]?\b"],
    "Vitamin D": [r"\bVitamin\s*D\b", r"\bVit\s*D\b"],
    "Vitamin B12": [r"\bVitamin\s*B12\b", r"\bVit\s*B12\b"],
    "Total Cholesterol": [r"\bTotal\s*Cholesterol\b"],
    "HDL": [r"\bHDL\b"],
    "LDL": [r"\bLDL\b"],
    "Triglycerides": [r"\bTriglycerides\b"],
}


def extract_test_value(line: str):
    """
    Look for a pattern like:  'Hb  10.5 g/dL'  or 'Hemoglobin:  13.2 g/dL'
    Returns (value, unit) or (None, None)
    """
    # number (maybe decimal) followed by optional unit text
    match = re.search(r"(\d+(\.\d+)?)\s*([a-zA-Z/%]+)?", line)
    if not match:
        return None, None
    value = float(match.group(1))
    unit = match.group(3) or ""
    return value, unit


def parse_report_text(report_text: str) -> Dict[str, Any]:
    """
    Very rough parser:
    - Splits into lines
    - For each known test, if a pattern matches a line, tries to read a numeric value + unit.
    Returns dict { test_name: {"value": x, "unit": "g/dL"} }
    """
    results: Dict[str, Any] = {}
    lines = report_text.splitlines()

    for line in lines:
        # Skip empty/short lines
        if len(line.strip()) < 3:
            continue

        for test_name, patterns in TEST_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, line, flags=re.IGNORECASE):
                    value, unit = extract_test_value(line)
                    if value is not None:
                        # store only first found occurrence
                        if test_name not in results:
                            results[test_name] = {
                                "value": value,
                                "unit": unit
                            }
                    break

    return results
