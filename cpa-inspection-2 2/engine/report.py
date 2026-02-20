"""Generate inspection readiness report text from scan results."""

from datetime import date
from engine.models import ScanResult


def generate_report_text(result: ScanResult) -> str:
    """Generate a formatted text report from scan results."""
    lines = []
    lines.append("=" * 70)
    lines.append("CPA PRACTICE INSPECTION READINESS REPORT")
    lines.append("Powered by IAM-Audit - Interpretive AI for Accounting & Assurance")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Firm:            {result.firm_name}")
    lines.append(f"License:         {result.license_number}")
    lines.append(f"Jurisdiction:    {result.jurisdiction}")
    lines.append(f"Report Date:     {date.today().isoformat()}")
    lines.append(f"Inspection Due:  {result.next_inspection_due}")
    lines.append("")
    lines.append("-" * 70)
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 70)
    lines.append("")
    lines.append(f"Readiness Score:     {result.readiness_score}%")
    lines.append(f"Predicted Outcome:   {result.predicted_outcome}")
    lines.append(f"Assertions Checked:  {result.total_assertions}")
    lines.append(f"Assertions Passed:   {result.passed_assertions}")
    lines.append(f"Critical Gaps:       {result.critical_count}")
    lines.append(f"Warnings:            {result.warning_count}")
    lines.append(f"Info Items:          {result.info_count}")
    lines.append(f"Files Scanned:       {result.files_scanned}")
    lines.append("")

    # Component summary
    lines.append("-" * 70)
    lines.append("FIRM-LEVEL COMPONENT STATUS")
    lines.append("-" * 70)
    lines.append("")
    for comp in result.components:
        icon = {"pass": "PASS", "warning": "WARN", "critical": "FAIL"}.get(comp.status, "????")
        lines.append(f"[{icon}] {comp.name}")
        if comp.findings:
            for f in comp.findings:
                sev = f.severity.upper()
                lines.append(f"       [{sev}] {f.rule_id}: {f.issue}")
        else:
            lines.append("       No issues found.")
        lines.append("")

    # File results
    lines.append("-" * 70)
    lines.append("ENGAGEMENT FILE RESULTS")
    lines.append("-" * 70)
    lines.append("")
    for fr in result.file_results:
        status_label = {
            "pass": "PASS", "pass_with_warning": "WARN", "fail": "FAIL"
        }.get(fr.overall_status, fr.overall_status.upper())
        lines.append(f"[{status_label}] {fr.client_name} ({fr.file_id})")
        lines.append(f"       Type: {fr.engagement_type.title()} | Standard: {fr.standard}")
        lines.append(f"       Partner: {fr.engagement_partner} | Prepared by: {fr.prepared_by}")
        lines.append(f"       Assertions: {fr.assertions_passed}/{fr.assertions_total} passed")
        if fr.findings:
            for f in fr.findings:
                sev = f.severity.upper()
                lines.append(f"       [{sev}] {f.rule_id}: {f.issue}")
        lines.append("")

    # Prioritized remediation
    lines.append("-" * 70)
    lines.append("PRIORITIZED REMEDIATION PLAN")
    lines.append("-" * 70)
    lines.append("")

    critical_findings = [f for f in result.all_findings if f.severity == "critical"]
    warning_findings = [f for f in result.all_findings if f.severity == "warning"]
    info_findings = [f for f in result.all_findings if f.severity == "info"]

    for i, f in enumerate(critical_findings, 1):
        lines.append(f"{i}. [CRITICAL] {f.rule_id} — {f.location}")
        lines.append(f"   Issue: {f.issue}")
        lines.append(f"   Fix: {f.remediation}")
        lines.append(f"   Est. Time: {f.estimated_fix_time}")
        lines.append("")

    for i, f in enumerate(warning_findings, len(critical_findings) + 1):
        lines.append(f"{i}. [WARNING] {f.rule_id} — {f.location}")
        lines.append(f"   Issue: {f.issue}")
        lines.append(f"   Fix: {f.remediation}")
        lines.append(f"   Est. Time: {f.estimated_fix_time}")
        lines.append("")

    for i, f in enumerate(info_findings, len(critical_findings) + len(warning_findings) + 1):
        lines.append(f"{i}. [INFO] {f.rule_id} — {f.location}")
        lines.append(f"   Issue: {f.issue}")
        lines.append(f"   Fix: {f.remediation}")
        lines.append(f"   Est. Time: {f.estimated_fix_time}")
        lines.append("")

    lines.append("=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)

    return "\n".join(lines)


def generate_csv_rows(result: ScanResult) -> list[dict]:
    """Generate CSV-exportable rows from findings."""
    rows = []
    for f in result.all_findings:
        rows.append({
            "Priority": f.severity.upper(),
            "Rule ID": f.rule_id,
            "Description": f.description,
            "Location": f.location,
            "Component": f.component,
            "Issue": f.issue,
            "Remediation": f.remediation,
            "Est. Fix Time": f.estimated_fix_time,
        })
    return rows
