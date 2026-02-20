# IAM-Audit: SR&ED Claim Readiness Scanner — Streamlit POC Build Spec

**Purpose**: Build a fully functional Streamlit demo application that simulates an AI-powered SR&ED (Scientific Research & Experimental Development) claim readiness scanner. The app ingests dummy client data (pre-loaded), runs it against real CRA rules, and produces a compliance readiness report with risk scores, flagged issues, and remediation guidance.

**Target audience for the demo**: CPAs, SR&ED consultants, and bank controllers evaluating IAM-Audit.

**Tech stack**: Python 3.11+, Streamlit, Plotly, pandas. No external APIs. All data is synthetic and embedded.

---

## 1. APPLICATION ARCHITECTURE

```
app.py                    # Main entry, page routing, session state
pages/
  1_Dashboard.py          # Executive summary dashboard
  2_Project_Eligibility.py # Five-question test per project
  3_Expenditures.py       # T661 Parts 3-4 expenditure analysis
  4_Documentation.py      # Evidence trail audit
  5_Form_T661_Review.py   # Full form completeness check (all 10 parts)
  6_Risk_Report.py        # Final risk score + remediation plan
  7_ITC_Calculator.py     # Federal + provincial ITC estimate
data/
  client_profile.json     # Company info, fiscal year, CCPC status
  projects.json           # 3 SR&ED projects with narratives
  expenditures.json       # Salary, materials, contracts, overhead
  documentation_log.json  # Evidence items with timestamps
  t661_form_data.json     # Simulated T661 field values (all 10 parts)
utils/
  scoring.py              # Risk scoring engine
  rules.py                # CRA rule definitions
  constants.py            # ITC rates, YMPE, thresholds, line numbers
  formatters.py           # Currency, percentage, status badge helpers
```

---

## 2. DUMMY CLIENT DATA

### 2.1 Client Profile (`client_profile.json`)

```json
{
  "company_name": "NovaTech Solutions Inc.",
  "business_number": "123456789RC0001",
  "fiscal_year_end": "2024-12-31",
  "corporation_type": "CCPC",
  "taxable_income_prior_year": 485000,
  "taxable_capital": 8200000,
  "associated_corps": 0,
  "province": "Ontario",
  "naics_code": "541514",
  "naics_description": "Computer systems design and related services",
  "first_time_claimant": false,
  "contact": {
    "name": "Priya Chakraborty",
    "title": "VP Engineering",
    "phone": "416-555-0142",
    "email": "priya@novatech.example.com"
  },
  "preparer": {
    "name": "Greenfield SR&ED Advisory Inc.",
    "business_number": "987654321RC0001",
    "contact_name": "Marcus Greenfield, CPA",
    "billing_arrangement": 1,
    "billing_code_meaning": "Contingency fee",
    "fee_percentage": 25
  }
}
```

**Why this matters**: Contingency fee preparer (billing_arrangement=1) is a CRA risk flag. The scanner must catch this.

### 2.2 Projects (`projects.json`)

Three projects with deliberately different eligibility profiles:

