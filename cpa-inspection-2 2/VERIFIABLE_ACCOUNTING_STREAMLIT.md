# CPA Practice Inspection Readiness Scanner — Streamlit Demo App Spec

## CRITICAL CONTEXT — READ FIRST

**THIS APPLICATION HAS NOTHING TO DO WITH CLOUD SECURITY, RBAC, AWS IAM, AZURE AD, OR IDENTITY/ACCESS MANAGEMENT.**

The product name "Verifiable Accounting" reflects an evidence-first readiness workflow for **Canadian CPA (Chartered Professional Accountant) firms** preparing for **mandatory practice inspections** conducted by provincial CPA bodies (like CPA Ontario, CPA BC, etc.).

**THE DOMAIN IS ACCOUNTING. THE USER IS AN ACCOUNTANT. THE PROBLEM IS PASSING A CPA PRACTICE INSPECTION.**

Do NOT generate anything related to: cloud infrastructure, IAM roles/policies, RBAC, permissions, AWS, Azure, GCP, security audits, access controls, identity management, or any IT/cloud concepts whatsoever.

## Overview

Build a Streamlit application that demonstrates a **CPA Practice Inspection Readiness Scanner**. The app simulates scanning a small Canadian CPA accounting firm's documents against CSQM 1 (Canadian Standard on Quality Management 1) inspection requirements and produces a readiness report showing gaps, warnings, and a pass/fail score.

Think of it as: a tax accountant's firm is about to be inspected by their licensing body (like CPA Ontario). The inspector will check their quality management system, engagement files (client work), independence declarations, monitoring logs, etc. This tool scans all of that BEFORE the inspector arrives and tells the accountant what to fix.

This is a DEMO with fake but realistic accounting documents. No real compiler backend. The "engine" is Python logic that checks document metadata against CPA inspection rules. The goal is to show CPA firm partners (accountants) what the product does so they understand the value proposition.

## Tech Stack

- Python 3.11+
- Streamlit (latest)
- No database needed — all data is in-memory or JSON/YAML files
- Use streamlit native components (st.metric, st.progress_bar, st.expander, st.tabs, st.columns, st.dataframe, st.status)
- Dark theme preferred (set in .streamlit/config.toml)
- No external APIs needed — everything runs locally

**REMINDER: This app is for ACCOUNTANTS preparing for a PRACTICE INSPECTION by their CPA licensing body. Not cloud. Not security. Not IT. Accounting.**

## Project Structure

```
verifiable-accounting-demo/
├── app.py                          # Main Streamlit app — CPA INSPECTION scanner
├── .streamlit/
│   └── config.toml                 # Dark theme config
├── engine/
│   ├── __init__.py
│   ├── scanner.py                  # Core scanning logic (checks CPA documents)
│   ├── rules.py                    # CPA Inspection rules definitions
│   ├── models.py                   # Data models (dataclasses)
│   └── report.py                   # Inspection readiness report generation
├── data/
│   ├── firm_profile.json           # CPA firm metadata (partners, staff, clients)
│   ├── documents/                  # Fake CPA ACCOUNTING document metadata
│   │   ├── firm_level/
│   │   │   ├── soqm_manual.json            # System of Quality Management manual
│   │   │   ├── independence_declarations.json  # CPA independence declarations
│   │   │   ├── cpd_records.json            # Continuing Professional Development
│   │   │   ├── monitoring_log.json         # Internal quality monitoring
│   │   │   ├── soqm_evaluation.json        # Annual quality evaluation
│   │   │   ├── remediation_log.json        # Deficiency fix tracking
│   │   │   ├── conflict_register.json      # Conflict of interest register
│   │   │   ├── governance_policies.json    # Firm quality policies
│   │   │   ├── client_acceptance_forms.json # New client screening forms
│   │   │   ├── complaints_procedure.json   # Complaints handling procedure
│   │   │   └── policy_distribution_log.json # Staff policy acknowledgments
│   │   └── engagement_files/               # CLIENT WORK FILES (what inspector reviews)
│   │       ├── file_1_abc_manufacturing.json   # Clean compilation file
│   │       ├── file_2_xyz_holdings.json        # Minor warning
│   │       ├── file_3_123_restaurant.json      # BAD FILE — multiple deficiencies
│   │       └── file_4_def_services_review.json # Clean review engagement
│   └── policies/
│       └── csqm1_full.yaml         # CPA inspection policy definition
├── assets/
│   └── logo.png                    # Optional placeholder
└── requirements.txt
```

## .streamlit/config.toml

```toml
[theme]
primaryColor = "#f97316"
backgroundColor = "#0a0a0f"
secondaryBackgroundColor = "#111520"
textColor = "#e4e6ed"
font = "monospace"
```

