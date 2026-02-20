"""Core scanning logic — loads CPA documents and runs inspection rules."""

import json
from pathlib import Path

from engine.models import ScanResult, ComponentResult, FileResult, Finding
from engine.rules import (
    check_governance,
    check_ethics,
    check_acceptance,
    check_resources,
    check_communication,
    check_monitoring,
    check_engagement_file,
)

DATA_DIR = Path(__file__).parent.parent / "data"


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_firm_docs() -> dict:
    """Load all firm-level documents into a dict keyed by document_type."""
    firm_dir = DATA_DIR / "documents" / "firm_level"
    docs = {}
    for p in firm_dir.glob("*.json"):
        data = load_json(p)
        doc_type = data.get("document_type", p.stem)
        docs[doc_type] = data
    return docs


def load_engagement_files() -> list[dict]:
    """Load all engagement file JSONs."""
    eng_dir = DATA_DIR / "documents" / "engagement_files"
    files = []
    for p in sorted(eng_dir.glob("*.json")):
        files.append(load_json(p))
    return files


def _count_bool_checks(data: dict, depth: int = 0) -> tuple[int, int]:
    """Recursively count boolean fields as assertions (total, passed)."""
    total = 0
    passed = 0
    if depth > 4:
        return total, passed
    for k, v in data.items():
        if k in ("status", "issue", "issues", "notes", "document_type"):
            continue
        if isinstance(v, bool):
            total += 1
            if v:
                passed += 1
        elif isinstance(v, dict):
            t, p = _count_bool_checks(v, depth + 1)
            total += t
            passed += p
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    t, p = _count_bool_checks(item, depth + 1)
                    total += t
                    passed += p
    return total, passed


def _count_assertions(firm_docs: dict, engagement_files: list[dict]) -> tuple[int, int]:
    """Count all granular boolean assertions across firm docs and engagement files."""
    total = 0
    passed = 0
    for doc in firm_docs.values():
        t, p = _count_bool_checks(doc)
        total += t
        passed += p
    for ef in engagement_files:
        t, p = _count_bool_checks(ef.get("checks", {}))
        total += t
        passed += p
    return total, passed


def _parse_total_hours(findings: list[Finding]) -> float:
    """Parse estimated_fix_time strings and sum total hours."""
    import re
    total = 0.0
    for f in findings:
        text = f.estimated_fix_time.lower()
        # Match patterns like "2 hours", "30 minutes", "1 hour"
        hour_match = re.search(r"(\d+)\s*hour", text)
        min_match = re.search(r"(\d+)\s*min", text)
        if hour_match:
            total += float(hour_match.group(1))
        if min_match:
            total += float(min_match.group(1)) / 60
    return round(total, 1)


def run_scan() -> ScanResult:
    """Execute the full CPA practice inspection readiness scan."""
    firm_profile = load_json(DATA_DIR / "firm_profile.json")
    firm_docs = load_firm_docs()
    engagement_files = load_engagement_files()

    # --- Firm-level checks ---
    components = []

    gov_findings = check_governance(firm_docs)
    components.append(ComponentResult(
        name="Governance & Leadership",
        description="CSQM 1 Component 1 — Firm governance, leadership, and culture supporting quality",
        findings=gov_findings,
    ))

    eth_findings = check_ethics(firm_docs)
    components.append(ComponentResult(
        name="Ethics & Independence",
        description="CSQM 1 Component 2 — Ethical requirements including independence",
        findings=eth_findings,
    ))

    acc_findings = check_acceptance(firm_docs)
    components.append(ComponentResult(
        name="Client Acceptance & Continuance",
        description="CSQM 1 Component 3 — Accepting and continuing client relationships",
        findings=acc_findings,
    ))

    res_findings = check_resources(firm_docs)
    components.append(ComponentResult(
        name="Resources",
        description="CSQM 1 Component 4 — Human resources, intellectual resources, and CPD",
        findings=res_findings,
    ))

    com_findings = check_communication(firm_docs)
    components.append(ComponentResult(
        name="Information & Communication",
        description="CSQM 1 Component 5 — Information systems, policy communication, and complaints",
        findings=com_findings,
    ))

    mon_findings = check_monitoring(firm_docs)
    components.append(ComponentResult(
        name="Monitoring & Remediation",
        description="CSQM 1 Component 7 — Monitoring activities and remediation of deficiencies",
        findings=mon_findings,
    ))

    # --- Engagement file checks ---
    file_results = []
    for ef in engagement_files:
        ef_findings = check_engagement_file(ef)
        file_results.append(FileResult(
            file_id=ef.get("file_id", ""),
            client_name=ef.get("client_name", ""),
            engagement_type=ef.get("engagement_type", ""),
            standard=ef.get("standard", ""),
            engagement_partner=ef.get("engagement_partner", ""),
            prepared_by=ef.get("prepared_by", ""),
            assertions_passed=ef.get("assertions_passed", 0),
            assertions_total=ef.get("assertions_total", 0),
            overall_status=ef.get("overall_status", ""),
            findings=ef_findings,
        ))

    # --- Aggregate ---
    all_findings: list[Finding] = []
    for c in components:
        all_findings.extend(c.findings)
    for fr in file_results:
        all_findings.extend(fr.findings)

    critical_count = sum(1 for f in all_findings if f.severity == "critical")
    warning_count = sum(1 for f in all_findings if f.severity == "warning")
    info_count = sum(1 for f in all_findings if f.severity == "info")

    # Granular assertion counting — each boolean check field is one assertion
    total_assertions, passed_assertions = _count_assertions(firm_docs, engagement_files)

    # Score per spec: base_score - penalty
    base_score = passed_assertions / total_assertions if total_assertions > 0 else 0
    penalty = critical_count * 0.012 + warning_count * 0.002
    readiness_score = max(0, base_score - penalty)
    readiness_score = round(readiness_score * 100, 1)

    # Predicted outcome
    if critical_count > 0:
        predicted_outcome = "Does Not Meet Requirements"
    elif warning_count > 3:
        predicted_outcome = "Meets Requirements (with notes)"
    else:
        predicted_outcome = "Meets Requirements"

    # Post-fix projection: what score/outcome if all critical items are fixed
    post_fix_penalty = warning_count * 0.002  # only warnings remain
    post_fix_score_raw = base_score - post_fix_penalty
    post_fix_score = round(max(0, post_fix_score_raw) * 100, 1)

    if warning_count > 3:
        post_fix_outcome = "Meets Requirements (with notes)"
    else:
        post_fix_outcome = "Meets Requirements"

    # Estimated total fix hours from findings
    estimated_fix_hours = _parse_total_hours(all_findings)

    return ScanResult(
        firm_name=firm_profile["firm_name"],
        license_number=firm_profile["license_number"],
        jurisdiction=firm_profile["jurisdiction"],
        next_inspection_due=firm_profile["next_inspection_due"],
        readiness_score=readiness_score,
        predicted_outcome=predicted_outcome,
        total_assertions=total_assertions,
        passed_assertions=passed_assertions,
        critical_count=critical_count,
        warning_count=warning_count,
        info_count=info_count,
        files_scanned=len(file_results),
        post_fix_score=post_fix_score,
        post_fix_outcome=post_fix_outcome,
        estimated_fix_hours=estimated_fix_hours,
        components=components,
        file_results=file_results,
        all_findings=all_findings,
    )
