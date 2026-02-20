"""CPA Practice Inspection rules — hardcoded checks against JSON document metadata."""

from engine.models import Finding


# ---------------------------------------------------------------------------
# Firm-Level Rules
# ---------------------------------------------------------------------------

def check_governance(docs: dict) -> list[Finding]:
    findings = []
    gov = docs.get("governance_policies", {})

    if not gov.get("tone_at_top_policy"):
        findings.append(Finding(
            rule_id="GOV-01", description="Tone-at-top policy documented",
            severity="critical", location="Firm-Level", component="Governance",
            issue="No tone-at-top quality policy found.",
            remediation="Document a firm-wide quality commitment policy signed by partners.",
            estimated_fix_time="2 hours",
        ))
    if not gov.get("quality_responsibility_assigned_to"):
        findings.append(Finding(
            rule_id="GOV-02", description="Quality responsibility assigned to individual",
            severity="critical", location="Firm-Level", component="Governance",
            issue="No individual assigned quality management responsibility.",
            remediation="Assign a partner as the quality management leader and document it.",
            estimated_fix_time="30 minutes",
        ))
    if not gov.get("strategic_quality_review_documented"):
        findings.append(Finding(
            rule_id="GOV-03", description="Strategic quality review documented",
            severity="warning", location="Firm-Level", component="Governance",
            issue="Strategic quality review not documented.",
            remediation="Document annual strategic review of quality objectives.",
            estimated_fix_time="1 hour",
        ))
    return findings


def check_ethics(docs: dict) -> list[Finding]:
    findings = []
    indep = docs.get("independence_declarations", {})
    declarations = indep.get("declarations", [])

    # ETH-01: All personnel have signed independence declaration
    unsigned = [d for d in declarations if not d.get("signed")]
    if unsigned:
        names = ", ".join(d["person"] for d in unsigned)
        findings.append(Finding(
            rule_id="ETH-01",
            description="All personnel have signed independence declaration",
            severity="critical", location="Firm-Level", component="Ethics & Independence",
            issue=f"Missing independence declaration for: {names}.",
            remediation="Obtain signed independence declarations from all personnel immediately.",
            estimated_fix_time="1 hour",
        ))

    # ETH-02: Late declarations
    late = [d for d in declarations if d.get("status") == "late"]
    if late:
        for d in late:
            findings.append(Finding(
                rule_id="ETH-02",
                description="Independence declarations dated before engagement work",
                severity="critical", location="Firm-Level", component="Ethics & Independence",
                issue=d.get("issue", f"{d['person']}'s declaration was signed late."),
                remediation="Ensure all declarations are signed at the start of the coverage period, before any engagement work begins.",
                estimated_fix_time="30 minutes",
            ))

    # ETH-03: Conflict register
    conflict = docs.get("conflict_register", {})
    if not conflict.get("exists"):
        findings.append(Finding(
            rule_id="ETH-03", description="Conflict of interest register maintained",
            severity="warning", location="Firm-Level", component="Ethics & Independence",
            issue="No conflict of interest register found.",
            remediation="Create and maintain a conflict of interest register.",
            estimated_fix_time="1 hour",
        ))
    return findings


def check_acceptance(docs: dict) -> list[Finding]:
    findings = []
    forms = docs.get("client_acceptance_forms", {}).get("forms", [])

    missing_forms = [f for f in forms if not f.get("form_exists")]
    if missing_forms:
        names = ", ".join(f["client"] for f in missing_forms)
        findings.append(Finding(
            rule_id="ACC-01",
            description="Client acceptance form exists for all inspected clients",
            severity="critical", location="Firm-Level", component="Client Acceptance",
            issue=f"Missing client acceptance forms for: {names}.",
            remediation="Complete client acceptance forms for all clients.",
            estimated_fix_time="2 hours",
        ))

    missing_risk = [f for f in forms if not f.get("risk_assessment")]
    if missing_risk:
        names = ", ".join(f["client"] for f in missing_risk)
        findings.append(Finding(
            rule_id="ACC-02", description="Risk assessment completed per client",
            severity="critical", location="Firm-Level", component="Client Acceptance",
            issue=f"Missing risk assessment for: {names}.",
            remediation="Complete risk assessment for all clients.",
            estimated_fix_time="1 hour per client",
        ))

    missing_integrity = [f for f in forms if not f.get("integrity_eval")]
    if missing_integrity:
        names = ", ".join(f["client"] for f in missing_integrity)
        issues = [f.get("issue", "") for f in missing_integrity if f.get("issue")]
        issue_text = f"Missing client integrity evaluation for: {names}."
        if issues:
            issue_text += " " + " ".join(issues)
        findings.append(Finding(
            rule_id="ACC-03", description="Client integrity evaluation documented",
            severity="warning", location="Firm-Level", component="Client Acceptance",
            issue=issue_text,
            remediation="Document integrity evaluation for all clients, especially cash-heavy businesses.",
            estimated_fix_time="1 hour",
        ))
    return findings