## requirements.txt

```
streamlit>=1.30.0
pyyaml>=6.0
```

---

## DATA LAYER: Fake Documents

### data/firm_profile.json

```json
{
  "firm_name": "Avery Professional Corporation",
  "license_number": "CPA-ON-2019-4472",
  "jurisdiction": "CPA Ontario",
  "partners": [
    {
      "name": "Avery Patel",
      "role": "Managing Partner",
      "cpa_number": "ON-112847",
      "admitted": "2012-06-15"
    },
    {
      "name": "Priya Sharma",
      "role": "Partner",
      "cpa_number": "ON-118923",
      "admitted": "2015-09-01"
    }
  ],
  "staff": [
    {
      "name": "Marcus Chen",
      "role": "Senior Accountant",
      "hire_date": "2021-03-15",
      "cpa_candidate": true
    },
    {
      "name": "Aisha Okonkwo",
      "role": "Staff Accountant",
      "hire_date": "2023-08-01",
      "cpa_candidate": true
    },
    {
      "name": "Tyler Robinson",
      "role": "Junior Accountant",
      "hire_date": "2025-09-10",
      "cpa_candidate": false
    }
  ],
  "office_count": 1,
  "engagement_types": ["compilation", "review"],
  "industries_served": ["manufacturing", "restaurants", "professional_services", "retail"],
  "total_clients": 87,
  "last_inspection": "2023-04-15",
  "last_inspection_result": "Meets Requirements",
  "next_inspection_due": "2026-04-15"
}
```

### data/documents/firm_level/soqm_manual.json

```json
{
  "document_type": "soqm_manual",
  "title": "System of Quality Management Manual",
  "version": "2.1",
  "created_date": "2024-01-15",
  "last_updated": "2024-01-15",
  "author": "Clearline Consulting (external)",
  "components_addressed": [1, 2, 3, 4, 5, 6, 7],
  "has_quality_objectives": true,
  "has_risk_register": true,
  "has_response_policies": true,
  "notes": "Written by consultant. Has not been updated since creation. Component 7 monitoring section is generic template — not customized to firm."
}
```

### data/documents/firm_level/independence_declarations.json

```json
{
  "document_type": "independence_declarations",
  "declarations": [
    {
      "person": "Avery Patel",
      "signed": true,
      "date_signed": "2025-04-01",
      "period_covered": "2025-04-01 to 2026-03-31",
      "status": "ok"
    },
    {
      "person": "Priya Sharma",
      "signed": true,
      "date_signed": "2025-11-03",
      "period_covered": "2025-04-01 to 2026-03-31",
      "status": "late",
      "issue": "Signed 7 months into the period. Engagement letter for Client #3 (123 Restaurant) was dated 2025-10-15, which is BEFORE this declaration."
    },
    {
      "person": "Marcus Chen",
      "signed": true,
      "date_signed": "2025-04-05",
      "period_covered": "2025-04-01 to 2026-03-31",
      "status": "ok"
    },
    {
      "person": "Aisha Okonkwo",
      "signed": true,
      "date_signed": "2025-04-10",
      "period_covered": "2025-04-01 to 2026-03-31",
      "status": "ok"
    },
    {
      "person": "Tyler Robinson",
      "signed": false,
      "date_signed": null,
      "period_covered": null,
      "status": "missing",
      "issue": "New hire Sep 2025. No independence declaration obtained."
    }
  ]
}
```

### data/documents/firm_level/cpd_records.json

```json
{
  "document_type": "cpd_records",
  "requirement_hours_per_year": 20,
  "records": [
    {
      "person": "Avery Patel",
      "hours_completed_2025": 32,
      "status": "compliant",
      "courses": ["CSQM 1 Implementation (8h)", "Tax Update (12h)", "Ethics (4h)", "CSRS 4200 (8h)"]
    },
    {
      "person": "Priya Sharma",
      "hours_completed_2025": 24,
      "status": "compliant",
      "courses": ["Audit Quality (8h)", "Tax Update (12h)", "Ethics (4h)"]
    },
    {
      "person": "Marcus Chen",
      "hours_completed_2025": 20,
      "status": "compliant",
      "courses": ["CPA PEP Module (12h)", "Tax Basics (8h)"]
    },
    {
      "person": "Aisha Okonkwo",
      "hours_completed_2025": 16,
      "status": "warning",
      "issue": "4 hours short of 20-hour requirement. Due by Dec 31.",
      "courses": ["CPA PEP Module (12h)", "Ethics (4h)"]
    },
    {
      "person": "Tyler Robinson",
      "hours_completed_2025": 0,
      "status": "missing",
      "issue": "New hire Sep 2025. No CPD plan or record established yet."
    }
  ]
}
```

