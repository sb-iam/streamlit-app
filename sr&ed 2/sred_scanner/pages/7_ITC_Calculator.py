import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.formatters import fmt_currency
from utils.constants import (
    ITC_CCPC_ENHANCED_RATE,
    ITC_CCPC_ENHANCED_LIMIT,
    ITC_CCPC_BASE_RATE,
    TAXABLE_CAPITAL_PHASEOUT_LOW,
    TAXABLE_CAPITAL_PHASEOUT_HIGH,
    TAXABLE_INCOME_PHASEOUT_LOW,
    TAXABLE_INCOME_PHASEOUT_HIGH,
    ARMS_LENGTH_CONTRACT_ITC_RATE,
    PROVINCIAL_CREDITS,
)
from utils.scoring import calculate_corrected_expenditures, calculate_uncorrected_expenditures
from utils.data_loader import ensure_data_loaded

ensure_data_loaded()

client = st.session_state.client_profile
expenditures = st.session_state.expenditures

corrected = calculate_corrected_expenditures(expenditures)
uncorrected = calculate_uncorrected_expenditures(expenditures)

st.header("Investment Tax Credit (ITC) Calculator")

st.divider()

# --- Input Summary ---
st.subheader("Input Summary (Corrected Expenditures)")

col1, col2 = st.columns(2)
with col1:
    st.metric("Qualified SR&ED Expenditures", fmt_currency(corrected["total"]))
    st.metric("Corporation Type", client["corporation_type"])
    st.metric("Taxable Capital", fmt_currency(client["taxable_capital"]))
with col2:
    st.metric("Taxable Income (Prior Year)", fmt_currency(client["taxable_income_prior_year"]))
    st.metric("Province", client["province"])
    st.metric("First-Time Claimant", "No" if not client["first_time_claimant"] else "Yes")

# Phase-out check
st.divider()
st.subheader("Enhanced Rate Eligibility Check")

cap_ok = client["taxable_capital"] < TAXABLE_CAPITAL_PHASEOUT_LOW
income_ok = client["taxable_income_prior_year"] < TAXABLE_INCOME_PHASEOUT_LOW

col_cap, col_inc = st.columns(2)
with col_cap:
    if cap_ok:
        st.success(
            f"**Taxable Capital:** {fmt_currency(client['taxable_capital'])} < "
            f"{fmt_currency(TAXABLE_CAPITAL_PHASEOUT_LOW)} threshold\n\n"
            "Full enhanced rate available."
        )
    else:
        st.warning(f"**Taxable Capital:** {fmt_currency(client['taxable_capital'])} exceeds phase-out threshold.")

with col_inc:
    if income_ok:
        st.success(
            f"**Taxable Income:** {fmt_currency(client['taxable_income_prior_year'])} < "
            f"{fmt_currency(TAXABLE_INCOME_PHASEOUT_LOW)} threshold\n\n"
            "Full enhanced rate available."
        )
    else:
        st.warning(f"**Taxable Income:** {fmt_currency(client['taxable_income_prior_year'])} exceeds phase-out threshold.")

st.divider()

# --- Federal ITC Calculation ---
st.subheader("Federal ITC Calculation")

qualified = corrected["total"]

if qualified <= ITC_CCPC_ENHANCED_LIMIT:
    federal_itc = round(qualified * ITC_CCPC_ENHANCED_RATE)
    st.markdown(f"""
```
Corrected Qualified Expenditures:    {fmt_currency(qualified)}
Enhanced rate (35% on first $6M):    {fmt_currency(qualified)} x 35% = {fmt_currency(federal_itc)}
(Expenditures below $6M limit, so all at enhanced rate)

Refundability: 100% refundable (CCPC, current expenditures)
Federal ITC:  {fmt_currency(federal_itc)} (fully refundable)
```
""")
else:
    enhanced_portion = round(ITC_CCPC_ENHANCED_LIMIT * ITC_CCPC_ENHANCED_RATE)
    base_portion = round((qualified - ITC_CCPC_ENHANCED_LIMIT) * ITC_CCPC_BASE_RATE)
    federal_itc = enhanced_portion + base_portion
    st.markdown(f"""
```
Corrected Qualified Expenditures:    {fmt_currency(qualified)}
Enhanced rate (35% on first $6M):    {fmt_currency(ITC_CCPC_ENHANCED_LIMIT)} x 35% = {fmt_currency(enhanced_portion)}
Base rate (15% on remainder):        {fmt_currency(qualified - ITC_CCPC_ENHANCED_LIMIT)} x 15% = {fmt_currency(base_portion)}

Federal ITC:  {fmt_currency(federal_itc)}
```
""")

st.divider()

# --- Provincial ITC Calculation ---
st.subheader("Provincial ITC Calculation")

# Province selector for demo
selected_province = st.selectbox(
    "Select Province (demo — switch to see different provincial credits)",
    options=list(PROVINCIAL_CREDITS.keys()),
    index=list(PROVINCIAL_CREDITS.keys()).index(client["province"]),
)

prov_credits = PROVINCIAL_CREDITS.get(selected_province, {})

if "note" in prov_credits:
    st.info(f"**{selected_province}:** {prov_credits['note']}")
    provincial_total = 0
    provincial_refundable = 0
    prov_rows = []