def check_resources(docs: dict) -> list[Finding]:
    findings = []
    cpd = docs.get("cpd_records", {})
    records = cpd.get("records", [])

    non_compliant = [r for r in records if r.get("status") in ("warning", "missing")]
    if non_compliant:
        details = []
        for r in non_compliant:
            detail = r["person"]
            if r.get("issue"):
                detail += f" — {r['issue']}"
            details.append(detail)
        findings.append(Finding(
            rule_id="RES-01", description="All staff CPD records current",
            severity="warning", location="Firm-Level", component="Resources",
            issue="CPD requirements not met for: " + "; ".join(details),
            remediation="Ensure all personnel complete required CPD hours. Establish CPD plan for new hires.",
            estimated_fix_time="Varies (4-20 hours per person)",
        ))

    soqm = docs.get("soqm_manual", {})
    if not soqm:
        findings.append(Finding(
            rule_id="RES-02", description="SoQM manual exists",
            severity="critical", location="Firm-Level", component="Resources",
            issue="No System of Quality Management manual found.",
            remediation="Obtain or create a CSQM 1 compliant SoQM manual.",
            estimated_fix_time="20+ hours",
        ))
    return findings


def check_communication(docs: dict) -> list[Finding]:
    findings = []
    pdl = docs.get("policy_distribution_log", {})
    distributions = pdl.get("distributions", [])

    if not distributions:
        findings.append(Finding(
            rule_id="COM-01", description="Policy distribution log maintained",
            severity="warning", location="Firm-Level", component="Communication",
            issue="No policy distribution log found.",
            remediation="Create a log tracking policy distribution and staff acknowledgment.",
            estimated_fix_time="1 hour",
        ))
    else:
        for dist in distributions:
            missing = dist.get("missing_acknowledgment", [])
            if missing:
                findings.append(Finding(
                    rule_id="COM-02",
                    description="All staff acknowledged receiving policies",
                    severity="warning", location="Firm-Level", component="Communication",
                    issue=dist.get("issue", f"Missing acknowledgment from: {', '.join(missing)}"),
                    remediation="Distribute policies to new hires and obtain written acknowledgment.",
                    estimated_fix_time="30 minutes",
                ))

    complaints = docs.get("complaints_procedure", {})
    if not complaints.get("procedure_exists"):
        findings.append(Finding(
            rule_id="COM-03", description="Complaints procedure documented",
            severity="warning", location="Firm-Level", component="Communication",
            issue="No complaints handling procedure documented.",
            remediation="Document a complaints procedure in the SoQM manual.",
            estimated_fix_time="1 hour",
        ))
    return findings