### data/documents/firm_level/monitoring_log.json

```json
{
  "document_type": "monitoring_log",
  "annual_file_monitoring": {
    "performed": true,
    "date_performed": "2025-06-15",
    "performed_by": "Avery Patel",
    "files_reviewed": ["ABC Manufacturing 2024", "GHI Retail 2024"],
    "findings": [
      {
        "finding": "GHI Retail file missing signed engagement letter",
        "severity": "reportable",
        "remediated": true,
        "remediation_date": "2025-07-01",
        "remediation_action": "Letter signed and added to file"
      }
    ],
    "status": "ok"
  },
  "completed_engagement_monitoring": {
    "performed": true,
    "date_performed": "2025-08-20",
    "performed_by": "Marcus Chen",
    "reviewer_independent": false,
    "issue": "Marcus Chen prepared the GHI Retail file that was included in the review. Independence requirement NOT met. Should be an external reviewer or someone who did not work on any of the files.",
    "files_reviewed": ["DEF Services 2024", "GHI Retail 2024"],
    "findings": [],
    "status": "fail_independence"
  },
  "soqm_evaluation": null
}
```

### data/documents/firm_level/soqm_evaluation.json

```json
{
  "document_type": "soqm_evaluation",
  "evaluations": [
    {
      "period": "2024",
      "date_performed": "2024-12-01",
      "performed_by": "Avery Patel",
      "conclusion": "SoQM operating effectively with minor improvements needed",
      "considered_monitoring_results": true,
      "considered_external_inspections": true,
      "considered_complaints": true,
      "documented": true,
      "status": "ok"
    }
  ],
  "latest_evaluation_date": "2024-12-01",
  "months_since_latest": 14,
  "overdue": true,
  "issue": "Annual evaluation due by Dec 2025. It is now Feb 2026. 14 months since last evaluation — overdue."
}
```

### data/documents/firm_level/remediation_log.json

```json
{
  "document_type": "remediation_log",
  "entries": [
    {
      "id": 1,
      "source": "2023 Practice Inspection",
      "deficiency": "Engagement letters not consistently referencing CSRS 4200",
      "date_identified": "2023-06-15",
      "root_cause": "Old template still in use",
      "corrective_action": "Updated engagement letter template to reference CSRS 4200",
      "action_date": "2023-07-01",
      "followup_verified": true,
      "status": "closed"
    },
    {
      "id": 2,
      "source": "2025 Annual File Monitoring",
      "deficiency": "GHI Retail file missing signed engagement letter",
      "date_identified": "2025-06-15",
      "root_cause": "Staff forgot to obtain signature before starting work",
      "corrective_action": "Letter signed and added to file. Reminder added to onboarding checklist.",
      "action_date": "2025-07-01",
      "followup_verified": true,
      "status": "closed"
    },
    {
      "id": 3,
      "source": "2025 Completed Engagement Monitoring",
      "deficiency": "Reviewer was not independent of files reviewed",
      "date_identified": "2025-08-20",
      "root_cause": null,
      "corrective_action": null,
      "action_date": null,
      "followup_verified": false,
      "status": "open",
      "issue": "Deficiency identified but no corrective action documented. No root cause analysis. This will be flagged by inspector."
    }
  ]
}
```

### data/documents/firm_level/governance_policies.json

```json
{
  "document_type": "governance_policies",
  "tone_at_top_policy": true,
  "quality_responsibility_assigned_to": "Avery Patel",
  "quality_in_performance_reviews": true,
  "strategic_quality_review_documented": true,
  "commercial_override_policy": true,
  "last_reviewed": "2024-01-15",
  "status": "ok"
}
```

### data/documents/firm_level/client_acceptance_forms.json

```json
{
  "document_type": "client_acceptance_forms",
  "forms": [
    {"client": "ABC Manufacturing Ltd", "form_exists": true, "risk_assessment": true, "competence_eval": true, "integrity_eval": true, "aml_check": true, "status": "ok"},
    {"client": "XYZ Holdings Ltd", "form_exists": true, "risk_assessment": true, "competence_eval": true, "integrity_eval": true, "aml_check": true, "status": "ok"},
    {"client": "123 Restaurant Inc", "form_exists": true, "risk_assessment": true, "competence_eval": true, "integrity_eval": false, "aml_check": true, "status": "warning", "issue": "Client integrity evaluation not documented. Cash-heavy business — should have enhanced assessment."},
    {"client": "DEF Services Corp", "form_exists": true, "risk_assessment": true, "competence_eval": true, "integrity_eval": true, "aml_check": true, "status": "ok"}
  ]
}
```

