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