```json
[
  {
    "project_id": "P001",
    "title": "Adaptive Signal Processing for Noisy IoT Sensor Fusion",
    "field_of_science_code": "2.02.01",
    "field_of_science": "Electrical and Electronic Engineering",
    "start_date": "2024-01-15",
    "end_date": "2024-11-30",
    "status": "completed",
    "keyword_codes": ["2090", "2190"],
    "eligibility_strength": "STRONG",
    "line_242_scientific_technological_advancement": "This project sought to advance the capability of sensor fusion algorithms to operate reliably in environments with signal-to-noise ratios below 3dB. Existing Kalman filter approaches in the published literature (IEEE Sensors Journal, 2022; Elsevier Signal Processing, 2023) assume Gaussian noise distributions which fail in industrial IoT deployments where interference patterns are non-stationary and multi-modal. We hypothesized that a hybrid approach combining wavelet decomposition with adaptive extended Kalman filtering could maintain sensor fusion accuracy above 92% in sub-3dB SNR conditions. No known methodology in the public domain or standard industrial practice addressed this specific combination of constraints. The technological advancement sought was a generalizable signal processing architecture that could be deployed on resource-constrained edge devices (under 512KB RAM) while maintaining real-time fusion rates of 100Hz or greater.",
    "line_242_word_count": 138,
    "line_244_technological_uncertainty": "Three specific technological uncertainties were identified at the project outset and documented in our project initiation record (PIR-2024-001, dated January 15, 2024). First, it was unknown whether wavelet decomposition could be performed within the memory constraints of ARM Cortex-M4 processors with only 256KB available RAM after OS overhead. Standard discrete wavelet transform implementations require O(n) memory scaling that exceeded available resources for our target window sizes. Second, the interaction between adaptive EKF gain scheduling and non-stationary noise characteristics was theoretically unpredictable. Published convergence proofs for EKF assume bounded process noise covariance, which does not hold in our target environment where electromagnetic interference creates transient noise spikes 40dB above baseline. Third, we could not determine in advance whether the fused output would maintain temporal coherence across sensor modalities with different native sampling rates (accelerometer at 1kHz, temperature at 10Hz, pressure at 100Hz) when processed through a unified wavelet domain. Our systematic investigation involved: (a) developing three candidate wavelet basis functions optimized for memory-constrained environments, (b) implementing and testing four EKF gain scheduling strategies against recorded industrial noise profiles from three manufacturing facilities, (c) conducting 847 controlled experiments varying SNR from 0dB to 10dB across all sensor modality combinations. Hypotheses were formulated, tested, and recorded in our lab notebook system (Confluence space 'SensorFusion-R&D', 342 entries). Results from Phase 1 (wavelet basis selection) directly informed the experimental design of Phase 2 (EKF adaptation), demonstrating the iterative, hypothesis-driven nature of the investigation. The technological uncertainties were resolved through this systematic process, though two secondary uncertainties regarding long-term drift compensation remain open for future work.",
    "line_244_word_count": 247,
    "line_246_work_performed": "Work began January 15 with a literature review and gap analysis (documented in PIR-2024-001). From January to March, we developed three candidate wavelet basis functions: Daubechies-4 modified for fixed-point arithmetic, a custom Haar variant with adaptive thresholding, and a biorthogonal spline wavelet optimized for in-place computation. Each was implemented in C on ARM Cortex-M4 evaluation boards and benchmarked for memory usage, computational latency, and reconstruction accuracy. The custom Haar variant achieved 94% reconstruction accuracy within 187KB RAM, meeting our constraint. From April to July, we implemented four EKF gain scheduling strategies and tested each against 12 recorded industrial noise profiles. Strategy 3 (exponentially weighted moving average of innovation covariance) demonstrated stable convergence in 9 of 12 profiles. We modified Strategy 3 with a bounded forgetting factor (lambda between 0.95 and 0.99) which achieved convergence in 11 of 12 profiles. From August to November, we integrated the wavelet preprocessing with the modified EKF and conducted 847 fusion experiments. Final system achieved 93.7% fusion accuracy at 2.5dB SNR on Cortex-M4, exceeding our 92% target. Results were documented in internal technical report TR-2024-SF-Final (November 22, 2024).",
    "line_246_word_count": 194,
    "five_question_test": {
      "q1_uncertainty": true,
      "q1_evidence": "Sub-3dB SNR fusion on memory-constrained devices had no known solution in published literature. PIR-2024-001 documents gap analysis.",
      "q2_hypothesis": true,
      "q2_evidence": "Three specific hypotheses documented in PIR-2024-001. Each tested systematically.",
      "q3_systematic": true,
      "q3_evidence": "847 controlled experiments with documented variables. Confluence space with 342 entries.",
      "q4_advancement": true,
      "q4_evidence": "Novel wavelet-EKF hybrid achieving 93.7% accuracy at 2.5dB SNR on Cortex-M4. No prior art.",
      "q5_record": true,
      "q5_evidence": "Confluence space 'SensorFusion-R&D' (342 entries), lab notebooks, PIR-2024-001, TR-2024-SF-Final."
    },
    "personnel": [
      {"name": "Dr. Anika Patel", "role": "Principal Researcher", "hours_sred": 1200, "hours_total": 1800, "salary": 145000, "is_specified_employee": false},
      {"name": "James Wu", "role": "Embedded Systems Engineer", "hours_sred": 950, "hours_total": 1800, "salary": 112000, "is_specified_employee": false},
      {"name": "Fatima Al-Rashidi", "role": "DSP Specialist (Contract)", "hours_sred": 600, "hours_total": 600, "salary": null, "is_specified_employee": false, "is_contractor": true, "contract_value": 72000, "arms_length": true}
    ]
  },
  {
    "project_id": "P002",
    "title": "Automated Anomaly Detection in Multi-Tenant Cloud Telemetry Streams",
    "field_of_science_code": "1.02.01",
    "field_of_science": "Computer Sciences",
    "start_date": "2024-03-01",
    "end_date": "2024-12-31",
    "status": "ongoing",
    "keyword_codes": ["2090", "8020"],
    "eligibility_strength": "MEDIUM",
    "line_242_scientific_technological_advancement": "This project aimed to develop an anomaly detection system capable of identifying performance degradation patterns across multi-tenant cloud infrastructure where tenant workloads create correlated noise that masks genuine anomalies. Standard statistical methods (Z-score, IQR) and existing ML approaches (isolation forests, autoencoders) evaluated in our preliminary study (documented in feasibility report FR-2024-002) failed to distinguish tenant-induced variability from infrastructure-level anomalies when correlation coefficients exceeded 0.7. The advancement sought was a detection methodology maintaining precision above 85% and recall above 90% in environments with inter-tenant correlation above 0.8.",
    "line_242_word_count": 102,
    "line_244_technological_uncertainty": "The primary uncertainty was whether temporal graph neural networks could model the dynamic dependency structure between tenants and infrastructure components with sufficient fidelity to separate correlated tenant noise from genuine anomalies. While GNNs have been applied to static network topologies for anomaly detection, the application to dynamically changing multi-tenant cloud graphs with variable node and edge counts was unexplored in published literature. We conducted a literature review (March 2024, documented in LR-2024-002) confirming no existing approach addressed graphs with more than 500 dynamically changing nodes at sub-minute granularity. A secondary uncertainty was whether the model could be trained on synthetic anomalies and generalize to real-world failure modes it had never seen, given that real cloud failures are rare and heterogeneous. We designed a systematic experimental program involving: synthetic graph generation with controlled correlation parameters, injection of 12 categories of known failure modes at varying intensities, and ablation studies on graph construction strategies.",
    "line_244_word_count": 157,
    "line_246_work_performed": "March through May: literature review, feasibility study, and synthetic data generation framework. Generated 2.4M synthetic telemetry snapshots across 847 simulated tenant configurations. June through September: implemented three GNN architectures (GAT, GraphSAGE, temporal GCN) and benchmarked against baseline methods. Temporal GCN showed 78% precision at 0.8 correlation, below our 85% target. October through December: developed a novel attention mechanism weighting edges by temporal stability. Achieved 83% precision and 91% recall at 0.8 correlation. Work is ongoing to close the precision gap. [NOTE: documentation gap exists between June 15 and September 3, 2024 — team lead was on parental leave and lab notebook entries were not maintained during this period].",
    "line_246_word_count": 122,
    "five_question_test": {
      "q1_uncertainty": true,
      "q1_evidence": "GNNs on dynamic multi-tenant graphs with 500+ nodes at sub-minute granularity — no published approach. LR-2024-002.",
      "q2_hypothesis": true,
      "q2_evidence": "Hypothesis that temporal edge attention would separate correlated noise. Documented in FR-2024-002.",
      "q3_systematic": true,
      "q3_evidence": "2.4M synthetic snapshots, 3 GNN architectures, ablation studies. BUT 3-month documentation gap.",
      "q4_advancement": true,
      "q4_evidence": "Novel temporal attention mechanism. 83% precision at 0.8 correlation. Partial — target not fully met.",
      "q5_record": false,
      "q5_evidence": "3-month gap (June 15 to September 3) in lab notebooks. Team lead parental leave. No delegate assigned."
    },
    "personnel": [
      {"name": "Dr. Anika Patel", "role": "Technical Advisor", "hours_sred": 200, "hours_total": 1800, "salary": 145000, "is_specified_employee": false},
      {"name": "Carlos Mendes", "role": "ML Engineer", "hours_sred": 1400, "hours_total": 1800, "salary": 128000, "is_specified_employee": false},
      {"name": "Sarah Kim", "role": "Cloud Infrastructure", "hours_sred": 400, "hours_total": 1800, "salary": 105000, "is_specified_employee": false}
    ]
  },
  {
    "project_id": "P003",
    "title": "Migration of Legacy REST APIs to GraphQL Federation Architecture",
    "field_of_science_code": "1.02.01",
    "field_of_science": "Computer Sciences",
    "start_date": "2024-02-01",
    "end_date": "2024-09-30",
    "status": "completed",
    "keyword_codes": ["2090"],
    "eligibility_strength": "INELIGIBLE",
    "line_242_scientific_technological_advancement": "This project converted 47 legacy REST API endpoints to a unified GraphQL federation gateway using Apollo Federation v2. The goal was to reduce frontend API call volume by 60% and improve developer productivity by providing a single schema across all microservices. We adopted industry best practices from Apollo's published migration guides and the GraphQL Foundation's specification documents.",
    "line_242_word_count": 55,
    "line_244_technological_uncertainty": "The main challenge was coordinating schema ownership across 6 development teams and resolving naming conflicts in the federated supergraph. We also needed to ensure backward compatibility with mobile clients still consuming REST endpoints during the transition period. Our approach followed Apollo's published federation migration playbook and we engaged Apollo's professional services team for architecture review.",
    "line_244_word_count": 55,
    "line_246_work_performed": "February to April: schema inventory and conflict resolution across 6 teams. May to July: implemented federation gateway, entity resolvers, and REST-to-GraphQL adapter layer. August to September: load testing, performance tuning, and phased rollout. Achieved 58% reduction in frontend API calls. Migration completed on schedule.",
    "line_246_word_count": 47,
    "five_question_test": {
      "q1_uncertainty": false,
      "q1_evidence": "FAIL: No technological uncertainty. REST-to-GraphQL migration is well-documented standard practice. Apollo publishes migration playbooks. This is a technical problem, not a technological uncertainty.",
      "q2_hypothesis": false,
      "q2_evidence": "FAIL: No hypotheses formulated. Team followed vendor's published migration guide step-by-step.",
      "q3_systematic": false,
      "q3_evidence": "FAIL: No systematic investigation. Standard software engineering project management, not experimental design.",
      "q4_advancement": false,
      "q4_evidence": "FAIL: No technological advancement. Used existing tools (Apollo Federation v2) exactly as documented. Result is business improvement, not technological advancement.",
      "q5_record": false,
      "q5_evidence": "FAIL: No experimental records kept. Standard project documentation (Jira tickets, PRs) — not hypothesis/result records."
    },
    "personnel": [
      {"name": "Raj Gupta", "role": "Senior Developer", "hours_sred": 800, "hours_total": 1800, "salary": 118000, "is_specified_employee": true, "ownership_percentage": 15},
      {"name": "Emily Chen", "role": "Developer", "hours_sred": 600, "hours_total": 1800, "salary": 95000, "is_specified_employee": false},
      {"name": "DevOps Contractor (TechBridge Ltd.)", "role": "Infrastructure", "hours_sred": 300, "hours_total": 300, "salary": null, "is_specified_employee": false, "is_contractor": true, "contract_value": 45000, "arms_length": true}
    ]
  }
]
```

