import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.formatters import fmt_currency
from utils.constants import (
    YMPE_2024, SPECIFIED_EMPLOYEE_SALARY_PERCENTAGE,
    SPECIFIED_EMPLOYEE_PPA_CAP_MULTIPLIER, PROXY_RATE,
    ARMS_LENGTH_CONTRACT_ITC_RATE,
)
from utils.scoring import calculate_corrected_expenditures, calculate_uncorrected_expenditures
from utils.data_loader import ensure_data_loaded

ensure_data_loaded()

expenditures = st.session_state.expenditures

st.header("Expenditure Analysis")

# Method indicator
st.info(
    "**Method: Proxy (Traditional not elected)**\n\n"
    "The proxy method calculates overhead as 55% of the salary base. "
    "This amount is not deductible as a current expense but qualifies for ITC. "
    "Source: ITA 37(8)."
)

st.divider()

# --- Salary Analysis (Line 300) ---
st.subheader("Salary Analysis (Line 300)")

salary_data = []
for s in expenditures["salaries"]["breakdown"]:
    pct = s["sred_portion"] / s["total_salary"] * 100 if s["total_salary"] > 0 else 0
    projects = ", ".join(s["project_allocation"].keys())
    row = {
        "Name": s["name"],
        "Total Salary": fmt_currency(s["total_salary"]),
        "SR&ED Portion": fmt_currency(s["sred_portion"]),
        "% Allocation": f"{pct:.1f}%",
        "Projects": projects,
        "Specified Employee": "⚠️ Yes" if s["specified_employee"] else "No",
        "Paid ≤180 Days": "✅" if s["paid_within_180_days"] else "❌",
    }
    salary_data.append(row)

df_salary = pd.DataFrame(salary_data)
st.dataframe(df_salary, use_container_width=True, hide_index=True)

st.metric("Total SR&ED Salaries (Line 300)", fmt_currency(expenditures["salaries"]["total_sred_salaries"]))

# Specified Employee Flag
st.divider()
st.subheader("Specified Employee Analysis")

for s in expenditures["salaries"]["breakdown"]:
    if s["specified_employee"]:
        cap_75 = s["total_salary"] * SPECIFIED_EMPLOYEE_SALARY_PERCENTAGE
        cap_ympe = YMPE_2024 * SPECIFIED_EMPLOYEE_PPA_CAP_MULTIPLIER
        actual_cap = min(cap_75, cap_ympe)

        st.warning(f"**{s['name']}** — Specified Employee ({s.get('ownership_percentage', 'N/A')}% shareholder)")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("75% of Salary", fmt_currency(cap_75))
        with col2:
            st.metric(f"2.5x YMPE ({fmt_currency(YMPE_2024)})", fmt_currency(cap_ympe))
        with col3:
            st.metric("PPA Cap (lesser of)", fmt_currency(actual_cap))

        with st.expander("Rule Detail"):
            st.markdown(
                f"- 75% of ${s['total_salary']:,} = ${cap_75:,.0f}\n"
                f"- 2.5 x YMPE (${YMPE_2024:,}) = ${cap_ympe:,.0f}\n"
                f"- Cap = lesser = ${actual_cap:,.0f}\n"
                f"- SR&ED allocation: ${s['sred_portion']:,} (on project {''.join(s['project_allocation'].keys())})\n\n"
                "**Note:** This is currently moot because P003 is ineligible and should be removed "
                "entirely from the claim. However, the scanner catches this rule proactively.\n\n"
                "*Source: ITA 37(9.1), CRA Salary/Wages Policy (2025-01-28)*"
            )

st.divider()

# --- Materials Analysis (Line 360) ---
st.subheader("Materials Analysis (Line 360)")

mat_data = []
for m in expenditures["materials"]["items"]:
    status = "✅ Eligible" if m["eligible"] else "❌ Ineligible"
    row = {
        "Description": m["description"],
        "Amount": fmt_currency(m["amount"]),
        "Project": m["project"],
        "Consumed/Transformed": m["consumed_or_transformed"],
        "Status": status,
    }
    mat_data.append(row)

df_mat = pd.DataFrame(mat_data)
st.dataframe(df_mat, use_container_width=True, hide_index=True)