else:
    prov_rows = []
    provincial_total = 0
    provincial_refundable = 0

    for credit_code, credit_info in prov_credits.items():
        if credit_code == "note":
            continue

        name = credit_info["name"]

        # Calculate based on credit structure
        if "rate" in credit_info:
            rate = credit_info["rate"]
            limit = credit_info.get("limit")
            base = min(qualified, limit) if limit else qualified
            amount = round(base * rate)
            refundable = credit_info.get("refundable", False)

            st.markdown(f"""
**{name} ({credit_code}):**
```
Rate: {rate:.1%} {'refundable' if refundable else 'non-refundable'}{f' on first {fmt_currency(limit)}' if limit else ''} qualified expenditures
{fmt_currency(base)} x {rate:.1%} = {fmt_currency(amount)}
```
""")
            prov_rows.append({
                "Credit": f"{name} ({credit_code})",
                "Amount": amount,
                "Refundable": "Yes" if refundable else "No",
            })
            provincial_total += amount
            if refundable:
                provincial_refundable += amount

        elif "rate_first_1m" in credit_info:
            # Quebec-style tiered
            first_1m = min(qualified, 1000000)
            above = max(0, qualified - 1000000)
            amount_1 = round(first_1m * credit_info["rate_first_1m"])
            amount_2 = round(above * credit_info["rate_above"])
            amount = amount_1 + amount_2
            refundable = credit_info.get("refundable", False)

            st.markdown(f"""
**{name} ({credit_code}):**
```
First $1M: {fmt_currency(first_1m)} x {credit_info['rate_first_1m']:.0%} = {fmt_currency(amount_1)}
Above $1M: {fmt_currency(above)} x {credit_info['rate_above']:.0%} = {fmt_currency(amount_2)}
Total: {fmt_currency(amount)}
```
""")
            prov_rows.append({
                "Credit": f"{name} ({credit_code})",
                "Amount": amount,
                "Refundable": "Yes" if refundable else "No",
            })
            provincial_total += amount
            if refundable:
                provincial_refundable += amount

        elif "rate_base" in credit_info:
            # Alberta-style base + incremental
            base_amount = round(qualified * credit_info["rate_base"])
            inc_limit = credit_info.get("incremental_limit", 0)
            inc_base = min(qualified, inc_limit)
            inc_amount = round(inc_base * credit_info.get("rate_incremental", 0))
            amount = base_amount + inc_amount
            refundable = credit_info.get("refundable", False)

            st.markdown(f"""
**{name} ({credit_code}):**
```
Base: {fmt_currency(qualified)} x {credit_info['rate_base']:.0%} = {fmt_currency(base_amount)}
Incremental: {fmt_currency(inc_base)} x {credit_info['rate_incremental']:.0%} = {fmt_currency(inc_amount)}
Total: {fmt_currency(amount)}
```
""")
            prov_rows.append({
                "Credit": f"{name} ({credit_code})",
                "Amount": amount,
                "Refundable": "Yes" if refundable else "No",
            })
            provincial_total += amount
            if refundable:
                provincial_refundable += amount

st.divider()

# --- Total Credits Summary ---
st.subheader("Total Credits Summary")

summary_rows = [
    {"Credit": f"Federal ITC (35%)", "Amount": fmt_currency(federal_itc), "Refundable": "Yes"},
]
for row in prov_rows:
    summary_rows.append({
        "Credit": row["Credit"],
        "Amount": fmt_currency(row["Amount"]),
        "Refundable": row["Refundable"],
    })

total_credits = federal_itc + provincial_total
total_refundable = federal_itc + provincial_refundable

summary_rows.append({
    "Credit": "**TOTAL**",
    "Amount": fmt_currency(total_credits),
    "Refundable": fmt_currency(total_refundable) + " refundable",
})

df_summary = pd.DataFrame(summary_rows)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

st.info(
    "**Note:** Provincial credits reduce the federal qualified expenditure base "
    "(treated as government assistance under ITA 127(9)). The federal ITC shown above "
    "does not yet account for this reduction. In practice, the net federal ITC would be "
    "slightly lower after the provincial credit offset."
)

st.divider()

# --- Comparison with Uncorrected ---
st.subheader("Corrected vs Uncorrected Claim Comparison")

uncorrected_itc = round(uncorrected["total"] * ITC_CCPC_ENHANCED_RATE)

col_unc, col_cor = st.columns(2)

with col_unc:
    st.markdown("### Uncorrected (As Filed)")
    st.metric("Qualified Expenditures", fmt_currency(uncorrected["total"]))
    st.metric("Federal ITC (35%)", fmt_currency(uncorrected_itc))
    st.error("**Audit Risk: HIGH**")
    st.markdown(
        "The uncorrected claim includes an ineligible project (P003) and several expenditure errors. "
        "CRA review would likely result in partial or full denial of the claim, "
        "potentially triggering a broader audit of the company's SR&ED history."
    )

with col_cor:
    st.markdown("### Corrected (Recommended)")
    st.metric(
        "Qualified Expenditures",
        fmt_currency(corrected["total"]),
        delta=fmt_currency(corrected["total"] - uncorrected["total"]),
    )
    st.metric(
        "Federal ITC (35%)",
        fmt_currency(federal_itc),
        delta=fmt_currency(federal_itc - uncorrected_itc),
    )
    st.success("**Audit Risk: LOW**")
    st.markdown(
        "The corrected claim removes ineligible expenditures and projects. "
        "While the nominal amount is lower, the expected value is higher because "
        "the claim is defensible and likely to be approved in full."
    )

st.info(
    f"**Key Insight:** The corrected claim is {fmt_currency(uncorrected['total'] - corrected['total'])} lower, "
    f"but the ITC difference is only {fmt_currency(uncorrected_itc - federal_itc)}. "
    "Given that the uncorrected claim has a high probability of denial upon CRA review, "
    "the expected value of the corrected claim significantly exceeds the uncorrected version."
)