def check_monitoring(docs: dict) -> list[Finding]:
    findings = []
    mon = docs.get("monitoring_log", {})

    # MON-01
    afm = mon.get("annual_file_monitoring", {})
    if not afm.get("performed"):
        findings.append(Finding(
            rule_id="MON-01", description="Annual file monitoring performed",
            severity="critical", location="Firm-Level", component="Monitoring",
            issue="Annual file monitoring has not been performed.",
            remediation="Perform annual file monitoring review and document results.",
            estimated_fix_time="4 hours",
        ))

    # MON-02
    cem = mon.get("completed_engagement_monitoring", {})
    if not cem.get("performed"):
        findings.append(Finding(
            rule_id="MON-02", description="Completed engagement monitoring performed",
            severity="critical", location="Firm-Level", component="Monitoring",
            issue="Completed engagement monitoring has not been performed.",
            remediation="Perform completed engagement monitoring review.",
            estimated_fix_time="4 hours",
        ))

    # MON-03
    if cem.get("performed") and not cem.get("reviewer_independent"):
        findings.append(Finding(
            rule_id="MON-03",
            description="Monitoring reviewer independent of files reviewed",
            severity="critical", location="Firm-Level", component="Monitoring",
            issue=cem.get("issue", "Monitoring reviewer was not independent of the files reviewed."),
            remediation="Engage an external reviewer or assign someone who did not work on any of the reviewed files.",
            estimated_fix_time="2 hours (plus re-review cost)",
        ))

    # MON-04
    soqm_eval = docs.get("soqm_evaluation", {})
    if soqm_eval.get("overdue"):
        findings.append(Finding(
            rule_id="MON-04", description="Annual SoQM evaluation performed",
            severity="critical", location="Firm-Level", component="Monitoring",
            issue=soqm_eval.get("issue", "Annual SoQM evaluation is overdue."),
            remediation="Complete the annual SoQM evaluation immediately. Consider all monitoring results, external inspections, and complaints.",
            estimated_fix_time="3 hours",
        ))

    # MON-05 & MON-06
    remediation = docs.get("remediation_log", {})
    entries = remediation.get("entries", [])
    open_without_action = [e for e in entries if e.get("status") == "open" and not e.get("corrective_action")]
    if open_without_action:
        for e in open_without_action:
            findings.append(Finding(
                rule_id="MON-05",
                description="All remediation entries have corrective actions",
                severity="critical", location="Firm-Level", component="Monitoring",
                issue=e.get("issue", f"Open deficiency without corrective action: {e.get('deficiency', '')}"),
                remediation="Document corrective action for each identified deficiency. The inspector will flag open items with no response.",
                estimated_fix_time="1 hour",
            ))

    missing_root_cause = [e for e in entries if e.get("status") == "open" and not e.get("root_cause")]
    if missing_root_cause:
        findings.append(Finding(
            rule_id="MON-06",
            description="Root cause analysis documented for all deficiencies",
            severity="warning", location="Firm-Level", component="Monitoring",
            issue="Open deficiencies without root cause analysis documented.",
            remediation="Perform and document root cause analysis for all open deficiencies.",
            estimated_fix_time="1 hour",
        ))
    return findings


# ---------------------------------------------------------------------------
# Engagement File Rules
# ---------------------------------------------------------------------------

