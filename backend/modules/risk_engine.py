import pandas as pd

def get_all_risks():
    """Returns all 24 risks formatted with IIA standard fields."""
    risks_list = [
        {
            "risk_id": "R01",
            "name": "Supplier concentration (NEXANS >38% spend)",
            "category": "Operational",
            "coso_component": "Risk Assessment",
            "likelihood": 5, "impact": 4, "risk_score": 20, "risk_level": "Critical",
            "detection_method": "Data Analysis", "evidence_source": "supplier_master.csv", "department": "Procurement",
            "condition": "Supplier NEXANS accounts for more than 38% of total annual procurement spend.",
            "criteria": "Internal policy and IIA standards require supplier diversification to prevent supply chain disruption.",
            "cause": "Lack of automated concentration monitoring and weak enforcement of vendor diversification policy.",
            "effect": "High risk of operational disruption if the primary supplier fails or changes terms.",
            "recommendation": "Implement automated supplier spend tracking and enforce a 20% hard limit per supplier. Owner: CPO. Target: 90 days."
        },
        {
            "risk_id": "R02",
            "name": "IT system obsolescence (ERP >7 years old)",
            "category": "IT",
            "coso_component": "Control Environment",
            "likelihood": 4, "impact": 5, "risk_score": 20, "risk_level": "Critical",
            "detection_method": "Document Review", "evidence_source": "general_ledger.xlsx", "department": "IT",
            "condition": "Legacy ERP maintenance costs exceed 250k MAD and system is past vendor support lifecycle.",
            "criteria": "COSO 2013 Principle 11 requires organizations to select and develop general control activities over technology.",
            "cause": "Deferred capital expenditure and absence of an IT modernization roadmap.",
            "effect": "System failure, data loss, and escalating maintenance costs.",
            "recommendation": "Develop and fund a 3-year ERP migration plan to a supported cloud ERP. Owner: CIO. Target: 180 days."
        },
        {
            "risk_id": "R03",
            "name": "Foreign exchange exposure EUR/MAD",
            "category": "Financial",
            "coso_component": "Risk Assessment",
            "likelihood": 4, "impact": 3, "risk_score": 12, "risk_level": "High",
            "detection_method": "Market Analysis", "evidence_source": "External Data", "department": "Finance",
            "condition": "Significant volume of unhedged EUR-denominated transactions.",
            "criteria": "Financial risk management policy requires hedging for FX exposure over 100k EUR.",
            "cause": "Lack of automated FX risk monitoring and delayed treasury action.",
            "effect": "Financial losses due to adverse currency fluctuations.",
            "recommendation": "Implement an automated FX exposure dashboard and execute forward contracts. Owner: Treasurer. Target: 30 days."
        },
        {
            "risk_id": "R04",
            "name": "Duplicate payroll payments detected",
            "category": "Fraud",
            "coso_component": "Control Activities",
            "likelihood": 5, "impact": 3, "risk_score": 15, "risk_level": "High",
            "detection_method": "Data Analysis", "evidence_source": "payroll.xlsx", "department": "HR",
            "condition": "Instances of duplicate salary payments detected for the same employee within the same month.",
            "criteria": "IIA Standard 2320 and internal payment policy require duplicate payment controls.",
            "cause": "Absence of automated pre-payment duplicate detection in the ERP system.",
            "effect": "Direct financial loss from overpayment and reputational risk.",
            "recommendation": "Implement automated duplicate check on employee + amount + month. Owner: CFO. Target: 60 days."
        },
        {
            "risk_id": "R05",
            "name": "Ghost employee payments post-termination",
            "category": "Fraud",
            "coso_component": "Control Activities",
            "likelihood": 4, "impact": 4, "risk_score": 16, "risk_level": "Critical",
            "detection_method": "Data Analysis", "evidence_source": "payroll.xlsx", "department": "HR",
            "condition": "Terminated employees continued to receive salary payments after their termination date.",
            "criteria": "Access and payroll policies require immediate cessation of payments upon termination.",
            "cause": "Disconnect between HR termination system and payroll processing system.",
            "effect": "Financial leakage and potential fraud risk.",
            "recommendation": "Automate HR to Payroll status sync. Owner: HR Director. Target: 30 days."
        },
        {
            "risk_id": "R06",
            "name": "GDPR/data protection compliance gaps",
            "category": "Compliance",
            "coso_component": "Information & Communication",
            "likelihood": 3, "impact": 3, "risk_score": 9, "risk_level": "High",
            "detection_method": "Document Review", "evidence_source": "Policy Review", "department": "IT",
            "condition": "Data protection policies do not meet current GDPR requirements.",
            "criteria": "Regulatory compliance requires adherence to data privacy laws.",
            "cause": "Outdated policy frameworks not reflecting new regulations.",
            "effect": "Regulatory fines and reputational damage.",
            "recommendation": "Conduct a comprehensive privacy impact assessment. Owner: DPO. Target: 90 days."
        },
        {
            "risk_id": "R07",
            "name": "Threshold avoidance pattern in procurement",
            "category": "Fraud",
            "coso_component": "Monitoring Activities",
            "likelihood": 4, "impact": 3, "risk_score": 12, "risk_level": "High",
            "detection_method": "Data Analysis", "evidence_source": "general_ledger.xlsx", "department": "Procurement",
            "condition": "Multiple transactions clustered just below approval thresholds (e.g., 9,900 MAD).",
            "criteria": "Procurement policy prohibits splitting POs to avoid higher-level approvals.",
            "cause": "Lack of aggregation controls across vendors within a short timeframe.",
            "effect": "Unauthorized spend bypassing managerial scrutiny.",
            "recommendation": "Implement cumulative spend alerts per vendor within 30 days. Owner: CPO. Target: 60 days."
        },
        {
            "risk_id": "R08",
            "name": "Rising product defect rate (1.2% -> 3.9%)",
            "category": "Operational",
            "coso_component": "Monitoring Activities",
            "likelihood": 5, "impact": 3, "risk_score": 15, "risk_level": "High",
            "detection_method": "Trend Analysis", "evidence_source": "kpi_data.xlsx", "department": "Production",
            "condition": "Defect rate steadily increased over 24 months, exceeding acceptable thresholds.",
            "criteria": "Quality management system mandates a defect rate below 2.0%.",
            "cause": "Deteriorating machinery calibration and lack of operator training.",
            "effect": "Increased scrap costs, customer returns, and brand damage.",
            "recommendation": "Initiate comprehensive maintenance and training program. Owner: Plant Manager. Target: 45 days."
        },
        {
            "risk_id": "R09",
            "name": "Single-source suppliers without audit (9 cases)",
            "category": "Operational",
            "coso_component": "Control Activities",
            "likelihood": 3, "impact": 4, "risk_score": 12, "risk_level": "High",
            "detection_method": "Data Analysis", "evidence_source": "supplier_master.csv", "department": "Procurement",
            "condition": "Multiple single-source suppliers have not been audited in over 3 years.",
            "criteria": "Procurement policy requires annual risk audits for sole-source vendors.",
            "cause": "Resource constraints in the vendor management team.",
            "effect": "Unidentified supply chain risks and potential compliance issues.",
            "recommendation": "Schedule immediate audits for all backlogged single-source vendors. Owner: CPO. Target: 90 days."
        },
        {
            "risk_id": "R10",
            "name": "IT security policy outdated (last reviewed 2019)",
            "category": "IT",
            "coso_component": "Control Environment",
            "likelihood": 5, "impact": 4, "risk_score": 20, "risk_level": "Critical",
            "detection_method": "Document Review", "evidence_source": "it_security_policy.pdf", "department": "IT",
            "condition": "The primary IT security policy has not been updated since 2019.",
            "criteria": "COSO and ISO 27001 require annual review of security policies.",
            "cause": "Lack of formalized policy review cadence and assigned ownership.",
            "effect": "Organization is exposed to modern cyber threats not covered by old policies.",
            "recommendation": "Completely revise IT policy and establish annual review cycle. Owner: CISO. Target: 30 days."
        },
        {
            "risk_id": "R11",
            "name": "IT staff turnover 28% in 2024",
            "category": "IT",
            "coso_component": "Control Environment",
            "likelihood": 4, "impact": 3, "risk_score": 12, "risk_level": "High",
            "detection_method": "Trend Analysis", "evidence_source": "kpi_data.xlsx", "department": "IT",
            "condition": "IT staff turnover reached 28%, significantly above industry average.",
            "criteria": "HR retention targets aim for less than 15% annual turnover.",
            "cause": "Below-market compensation and lack of career development paths.",
            "effect": "Loss of institutional knowledge and increased recruitment costs.",
            "recommendation": "Conduct market salary benchmarking and retention interviews. Owner: HR Director. Target: 60 days."
        },
        {
            "risk_id": "R12",
            "name": "IT downtime spike (63 hours, Sept 2024)",
            "category": "IT",
            "coso_component": "Control Activities",
            "likelihood": 3, "impact": 4, "risk_score": 12, "risk_level": "High",
            "detection_method": "Data Analysis", "evidence_source": "kpi_data.xlsx", "department": "IT",
            "condition": "A massive spike in IT downtime occurred in September 2024.",
            "criteria": "Service level agreements (SLAs) mandate 99.9% uptime.",
            "cause": "Unplanned system outages due to legacy hardware failure.",
            "effect": "Significant operational halt and financial loss during downtime.",
            "recommendation": "Implement high-availability redundancy for critical systems. Owner: CIO. Target: 120 days."
        },
        {
            "risk_id": "R13",
            "name": "Approval threshold controls absent for <10K",
            "category": "Compliance",
            "coso_component": "Control Activities",
            "likelihood": 3, "impact": 3, "risk_score": 9, "risk_level": "High",
            "detection_method": "Document Review", "evidence_source": "procurement_policy.pdf", "department": "Finance",
            "condition": "No formal approval matrix exists for purchases under 10,000 MAD.",
            "criteria": "Financial controls require approval tracking for all spend levels.",
            "cause": "Policy design flaw assuming low-value spend represents low risk.",
            "effect": "Accumulated unauthorized spend leading to budget overruns.",
            "recommendation": "Update matrix to require minimum manager approval for all POs. Owner: CFO. Target: 30 days."
        },
        {
            "risk_id": "R14",
            "name": "Missing supplier concentration policy",
            "category": "Compliance",
            "coso_component": "Control Environment",
            "likelihood": 4, "impact": 4, "risk_score": 16, "risk_level": "Critical",
            "detection_method": "Document Review", "evidence_source": "procurement_policy.pdf", "department": "Procurement",
            "condition": "The procurement policy completely omits rules on supplier concentration.",
            "criteria": "COSO Risk Assessment principles require defining risk tolerances for dependencies.",
            "cause": "Oversight during the last policy drafting phase.",
            "effect": "Inability to hold procurement accountable for excessive supplier reliance.",
            "recommendation": "Draft and board-approve a supplier diversification addendum. Owner: CPO. Target: 45 days."
        },
        {
            "risk_id": "R15",
            "name": "Contract clustering — 4 German suppliers expiring same quarter",
            "category": "Operational",
            "coso_component": "Risk Assessment",
            "likelihood": 3, "impact": 3, "risk_score": 9, "risk_level": "High",
            "detection_method": "Data Analysis", "evidence_source": "supplier_master.csv", "department": "Procurement",
            "condition": "Multiple critical international contracts expire in the same 60-day window.",
            "criteria": "Procurement strategy requires staggered contract expirations to manage workload.",
            "cause": "Reactive contract signing without a centralized portfolio strategy.",
            "effect": "Negotiation leverage loss and risk of simultaneous supply interruptions.",
            "recommendation": "Proactively renegotiate terms to stagger expiration dates. Owner: Procurement Mgr. Target: 90 days."
        },
        {
            "risk_id": "R16",
            "name": "Benford anomaly in Logistics transactions",
            "category": "Fraud",
            "coso_component": "Monitoring Activities",
            "likelihood": 4, "impact": 3, "risk_score": 12, "risk_level": "High",
            "detection_method": "Data Analysis", "evidence_source": "general_ledger.xlsx", "department": "Logistics",
            "condition": "The digit '6' appears as the first digit 22% of the time, violating Benford's Law.",
            "criteria": "Statistical distribution of natural datasets should follow Benford expected frequencies.",
            "cause": "Potential manual manipulation of invoices or artificial structuring of transport costs.",
            "effect": "High probability of fraudulent expense reporting.",
            "recommendation": "Conduct targeted substantive testing on all Logistics transactions starting with 6. Owner: Internal Audit. Target: Immediate."
        },
        {
            "risk_id": "R17",
            "name": "No cloud/remote access security controls",
            "category": "IT",
            "coso_component": "Control Environment",
            "likelihood": 4, "impact": 3, "risk_score": 12, "risk_level": "High",
            "detection_method": "Document Review", "evidence_source": "it_security_policy.pdf", "department": "IT",
            "condition": "IT policies contain no provisions for cloud infrastructure or remote VPN access.",
            "criteria": "Modern IT frameworks (NIST, ISO) mandate strict remote access controls.",
            "cause": "Failure to update policies to match the shift to remote work and cloud adoption.",
            "effect": "Unsecured remote access vectors leading to data breaches.",
            "recommendation": "Deploy MFA for all remote access and draft a Cloud Security Policy. Owner: CISO. Target: 30 days."
        },
        {
            "risk_id": "R18",
            "name": "Absence of data backup frequency policy",
            "category": "IT",
            "coso_component": "Control Activities",
            "likelihood": 3, "impact": 3, "risk_score": 9, "risk_level": "High",
            "detection_method": "Document Review", "evidence_source": "it_security_policy.pdf", "department": "IT",
            "condition": "No defined Recovery Point Objective (RPO) or backup frequency in policies.",
            "criteria": "Business Continuity Planning requires formal definition of backup schedules.",
            "cause": "Overreliance on informal, ad-hoc backup procedures by IT staff.",
            "effect": "Potential permanent data loss in the event of ransomware or hardware failure.",
            "recommendation": "Formalize daily immutable backups for critical data. Owner: IT Manager. Target: 30 days."
        },
        {
            "risk_id": "R19",
            "name": "Rising employee turnover — operational continuity",
            "category": "Operational",
            "coso_component": "Control Environment",
            "likelihood": 3, "impact": 3, "risk_score": 9, "risk_level": "High",
            "detection_method": "Trend Analysis", "evidence_source": "kpi_data.xlsx", "department": "HR",
            "condition": "Overall employee turnover shows an increasing trend across key departments.",
            "criteria": "Organizational stability requires managing turnover within industry benchmarks.",
            "cause": "Lack of employee engagement programs and competitive benefits.",
            "effect": "Decreased productivity and high onboarding costs.",
            "recommendation": "Implement a quarterly employee satisfaction survey and retention bonus pool. Owner: HR. Target: 90 days."
        },
        {
            "risk_id": "R20",
            "name": "On-time delivery declining trend",
            "category": "Operational",
            "coso_component": "Monitoring Activities",
            "likelihood": 3, "impact": 2, "risk_score": 6, "risk_level": "Moderate",
            "detection_method": "Trend Analysis", "evidence_source": "kpi_data.xlsx", "department": "Logistics",
            "condition": "On-time delivery metrics are steadily declining below the 90% SLA.",
            "criteria": "Customer contracts specify 90%+ on-time delivery metrics.",
            "cause": "Logistics bottlenecks and poor vendor coordination.",
            "effect": "SLA penalties and customer dissatisfaction.",
            "recommendation": "Review 3PL performance and optimize route planning. Owner: Logistics Manager. Target: 60 days."
        },
        {
            "risk_id": "R21",
            "name": "Customer complaint increase",
            "category": "Strategic",
            "coso_component": "Monitoring Activities",
            "likelihood": 2, "impact": 3, "risk_score": 6, "risk_level": "Moderate",
            "detection_method": "Trend Analysis", "evidence_source": "kpi_data.xlsx", "department": "Sales",
            "condition": "Volume of customer complaints has increased concurrently with defect rates.",
            "criteria": "ISO 9001 requires continuous improvement of customer satisfaction.",
            "cause": "Product quality issues trickling down to end users.",
            "effect": "Loss of future sales and contract non-renewals.",
            "recommendation": "Establish a rapid-response quality task force. Owner: Quality Director. Target: 30 days."
        },
        {
            "risk_id": "R22",
            "name": "EBITDA margin pressure",
            "category": "Financial",
            "coso_component": "Risk Assessment",
            "likelihood": 3, "impact": 3, "risk_score": 9, "risk_level": "High",
            "detection_method": "Financial Analysis", "evidence_source": "kpi_data.xlsx", "department": "Finance",
            "condition": "EBITDA margins are tightening despite revenue growth.",
            "criteria": "Financial planning targets mandate maintaining a 18% EBITDA margin.",
            "cause": "Uncontrolled operating expenses and rising material costs.",
            "effect": "Reduced profitability and shareholder value.",
            "recommendation": "Implement zero-based budgeting for next fiscal year. Owner: CFO. Target: 120 days."
        },
        {
            "risk_id": "R23",
            "name": "Absence of payroll reconciliation control",
            "category": "Compliance",
            "coso_component": "Control Activities",
            "likelihood": 4, "impact": 3, "risk_score": 12, "risk_level": "High",
            "detection_method": "Process Review", "evidence_source": "Internal Audit", "department": "HR",
            "condition": "No formal month-end reconciliation between HR master data and payroll disbursements.",
            "criteria": "Segregation of duties and financial accuracy standards require independent payroll review.",
            "cause": "Resource limitations and lack of defined control procedures.",
            "effect": "Undetected ghost employees and duplicate payments.",
            "recommendation": "Mandate finance review of HR variance reports before payroll execution. Owner: Controller. Target: Immediate."
        },
        {
            "risk_id": "R24",
            "name": "Vendor master data not periodically reviewed",
            "category": "Fraud",
            "coso_component": "Monitoring Activities",
            "likelihood": 3, "impact": 2, "risk_score": 6, "risk_level": "Moderate",
            "detection_method": "Process Review", "evidence_source": "supplier_master.csv", "department": "Procurement",
            "condition": "Vendor master file contains outdated, duplicate, and unverified vendor entries.",
            "criteria": "Master data management policies require annual cleanup and verification.",
            "cause": "No assigned data steward for the vendor master.",
            "effect": "Risk of payments to fraudulent or sanctioned entities.",
            "recommendation": "Execute a full vendor master cleanup project. Owner: Master Data Mgr. Target: 90 days."
        }
    ]
    
    # Apply control_status logic
    fraud_risks = ['R04', 'R05', 'R07', 'R16', 'R24']
    weak_risks = ['R01', 'R02', 'R09', 'R10', 'R13', 'R14', 'R17', 'R18']
    strong_risks = ['R20', 'R21']
    
    for r in risks_list:
        if r['risk_id'] in fraud_risks:
            r['control_status'] = 'None'
        elif r['risk_id'] in strong_risks:
            r['control_status'] = 'Strong'
        elif r['risk_id'] in weak_risks:
            r['control_status'] = 'Weak'
        else:
            r['control_status'] = 'Weak'
            
    return risks_list