### 2.3 Expenditures (`expenditures.json`)

```json
{
  "method": "proxy",
  "fiscal_year": "2024",
  "ympe_2024": 68500,
  "salaries": {
    "line_300_total_salary_expenditures": 730000,
    "breakdown": [
      {"name": "Dr. Anika Patel", "total_salary": 145000, "sred_portion": 112778, "project_allocation": {"P001": 96667, "P002": 16111}, "specified_employee": false, "paid_within_180_days": true},
      {"name": "James Wu", "total_salary": 112000, "sred_portion": 59111, "project_allocation": {"P001": 59111}, "specified_employee": false, "paid_within_180_days": true},
      {"name": "Carlos Mendes", "total_salary": 128000, "sred_portion": 99556, "project_allocation": {"P002": 99556}, "specified_employee": false, "paid_within_180_days": true},
      {"name": "Sarah Kim", "total_salary": 105000, "sred_portion": 23333, "project_allocation": {"P002": 23333}, "specified_employee": false, "paid_within_180_days": true},
      {"name": "Raj Gupta", "total_salary": 118000, "sred_portion": 52444, "project_allocation": {"P003": 52444}, "specified_employee": true, "ownership_percentage": 15, "paid_within_180_days": true},
      {"name": "Emily Chen", "total_salary": 95000, "sred_portion": 31667, "project_allocation": {"P003": 31667}, "specified_employee": false, "paid_within_180_days": true}
    ],
    "total_sred_salaries": 378889,
    "specified_employee_salary_included": 52444
  },
  "materials": {
    "line_360_total": 18700,
    "items": [
      {"description": "IoT sensor evaluation boards (ARM Cortex-M4 x 24)", "amount": 8400, "project": "P001", "consumed_or_transformed": "consumed", "eligible": true},
      {"description": "Cloud compute credits (GCP) for GNN training", "amount": 6800, "project": "P002", "consumed_or_transformed": "consumed", "eligible": true},
      {"description": "Office supplies and printer cartridges", "amount": 1200, "project": "GENERAL", "consumed_or_transformed": "neither", "eligible": false, "flag_reason": "Office supplies are not consumed or transformed by SR&ED. Ineligible under ITA 37(1)(a)(ii)."},
      {"description": "USB cables and adapters for test rigs", "amount": 2300, "project": "P001", "consumed_or_transformed": "consumed", "eligible": true}
    ]
  },
  "contracts": {
    "line_370_total": 117000,
    "items": [
      {"payee": "Fatima Al-Rashidi (sole proprietor)", "amount": 72000, "project": "P001", "arms_length": true, "for_sred": true, "contract_specifies_sred": true, "eligible": true, "itc_eligible_amount": 57600, "itc_note": "Arms-length contract: 100% deductible, 80% qualifies for ITC"},
      {"payee": "TechBridge Ltd.", "amount": 45000, "project": "P003", "arms_length": true, "for_sred": false, "contract_specifies_sred": false, "eligible": false, "flag_reason": "Contract does not specify SR&ED work. Project P003 is ineligible. Contract language references 'migration services' not 'experimental development'. Ineligible under ITA 37(1)(a)(i)."}
    ]
  },
  "overhead": {
    "method": "proxy",
    "proxy_base_salaries": 326445,
    "proxy_rate": 0.55,
    "proxy_amount": 179545,
    "note": "Proxy method: 55% of salary base (excluding specified employees for PPA). Not deductible but earns ITC. Specified employee Raj Gupta salary excluded from PPA base per ITA 37(9.1)."
  },
  "deliberate_errors": [
    {
      "error_id": "EXP-001",
      "category": "materials",
      "description": "Office supplies ($1,200) claimed as SR&ED materials",
      "severity": "MEDIUM",
      "rule": "Materials must be consumed or transformed by SR&ED. Office supplies are neither. CRA Policy: Materials for SR&ED (2024-01-23), Section 3.2.",
      "remediation": "Remove $1,200 from materials claim. Reduces qualified expenditures."
    },
    {
      "error_id": "EXP-002",
      "category": "contracts",
      "description": "TechBridge Ltd. contract ($45,000) on ineligible project P003",
      "severity": "HIGH",
      "rule": "Project P003 fails all five questions of the eligibility test. No expenditures on this project qualify. CRA Filing Requirements Policy (2025-01-28).",
      "remediation": "Remove entire P003 from claim. Reduces qualified expenditures by $129,111 (salaries $84,111 + contract $45,000)."
    },
    {
      "error_id": "EXP-003",
      "category": "contracts",
      "description": "TechBridge contract language does not specify SR&ED",
      "severity": "HIGH",
      "rule": "Contract must specify that work is SR&ED for expenditure to qualify. CRA Contract Expenditures for SR&ED Policy, Section 4.1.",
      "remediation": "Even if project were eligible, contract would need amendment to specify SR&ED clause."
    },
    {
      "error_id": "EXP-004",
      "category": "specified_employee",
      "description": "Raj Gupta (15% shareholder) salary not capped for PPA calculation",
      "severity": "LOW",
      "rule": "Specified employees (10%+ shareholders) salary capped at lesser of: (a) 75% of salary, or (b) 2.5x YMPE ($171,250 for 2024 YMPE $68,500) for PPA base. Raj salary $118,000 x 75% = $88,500 cap applies for PPA. However, since P003 is ineligible, this is moot.",
      "remediation": "If P003 were eligible, PPA base for Raj would be $88,500 x (800/1800) = $39,333 not $52,444. Currently moot because P003 should be removed entirely."
    }
  ]
}
```