### data/documents/firm_level/conflict_register.json

```json
{
  "document_type": "conflict_register",
  "exists": true,
  "last_updated": "2025-04-01",
  "entries": [
    {
      "conflict": "Avery Patel's spouse employed by ABC Manufacturing",
      "threat_type": "familiarity",
      "safeguard": "Priya Sharma assigned as engagement partner for ABC Manufacturing",
      "documented": true,
      "status": "ok"
    }
  ],
  "status": "ok"
}
```

### data/documents/firm_level/complaints_procedure.json

```json
{
  "document_type": "complaints_procedure",
  "procedure_exists": true,
  "documented_in_soqm": true,
  "complaints_received": 0,
  "status": "ok"
}
```

### data/documents/firm_level/policy_distribution_log.json

```json
{
  "document_type": "policy_distribution_log",
  "distributions": [
    {
      "policy": "SoQM Manual v2.1",
      "date_distributed": "2024-01-20",
      "method": "email",
      "acknowledged_by": ["Avery Patel", "Priya Sharma", "Marcus Chen", "Aisha Okonkwo"],
      "missing_acknowledgment": ["Tyler Robinson"],
      "issue": "Tyler Robinson (hired Sep 2025) has not received or acknowledged the SoQM manual."
    }
  ],
  "status": "warning"
}
```

---

### ENGAGEMENT FILES

### data/documents/engagement_files/file_1_abc_manufacturing.json

```json
{
  "file_id": "FILE-001",
  "client_name": "ABC Manufacturing Ltd",
  "engagement_type": "compilation",
  "standard": "CSRS 4200",
  "fiscal_year_end": "2025-06-30",
  "engagement_partner": "Priya Sharma",
  "prepared_by": "Marcus Chen",
  "checks": {
    "engagement_letter": {
      "exists": true,
      "signed_by_client": true,
      "signed_by_firm": true,
      "date_signed": "2025-07-05",
      "work_start_date": "2025-07-15",
      "references_csrs_4200": true,
      "describes_mgmt_responsibilities": true,
      "describes_accountant_responsibilities": true,
      "states_no_assurance": true,
      "identifies_framework": "ASPE",
      "status": "ok"
    },
    "independence": {
      "assessment_documented": true,
      "threats_evaluated": true,
      "safeguards_applied": "Priya Sharma as EP due to Avery conflict",
      "declaration_on_file": true,
      "status": "ok"
    },
    "knowledge_of_client": {
      "industry_understanding": true,
      "framework_understanding": true,
      "documented": true,
      "status": "ok"
    },
    "compilation_procedures": {
      "data_accumulated": true,
      "data_classified": true,
      "statements_read_for_errors": true,
      "misleading_considered": true,
      "adjustments_documented": true,
      "working_papers_present": true,
      "status": "ok"
    },
    "financial_statements": {
      "framework_compliant": true,
      "basis_of_accounting_note": true,
      "required_disclosures_present": true,
      "comparatives_correct": true,
      "notes_tie_to_statements": true,
      "status": "ok"
    },
    "report": {
      "correct_standard_wording": true,
      "uses_csrs_4200_format": true,
      "not_old_section_9200": true,
      "addressed_appropriately": true,
      "dated": "2025-08-10",
      "signed": true,
      "independence_impairment_disclosed": false,
      "basis_described": true,
      "status": "ok"
    },
    "file_assembly": {
      "assembled_within_60_days": true,
      "assembly_date": "2025-09-15",
      "report_date": "2025-08-10",
      "days_elapsed": 36,
      "no_post_assembly_changes": true,
      "status": "ok"
    }
  },
  "overall_status": "pass",
  "assertions_passed": 7,
  "assertions_total": 7,
  "issues": []
}
```

### data/documents/engagement_files/file_2_xyz_holdings.json

