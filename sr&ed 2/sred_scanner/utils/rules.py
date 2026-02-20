"""CRA rule definitions for SR&ED claim validation."""

FIVE_QUESTIONS = [
    {
        "id": "Q1",
        "key": "q1_uncertainty",
        "evidence_key": "q1_evidence",
        "question": "Was there scientific or technological uncertainty that could not be resolved by standard practice?",
        "source": "Northwest Hydraulic Consultants Ltd. v. The Queen (1998); CRA Guidelines on Eligibility (2021), Section 2.1"
    },
    {
        "id": "Q2",
        "key": "q2_hypothesis",
        "evidence_key": "q2_evidence",
        "question": "Did the effort involve formulating hypotheses specifically aimed at reducing or eliminating that uncertainty?",
        "source": "CRA Guidelines on Eligibility (2021), Section 2.2"
    },
    {
        "id": "Q3",
        "key": "q3_systematic",
        "evidence_key": "q3_evidence",
        "question": "Was the overall approach adopted consistent with a systematic investigation or search, including formulating and testing hypotheses by means of experiment or analysis?",
        "source": "CRA Guidelines on Eligibility (2021), Section 2.3"
    },
    {
        "id": "Q4",
        "key": "q4_advancement",
        "evidence_key": "q4_evidence",
        "question": "Was the overall approach undertaken for the purpose of achieving a scientific or technological advancement?",
        "source": "CRA Guidelines on Eligibility (2021), Section 2.4"
    },
    {
        "id": "Q5",
        "key": "q5_record",
        "evidence_key": "q5_evidence",
        "question": "Was a record of the hypotheses tested and results kept as the work progressed?",
        "source": "CRA Guidelines on Eligibility (2021), Section 6"
    },
]

CRA_RULES = {
    "R01": {
        "title": "Five-Question Eligibility Test",
        "description": "All five questions must be answered YES for project to be eligible.",
        "source": "Northwest Hydraulic (1998), CRA Guidelines on Eligibility (2021)"
    },
    "R02": {
        "title": "Technological Uncertainty vs Technical Problem",
        "description": "Technological uncertainty (solution/method unknown) differs from technical problems (existing knowledge sufficient). Complexity, novelty of application, or business value do not qualify.",
        "source": "CRA Guidelines on Eligibility, Section 2.1.1"
    },
    "R03": {
        "title": "Materials Eligibility",
        "description": "Materials must be consumed or transformed by SR&ED to be eligible.",
        "source": "ITA 37(1)(a)(ii), CRA Materials Policy (2024-01-23), Section 3.2"
    },
    "R04": {
        "title": "Contract SR&ED Specification",
        "description": "Contract must specify that work is SR&ED for expenditure to qualify.",
        "source": "CRA Contract Expenditures for SR&ED Policy, Section 4.1"
    },
    "R05": {
        "title": "Arm's-Length Contract ITC Rate",
        "description": "Arm's-length contracts: 100% deductible, 80% qualifies for ITC.",
        "source": "ITA 127(9), definition of qualified expenditure"
    },
    "R06": {
        "title": "Specified Employee Salary Cap",
        "description": "Specified employee (10%+ shareholder): salary capped for PPA at lesser of 75% salary or 2.5x YMPE.",
        "source": "ITA 37(9.1), CRA Salary/Wages Policy (2025-01-28)"
    },
    "R07": {
        "title": "PPA Cap Calculation",
        "description": "PPA cap for specified employees: lesser of 75% of salary or 2.5x YMPE.",
        "source": "ITA 37(9.1)(a)"
    },
    "R08": {
        "title": "Proxy Method Rate",
        "description": "Proxy method: 55% of salary base, not deductible but earns ITC.",
        "source": "ITA 37(8)"
    },
    "R09": {
        "title": "Filing Deadline",
        "description": "Filing deadline: 18 months from fiscal year end (absolute, no extensions).",
        "source": "ITA 37(11)"
    },
    "R10": {
        "title": "Preparer Disclosure",
        "description": "Part 9 preparer disclosure mandatory. $1,000 penalty if missing or inaccurate.",
        "source": "ITA 162(5.2)"
    },
    "R11": {
        "title": "Contingency Fee Preparer Risk",
        "description": "Contingency fee preparers face elevated CRA scrutiny and higher audit rates.",
        "source": "CRA public warnings (April 2022, October 2022)"
    },
    "R12": {
        "title": "Contemporaneous Documentation",
        "description": "Contemporaneous documentation is CRA's primary review focus. While not a statutory requirement (Abeilles v. The Queen, 2014 TCC 313), gaps trigger CRA requests.",
        "source": "CRA Guidelines on Eligibility, Section 6"
    },
    "R13": {
        "title": "CCPC Enhanced ITC Rate",
        "description": "CCPC enhanced ITC rate: 35% on first $6M of qualified expenditures.",
        "source": "ITA 127.1(2), Budget 2025"
    },
    "R14": {
        "title": "Provincial Credits as Government Assistance",
        "description": "Provincial credits reduce federal qualified expenditure base (treated as government assistance).",
        "source": "ITA 127(9), definition of government assistance"
    },
    "R15": {
        "title": "Narrative Word Limits",
        "description": "Line 242 limit 350 words, Line 244 limit 700 words, Line 246 limit 350 words.",
        "source": "T661 form instructions"
    },
    "R16": {
        "title": "Salary Payment Deadline",
        "description": "Salaries must be paid within 180 days of fiscal year end to be eligible.",
        "source": "ITA 78(4)"
    },
    "R17": {
        "title": "Capital Expenditures Restored",
        "description": "Capital expenditures restored for property acquired after Dec 15, 2024.",
        "source": "Budget 2025, effective date provision"
    },
}