### 2.4 Documentation Log (`documentation_log.json`)

```json
{
  "evidence_items": [
    {"id": "DOC-001", "project": "P001", "type": "project_initiation_record", "title": "PIR-2024-001: Sensor Fusion R&D Plan", "date": "2024-01-15", "format": "PDF", "contemporaneous": true},
    {"id": "DOC-002", "project": "P001", "type": "literature_review", "title": "Gap Analysis: Sub-3dB SNR Fusion Methods", "date": "2024-01-22", "format": "PDF", "contemporaneous": true},
    {"id": "DOC-003", "project": "P001", "type": "lab_notebook", "title": "Confluence: SensorFusion-R&D Space", "date_range": "2024-01-15 to 2024-11-22", "entries": 342, "format": "Digital (Confluence)", "contemporaneous": true},
    {"id": "DOC-004", "project": "P001", "type": "test_data", "title": "Experiment logs: 847 fusion experiments", "date_range": "2024-08-01 to 2024-11-15", "format": "CSV/JSON", "contemporaneous": true},
    {"id": "DOC-005", "project": "P001", "type": "technical_report", "title": "TR-2024-SF-Final: Sensor Fusion Results", "date": "2024-11-22", "format": "PDF", "contemporaneous": true},
    {"id": "DOC-006", "project": "P001", "type": "source_code", "title": "Git repo: novatech/sensor-fusion-rd", "date_range": "2024-01-20 to 2024-11-28", "commits": 287, "format": "Git", "contemporaneous": true},
    {"id": "DOC-007", "project": "P001", "type": "timesheets", "title": "Harvest time entries — Patel, Wu", "date_range": "2024-01-15 to 2024-11-30", "format": "CSV export", "contemporaneous": true},

    {"id": "DOC-008", "project": "P002", "type": "feasibility_report", "title": "FR-2024-002: Anomaly Detection Feasibility", "date": "2024-03-05", "format": "PDF", "contemporaneous": true},
    {"id": "DOC-009", "project": "P002", "type": "literature_review", "title": "LR-2024-002: GNN for Cloud Anomaly Detection", "date": "2024-03-18", "format": "PDF", "contemporaneous": true},
    {"id": "DOC-010", "project": "P002", "type": "lab_notebook", "title": "Confluence: CloudAnomaly-R&D Space", "date_range": "2024-03-01 to 2024-06-14", "entries": 89, "format": "Digital (Confluence)", "contemporaneous": true, "gap_flag": true, "gap_start": "2024-06-15", "gap_end": "2024-09-03", "gap_reason": "Team lead parental leave. No delegate assigned for documentation."},
    {"id": "DOC-011", "project": "P002", "type": "lab_notebook", "title": "Confluence: CloudAnomaly-R&D Space (resumed)", "date_range": "2024-09-04 to 2024-12-31", "entries": 67, "format": "Digital (Confluence)", "contemporaneous": true},
    {"id": "DOC-012", "project": "P002", "type": "source_code", "title": "Git repo: novatech/cloud-anomaly-gnn", "date_range": "2024-03-10 to 2024-12-28", "commits": 412, "format": "Git", "contemporaneous": true, "note": "Git commits continued during documentation gap — code exists but no experimental rationale recorded"},
    {"id": "DOC-013", "project": "P002", "type": "timesheets", "title": "Harvest time entries — Mendes, Kim, Patel", "date_range": "2024-03-01 to 2024-12-31", "format": "CSV export", "contemporaneous": true},

    {"id": "DOC-014", "project": "P003", "type": "project_plan", "title": "GraphQL Migration Project Plan", "date": "2024-02-05", "format": "Confluence page", "contemporaneous": true, "flag": "Standard project plan, not SR&ED PIR. No hypotheses, no uncertainty analysis."},
    {"id": "DOC-015", "project": "P003", "type": "jira_tickets", "title": "Jira: GQLMIG epic (47 stories)", "date_range": "2024-02-01 to 2024-09-30", "format": "Jira export", "contemporaneous": true, "flag": "Standard development tickets. No experimental design or hypothesis tracking."},
    {"id": "DOC-016", "project": "P003", "type": "timesheets", "title": "Harvest time entries — Gupta, Chen", "date_range": "2024-02-01 to 2024-09-30", "format": "CSV export", "contemporaneous": true}
  ],
  "t661_evidence_checklist": {
    "line_270_lab_notebooks": {"P001": true, "P002": "partial", "P003": false},
    "line_272_project_planning_docs": {"P001": true, "P002": true, "P003": "wrong_type"},
    "line_274_design_docs": {"P001": true, "P002": true, "P003": false},
    "line_276_test_protocols_data": {"P001": true, "P002": "partial", "P003": false},
    "line_278_photographs_videos": {"P001": false, "P002": false, "P003": false},
    "line_280_contracts_invoices": {"P001": true, "P002": true, "P003": true},
    "line_282_other": {"P001": true, "P002": true, "P003": false}
  }
}
```

### 2.5 Form T661 Simulated Data (`t661_form_data.json`)

```json
{
  "form_version": "T661 E (24)",
  "parts_status": {
    "part_1_general_info": {
      "status": "COMPLETE",
      "lines": {
        "010_corp_name": "NovaTech Solutions Inc.",
        "020_bn": "123456789RC0001",
        "030_tax_year_start": "2024-01-01",
        "040_tax_year_end": "2024-12-31",
        "050_first_time": "No",
        "060_total_claim": 3,
        "070_province": "Ontario"
      },
      "issues": []
    },
    "part_2_project_info": {
      "status": "ISSUES_FOUND",
      "section_a_fields": "See projects.json for per-project data",
      "section_b_three_questions": {
        "P001": {"line_242": "PASS", "line_244": "PASS", "line_246": "PASS"},
        "P002": {"line_242": "PASS", "line_244": "PASS", "line_246": "CAUTION — documentation gap"},
        "P003": {"line_242": "FAIL", "line_244": "FAIL", "line_246": "FAIL"}
      },
      "section_c_personnel_evidence": {
        "P001": "COMPLETE",
        "P002": "PARTIAL — 3-month documentation gap",
        "P003": "INADEQUATE — no SR&ED-type records"
      },
      "issues": [
        "P003 fails all three narrative questions. Must be removed from claim.",
        "P002 has 3-month documentation gap (lines 270-276). CRA will likely request clarification.",
        "P003 line 242 is only 55 words (limit 350). Vague, no uncertainty articulated.",
        "P003 line 244 is only 55 words (limit 700). Describes challenges, not technological uncertainties."
      ]
    },
    "part_3_expenditures": {
      "status": "ISSUES_FOUND",
      "section_a_method": "Proxy (Traditional not elected)",
      "section_b_summary": {
        "line_300_salaries": 378889,
        "line_360_materials": 18700,
        "line_370_contracts": 117000,
        "line_380_total_sr_ed_expenditures": 514589
      },
      "issues": [
        "Materials include $1,200 ineligible office supplies (line 360)",
        "Contracts include $45,000 for ineligible project P003 (line 370)",
        "Specified employee Raj Gupta salary included at full rate in PPA base"
      ]
    },
    "part_4_qualified_expenditures": {
      "status": "NOT_CALCULATED",
      "note": "Cannot finalize until Part 3 issues resolved"
    },
    "part_5_ppa": {
      "status": "ISSUES_FOUND",
      "proxy_base_before_corrections": 326445,
      "proxy_amount_before_corrections": 179545,
      "issues": [
        "PPA base includes salaries from ineligible P003. Must recalculate after removing P003."
      ]
    },
    "part_6_per_project_breakdown": {
      "status": "ISSUES_FOUND",
      "issues": ["P003 must be removed. Per-project totals need recalculation."]
    },
    "part_7_statistical_info": {
      "status": "INCOMPLETE",
      "issues": ["Total R&D personnel count not finalized"]
    },
    "part_8_checklist": {
      "status": "ISSUES_FOUND",
      "issues": [
        "Evidence checklist (lines 270-282) shows gaps for P002 and failures for P003"
      ]
    },
    "part_9_preparer": {
      "status": "WARNING",
      "preparer_name": "Greenfield SR&ED Advisory Inc.",
      "preparer_bn": "987654321RC0001",
      "billing_arrangement_code": 1,
      "billing_arrangement_text": "Contingency fee",
      "fee_percentage": 25,
      "issues": [
        "RISK FLAG: Contingency fee arrangement (Code 1). CRA uses Part 9 data for risk scoring.",
        "Contingency fee preparers have elevated audit rates per CRA's 2022 public warnings.",
        "Penalty: $1,000 if Part 9 is missing, incomplete, or inaccurate (joint preparer/claimant liability)."
      ]
    },
    "part_10_certification": {
      "status": "NOT_SIGNED",
      "issues": ["Certification cannot be completed until all issues resolved"]
    }
  }
}
```