```json
{
  "file_id": "FILE-002",
  "client_name": "XYZ Holdings Ltd",
  "engagement_type": "compilation",
  "standard": "CSRS 4200",
  "fiscal_year_end": "2025-09-30",
  "engagement_partner": "Avery Patel",
  "prepared_by": "Aisha Okonkwo",
  "checks": {
    "engagement_letter": {
      "exists": true,
      "signed_by_client": true,
      "signed_by_firm": true,
      "date_signed": "2025-10-05",
      "work_start_date": "2025-10-10",
      "references_csrs_4200": true,
      "describes_mgmt_responsibilities": true,
      "describes_accountant_responsibilities": true,
      "states_no_assurance": true,
      "identifies_framework": "ASPE",
      "status": "ok"
    },
    "independence": {
      "assessment_documented": true,
      "threats_evaluated": true,
      "safeguards_applied": null,
      "declaration_on_file": true,
      "status": "ok"
    },
    "knowledge_of_client": {
      "industry_understanding": true,
      "framework_understanding": true,
      "documented": true,
      "status": "ok"
    },
    "compilation_procedures": {
      "data_accumulated": true,
      "data_classified": true,
      "statements_read_for_errors": true,
      "misleading_considered": true,
      "adjustments_documented": true,
      "working_papers_present": true,
      "status": "ok"
    },
    "financial_statements": {
      "framework_compliant": true,
      "basis_of_accounting_note": true,
      "required_disclosures_present": true,
      "comparatives_correct": false,
      "notes_tie_to_statements": true,
      "status": "warning",
      "issue": "Prior year comparative figures do not agree to prior year issued statements. Difference of $2,340 in accounts payable. Likely a reclassification not documented."
    },
    "report": {
      "correct_standard_wording": true,
      "uses_csrs_4200_format": true,
      "not_old_section_9200": true,
      "addressed_appropriately": true,
      "dated": "2025-11-20",
      "signed": true,
      "independence_impairment_disclosed": false,
      "basis_described": true,
      "status": "ok"
    },
    "file_assembly": {
      "assembled_within_60_days": true,
      "assembly_date": "2025-12-15",
      "report_date": "2025-11-20",
      "days_elapsed": 25,
      "no_post_assembly_changes": true,
      "status": "ok"
    }
  },
  "overall_status": "pass_with_warning",
  "assertions_passed": 6,
  "assertions_total": 7,
  "issues": [
    {
      "severity": "warning",
      "component": "financial_statements",
      "description": "Comparative figures discrepancy of $2,340 in accounts payable not documented"
    }
  ]
}
```

### data/documents/engagement_files/file_3_123_restaurant.json

This is the BAD file with multiple issues — the demo showpiece.

```json
{
  "file_id": "FILE-003",
  "client_name": "123 Restaurant Inc",
  "engagement_type": "compilation",
  "standard": "CSRS 4200",
  "fiscal_year_end": "2025-08-31",
  "engagement_partner": "Priya Sharma",
  "prepared_by": "Aisha Okonkwo",
  "checks": {
    "engagement_letter": {
      "exists": true,
      "signed_by_client": true,
      "signed_by_firm": true,
      "date_signed": "2025-11-20",
      "work_start_date": "2025-10-15",
      "references_csrs_4200": false,
      "describes_mgmt_responsibilities": true,
      "describes_accountant_responsibilities": true,
      "states_no_assurance": true,
      "identifies_framework": "ASPE",
      "status": "critical",
      "issues": [
        "Engagement letter dated 2025-11-20 but work started 2025-10-15 — letter is BACKDATED (signed after work began)",
        "Letter does not reference CSRS 4200 — uses old language"
      ]
    },
    "independence": {
      "assessment_documented": true,
      "threats_evaluated": true,
      "safeguards_applied": null,
      "declaration_on_file": true,
      "status": "warning",
      "issue": "Priya Sharma's independence declaration was signed 2025-11-03 but engagement letter for this client is dated 2025-10-15. Declaration was not in effect when work started."
    },
    "knowledge_of_client": {
      "industry_understanding": true,
      "framework_understanding": true,
      "documented": true,
      "status": "ok"
    },
    "compilation_procedures": {
      "data_accumulated": true,
      "data_classified": true,
      "statements_read_for_errors": true,
      "misleading_considered": false,
      "adjustments_documented": true,
      "working_papers_present": true,
      "status": "warning",
      "issue": "No documentation that accountant considered whether compiled statements might be misleading. Cash-heavy restaurant — heightened risk."
    },
    "financial_statements": {
      "framework_compliant": true,
      "basis_of_accounting_note": false,
      "required_disclosures_present": true,
      "comparatives_correct": true,
      "notes_tie_to_statements": true,
      "status": "critical",
      "issue": "MISSING basis of accounting note. CSRS 4200 requires a note describing the applicable financial reporting framework. This is the #3 most common deficiency found in CPA practice inspections."
    },
    "report": {
      "correct_standard_wording": false,
      "uses_csrs_4200_format": false,
      "not_old_section_9200": false,
      "addressed_appropriately": true,
      "dated": "2025-12-01",
      "signed": true,
      "independence_impairment_disclosed": false,
      "basis_described": false,
      "status": "critical",
      "issue": "Report still uses old Section 9200 'Notice to Reader' wording. Must be updated to CSRS 4200 compilation report format. This is the #1 most common deficiency in practice inspections."
    },
    "file_assembly": {
      "assembled_within_60_days": true,
      "assembly_date": "2026-01-15",
      "report_date": "2025-12-01",
      "days_elapsed": 45,
      "no_post_assembly_changes": true,
      "status": "ok"
    }
  },
  "overall_status": "fail",
  "assertions_passed": 3,
  "assertions_total": 7,
  "issues": [
    {
      "severity": "critical",
      "component": "engagement_letter",
      "description": "Letter dated after work started (backdated) and does not reference CSRS 4200"
    },
    {
      "severity": "warning",
      "component": "independence",
      "description": "Partner independence declaration not in effect when engagement work began"
    },
    {
      "severity": "warning",
      "component": "compilation_procedures",
      "description": "No consideration of whether statements might be misleading for cash-heavy business"
    },
    {
      "severity": "critical",
      "component": "financial_statements",
      "description": "Missing basis of accounting note (CSRS 4200 requirement)"
    },
    {
      "severity": "critical",
      "component": "report",
      "description": "Still using old Section 9200 Notice to Reader — must use CSRS 4200 format"
    }
  ]
}
```