for m in expenditures["materials"]["items"]:
    if not m["eligible"]:
        st.error(
            f"**Flag: {m['description']}** ({fmt_currency(m['amount'])})\n\n"
            f"{m.get('flag_reason', 'Ineligible material.')}\n\n"
            "*Source: ITA 37(1)(a)(ii), CRA Materials Policy (2024-01-23), Section 3.2*"
        )

st.metric("Total Materials (Line 360)", fmt_currency(expenditures["materials"]["line_360_total"]))

st.divider()

# --- Contract Analysis (Line 370) ---
st.subheader("Contract Analysis (Line 370)")

contract_data = []
for c in expenditures["contracts"]["items"]:
    status = "✅ Eligible" if c["eligible"] else "❌ Ineligible"
    itc_amt = c.get("itc_eligible_amount", 0) if c["eligible"] else 0
    row = {
        "Payee": c["payee"],
        "Amount": fmt_currency(c["amount"]),
        "Project": c["project"],
        "Arm's Length": "Yes" if c["arms_length"] else "No",
        "SR&ED in Contract": "Yes" if c["contract_specifies_sred"] else "❌ No",
        "ITC Eligible (80%)": fmt_currency(itc_amt),
        "Status": status,
    }
    contract_data.append(row)

df_contract = pd.DataFrame(contract_data)
st.dataframe(df_contract, use_container_width=True, hide_index=True)

for c in expenditures["contracts"]["items"]:
    if c["eligible"]:
        st.success(
            f"**{c['payee']}**: Arm's-length contract. 100% deductible, "
            f"80% qualifies for ITC = {fmt_currency(c.get('itc_eligible_amount', 0))}. "
            "*Source: ITA 127(9)*"
        )
    else:
        st.error(
            f"**Flag: {c['payee']}** ({fmt_currency(c['amount'])})\n\n"
            f"{c.get('flag_reason', 'Ineligible contract.')}\n\n"
            "*Source: CRA Contract Expenditures for SR&ED Policy, Section 4.1*"
        )

st.metric("Total Contracts (Line 370)", fmt_currency(expenditures["contracts"]["line_370_total"]))

st.divider()

# --- PPA Calculation ---
st.subheader("Prescribed Proxy Amount (PPA) — Proxy Method")

overhead = expenditures["overhead"]
st.markdown(
    f"- **PPA Base (salaries excl. specified employees for PPA):** {fmt_currency(overhead['proxy_base_salaries'])}\n"
    f"- **Proxy Rate:** {PROXY_RATE:.0%}\n"
    f"- **PPA Amount:** {fmt_currency(overhead['proxy_amount'])}\n\n"
    f"*{overhead['note']}*"
)

st.divider()

# --- Expenditure Summary ---
st.subheader("Expenditure Summary: Before vs After Correction")

uncorrected = calculate_uncorrected_expenditures(expenditures)
corrected = calculate_corrected_expenditures(expenditures)

summary_data = {
    "Category": ["Salaries (eligible)", "Materials", "Contracts", "PPA (55%)", "**Total**"],
    "As Filed": [
        fmt_currency(uncorrected["salaries"]),
        fmt_currency(uncorrected["materials"]),
        fmt_currency(uncorrected["contracts"]),
        fmt_currency(uncorrected["ppa"]),
        fmt_currency(uncorrected["total"]),
    ],
    "Corrected": [
        fmt_currency(corrected["salaries"]),
        fmt_currency(corrected["materials"]),
        fmt_currency(corrected["contracts"]),
        fmt_currency(corrected["ppa"]),
        fmt_currency(corrected["total"]),
    ],
    "Delta": [
        fmt_currency(corrected["salaries"] - uncorrected["salaries"]),
        fmt_currency(corrected["materials"] - uncorrected["materials"]),
        fmt_currency(corrected["contracts"] - uncorrected["contracts"]),
        fmt_currency(corrected["ppa"] - uncorrected["ppa"]),
        fmt_currency(corrected["total"] - uncorrected["total"]),
    ],
}

df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

st.info(
    f"**Net Reduction:** {fmt_currency(uncorrected['total'] - corrected['total'])} in qualified expenditures "
    "after removing ineligible project P003 and correcting expenditure errors."
)
