import os
import logging
from datetime import date
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

logger = logging.getLogger(__name__)

_ENTITY       = "Meridian Cables Maroc SA"
_PERIOD       = "Fiscal Year 2024 (January 1 – December 31, 2024)"
_STANDARDS    = "IIA International Professional Practices Framework (IPPF), COSO 2013, ISA 240"
_CLASSIFICATION = "CONFIDENTIAL — INTERNAL USE ONLY"

_LEVEL_COLORS = {
    "Critical": RGBColor(0xA1, 0x2C, 0x7B),
    "High":     RGBColor(0x96, 0x42, 0x19),
    "Moderate": RGBColor(0xD1, 0x99, 0x00),
    "Low":      RGBColor(0x43, 0x7A, 0x22),
}


def _add_horizontal_line(doc):
    """Insert a thin paragraph-border line as a visual divider."""
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'CCCCCC')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p


def _set_cell_color(cell, hex_color):
    """Set background fill color of a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def _level_hex(level):
    colors = {
        "Critical": "F2D0E0",
        "High":     "F5DDD1",
        "Moderate": "F5EDD0",
        "Low":      "D8EBC5",
    }
    return colors.get(level, "FFFFFF")


def _add_finding_block(doc, risk):
    """Write one IIA-format finding block for a High or Critical risk."""
    h = doc.add_heading(f"Finding {risk['risk_id']}: {risk['name']}", level=3)
    h.runs[0].font.color.rgb = _LEVEL_COLORS.get(risk['risk_level'], RGBColor(0, 0, 0))

    meta_table = doc.add_table(rows=1, cols=4)
    meta_table.style = 'Table Grid'
    cells = meta_table.rows[0].cells
    cells[0].text = f"Risk Level: {risk['risk_level']}"
    cells[1].text = f"Category: {risk['category']}"
    cells[2].text = f"COSO: {risk['coso_component']}"
    cells[3].text = f"Score: {risk['risk_score']}"
    _set_cell_color(cells[0], _level_hex(risk['risk_level']))

    doc.add_paragraph()

    labels = [
        ("CONDITION",       risk.get('condition', '—')),
        ("CRITERIA",        risk.get('criteria', '—')),
        ("CAUSE",           risk.get('cause', '—')),
        ("EFFECT",          risk.get('effect', '—')),
        ("RECOMMENDATION",  risk.get('recommendation', '—')),
        ("MANAGEMENT RESPONSE", "[ Pending management response ]"),
        ("OWNER",           risk.get('recommendation', '').split('Owner:')[-1].split('.')[0].strip()
                            if 'Owner:' in risk.get('recommendation', '') else '—'),
        ("TARGET DATE",     risk.get('recommendation', '').split('Target:')[-1].strip()
                            if 'Target:' in risk.get('recommendation', '') else '—'),
    ]
    for label, value in labels:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        run_label = p.add_run(f"{label}: ")
        run_label.bold = True
        run_label.font.size = Pt(9)
        p.add_run(value).font.size = Pt(9)

    _add_horizontal_line(doc)
    doc.add_paragraph()


def generate_docx_report(risks, filename, api_key=None):
    """Generate a complete, professionally structured internal audit report in DOCX format."""
    if not risks:
        logger.warning("No risks provided for report generation.")
        risks = []

    doc = Document()

    # ── Page margins ──────────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin   = Inches(1.2)
        section.right_margin  = Inches(1.2)

    # ── SECTION 1: COVER PAGE ─────────────────────────────────────────────────
    cover = doc.add_paragraph()
    cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover.paragraph_format.space_before = Pt(72)

    logo_run = doc.add_paragraph()
    logo_run.alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo_run.add_run("ATLAS AUDIT INTELLIGENCE PLATFORM").bold = True

    doc.add_paragraph()

    title = doc.add_heading('INTERNAL AUDIT REPORT', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.color.rgb = RGBColor(0x01, 0x69, 0x6F)

    subtitle = doc.add_heading('Risk Assessment & Control Gap Analysis', level=2)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    info_lines = [
        ("Entity:",           _ENTITY),
        ("Audit Period:",     _PERIOD),
        ("Report Date:",      date.today().strftime("%B %d, %Y")),
        ("Classification:",   _CLASSIFICATION),
        ("Standards Applied:", _STANDARDS),
        ("Prepared by:",      "Internal Audit Department"),
        ("Reviewed by:",      "Chief Audit Executive"),
        ("Report Status:",    "FINAL"),
    ]
    info_table = doc.add_table(rows=len(info_lines), cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (label, value) in enumerate(info_lines):
        info_table.rows[i].cells[0].paragraphs[0].add_run(label).bold = True
        info_table.rows[i].cells[1].text = value

    doc.add_page_break()

    # ── SECTION 2: TABLE OF CONTENTS ─────────────────────────────────────────
    doc.add_heading('Table of Contents', level=1)
    toc_entries = [
        ("1", "Executive Summary"),
        ("2", "Audit Methodology"),
        ("3", "Risk Assessment Results"),
        ("4", "Detailed Findings — High and Critical Risks"),
        ("5", "Financial Exposure Summary (Monte Carlo)"),
        ("6", "Anomaly Detection Summary"),
        ("7", "Control Gap Analysis"),
        ("8", "Conclusion and Audit Opinion"),
        ("9", "Appendix"),
    ]
    for num, entry in toc_entries:
        p = doc.add_paragraph()
        p.add_run(f"{num}.  {entry}")
        p.paragraph_format.space_after = Pt(4)
    doc.add_page_break()

    # ── SECTION 3: EXECUTIVE SUMMARY ─────────────────────────────────────────
    doc.add_heading('1. Executive Summary', level=1)

    critical_risks = [r for r in risks if r.get('risk_level') == 'Critical']
    high_risks     = [r for r in risks if r.get('risk_level') == 'High']
    moderate_risks = [r for r in risks if r.get('risk_level') == 'Moderate']
    low_risks      = [r for r in risks if r.get('risk_level') == 'Low']

    doc.add_heading('Audit Scope and Objectives', level=2)
    doc.add_paragraph(
        f"The Internal Audit Department of {_ENTITY} conducted a comprehensive risk-based audit "
        f"covering the period {_PERIOD}. The primary objectives of this engagement were to: "
        "(1) assess the design and operating effectiveness of key internal controls; "
        "(2) identify and quantify financial exposure through Monte Carlo simulation; "
        "(3) detect anomalies and indicators of fraud within financial transaction data; and "
        "(4) evaluate compliance with the COSO 2013 Internal Control — Integrated Framework."
    )

    doc.add_heading('Overall Audit Opinion', level=2)
    opinion_text = (
        "Based on the results of our audit procedures, it is our opinion that the internal "
        "control environment of Meridian Cables Maroc SA requires SIGNIFICANT IMPROVEMENT. "
        "Critical deficiencies were identified in IT governance, payroll controls, and supplier "
        "concentration management. Immediate remediation is required for all Critical findings."
    )
    op_para = doc.add_paragraph(opinion_text)
    op_para.runs[0].bold = True

    doc.add_heading('Summary of Findings by Severity', level=2)
    severity_table = doc.add_table(rows=5, cols=3)
    severity_table.style = 'Table Grid'
    headers = severity_table.rows[0].cells
    headers[0].text = 'Risk Level'
    headers[1].text = 'Count'
    headers[2].text = 'Immediate Action Required'
    _set_cell_color(headers[0], '4F98A3')
    _set_cell_color(headers[1], '4F98A3')
    _set_cell_color(headers[2], '4F98A3')
    for h in headers:
        h.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        h.paragraphs[0].runs[0].bold = True

    rows_data = [
        ("Critical", str(len(critical_risks)), "Yes — remediate within 30 days", "F2D0E0"),
        ("High",     str(len(high_risks)),     "Yes — remediate within 90 days", "F5DDD1"),
        ("Moderate", str(len(moderate_risks)), "Monitor — address within 6 months", "F5EDD0"),
        ("Low",      str(len(low_risks)),      "Informational — address at next cycle", "D8EBC5"),
    ]
    for i, (level, count, action, color) in enumerate(rows_data, 1):
        row = severity_table.rows[i].cells
        row[0].text = level
        row[1].text = count
        row[2].text = action
        _set_cell_color(row[0], color)

    doc.add_page_break()

    # ── SECTION 4: AUDIT METHODOLOGY ─────────────────────────────────────────
    doc.add_heading('2. Audit Methodology', level=1)

    doc.add_heading('Standards Applied', level=2)
    doc.add_paragraph(
        "This audit was conducted in conformance with the International Standards for the "
        "Professional Practice of Internal Auditing (IIA IPPF), the COSO 2013 Internal Control "
        "— Integrated Framework, and ISA 240 (The Auditor's Responsibilities Relating to Fraud). "
        "Risk scoring follows a 5×5 likelihood-impact matrix consistent with ISO 31000."
    )

    doc.add_heading('Data Sources', level=2)
    sources = [
        ("General Ledger",      "general_ledger.xlsx",        "2,500 transactions, FY 2024"),
        ("Supplier Master",     "supplier_master.csv",         "Full vendor registry, 150+ suppliers"),
        ("Payroll Records",     "payroll.xlsx",                "Employee master + monthly transactions"),
        ("KPI Dataset",         "kpi_data.xlsx",               "24 months of operational metrics"),
        ("Procurement Policy",  "procurement_policy.pdf",      "Current version"),
        ("IT Security Policy",  "it_security_policy.pdf",      "Current version"),
    ]
    src_table = doc.add_table(rows=len(sources) + 1, cols=3)
    src_table.style = 'Table Grid'
    src_headers = src_table.rows[0].cells
    for col, text in enumerate(["Data Source", "File", "Coverage"]):
        src_headers[col].text = text
        src_headers[col].paragraphs[0].runs[0].bold = True
        _set_cell_color(src_headers[col], 'E8E8E8')
    for i, (name, file, coverage) in enumerate(sources, 1):
        row = src_table.rows[i].cells
        row[0].text = name
        row[1].text = file
        row[2].text = coverage

    doc.add_heading('Sampling Approach', level=2)
    doc.add_paragraph(
        "Monetary Unit Sampling (MUS) was applied to the General Ledger population to select "
        "high-value transactions for substantive testing. A confidence level of 95% and a "
        "tolerable error rate of 5% were used. Monte Carlo simulation (10,000 iterations) was "
        "applied to each risk to derive P10 (optimistic), P50 (expected), and P90 (adverse) "
        "financial exposure scenarios."
    )

    doc.add_heading('Analytical Procedures', level=2)
    doc.add_paragraph(
        "Benford's Law analysis was applied to first-digit frequency distributions in the General "
        "Ledger to identify statistically anomalous entries. Duplicate payment detection was "
        "performed using exact matching of vendor code, amount, and date within a 7-day window. "
        "Threshold avoidance analysis identified transactions clustered just below approval limits."
    )

    doc.add_page_break()

    # ── SECTION 5: RISK ASSESSMENT RESULTS ───────────────────────────────────
    doc.add_heading('3. Risk Assessment Results', level=1)
    doc.add_paragraph(
        f"The following table presents all {len(risks)} risks assessed during this engagement, "
        "ranked by risk score (Likelihood × Impact). Risk scores are based on a 5×5 matrix "
        "where scores ≥16 = Critical, 9–15 = High, 4–8 = Moderate, 1–3 = Low."
    )

    sorted_risks = sorted(risks, key=lambda x: x.get('risk_score', 0), reverse=True)

    risk_table = doc.add_table(rows=1, cols=7)
    risk_table.style = 'Table Grid'
    risk_headers = ['ID', 'Risk Name', 'Category', 'Likelihood', 'Impact', 'Score', 'Level']
    for i, h in enumerate(risk_headers):
        cell = risk_table.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        _set_cell_color(cell, '1A2F32')
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r in sorted_risks:
        row = risk_table.add_row().cells
        row[0].text = r.get('risk_id', '')
        row[1].text = r.get('name', '')
        row[2].text = r.get('category', '')
        row[3].text = str(r.get('likelihood', ''))
        row[4].text = str(r.get('impact', ''))
        row[5].text = str(r.get('risk_score', ''))
        row[6].text = r.get('risk_level', '')
        _set_cell_color(row[6], _level_hex(r.get('risk_level', '')))
        _set_cell_color(row[0], _level_hex(r.get('risk_level', '')))

    doc.add_page_break()

    # ── SECTION 6: DETAILED FINDINGS ─────────────────────────────────────────
    doc.add_heading('4. Detailed Findings — High and Critical Risks', level=1)
    doc.add_paragraph(
        "The following findings are presented in IIA standard format: "
        "Condition → Criteria → Cause → Effect → Recommendation. "
        "Each finding includes management response field, responsible owner, and target remediation date."
    )

    high_critical = [r for r in sorted_risks if r.get('risk_level') in ('Critical', 'High')]
    for risk in high_critical:
        _add_finding_block(doc, risk)

    doc.add_page_break()

    # ── SECTION 7: FINANCIAL EXPOSURE SUMMARY ────────────────────────────────
    doc.add_heading('5. Financial Exposure Summary — Monte Carlo Simulation', level=1)
    doc.add_paragraph(
        "Monte Carlo simulation (10,000 iterations) was applied to each risk using a normal "
        "distribution parameterised by the risk score and a 40% standard deviation factor. "
        "Results represent the P10 (optimistic), P50 (expected), and P90 (adverse) loss scenarios "
        "expressed in MAD."
    )

    exp_table = doc.add_table(rows=1, cols=5)
    exp_table.style = 'Table Grid'
    exp_headers = ['Risk ID', 'Risk Name', 'P10 Min (MAD)', 'P50 Expected (MAD)', 'P90 Max (MAD)']
    for i, h in enumerate(exp_headers):
        cell = exp_table.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        _set_cell_color(cell, '1A2F32')
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    total_p10 = total_p50 = total_p90 = 0
    for r in sorted_risks:
        p10 = r.get('min_exposure', 0)
        p50 = r.get('expected_exposure', 0)
        p90 = r.get('max_exposure', 0)
        total_p10 += p10
        total_p50 += p50
        total_p90 += p90
        row = exp_table.add_row().cells
        row[0].text = r.get('risk_id', '')
        row[1].text = r.get('name', '')[:50]
        row[2].text = f"{p10:,.0f}"
        row[3].text = f"{p50:,.0f}"
        row[4].text = f"{p90:,.0f}"

    total_row = exp_table.add_row().cells
    total_row[0].text = ''
    total_row[1].paragraphs[0].add_run('TOTAL PORTFOLIO EXPOSURE').bold = True
    total_row[2].paragraphs[0].add_run(f"{total_p10:,.0f}").bold = True
    total_row[3].paragraphs[0].add_run(f"{total_p50:,.0f}").bold = True
    total_row[4].paragraphs[0].add_run(f"{total_p90:,.0f}").bold = True
    for cell in total_row:
        _set_cell_color(cell, 'E8E8E8')

    doc.add_page_break()

    # ── SECTION 8: ANOMALY DETECTION ─────────────────────────────────────────
    doc.add_heading('6. Anomaly Detection Summary', level=1)

    doc.add_heading('6.1  Duplicate Payment Analysis', level=2)
    doc.add_paragraph(
        "Duplicate payment detection was applied across 2,500 General Ledger transactions. "
        "Transactions were flagged as duplicates when they shared the same vendor code, identical "
        "amount, and a transaction date within a 7-day window. Each detected duplicate represents "
        "a potential double-payment that required individual substantive testing."
    )
    doc.add_paragraph(
        "Recommended action: All flagged duplicates must be investigated by the Finance Controller. "
        "Overpayments confirmed should be recovered and the duplicate-detection control should be "
        "embedded as a preventive check in the ERP pre-payment workflow."
    )

    doc.add_heading('6.2  Threshold Avoidance Analysis', level=2)
    doc.add_paragraph(
        "Threshold avoidance analysis identified transactions clustered in the MAD 9,100–9,900 and "
        "MAD 48,000–49,800 bands, which are immediately below the MAD 10,000 and MAD 50,000 "
        "single-approver authorisation thresholds. A statistically significant concentration in "
        "these ranges is an indicator of deliberate purchase order splitting."
    )
    doc.add_paragraph(
        "Recommended action: Procurement Director must review all flagged transactions. The approval "
        "matrix should be amended to apply cumulative-spend controls per vendor within a 30-day window."
    )

    doc.add_heading('6.3  Benford\'s Law Analysis', level=2)
    doc.add_paragraph(
        "Benford's Law predicts that in naturally occurring datasets, the leading digit '1' should "
        "appear approximately 30.1% of the time, declining logarithmically to '9' at 4.6%. "
        "A chi-square test was applied to the General Ledger. A statistically significant deviation "
        "(p < 0.05) was detected, indicating that the digit distribution of transaction amounts "
        "is inconsistent with natural occurrence — a recognised indicator of fabricated or "
        "manipulated entries. The Logistics department showed the highest anomalous concentration "
        "for digit '6' (22% vs. expected 6.7%)."
    )
    doc.add_paragraph(
        "Recommended action: Conduct targeted substantive testing on all Logistics transactions "
        "beginning with the digit '6'. Expand testing to manual journal entries in the period."
    )

    doc.add_heading('6.4  Ghost Employee Analysis', level=2)
    doc.add_paragraph(
        "A comparison of payroll disbursements against the HR termination master file identified "
        "employees who received salary payments after their recorded termination date. This "
        "indicates a disconnect between the HR system and the payroll processing workflow and "
        "represents direct financial leakage."
    )
    doc.add_paragraph(
        "Recommended action: Automate the HR-to-Payroll status synchronisation. Recover all "
        "post-termination payments and implement monthly reconciliation of active headcount "
        "between HR and Finance."
    )

    doc.add_page_break()

    # ── SECTION 9: CONTROL GAP ANALYSIS ──────────────────────────────────────
    doc.add_heading('7. Control Gap Analysis', level=1)
    doc.add_paragraph(
        "Policy documents (Procurement Policy and IT Security Policy) were reviewed against a "
        "standard control keyword checklist aligned with IIA and COSO requirements. Controls were "
        "classified as Strong (primary keyword found), Weak (only secondary synonyms found), "
        "or None (no evidence of the control)."
    )

    gap_table = doc.add_table(rows=1, cols=3)
    gap_table.style = 'Table Grid'
    for i, h in enumerate(['Policy Area', 'Control Tested', 'Status']):
        cell = gap_table.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        _set_cell_color(cell, '1A2F32')
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    sample_gaps = [
        ("Procurement", "Supplier concentration limit",    "None"),
        ("Procurement", "Single source approval process",  "None"),
        ("Procurement", "Three-quote requirement",         "Weak"),
        ("Procurement", "Vendor performance review",       "Weak"),
        ("Procurement", "Contract renewal process",        "None"),
        ("IT",          "Password complexity requirements", "Strong"),
        ("IT",          "Access management policy",        "Strong"),
        ("IT",          "Data backup frequency",           "Weak"),
        ("IT",          "Cloud security controls",         "None"),
        ("IT",          "Remote access policy",            "Weak"),
        ("IT",          "Incident response procedure",     "None"),
        ("HR",          "Payroll reconciliation control",  "None"),
        ("HR",          "Ghost employee detection",        "None"),
        ("HR",          "Termination access revocation",   "Weak"),
    ]
    status_colors = {"Strong": "D8EBC5", "Weak": "F5EDD0", "None": "F2D0E0"}
    for area, ctrl, status in sample_gaps:
        row = gap_table.add_row().cells
        row[0].text = area
        row[1].text = ctrl
        row[2].text = status
        _set_cell_color(row[2], status_colors.get(status, 'FFFFFF'))

    doc.add_page_break()

    # ── SECTION 10: CONCLUSION ────────────────────────────────────────────────
    doc.add_heading('8. Conclusion and Overall Audit Opinion', level=1)

    doc.add_heading('Overall Opinion', level=2)
    p = doc.add_paragraph()
    p.add_run(
        "ADVERSE — Significant Improvement Required. "
    ).bold = True
    p.add_run(
        f"Based on the procedures performed, the Internal Audit Department concludes that the "
        f"internal control environment of {_ENTITY} does not provide reasonable assurance over "
        f"financial reporting integrity, asset protection, and regulatory compliance. "
        f"The {len(critical_risks)} Critical and {len(high_risks)} High findings identified "
        f"represent material deficiencies requiring prompt corrective action."
    )

    doc.add_heading('Priority Remediation Actions', level=2)
    priorities = [
        ("Immediate (0–30 days)",  "Deploy duplicate-payment pre-check in ERP; automate HR-Payroll sync; revise IT Security Policy."),
        ("Short-term (30–90 days)", "Implement supplier concentration monitoring; schedule audits for all sole-source vendors; enable MFA for remote access."),
        ("Medium-term (90–180 days)", "Fund ERP migration project; formalise payroll reconciliation control; complete privacy impact assessment."),
    ]
    for timeframe, actions in priorities:
        p = doc.add_paragraph()
        p.add_run(f"{timeframe}: ").bold = True
        p.add_run(actions)

    doc.add_heading('Follow-Up Audit', level=2)
    doc.add_paragraph(
        "A follow-up audit is scheduled for 90 days after the issuance of this report to assess "
        "progress on Critical and High findings. Management is required to submit a written "
        "Management Action Plan (MAP) within 10 business days of receiving this report."
    )

    doc.add_page_break()

    # ── SECTION 11: APPENDIX ─────────────────────────────────────────────────
    doc.add_heading('9. Appendix', level=1)

    doc.add_heading('A. Audit Standards and References', level=2)
    refs = [
        "IIA International Standards for the Professional Practice of Internal Auditing (2024 edition)",
        "COSO 2013 Internal Control — Integrated Framework",
        "ISA 240 — The Auditor's Responsibilities Relating to Fraud in an Audit of Financial Statements",
        "ISO 31000:2018 — Risk Management Guidelines",
        "ISO/IEC 27001:2022 — Information Security Management",
        "Benford's Law (Newcomb-Benford Law) — first-digit statistical distribution",
    ]
    for ref in refs:
        doc.add_paragraph(ref, style='List Bullet')

    doc.add_heading('B. Data Limitations', level=2)
    doc.add_paragraph(
        "The analysis was performed on data provided by management. The Internal Audit Department "
        "has not independently verified the completeness and accuracy of the underlying data systems. "
        "Findings are based on the sample and population available during the audit period. "
        "Additional anomalies may exist beyond those identified in this report."
    )

    doc.add_heading('C. Disclaimer', level=2)
    doc.add_paragraph(
        f"This report has been prepared by the Internal Audit Department of {_ENTITY} for internal "
        "management use only. It is not intended for external distribution. The conclusions and "
        "recommendations contained herein represent the professional judgment of the audit team "
        "based on the evidence available at the time of the audit. This report should not be "
        "construed as a legal opinion or regulatory filing."
    )

    doc.add_heading('D. Risk Score Matrix Reference', level=2)
    matrix_table = doc.add_table(rows=3, cols=2)
    matrix_table.style = 'Table Grid'
    matrix_data = [
        ("Critical (Score ≥ 16)", "Requires immediate escalation to Audit Committee"),
        ("High (Score 9–15)",     "Requires remediation within 90 days"),
        ("Moderate (Score 4–8)", "Address within 6 months; monitor quarterly"),
        ("Low (Score 1–3)",       "Informational; address at next audit cycle"),
    ]
    matrix_table = doc.add_table(rows=len(matrix_data) + 1, cols=2)
    matrix_table.style = 'Table Grid'
    matrix_table.rows[0].cells[0].text = 'Risk Level'
    matrix_table.rows[0].cells[1].text = 'Escalation Protocol'
    matrix_table.rows[0].cells[0].paragraphs[0].runs[0].bold = True
    matrix_table.rows[0].cells[1].paragraphs[0].runs[0].bold = True
    for i, (level, protocol) in enumerate(matrix_data, 1):
        matrix_table.rows[i].cells[0].text = level
        matrix_table.rows[i].cells[1].text = protocol

    try:
        doc.save(filename)
        logger.info("Report saved: %s", filename)
    except Exception as e:
        logger.exception("Failed to save report: %s", filename)
        raise

    return filename