### data/documents/engagement_files/file_4_def_services_review.json

```json
{
  "file_id": "FILE-004",
  "client_name": "DEF Services Corp",
  "engagement_type": "review",
  "standard": "CSRE 2400",
  "fiscal_year_end": "2025-12-31",
  "engagement_partner": "Avery Patel",
  "prepared_by": "Marcus Chen",
  "checks": {
    "engagement_letter": {
      "exists": true,
      "signed_by_client": true,
      "signed_by_firm": true,
      "date_signed": "2026-01-10",
      "work_start_date": "2026-01-12",
      "references_standard": true,
      "describes_mgmt_responsibilities": true,
      "describes_accountant_responsibilities": true,
      "states_limited_assurance": true,
      "identifies_framework": "ASPE",
      "status": "ok"
    },
    "independence": {
      "assessment_documented": true,
      "threats_evaluated": true,
      "safeguards_applied": null,
      "declaration_on_file": true,
      "status": "ok"
    },
    "analytical_procedures": {
      "performed": true,
      "documented": true,
      "areas_of_risk_identified": true,
      "explanations_obtained": true,
      "status": "ok"
    },
    "inquiries_of_management": {
      "performed": true,
      "documented": true,
      "status": "ok"
    },
    "management_representation_letter": {
      "obtained": true,
      "signed": true,
      "dated": "2026-02-05",
      "status": "ok"
    },
    "financial_statements": {
      "framework_compliant": true,
      "basis_of_accounting_note": true,
      "required_disclosures_present": true,
      "comparatives_correct": true,
      "notes_tie_to_statements": true,
      "status": "ok"
    },
    "report": {
      "correct_standard_wording": true,
      "uses_csre_2400_format": true,
      "addressed_appropriately": true,
      "dated": "2026-02-08",
      "signed": true,
      "basis_described": true,
      "status": "ok"
    },
    "file_assembly": {
      "assembled_within_60_days": false,
      "assembly_date": null,
      "report_date": "2026-02-08",
      "days_elapsed": null,
      "no_post_assembly_changes": null,
      "status": "pending",
      "issue": "File assembly not yet completed. 60-day deadline is 2026-04-09. Currently within deadline but should be assembled soon."
    }
  },
  "overall_status": "pass",
  "assertions_passed": 7,
  "assertions_total": 8,
  "issues": [
    {
      "severity": "info",
      "component": "file_assembly",
      "description": "File assembly pending — deadline 2026-04-09 (within time limit)"
    }
  ]
}
```

---

## POLICY DEFINITION

### data/policies/csqm1_full.yaml