def check_engagement_file(file_data: dict) -> list[Finding]:
    findings = []
    client = file_data.get("client_name", "Unknown")
    file_id = file_data.get("file_id", "")
    location = f"{client} ({file_id})"
    checks = file_data.get("checks", {})
    eng_type = file_data.get("engagement_type", "compilation")

    # ENG-01: Engagement letter exists and signed
    el = checks.get("engagement_letter", {})
    if not (el.get("exists") and el.get("signed_by_client") and el.get("signed_by_firm")):
        findings.append(Finding(
            rule_id="ENG-01",
            description="Engagement letter exists and signed by both parties",
            severity="critical", location=location, component="Engagement Letter",
            issue="Engagement letter is missing or not signed by both parties.",
            remediation="Obtain a properly executed engagement letter signed by both client and firm.",
            estimated_fix_time="1 hour",
        ))

    # ENG-02: Letter dated before work started
    if el.get("date_signed") and el.get("work_start_date"):
        if el["date_signed"] > el["work_start_date"]:
            findings.append(Finding(
                rule_id="ENG-02",
                description="Engagement letter dated before or at start of work",
                severity="critical", location=location, component="Engagement Letter",
                issue=f"Engagement letter dated {el['date_signed']} but work started {el['work_start_date']} — letter signed after work began.",
                remediation="Ensure engagement letters are always signed BEFORE beginning any work. This cannot be retroactively fixed for this file — document the gap and implement controls to prevent recurrence.",
                estimated_fix_time="30 minutes (documentation)",
            ))

    # ENG-03: References applicable standard
    if eng_type == "compilation" and not el.get("references_csrs_4200"):
        findings.append(Finding(
            rule_id="ENG-03",
            description="Engagement letter references applicable standard",
            severity="critical", location=location, component="Engagement Letter",
            issue="Engagement letter does not reference CSRS 4200.",
            remediation="Update engagement letter template to reference CSRS 4200. Issue an updated letter for next engagement.",
            estimated_fix_time="30 minutes",
        ))

    # ENG-04: Independence assessment
    indep = checks.get("independence", {})
    if not indep.get("assessment_documented"):
        findings.append(Finding(
            rule_id="ENG-04",
            description="Independence assessment documented",
            severity="critical", location=location, component="Independence",
            issue="No independence assessment documented for this engagement.",
            remediation="Document independence assessment including threat evaluation.",
            estimated_fix_time="30 minutes",
        ))
    if indep.get("status") == "warning" and indep.get("issue"):
        findings.append(Finding(
            rule_id="ETH-02",
            description="Independence declaration timing",
            severity="warning", location=location, component="Independence",
            issue=indep["issue"],
            remediation="Ensure independence declarations are signed before engagement work begins.",
            estimated_fix_time="30 minutes",
        ))

    # ENG-05: Basis of accounting note
    fs = checks.get("financial_statements", {})
    if not fs.get("basis_of_accounting_note"):
        findings.append(Finding(
            rule_id="ENG-05",
            description="Financial statements include basis of accounting note",
            severity="critical", location=location, component="Financial Statements",
            issue=fs.get("issue", "Missing basis of accounting note in financial statements."),
            remediation="Add a note describing the applicable financial reporting framework (e.g., ASPE). This is a CSRS 4200 requirement.",
            estimated_fix_time="1 hour",
        ))

    # Comparatives check (warning)
    if fs.get("status") == "warning" and fs.get("issue"):
        findings.append(Finding(
            rule_id="ENG-05b",
            description="Financial statement comparatives agree",
            severity="warning", location=location, component="Financial Statements",
            issue=fs["issue"],
            remediation="Investigate and document the comparative figure discrepancy. Correct the financial statements if needed.",
            estimated_fix_time="1 hour",
        ))

    # ENG-06: Report uses current standard wording
    report = checks.get("report", {})
    if eng_type == "compilation" and report.get("not_old_section_9200") is False:
        findings.append(Finding(
            rule_id="ENG-06",
            description="Report uses current CSRS 4200 wording (not old Section 9200)",
            severity="critical", location=location, component="Report",
            issue=report.get("issue", "Report still uses old Section 9200 'Notice to Reader' wording."),
            remediation="Reissue the report using the current CSRS 4200 compilation report format. Update all report templates.",
            estimated_fix_time="1 hour",
        ))

    # ENG-07: File assembly
    assembly = checks.get("file_assembly", {})
    if assembly.get("status") == "ok":
        pass
    elif assembly.get("status") == "pending":
        findings.append(Finding(
            rule_id="ENG-07",
            description="File assembled within 60 days of report date",
            severity="info", location=location, component="File Assembly",
            issue=assembly.get("issue", "File assembly not yet completed."),
            remediation="Complete file assembly before the 60-day deadline.",
            estimated_fix_time="1 hour",
        ))
    elif assembly.get("assembled_within_60_days") is False and assembly.get("days_elapsed"):
        findings.append(Finding(
            rule_id="ENG-07",
            description="File assembled within 60 days of report date",
            severity="warning", location=location, component="File Assembly",
            issue=f"File assembled {assembly['days_elapsed']} days after report date (exceeds 60-day limit).",
            remediation="Implement a tracking system to ensure files are assembled within 60 days.",
            estimated_fix_time="30 minutes",
        ))

    # Compilation-specific: misleading consideration
    comp = checks.get("compilation_procedures", {})
    if comp.get("status") == "warning" and comp.get("issue"):
        findings.append(Finding(
            rule_id="ENG-05c",
            description="Consideration of misleading statements",
            severity="warning", location=location, component="Compilation Procedures",
            issue=comp["issue"],
            remediation="Document consideration of whether the compiled financial statements might be misleading.",
            estimated_fix_time="30 minutes",
        ))

    # Review-specific rules
    if eng_type == "review":
        ap = checks.get("analytical_procedures", {})
        if not ap.get("performed"):
            findings.append(Finding(
                rule_id="REV-01",
                description="Analytical procedures performed and documented",
                severity="critical", location=location, component="Analytical Procedures",
                issue="Analytical procedures not performed for review engagement.",
                remediation="Perform and document analytical procedures as required by CSRE 2400.",
                estimated_fix_time="3 hours",
            ))
        mrl = checks.get("management_representation_letter", {})
        if not mrl.get("obtained"):
            findings.append(Finding(
                rule_id="REV-02",
                description="Management representation letter obtained",
                severity="critical", location=location, component="Management Representation",
                issue="Management representation letter not obtained.",
                remediation="Obtain a signed management representation letter.",
                estimated_fix_time="1 hour",
            ))

    return findings
