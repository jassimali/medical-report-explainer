# backend/parsed_report_utils.py

import re
from typing import Dict, Any


# Simple patterns for some common tests (you can add more)
TEST_PATTERNS = {

    # =========================
    # CBC - Complete Blood Count
    # =========================
    "Hemoglobin": [
        r"\bHb\b",
        r"\bHgb\b",
        r"\bHemoglobin\b"
    ],

    "RBC": [
        r"\bRBC\b",
        r"\bRed\s*Blood\s*Cells?\b",
        r"\bRed\s*Cell\s*Count\b"
    ],

    "WBC": [
        r"\bWBC\b",
        r"\bWhite\s*Blood\s*Cells?\b",
        r"\bTotal\s*Leukocyte\s*Count\b",
        r"\bTLC\b"
    ],

    "Platelets": [
        r"\bPlatelet[s]?\b",
        r"\bPlatelet\s*Count\b"
    ],

    "Hematocrit": [
        r"\bHCT\b",
        r"\bHematocrit\b",
        r"\bPCV\b",
        r"\bPacked\s*Cell\s*Volume\b"
    ],

    "MCV": [
        r"\bMCV\b",
        r"\bMean\s*Corpuscular\s*Volume\b"
    ],

    "MCH": [
        r"\bMCH\b",
        r"\bMean\s*Corpuscular\s*Hemoglobin\b"
    ],

    "MCHC": [
        r"\bMCHC\b",
        r"\bMean\s*Corpuscular\s*Hemoglobin\s*Concentration\b"
    ],

    "RDW": [
        r"\bRDW\b",
        r"\bRed\s*Cell\s*Distribution\s*Width\b"
    ],


    # =========================
    # BLOOD SUGAR / DIABETES
    # =========================
    "Fasting Blood Sugar": [
        r"\bFasting\s*(Blood\s*)?Sugar\b",
        r"\bFasting\s*Glucose\b",
        r"\bFBS\b",
        r"\bFBG\b"
    ],

    "Postprandial Blood Sugar": [
        r"\bPost\s*Prandial\s*(Blood\s*)?Sugar\b",
        r"\bPostprandial\s*Glucose\b",
        r"\bPPBS\b",
        r"\bPPBG\b"
    ],

    "Random Blood Sugar": [
        r"\bRandom\s*(Blood\s*)?Sugar\b",
        r"\bRandom\s*Glucose\b",
        r"\bRBS\b",
        r"\bRBG\b"
    ],

    "Blood Glucose": [
        r"\bBlood\s*Glucose\b",
        r"\bGlucose\b"
    ],

    "HbA1c": [
        r"\bHbA1c\b",
        r"\bA1C\b",
        r"\bGlycated\s*Hemoglobin\b",
        r"\bGlycosylated\s*Hemoglobin\b"
    ],


    # =========================
    # LIPID PROFILE
    # =========================
    "Total Cholesterol": [
        r"\bTotal\s*Cholesterol\b",
        r"\bCholesterol\b"
    ],

    "HDL": [
        r"\bHDL\b",
        r"\bHDL\s*Cholesterol\b"
    ],

    "LDL": [
        r"\bLDL\b",
        r"\bLDL\s*Cholesterol\b"
    ],

    "VLDL": [
        r"\bVLDL\b",
        r"\bVLDL\s*Cholesterol\b"
    ],

    "Triglycerides": [
        r"\bTriglycerides?\b",
        r"\bTG\b"
    ],

    "Non-HDL Cholesterol": [
        r"\bNon[-\s]?HDL\b",
        r"\bNon[-\s]?HDL\s*Cholesterol\b"
    ],


    # =========================
    # LIVER FUNCTION TEST - LFT
    # =========================
    "Bilirubin Total": [
        r"\bTotal\s*Bilirubin\b",
        r"\bBilirubin\s*Total\b"
    ],

    "Bilirubin Direct": [
        r"\bDirect\s*Bilirubin\b",
        r"\bConjugated\s*Bilirubin\b",
        r"\bBilirubin\s*Direct\b"
    ],

    "Bilirubin Indirect": [
        r"\bIndirect\s*Bilirubin\b",
        r"\bUnconjugated\s*Bilirubin\b",
        r"\bBilirubin\s*Indirect\b"
    ],

    "ALT": [
        r"\bALT\b",
        r"\bSGPT\b",
        r"\bAlanine\s*Aminotransferase\b"
    ],

    "AST": [
        r"\bAST\b",
        r"\bSGOT\b",
        r"\bAspartate\s*Aminotransferase\b"
    ],

    "ALP": [
        r"\bALP\b",
        r"\bAlkaline\s*Phosphatase\b"
    ],

    "GGT": [
        r"\bGGT\b",
        r"\bGamma[-\s]?GT\b",
        r"\bGamma\s*Glutamyl\s*Transferase\b"
    ],

    "Total Protein": [
        r"\bTotal\s*Protein\b"
    ],

    "Albumin": [
        r"\bAlbumin\b"
    ],

    "Globulin": [
        r"\bGlobulin\b"
    ],

    "A/G Ratio": [
        r"\bA/?G\s*Ratio\b",
        r"\bAlbumin\s*/\s*Globulin\s*Ratio\b"
    ],


    # =========================
    # KIDNEY FUNCTION - KFT/RFT
    # =========================
    "Creatinine": [
        r"\bCreatinine\b",
        r"\bSerum\s*Creatinine\b"
    ],

    "Blood Urea": [
        r"\bBlood\s*Urea\b",
        r"\bUrea\b",
        r"\bSerum\s*Urea\b"
    ],

    "BUN": [
        r"\bBUN\b",
        r"\bBlood\s*Urea\s*Nitrogen\b"
    ],

    "Uric Acid": [
        r"\bUric\s*Acid\b",
        r"\bSerum\s*Uric\s*Acid\b"
    ],

    "eGFR": [
        r"\beGFR\b",
        r"\bEstimated\s*GFR\b",
        r"\bEstimated\s*Glomerular\s*Filtration\s*Rate\b"
    ],


    # =========================
    # ELECTROLYTES
    # =========================
    "Sodium": [
        r"\bSodium\b",
        r"\bNa\+?\b"
    ],

    "Potassium": [
        r"\bPotassium\b",
        r"\bK\+?\b"
    ],

    "Chloride": [
        r"\bChloride\b",
        r"\bCl[-]?\b"
    ],

    "Calcium": [
        r"\bCalcium\b",
        r"\bCa\b"
    ],

    "Magnesium": [
        r"\bMagnesium\b",
        r"\bMg\b"
    ],

    "Phosphorus": [
        r"\bPhosphorus\b",
        r"\bPhosphate\b"
    ],


    # =========================
    # THYROID FUNCTION
    # =========================
    "TSH": [
        r"\bTSH\b",
        r"\bThyroid\s*Stimulating\s*Hormone\b"
    ],

    "Free T3": [
        r"\bFree\s*T3\b",
        r"\bFT3\b"
    ],

    "Free T4": [
        r"\bFree\s*T4\b",
        r"\bFT4\b"
    ],

    "Total T3": [
        r"\bTotal\s*T3\b"
    ],

    "Total T4": [
        r"\bTotal\s*T4\b"
    ],


    # =========================
    # VITAMINS
    # =========================
    "Vitamin D": [
        r"\bVitamin\s*D\b",
        r"\bVit\s*D\b",
        r"\b25[-\s]?OH\s*Vitamin\s*D\b",
        r"\b25[-\s]?Hydroxy\s*Vitamin\s*D\b"
    ],

    "Vitamin B12": [
        r"\bVitamin\s*B12\b",
        r"\bVit\s*B12\b",
        r"\bCobalamin\b"
    ],

    "Folate": [
        r"\bFolate\b",
        r"\bFolic\s*Acid\b",
        r"\bVitamin\s*B9\b"
    ],


    # =========================
    # IRON PROFILE
    # =========================
    "Serum Iron": [
        r"\bSerum\s*Iron\b",
        r"\bIron\b"
    ],

    "Ferritin": [
        r"\bFerritin\b"
    ],

    "TIBC": [
        r"\bTIBC\b",
        r"\bTotal\s*Iron\s*Binding\s*Capacity\b"
    ],

    "Transferrin": [
        r"\bTransferrin\b"
    ],

    "Transferrin Saturation": [
        r"\bTransferrin\s*Saturation\b",
        r"\bTSAT\b"
    ],


    # =========================
    # PANCREATIC
    # =========================
    "Amylase": [
        r"\bAmylase\b"
    ],

    "Lipase": [
        r"\bLipase\b"
    ],


    # =========================
    # INFLAMMATION / INFECTION
    # =========================
    "CRP": [
        r"\bCRP\b",
        r"\bC[-\s]?Reactive\s*Protein\b"
    ],

    "ESR": [
        r"\bESR\b",
        r"\bErythrocyte\s*Sedimentation\s*Rate\b"
    ],


    # =========================
    # URINE TESTS
    # =========================
    "Urine Protein": [
        r"\bUrine\s*Protein\b",
        r"\bProtein\s*Urine\b"
    ],

    "Urine Glucose": [
        r"\bUrine\s*Glucose\b",
        r"\bGlucose\s*Urine\b"
    ],

    "Urine Ketones": [
        r"\bUrine\s*Ketones?\b",
        r"\bKetones?\s*Urine\b"
    ],

    "Urine Blood": [
        r"\bUrine\s*Blood\b",
        r"\bBlood\s*in\s*Urine\b"
    ],

    "Urine pH": [
        r"\bUrine\s*pH\b"
    ],


    # =========================
    # OTHER COMMON TESTS
    # =========================
    "PSA": [
        r"\bPSA\b",
        r"\bProstate\s*Specific\s*Antigen\b"
    ],

    "LDH": [
        r"\bLDH\b",
        r"\bLactate\s*Dehydrogenase\b"
    ],

    "Vitamin B6": [
        r"\bVitamin\s*B6\b",
        r"\bPyridoxine\b"
    ]
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
