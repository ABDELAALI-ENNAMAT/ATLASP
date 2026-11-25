import json
import os
import re
import logging
import pdfplumber

logger = logging.getLogger(__name__)

_OUTDATED_YEARS = {'2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021'}


def detect_policy_date(text):
    """Extract the most recent date from policy review/effective date patterns."""
    patterns = [
        r'last reviewed[:\s]+([a-zA-Z]+\s+\d{4}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})',
        r'effective date[:\s]+([a-zA-Z]+\s+\d{4}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})',
        r'revision date[:\s]+([a-zA-Z]+\s+\d{4}|\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})',
    ]
    found = []
    for p in patterns:
        found.extend(re.findall(p, text, re.IGNORECASE))
    return found[0] if found else None


def get_synonyms(control_name):
    """Return keyword clusters for a control name (primary + secondary terms)."""
    synonyms = {
        "supplier concentration limit": [
            ["concentration limit", "spend limit", "concentration risk"],           # primary
            ["maximum single-source", "maximum supplier", "single vendor cap"]       # secondary
        ],
        "single source approval process": [
            ["single source", "sole source"],
            ["exception approval", "waiver process"]
        ],
        "three quote requirement": [
            ["three quote", "3 quotes", "minimum quotes"],
            ["competitive bidding", "tender process"]
        ],
        "vendor performance review": [
            ["vendor performance", "supplier evaluation"],
            ["vendor audit", "supplier review", "kpi review"]
        ],
        "contract renewal process": [
            ["contract renewal", "renewal process"],
            ["contract expiry", "contract management"]
        ],
        "geographic diversification policy": [
            ["geographic diversif", "regional spread"],
            ["country risk", "supplier geography"]
        ],
        "password complexity requirements": [
            ["password complexity", "length and complexity"],
            ["special characters", "password strength", "minimum length"]
        ],
        "access management policy": [
            ["access management", "least privilege"],
            ["role-based access", "user provisioning", "rbac"]
        ],
        "data backup frequency": [
            ["backup frequency", "recovery point objective", "rpo"],
            ["daily backup", "backup schedule", "data recovery"]
        ],
        "cloud security controls": [
            ["cloud security", "aws", "azure"],
            ["cloud provider", "saas security", "cloud access"]
        ],
        "remote access policy": [
            ["remote access", "vpn"],
            ["telecommuting", "work from home", "wfh policy"]
        ],
        "incident response procedure": [
            ["incident response", "security breach"],
            ["response plan", "breach notification", "ir procedure"]
        ],
        "policy review cycle": [
            ["policy review", "annual review"],
            ["review cycle", "policy update", "review cadence"]
        ],
        "payroll reconciliation": [
            ["payroll reconciliation", "payroll review"],
            ["payroll variance", "payroll audit", "reconciliation report"]
        ],
        "termination access revocation": [
            ["termination", "offboarding"],
            ["access revocation", "account deactivation"]
        ],
    }
    entry = synonyms.get(control_name)
    if entry:
        return entry  # [[primary_terms], [secondary_terms]]
    # Fallback: treat the control name itself as primary, no secondary
    return [[control_name], []]


def analyze_controls(pdf_path, category, rules_path):
    """
    Analyze a policy PDF against required controls.
    Returns Strong / Weak / None per control:
      - Strong  : primary keyword cluster found
      - Weak    : only secondary synonyms found
      - None    : no mention at all
    """
    if not os.path.exists(pdf_path):
        logger.warning("PDF not found: %s — returning empty results for %s", pdf_path, category)
        return {"results": {}, "gaps": [], "policy_date": None, "policy_date_flag": False}

    with open(rules_path, 'r') as f:
        rules = json.load(f)

    required_controls = rules.get(category, {}).get('required_controls', [])
    if not required_controls:
        return {"results": {}, "gaps": [], "policy_date": None, "policy_date_flag": False}

    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text.lower() + " "
    except Exception as e:
        logger.error("Failed to read PDF %s: %s", pdf_path, e)
        return {"results": {}, "gaps": [], "policy_date": None, "policy_date_flag": False}

    results = {}
    gaps = []

    for control in required_controls:
        clusters = get_synonyms(control)
        primary_terms = clusters[0] if len(clusters) > 0 else [control]
        secondary_terms = clusters[1] if len(clusters) > 1 else []

        primary_found = any(term.lower() in text for term in primary_terms)
        secondary_found = any(term.lower() in text for term in secondary_terms)

        if primary_found:
            status = "Strong"
        elif secondary_found:
            status = "Weak"
        else:
            status = "None"

        results[control] = status
        if status in ("None", "Weak"):
            gaps.append(control)

    policy_date = detect_policy_date(text)
    policy_date_flag = bool(
        policy_date and any(yr in policy_date for yr in _OUTDATED_YEARS)
    )

    return {
        "results": results,
        "gaps": gaps,
        "policy_date": policy_date,
        "policy_date_flag": policy_date_flag
    }