---

## 3. CONSTANTS AND RULES (`constants.py`)

```python
# 2024 Tax Year Constants
YMPE_2024 = 68500
SPECIFIED_EMPLOYEE_PPA_CAP_MULTIPLIER = 2.5  # 2.5x YMPE for PPA base
SPECIFIED_EMPLOYEE_TOTAL_CAP_MULTIPLIER = 5.0  # 5x YMPE for total allowable
SPECIFIED_EMPLOYEE_SALARY_PERCENTAGE = 0.75  # 75% of salary

# ITC Rates (post-Budget 2025 reforms, effective for expenditures after Dec 15 2024)
ITC_CCPC_ENHANCED_RATE = 0.35  # 35% on first $6M (up from $3M)
ITC_CCPC_ENHANCED_LIMIT = 6000000  # $6M (up from $3M)
ITC_CCPC_BASE_RATE = 0.15  # 15% on expenditures above enhanced limit
ITC_CCPC_REFUNDABLE_CURRENT = 1.00  # 100% refundable on current expenditures
ITC_CCPC_REFUNDABLE_CAPITAL = 0.40  # 40% refundable on capital (restored)

# Phase-out thresholds
TAXABLE_CAPITAL_PHASEOUT_LOW = 15000000  # $15M (up from $10M)
TAXABLE_CAPITAL_PHASEOUT_HIGH = 75000000  # $75M (up from $50M)
TAXABLE_INCOME_PHASEOUT_LOW = 500000
TAXABLE_INCOME_PHASEOUT_HIGH = 800000  # Expanded range

# Proxy method
PROXY_RATE = 0.55  # 55% of salary base

# Contract rules
ARMS_LENGTH_CONTRACT_ITC_RATE = 0.80  # 80% of arm's-length contract qualifies for ITC
NON_ARMS_LENGTH_CONTRACT_ITC_RATE = 0.00  # 0% ITC (must use T1146 transfer)

# Narrative word limits (Form T661 Part 2 Section B)
LINE_242_WORD_LIMIT = 350
LINE_244_WORD_LIMIT = 700
LINE_246_WORD_LIMIT = 350

# Filing deadline
FILING_DEADLINE_MONTHS = 18  # 18 months from fiscal year end, absolute

# Provincial ITC Rates (2024 tax year)
PROVINCIAL_CREDITS = {
    "Ontario": {
        "OITC": {"rate": 0.08, "limit": 3000000, "refundable": True, "name": "Ontario Innovation Tax Credit"},
        "ORDTC": {"rate": 0.035, "limit": None, "refundable": False, "name": "Ontario R&D Tax Credit"}
    },
    "Quebec": {
        "CRIC": {"rate_first_1m": 0.30, "rate_above": 0.20, "refundable": True, "name": "Credit for R&D (new March 2025)"}
    },
    "British Columbia": {
        "BCITC": {"rate": 0.10, "limit": 3000000, "refundable": True, "name": "BC SR&ED Tax Credit"}
    },
    "Alberta": {
        "ASRDITC": {"rate_base": 0.08, "rate_incremental": 0.20, "incremental_limit": 4000000, "refundable": False, "name": "Alberta SR&ED Tax Credit"}
    },
    "Saskatchewan": {
        "SRITC": {"rate": 0.10, "limit": 1000000, "half_refundable_ccpc": True, "name": "Saskatchewan R&D Tax Credit"}
    },
    "Manitoba": {
        "MRITC": {"rate": 0.15, "refundable_portion": 0.5, "name": "Manitoba R&D Tax Credit"}
    },
    "New Brunswick": {
        "NBRITC": {"rate": 0.15, "refundable": True, "name": "NB R&D Tax Credit"}
    },
    "Nova Scotia": {
        "NSRITC": {"rate": 0.15, "refundable": True, "name": "NS R&D Tax Credit"}
    },
    "Newfoundland": {
        "NLRITC": {"rate": 0.15, "refundable": True, "name": "NL R&D Tax Credit"}
    },
    "Yukon": {
        "YRITC": {"rate": 0.15, "bonus_university": 0.05, "refundable": True, "name": "Yukon R&D Tax Credit"}
    },
    "PEI": {"note": "No provincial SR&ED credit"},
    "NWT": {"note": "No provincial SR&ED credit"},
    "Nunavut": {"note": "No provincial SR&ED credit"}
}
```

---

## 4. PAGE-BY-PAGE SPECIFICATIONS

### Page 1: Dashboard (`1_Dashboard.py`)

**Layout**: Full-width Streamlit page with sidebar for client info.

**Sidebar**:
- Company name, BN, fiscal year, CCPC status
- Province badge
- Filing deadline countdown (fiscal year end + 18 months = June 30, 2026)
- Preparer info with risk flag indicator

**Main content** (top to bottom):

1. **Overall Readiness Score**: Large circular gauge (Plotly) showing composite score 0-100.
   - Scoring formula: weighted average of subscores
     - Project Eligibility: 35% weight
     - Expenditure Accuracy: 25% weight
     - Documentation Completeness: 25% weight
     - Form Completeness: 15% weight
   - Color coding: 0-40 Red, 41-70 Amber, 71-100 Green
   - **Expected score for this demo data: ~52 (Amber)** due to P003 ineligibility, documentation gap, expenditure errors

2. **Four metric cards** in a row:
   - Projects Eligible: "2 of 3" (amber)
   - Expenditure Issues: "4 found" (red)
   - Documentation Gaps: "1 critical" (amber)
   - Form T661 Status: "7 of 10 parts ready" (amber)