```yaml
policy:
  name: "CPA Practice Inspection — CSQM 1 Full"
  jurisdiction: CPA_Canada
  standards:
    - CSQM1
    - CSRS_4200
    - CSRE_2400

  firm_level_rules:
    governance:
      - id: GOV-01
        description: "Tone-at-top policy documented"
        check: governance_policies.tone_at_top_policy == true
        severity: critical
      - id: GOV-02
        description: "Quality responsibility assigned to individual"
        check: governance_policies.quality_responsibility_assigned_to != null
        severity: critical
      - id: GOV-03
        description: "Strategic quality review documented"
        check: governance_policies.strategic_quality_review_documented == true
        severity: warning

    ethics:
      - id: ETH-01
        description: "All personnel have signed independence declaration"
        check: all_personnel_have_signed_declaration
        severity: critical
      - id: ETH-02
        description: "Independence declarations dated before engagement work"
        check: declaration_dates_before_engagement_dates
        severity: critical
      - id: ETH-03
        description: "Conflict of interest register maintained"
        check: conflict_register.exists == true
        severity: warning

    acceptance:
      - id: ACC-01
        description: "Client acceptance form exists for all inspected clients"
        check: all_inspected_clients_have_acceptance_form
        severity: critical
      - id: ACC-02
        description: "Risk assessment completed per client"
        check: all_clients_have_risk_assessment
        severity: critical
      - id: ACC-03
        description: "Client integrity evaluation documented"
        check: all_clients_have_integrity_eval
        severity: warning

    resources:
      - id: RES-01
        description: "All staff CPD records current"
        check: all_staff_cpd_compliant
        severity: warning
      - id: RES-02
        description: "CPA Handbook subscription current"
        check: soqm_manual.exists
        severity: critical

    communication:
      - id: COM-01
        description: "Policy distribution log maintained"
        check: policy_distribution_log.exists
        severity: warning
      - id: COM-02
        description: "All staff acknowledged receiving policies"
        check: all_staff_acknowledged_policies
        severity: warning
      - id: COM-03
        description: "Complaints procedure documented"
        check: complaints_procedure.procedure_exists == true
        severity: warning

    monitoring:
      - id: MON-01
        description: "Annual file monitoring performed"
        check: monitoring_log.annual_file_monitoring.performed == true
        severity: critical
      - id: MON-02
        description: "Completed engagement monitoring performed"
        check: monitoring_log.completed_engagement_monitoring.performed == true
        severity: critical
      - id: MON-03
        description: "Monitoring reviewer independent of files reviewed"
        check: monitoring_log.completed_engagement_monitoring.reviewer_independent == true
        severity: critical
      - id: MON-04
        description: "Annual SoQM evaluation performed"
        check: soqm_evaluation.overdue == false
        severity: critical
      - id: MON-05
        description: "All remediation entries have corrective actions"
        check: all_remediation_entries_have_actions
        severity: critical
      - id: MON-06
        description: "Root cause analysis documented for all deficiencies"
        check: all_remediation_entries_have_root_cause
        severity: warning

  engagement_file_rules:
    compilation:
      - id: ENG-01
        description: "Engagement letter exists and signed by both parties"
        check: engagement_letter.exists and engagement_letter.signed_by_client and engagement_letter.signed_by_firm
        severity: critical
      - id: ENG-02
        description: "Engagement letter dated before or at start of work"
        check: engagement_letter.date_signed <= work_start_date
        severity: critical
      - id: ENG-03
        description: "Engagement letter references applicable standard"
        check: engagement_letter.references_csrs_4200 == true
        severity: critical
      - id: ENG-04
        description: "Independence assessment documented"
        check: independence.assessment_documented == true
        severity: critical
      - id: ENG-05
        description: "Financial statements include basis of accounting note"
        check: financial_statements.basis_of_accounting_note == true
        severity: critical
      - id: ENG-06
        description: "Report uses current CSRS 4200 wording (not old Section 9200)"
        check: report.not_old_section_9200 == true
        severity: critical
      - id: ENG-07
        description: "File assembled within 60 days of report date"
        check: file_assembly.assembled_within_60_days == true
        severity: warning

    review:
      - id: REV-01
        description: "Analytical procedures performed and documented"
        check: analytical_procedures.performed == true
        severity: critical
      - id: REV-02
        description: "Management representation letter obtained"
        check: management_representation_letter.obtained == true
        severity: critical
```

---

## APP BEHAVIOR

**DOMAIN REMINDER: Everything in this app is about ACCOUNTING practice inspections. The user is a CPA (accountant). The "documents" are things like engagement letters, financial statements, independence declarations, and quality management manuals. The "inspection" is by a CPA licensing body (like CPA Ontario) checking if the accountant's firm meets professional standards. This has ZERO connection to cloud security, IAM roles, RBAC, or IT audits.**

### app.py — Main Application

The app title should be: **"CPA Practice Inspection Readiness Scanner"** with subtitle "Powered by Verifiable Accounting"

The Streamlit app should have the following pages/tabs:

#### Page 1: Dashboard (Home)

- Firm name, license number, next inspection date with countdown
- Large readiness score circle/gauge (e.g., 78%)
- Summary metrics in st.metric cards:
  - Total assertions checked
  - Critical gaps found
  - Warnings found
  - Files scanned
- Traffic light status per CSQM 1 component (green/yellow/red)
- Call-to-action: "4 critical items need attention before your inspection"

#### Page 2: Firm-Level Scan

- Expandable sections per CSQM 1 component (1 through 8)
- Each section shows:
  - Component name and description
  - Rules checked with pass/fail/warning icons
  - For failures: the specific issue found and what to fix
  - Evidence chain visualization (simple: "Document A → links to → Requirement B")
