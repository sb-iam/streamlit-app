"""Risk scoring engine for SR&ED claim readiness."""


def calculate_eligibility_score(projects, expenditures):
    """Score project eligibility weighted by expenditure."""
    project_scores = {}
    project_spend = {}

    for p in projects:
        pid = p["project_id"]
        fqt = p["five_question_test"]
        passed = sum(1 for k in ["q1_uncertainty", "q2_hypothesis", "q3_systematic", "q4_advancement", "q5_record"] if fqt.get(k))
        # Score: 100 if 5/5, 80 if 4/5, 60 if 3/5, etc. 0 if 0/5
        project_scores[pid] = (passed / 5) * 100

        # Calculate spend for this project
        spend = 0
        for s in expenditures["salaries"]["breakdown"]:
            spend += s["project_allocation"].get(pid, 0)
        for m in expenditures["materials"]["items"]:
            if m["project"] == pid:
                spend += m["amount"]
        for c in expenditures["contracts"]["items"]:
            if c["project"] == pid:
                spend += c["amount"]
        project_spend[pid] = spend

    total_spend = sum(project_spend.values())
    if total_spend == 0:
        return 0

    weighted = sum(project_scores[pid] * (project_spend[pid] / total_spend) for pid in project_scores)
    return round(weighted)


def calculate_expenditure_score(expenditures):
    """Score expenditure accuracy. Start at 100, deduct per error."""
    score = 100
    for error in expenditures.get("deliberate_errors", []):
        if error["severity"] == "HIGH":
            score -= 15
        elif error["severity"] == "MEDIUM":
            score -= 10
        elif error["severity"] == "LOW":
            score -= 5
    return max(0, score)


def calculate_documentation_score(documentation):
    """Score documentation completeness across eligible projects."""
    checklist = documentation["t661_evidence_checklist"]
    scores = {"P001": 0, "P002": 0, "P003": 0}
    counts = {"P001": 0, "P002": 0, "P003": 0}

    for line_key, project_vals in checklist.items():
        for pid, val in project_vals.items():
            counts[pid] += 1
            if val is True:
                scores[pid] += 1
            elif val == "partial" or val == "wrong_type":
                scores[pid] += 0.5

    project_pcts = {}
    for pid in scores:
        if counts[pid] > 0:
            project_pcts[pid] = (scores[pid] / counts[pid]) * 100

    # Weight eligible projects more heavily
    if project_pcts:
        # P001 and P002 are eligible; P003 is not but still counts for scoring
        weights = {"P001": 0.45, "P002": 0.45, "P003": 0.10}
        weighted = sum(project_pcts.get(pid, 0) * w for pid, w in weights.items())
        return round(weighted)
    return 0


def calculate_form_score(form_data):
    """Score T661 form completeness."""
    parts = form_data["parts_status"]
    complete_count = 0
    total = len(parts)

    for part_key, part_val in parts.items():
        status = part_val["status"]
        if status == "COMPLETE":
            complete_count += 1
        elif status == "WARNING":
            complete_count += 0.5

    return round((complete_count / total) * 100) if total > 0 else 0


def calculate_overall_score(projects, expenditures, documentation, form_data):
    """
    Returns 0-100 composite score.

    Weights:
    - Project Eligibility: 35%
    - Expenditure Accuracy: 25%
    - Documentation Completeness: 25%
    - Form Completeness: 15%
    """
    W_ELIG = 0.35
    W_EXP = 0.25
    W_DOC = 0.25
    W_FORM = 0.15

    elig = calculate_eligibility_score(projects, expenditures)
    exp = calculate_expenditure_score(expenditures)
    doc = calculate_documentation_score(documentation)
    form = calculate_form_score(form_data)

    composite = (elig * W_ELIG + exp * W_EXP + doc * W_DOC + form * W_FORM)
    return round(composite), {
        "eligibility": elig,
        "expenditure": exp,
        "documentation": doc,
        "form": form,
    }