3. **Issues Summary Table**: All flagged issues sorted by severity (HIGH, MEDIUM, LOW)
   - Columns: Severity | Category | Issue | Affected Project | Remediation
   - Pre-populated from the deliberate errors in the data

4. **Estimated ITC Impact**: Two-column comparison
   - "As Filed (with errors)": Show ITC with all 3 projects
   - "Corrected (recommended)": Show ITC with P003 removed and errors fixed
   - Delta showing: "Removing ineligible project reduces claim but eliminates audit risk"

### Page 2: Project Eligibility (`2_Project_Eligibility.py`)

**Purpose**: Run each project through the CRA five-question eligibility test (Northwest Hydraulic Consultants Ltd. v. The Queen, 1998).

**Layout**:

1. **Project selector**: Tabs or selectbox for P001 / P002 / P003

2. **For each project, display**:

   a. **Project header**: Title, field of science, dates, status

   b. **Five-Question Test** displayed as an interactive checklist:

   | # | Question | Result | Evidence |
   |---|----------|--------|----------|
   | 1 | Was there scientific or technological uncertainty that could not be resolved by standard practice? | PASS/FAIL | [evidence text] |
   | 2 | Did the effort involve formulating hypotheses specifically aimed at reducing or eliminating that uncertainty? | PASS/FAIL | [evidence text] |
   | 3 | Was the overall approach adopted consistent with a systematic investigation or search, including formulating and testing hypotheses by means of experiment or analysis? | PASS/FAIL | [evidence text] |
   | 4 | Was the overall approach undertaken for the purpose of achieving a scientific or technological advancement? | PASS/FAIL | [evidence text] |
   | 5 | Was a record of the hypotheses tested and results kept as the work progressed? | PASS/FAIL | [evidence text] |

   Each row should use st.expander to show detailed evidence on click.

   c. **Verdict badge**:
   - P001: ✅ ELIGIBLE (5/5 pass)
   - P002: ⚠️ ELIGIBLE WITH RISK (4/5 pass, Q5 partial fail due to documentation gap)
   - P003: ❌ INELIGIBLE (0/5 pass)

   d. **For P003 specifically**, display educational callout:
   > **Why This Project Fails**: REST-to-GraphQL migration using vendor-published guides is *standard practice*, not SR&ED. CRA distinguishes between *technological uncertainty* (solution/method unknown) and *technical problems* (existing knowledge sufficient). Complexity, novelty of application, or business value do not qualify. See CRA Guidelines on Eligibility (August 2021), Section 2.1.1.

   e. **Narrative Analysis** for each project:
   - Line 242 word count vs 350 limit (with bar)
   - Line 244 word count vs 700 limit (with bar)
   - Line 246 word count vs 350 limit (with bar)
   - Flag if any narrative is under 50% of limit (P003 is way under)
   - Quality indicators: mentions of hypotheses, experiments, measurements, uncertainties

### Page 3: Expenditures (`3_Expenditures.py`)

**Purpose**: Validate all expenditure categories against CRA rules.

**Layout**:

1. **Method indicator**: "Proxy Method Selected" with explanation tooltip

2. **Salary Analysis** (Line 300):
   - Table of all personnel with: Name, Total Salary, SR&ED Portion, % Allocation, Specified Employee flag, Paid within 180 days
   - Flag Raj Gupta as specified employee (15% shareholder > 10% threshold)
   - Show specified employee cap calculation:
     - 75% of $118,000 = $88,500
     - 2.5 x YMPE ($68,500) = $171,250
     - Cap = lesser = $88,500
     - "Moot because P003 is ineligible, but scanner catches the rule"

3. **Materials Analysis** (Line 360):
   - Table of all materials with eligibility status
   - Red flag on office supplies ($1,200): "Not consumed or transformed by SR&ED"
   - Green check on sensor boards and cloud credits

4. **Contract Analysis** (Line 370):
   - Table with: Payee, Amount, Project, Arm's Length, SR&ED Specified in Contract, ITC Eligible Amount
   - Red flag on TechBridge: "Project P003 ineligible" AND "Contract does not specify SR&ED"
   - Show 80% rule for arm's-length contracts on Fatima's contract

5. **PPA Calculation** (Proxy Method):
   - Show base salary calculation excluding specified employees
   - Apply 55% rate
   - Show corrected vs uncorrected amounts

6. **Expenditure Summary** with before/after correction:

   | Category | As Filed | Corrected | Delta |
   |----------|----------|-----------|-------|
   | Salaries (eligible) | $378,889 | $294,778 | -$84,111 |
   | Materials | $18,700 | $17,500 | -$1,200 |
   | Contracts | $117,000 | $72,000 | -$45,000 |
   | PPA (55%) | $179,545 | $162,128 | -$17,417 |
   | **Total** | **$694,134** | **$546,406** | **-$147,728** |

### Page 4: Documentation (`4_Documentation.py`)

**Purpose**: Audit the evidence trail against CRA's contemporaneous documentation expectations.

**Layout**:

1. **Timeline visualization** (Plotly Gantt or scatter):
   - X-axis: calendar months Jan-Dec 2024
   - Y-axis: projects (P001, P002, P003)
   - Dots for each evidence item, colored by type
   - **Red highlighted gap**: P002 June 15 - September 3 (80 days with no lab notebook entries)
   - Visual makes the documentation gap immediately obvious

2. **Evidence Checklist** mapped to T661 lines 270-282:

   | Line | Evidence Type | P001 | P002 | P003 |
   |------|---------------|------|------|------|
   | 270 | Lab notebooks | ✅ | ⚠️ 3-month gap | ❌ None |
   | 272 | Project planning docs | ✅ PIR | ✅ FR | ⚠️ Wrong type |
   | 274 | Design/system architecture | ✅ | ✅ | ❌ |
   | 276 | Test protocols/data | ✅ 847 experiments | ⚠️ Gap period | ❌ |
   | 278 | Photos/videos | ❌ | ❌ | ❌ |
   | 280 | Contracts/invoices | ✅ | ✅ | ✅ |
   | 282 | Other records | ✅ Git (287 commits) | ✅ Git (412 commits) | ❌ |

3. **P002 Documentation Gap Deep Dive**:
   - Callout box explaining the 80-day gap
   - Note: "Git commits continued during gap — code exists but experimental rationale was not recorded"
   - CRA guidance: "While not a statutory requirement (Abeilles v. The Queen, 2014 TCC 313), contemporaneous documentation is CRA's primary review focus"
   - Risk assessment: "CRA reviewer will likely request explanation. Recommend preparing a memo reconstructing the experimental approach during this period using git commit messages and code review comments."

4. **P003 Documentation Failure**:
   - "Project documentation consists entirely of standard software engineering artifacts (Jira tickets, PRs). No SR&ED-type records (hypotheses, experimental design, uncertainty analysis) exist."

### Page 5: Form T661 Review (`5_Form_T661_Review.py`)

**Purpose**: Walk through all 10 parts of Form T661 with completeness status.

**Layout**: Accordion/expander for each part.