def detect_ghost_employees(payroll_master_df, payroll_trans_df):
    """Finds payments made to terminated employees."""
    ghosts = []
    if payroll_master_df is None or payroll_trans_df is None: return ghosts
    
    term_emps = payroll_master_df[payroll_master_df['Status'] == 'Terminated']
    for _, emp in term_emps.iterrows():
        emp_id = emp['Employee_ID']
        trans = payroll_trans_df[payroll_trans_df['Employee_ID'] == emp_id]
        if not trans.empty:
            total_amt = trans['Amount_MAD'].sum()
            ghosts.append({
                "employee_id": emp_id,
                "name": emp['Full_Name'],
                "department": emp['Department'],
                "termination_implied": True,
                "months_paid_after": len(trans),
                "total_amount": total_amt
            })
    return ghosts

def enrich_risks(risks, datasets):
    """Dynamically augments risks with real data from datasets."""
    from .benford import detect_anomalies
    
    for r in risks:
        if r['risk_id'] == 'R01':
            sm = datasets.get('supplier_master')
            if sm is not None:
                top_pct = (sm.iloc[0]['Annual_Spend_MAD'] / sm['Annual_Spend_MAD'].sum()) * 100
                r['name'] = f"Supplier concentration ({sm.iloc[0]['Supplier_Name']} >{top_pct:.1f}% spend)"
                r['condition'] = f"Supplier {sm.iloc[0]['Supplier_Name']} accounts for {top_pct:.1f}% of total spend."
                if top_pct > 30: r['likelihood'] = 5
                elif top_pct > 20: r['likelihood'] = 4
                else: r['likelihood'] = 3
                r['risk_score'] = r['likelihood'] * r['impact']
                
        elif r['risk_id'] == 'R04':
            gl = datasets.get('general_ledger')
            if gl is not None:
                anoms = detect_anomalies(gl)
                dups = len(anoms.get('duplicates', []))
                r['condition'] = f"{dups} instances of duplicate payments detected."
                if dups == 0: r['likelihood'] = 1
                elif dups <= 2: r['likelihood'] = 3
                else: r['likelihood'] = 5
                r['risk_score'] = r['likelihood'] * r['impact']
                
        elif r['risk_id'] == 'R05':
            pm = datasets.get('payroll_master')
            pt = datasets.get('payroll_trans')
            if pm is not None and pt is not None:
                ghosts = detect_ghost_employees(pm, pt)
                r['condition'] = f"{len(ghosts)} terminated employees received payments after termination."
                
        elif r['risk_id'] == 'R08':
            kpi = datasets.get('kpi_data')
            if kpi is not None and len(kpi) > 1:
                start = kpi.iloc[0]['Defect_Rate_Pct']
                end = kpi.iloc[-1]['Defect_Rate_Pct']
                r['name'] = f"Rising product defect rate ({start}% -> {end}%)"
                r['condition'] = f"Defect rate steadily increased from {start}% to {end}% over 24 months."
                
        elif r['risk_id'] == 'R10':
            # This would use the policy_date from control_gaps, implemented in the caller
            pass
            
    # Update risk level based on score
    for r in risks:
        score = r['risk_score']
        if score <= 3: r['risk_level'] = "Low"
        elif score <= 8: r['risk_level'] = "Moderate"
        elif score <= 14: r['risk_level'] = "High"
        else: r['risk_level'] = "Critical"
        
    return risks