- Highlight Component 7 (Monitoring) as having the most issues

#### Page 3: Engagement Files

- Tabs or selectbox for each file (File 1 through File 4)
- Per file: checklist view with pass/fail per item
- File 3 (123 Restaurant) should be visually highlighted as problematic
- Show the specific issues with File 3:
  - Backdated engagement letter
  - Missing basis of accounting note
  - Old Section 9200 report wording
- Side-by-side comparison view: what the file has vs. what inspector expects

#### Page 4: Gap Report

- Sorted list of ALL findings across firm and files
- Grouped by severity: Critical → Warning → Info
- Each finding shows:
  - Rule ID
  - Description
  - Where found (firm-level or which file)
  - What to fix (remediation suggestion)
  - Estimated time to fix
- Total estimated remediation time
- Predicted inspection outcome if unfixed vs. if fixed

#### Page 5: Evidence Graph

- Visual representation of the evidence chain
- Use streamlit graphviz_chart or a simple table-based visualization
- Show nodes as documents, edges as "links to requirement"
- Highlight broken chains in red
- Show the 304 assertion count and how many are connected

#### Page 6: Generate Report

- Button to generate the inspection readiness PDF/report
- Shows the formatted report (similar to the report output in the concept diagrams)
- Download button for the report

### Engine Logic (engine/scanner.py)

The scanner should:
1. Load firm_profile.json
2. Load all firm-level documents from data/documents/firm_level/
3. Load all engagement files from data/documents/engagement_files/
4. Load policy from data/policies/csqm1_full.yaml
5. Run each rule against the loaded data
6. Produce a results object with:
   - Overall readiness score (percentage)
   - Per-component results
   - Per-file results
   - List of all findings (critical, warning, info)
   - Evidence chain completeness

The rules dont need to actually parse the YAML dynamically — they can be hardcoded Python functions that check the JSON fields. The YAML policy file exists to show what the product WILL do. The scanner checks the JSON metadata fields.

### Scoring Logic

```python
# Readiness score calculation
total_assertions = firm_assertions + sum(file_assertions for each file)
passed_assertions = count where status in ["ok", "pass"]
warnings = count where status == "warning"
critical = count where status in ["critical", "fail"]

# Score: passed / total, with penalties
base_score = passed_assertions / total_assertions
penalty = critical * 0.05 + warnings * 0.01
readiness_score = max(0, base_score - penalty)

# Predicted outcome
if critical > 0:
    predicted_outcome = "Does Not Meet Requirements"
elif warnings > 3:
    predicted_outcome = "Meets Requirements (with notes)"
else:
    predicted_outcome = "Meets Requirements"
```

### Visual Style

- Use emoji for status: ✅ pass, ⚠️ warning, ❌ critical, ℹ️ info
- Use st.metric with delta for showing improvement potential
- Color code everything: green (pass), orange (warning), red (critical)
- Make File 3 obviously problematic at a glance
- The dashboard should feel like a "health check" — immediately clear what needs attention
- Add the Verifiable Accounting branding: orange accent color (#f97316)

### Key Demo Flow

When showing to a CPA client (like Avery), the flow should be:

1. Open app → Dashboard shows 78% readiness with 4 critical gaps
2. Click into Firm-Level → See that SoQM evaluation is overdue, monitoring has independence issue
3. Click into Engagement Files → See File 3 is red, click to see all the problems
4. Click Gap Report → See prioritized list of what to fix with time estimates
5. Click Generate Report → See what you would hand to the inspector
6. The pitch: "Fix those 4 items (6-8 hours of work), run the scan again, score goes to 96%. Pass your inspection."

### What NOT to Build

- No user authentication
- No real document upload (everything is pre-loaded fake data)
- No real MLIR/compiler backend
- No API calls
- No database
- No deployment config
- Keep it simple — this is a demo, not production

### Stretch Goals (only if core is solid)

- Toggle to simulate "after fixing" the critical items (score jumps to 96%)
- Side-by-side before/after view
- Timeline view showing when each document was created/signed
- Export gap report as CSV

---

## IMPORTANT CONTEXT

This demo is for showing to CPA firm partners during customer discovery interviews. The audience is accountants, NOT engineers. Every label, description, and UI element should use accounting language, not compiler language. No mention of MLIR, compilers, Mojo, or evidence chain reachability. Use terms like:

- "Inspection readiness" not "compliance verification"
- "Gap" not "broken evidence chain"
- "Your file is missing..." not "assertion failed"
- "The inspector will flag..." not "rule violation detected"
- "Fix this before inspection" not "remediate deficiency"

The goal is for Avery to look at this and say "YES, this is exactly what I need before my next inspection."