For each part, show:
- Part number and title
- Status badge: COMPLETE / ISSUES FOUND / INCOMPLETE / WARNING / NOT READY
- List of specific issues (if any)
- Key line numbers and their values

**Parts to display**:

| Part | Title | Status | Key Issues |
|------|-------|--------|------------|
| 1 | General Information | ✅ COMPLETE | None |
| 2 | Project Information | ❌ ISSUES | P003 fails all questions. P002 doc gap. P003 narratives too short. |
| 3 | Expenditure Calculation | ❌ ISSUES | Ineligible materials, ineligible contract, specified employee calc |
| 4 | Qualified Expenditures for ITC | ⏸ BLOCKED | Cannot finalize until Part 3 resolved |
| 5 | Prescribed Proxy Amount | ❌ ISSUES | PPA base includes ineligible project salaries |
| 6 | Per-Project Breakdown | ❌ ISSUES | P003 must be removed |
| 7 | Statistical Information | ⚠️ INCOMPLETE | Personnel count not finalized |
| 8 | Checklist | ❌ ISSUES | Evidence gaps for P002/P003 |
| 9 | Preparer Disclosure | ⚠️ WARNING | Contingency fee risk flag |
| 10 | Certification | ⏸ NOT READY | Cannot sign until all issues resolved |

### Page 6: Risk Report (`6_Risk_Report.py`)

**Purpose**: Generate a comprehensive risk assessment with prioritized remediation plan.

**Layout**:

1. **Risk Score Breakdown** (radar chart):
   - Axes: Eligibility, Expenditures, Documentation, Narratives, Preparer Risk, Filing Timeline
   - Each scored 0-100

2. **CRA Audit Risk Factors** identified in this claim:
   - ⚠️ Contingency fee preparer (elevated audit rate per CRA 2022 warnings)
   - ⚠️ Ineligible project included (P003 — routine development claimed as SR&ED)
   - ⚠️ Documentation gap on otherwise-eligible project (P002)
   - ⚠️ Ineligible expenditures (office supplies, non-SR&ED contract)
   - ✅ Not first-time claimant (lower risk)
   - ✅ Filing well within 18-month deadline

3. **Prioritized Remediation Plan** (numbered steps):

   | Priority | Action | Impact | Effort |
   |----------|--------|--------|--------|
   | 1 | Remove Project P003 entirely from claim | HIGH — eliminates most significant audit trigger | LOW |
   | 2 | Remove $1,200 office supplies from materials | MEDIUM — removes ineligible expenditure | LOW |
   | 3 | Prepare documentation memo for P002 gap period | HIGH — preempts CRA reviewer question | MEDIUM |
   | 4 | Recalculate PPA base excluding P003 salaries | MEDIUM — ensures accurate proxy amount | LOW |
   | 5 | Consider preparer arrangement discussion | LOW — contingency fee is legal but flagged | N/A |
   | 6 | Add photos/videos to evidence for P001/P002 | LOW — nice-to-have, not required | LOW |

4. **Before/After Comparison Summary**:
   - Claim amount before corrections
   - Claim amount after corrections
   - Estimated ITC before/after
   - Audit risk level before/after (High → Low)

5. **Downloadable Report** button (generates a text summary — use st.download_button)

### Page 7: ITC Calculator (`7_ITC_Calculator.py`)

**Purpose**: Calculate federal and provincial Investment Tax Credits.

**Layout**:

1. **Input summary** (from corrected expenditures):
   - Qualified SR&ED expenditures (after removing P003 and fixing errors)
   - Corporation type: CCPC
   - Taxable capital: $8.2M (below $15M threshold — full enhanced rate available)
   - Taxable income prior year: $485,000 (below $500K threshold — full enhanced rate)
   - Province: Ontario

2. **Federal ITC Calculation**:
   ```
   Corrected Qualified Expenditures:    $546,406
   Enhanced rate (35% on first $6M):    $546,406 x 35% = $191,242
   (Expenditures below $6M limit, so all at enhanced rate)

   Refundability: 100% refundable (CCPC, current expenditures)
   Federal ITC:  $191,242 (fully refundable)
   ```

3. **Provincial ITC Calculation** (Ontario):
   ```
   Ontario Innovation Tax Credit (OITC):
   Rate: 8% refundable on first $3M qualified expenditures
   $546,406 x 8% = $43,712 (refundable)

   Ontario R&D Tax Credit (ORDTC):
   Rate: 3.5% non-refundable on all qualified expenditures
   $546,406 x 3.5% = $19,124 (non-refundable, reduces Part II tax)

   Note: Provincial credits reduce federal qualified expenditure base
   (treated as government assistance)
   ```

4. **Total Credits Summary**:

   | Credit | Amount | Refundable |
   |--------|--------|------------|
   | Federal ITC (35%) | $191,242 | Yes |
   | Ontario OITC (8%) | $43,712 | Yes |
   | Ontario ORDTC (3.5%) | $19,124 | No |
   | **Total** | **$254,078** | **$234,954 refundable** |

5. **Province selector**: Dropdown to toggle province and show different provincial credits (for demo purposes — shows breadth of tool)

6. **Comparison with uncorrected claim**: Show that the uncorrected claim would have a higher ITC number BUT the audit risk makes it likely to be denied entirely. Net expected value of corrected claim is higher.

---

## 5. SCORING ENGINE (`scoring.py`)

```python
def calculate_overall_score(projects, expenditures, documentation, form_status):
    """
    Returns 0-100 composite score.

    Subscores:
    - eligibility_score: % of projects passing 5-question test (weighted by expenditure)
    - expenditure_score: 100 - (penalty per error found)
    - documentation_score: weighted evidence checklist completion
    - form_score: % of T661 parts with COMPLETE status
    """

    # Eligibility: P001=100, P002=80 (Q5 partial), P003=0. Weighted by spend.
    # Expenditure: Start at 100, -15 per HIGH error, -10 per MEDIUM, -5 per LOW
    # Documentation: Average of evidence checklist scores across eligible projects
    # Form: Count of COMPLETE parts / 10

    # Weights
    W_ELIG = 0.35
    W_EXP = 0.25
    W_DOC = 0.25
    W_FORM = 0.15

    composite = (elig * W_ELIG + exp * W_EXP + doc * W_DOC + form * W_FORM)
    return round(composite)
```

---

## 6. UI/UX REQUIREMENTS