def get_all_issues(projects, expenditures, documentation, form_data, client_profile):
    """Aggregate all issues across all data sources."""
    issues = []

    # Project eligibility issues
    for p in projects:
        pid = p["project_id"]
        fqt = p["five_question_test"]
        passed = sum(1 for k in ["q1_uncertainty", "q2_hypothesis", "q3_systematic", "q4_advancement", "q5_record"] if fqt.get(k))
        if passed == 0:
            issues.append({
                "severity": "HIGH",
                "category": "Eligibility",
                "issue": f"Project {pid} ({p['title'][:50]}...) fails all 5 eligibility questions",
                "project": pid,
                "remediation": f"Remove {pid} entirely from SR&ED claim. This is routine development, not SR&ED.",
            })
        elif passed < 5:
            failed_qs = [q for q in ["q1_uncertainty", "q2_hypothesis", "q3_systematic", "q4_advancement", "q5_record"] if not fqt.get(q)]
            issues.append({
                "severity": "MEDIUM",
                "category": "Eligibility",
                "issue": f"Project {pid}: {5-passed} question(s) failed in eligibility test",
                "project": pid,
                "remediation": f"Address documentation gaps for failed questions: {', '.join(failed_qs)}",
            })

    # Expenditure errors
    for error in expenditures.get("deliberate_errors", []):
        issues.append({
            "severity": error["severity"],
            "category": "Expenditure",
            "issue": error["description"],
            "project": error.get("category", "General"),
            "remediation": error["remediation"],
        })

    # Documentation gaps
    for item in documentation.get("evidence_items", []):
        if item.get("gap_flag"):
            issues.append({
                "severity": "HIGH",
                "category": "Documentation",
                "issue": f"Documentation gap: {item.get('gap_start')} to {item.get('gap_end')} ({item.get('gap_reason')})",
                "project": item["project"],
                "remediation": "Prepare memo reconstructing experimental approach during gap period using git commits and code reviews.",
            })

    # Preparer risk
    preparer = client_profile.get("preparer", {})
    if preparer.get("billing_arrangement") == 1:
        issues.append({
            "severity": "MEDIUM",
            "category": "Preparer",
            "issue": f"Contingency fee preparer ({preparer['name']}) — elevated CRA audit risk",
            "project": "All",
            "remediation": "Contingency fees are legal but flagged by CRA. Ensure all documentation is meticulous.",
        })

    # Sort by severity
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    issues.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return issues


def calculate_corrected_expenditures(expenditures):
    """Calculate expenditures after removing P003 and fixing errors."""
    # Corrected salaries: remove P003 allocations
    corrected_salaries = 0
    for s in expenditures["salaries"]["breakdown"]:
        for pid, amount in s["project_allocation"].items():
            if pid != "P003":
                corrected_salaries += amount

    # Corrected materials: remove ineligible items
    corrected_materials = 0
    for m in expenditures["materials"]["items"]:
        if m["eligible"] and m["project"] != "P003":
            corrected_materials += m["amount"]

    # Corrected contracts: remove ineligible
    corrected_contracts = 0
    for c in expenditures["contracts"]["items"]:
        if c["eligible"] and c["project"] != "P003":
            corrected_contracts += c["amount"]

    # Corrected PPA: 55% of eligible salary base (excluding specified employees on P003)
    corrected_ppa = round(corrected_salaries * 0.55)

    return {
        "salaries": corrected_salaries,
        "materials": corrected_materials,
        "contracts": corrected_contracts,
        "ppa": corrected_ppa,
        "total": corrected_salaries + corrected_materials + corrected_contracts + corrected_ppa,
    }


def calculate_uncorrected_expenditures(expenditures):
    """Calculate expenditures as-filed (with errors)."""
    salaries = expenditures["salaries"]["total_sred_salaries"]
    materials = expenditures["materials"]["line_360_total"]
    contracts = expenditures["contracts"]["line_370_total"]
    ppa = expenditures["overhead"]["proxy_amount"]

    return {
        "salaries": salaries,
        "materials": materials,
        "contracts": contracts,
        "ppa": ppa,
        "total": salaries + materials + contracts + ppa,
    }