### Visual Design
- **Color scheme**: Dark sidebar (#1E1E2E), white main area, accent color #0066CC (IAM-Audit blue)
- **Status badges**: Use st.success, st.warning, st.error for PASS/CAUTION/FAIL
- **Typography**: Use st.header, st.subheader consistently. No custom CSS needed.

### Sidebar (persistent across all pages)
- IAM-Audit logo placeholder (text: "🔍 IAM-Audit")
- Company: NovaTech Solutions Inc.
- Fiscal Year: 2024
- Province: Ontario
- Overall Score: [gauge mini]
- Filing Deadline: June 30, 2026
- Days Remaining: [calculated dynamically]

### Streamlit Configuration
```python
st.set_page_config(
    page_title="IAM-Audit | SR&ED Readiness Scanner",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### Interactive Elements
- All projects should be selectable/filterable
- Expenditure tables should be sortable
- ITC calculator province dropdown should update calculations live
- Risk report should have a download button generating a text summary
- Use st.expander liberally for detailed CRA rule explanations (keep main view clean)
- Use st.metric for key numbers with delta indicators
- Use st.tabs for project-level views

---

## 7. KEY CRA RULES THE SCANNER MUST ENFORCE

These rules drive the scanning logic. Each must be codified and referenced in the UI.

| Rule ID | Rule | Source | How Scanner Catches It |
|---------|------|--------|----------------------|
| R01 | All five questions must be answered YES for project to be eligible | Northwest Hydraulic (1998), CRA Guidelines on Eligibility (2021) | Five-question test per project |
| R02 | Technological uncertainty ≠ technical problem | CRA Guidelines on Eligibility, Section 2.1.1 | Narrative analysis for P003 |
| R03 | Materials must be consumed or transformed by SR&ED | ITA 37(1)(a)(ii), CRA Materials Policy (2024-01-23) | Materials eligibility check |
| R04 | Contract must specify SR&ED work | CRA Contract Expenditures Policy, Section 4.1 | Contract clause check |
| R05 | Arm's-length contracts: 80% qualifies for ITC | ITA 127(9), definition of qualified expenditure | ITC calculation |
| R06 | Specified employee (10%+ shareholder): salary capped for PPA | ITA 37(9.1), CRA Salary/Wages Policy (2025-01-28) | PPA calculation |
| R07 | PPA cap: lesser of 75% salary or 2.5x YMPE | ITA 37(9.1)(a) | Specified employee check |
| R08 | Proxy method: 55% of salary base, not deductible but earns ITC | ITA 37(8) | PPA calculation |
| R09 | Filing deadline: 18 months from fiscal year end (absolute) | ITA 37(11) | Deadline countdown |
| R10 | Part 9 preparer disclosure mandatory ($1,000 penalty) | ITA 162(5.2) | Form completeness check |
| R11 | Contingency fee preparers face elevated CRA scrutiny | CRA public warnings (April 2022, October 2022) | Risk scoring |
| R12 | Contemporaneous documentation is CRA's primary review focus | CRA Guidelines on Eligibility, Section 6 | Documentation audit |
| R13 | CCPC enhanced ITC rate: 35% on first $6M | ITA 127.1(2), Budget 2025 | ITC calculation |
| R14 | Provincial credits reduce federal qualified expenditure base | ITA 127(9), definition of government assistance | ITC calculation |
| R15 | Line 242 limit 350 words, Line 244 limit 700 words, Line 246 limit 350 words | T661 form instructions | Narrative word count check |
| R16 | Salaries must be paid within 180 days of fiscal year end | ITA 78(4) | Salary eligibility check |
| R17 | Capital expenditures restored for property acquired after Dec 15, 2024 | Budget 2025, effective date provision | ITC calculation (informational) |

---

## 8. DATA FLOW

```
[JSON Data Files] → [Load into session_state on app start]
                          ↓
                   [rules.py validates each data element]
                          ↓
                   [scoring.py computes subscores and composite]
                          ↓
                   [Each page reads from session_state]
                   [Each page renders validated data with flags]
                          ↓
                   [Risk Report aggregates all findings]
                   [ITC Calculator uses corrected numbers]
```

All data is loaded once via a `load_data()` function in app.py and stored in `st.session_state`. Pages read from session state. No database, no API calls, no file uploads in this POC.

---

## 9. FILE STRUCTURE AND DEPENDENCIES

### requirements.txt
```
streamlit>=1.30.0
plotly>=5.18.0
pandas>=2.1.0
```

### Run command
```bash
streamlit run app.py
```

### Folder structure to create
```
sred_scanner/
├── app.py
├── requirements.txt
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Project_Eligibility.py
│   ├── 3_Expenditures.py
│   ├── 4_Documentation.py
│   ├── 5_Form_T661_Review.py
│   ├── 6_Risk_Report.py
│   └── 7_ITC_Calculator.py
├── data/
│   ├── client_profile.json
│   ├── projects.json
│   ├── expenditures.json
│   ├── documentation_log.json
│   └── t661_form_data.json
└── utils/
    ├── __init__.py
    ├── scoring.py
    ├── rules.py
    ├── constants.py
    └── formatters.py
```

---

## 10. DEMO NARRATIVE

When presenting this demo, the story arc is:

1. **Dashboard** reveals overall score of ~52 (Amber). Immediate attention drawn to 4 expenditure issues and 1 critical documentation gap.

2. **Project Eligibility** shows the scanner catching that P003 (GraphQL migration) is routine software engineering, not SR&ED. The five-question test makes the failure systematic and defensible. Educational callout teaches the CPA about the technological uncertainty vs technical problem distinction.

3. **Expenditures** reveals four specific errors: ineligible office supplies, contract on ineligible project, missing SR&ED contract language, and specified employee cap issue. Each error cites the specific CRA policy.

4. **Documentation** timeline makes the P002 gap visually obvious. Scanner recommends proactive memo preparation rather than waiting for CRA to ask.

5. **Form T661 Review** walks through all 10 parts, showing that issues cascade (Part 2 failures affect Parts 3, 4, 5, 6). Part 9 preparer disclosure flags the contingency fee arrangement.

6. **Risk Report** prioritizes remediation: remove P003 first (biggest impact, least effort), then fix expenditure details, then address documentation gap.

7. **ITC Calculator** shows the counterintuitive result: removing P003 *reduces* the claim amount but *increases* the expected value because the corrected claim has near-zero audit risk while the uncorrected claim has high probability of full denial.

**Key sales message**: "The scanner found $147,728 in ineligible expenditures across 4 categories, a 3-month documentation gap that would trigger CRA review, and an entire project that fails the eligibility test. A human reviewer would need 6-8 hours to catch all of this. The scanner did it in seconds, citing specific CRA policies and line numbers."

---

## 11. IMPORTANT IMPLEMENTATION NOTES

1. **All data is synthetic**. Company name, people, projects are fictional. But all CRA rules, line numbers, word limits, ITC rates, YMPE values, and policy references are real and accurate as of January 2025.

2. **No AI/LLM calls in the POC**. The "scanning" is rule-based logic comparing data fields against CRA requirements. The demo simulates what IAM-Audit's compiler-based analysis would produce.

3. **The deliberate errors are the product**. The value is in the scanner catching things a human might miss: the ineligible project that "looks like" R&D, the office supplies buried in a materials list, the contract missing an SR&ED clause, the 3-month documentation gap.

4. **Every flag must cite a specific CRA source**: policy name, ITA section, or form line number. This is what differentiates IAM-Audit from generic checklist tools.

5. **The ITC calculator should handle province switching** even though the client is in Ontario. This demonstrates the tool's multi-jurisdictional capability for the demo.

6. **Use st.expander for CRA rule explanations** so the main view stays clean for executives while CPAs can drill into the regulatory detail.

7. **Corrected vs uncorrected comparison** is the most powerful demo element. Show that removing bad claims increases expected value.