import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.scoring import (
    calculate_overall_score,
    get_all_issues,
    calculate_corrected_expenditures,
    calculate_uncorrected_expenditures,
)
from utils.formatters import fmt_currency
from utils.constants import ITC_CCPC_ENHANCED_RATE
from utils.data_loader import ensure_data_loaded

ensure_data_loaded()

projects = st.session_state.projects
expenditures = st.session_state.expenditures
documentation = st.session_state.documentation
form_data = st.session_state.t661_form
client = st.session_state.client_profile

overall_score, subscores = calculate_overall_score(projects, expenditures, documentation, form_data)

st.header("Risk Assessment & Remediation Plan")

st.divider()

# --- Radar Chart ---
st.subheader("Risk Score Breakdown")

# Calculate additional scores
# Narrative score
narrative_scores = []
for p in projects:
    if p["eligibility_strength"] != "INELIGIBLE":
        wc_242 = p["line_242_word_count"] / 350 * 100
        wc_244 = p["line_244_word_count"] / 700 * 100
        wc_246 = p["line_246_word_count"] / 350 * 100
        narrative_scores.append(min(100, (wc_242 + wc_244 + wc_246) / 3))
narrative_score = round(sum(narrative_scores) / len(narrative_scores)) if narrative_scores else 0

# Preparer risk score
preparer_score = 60 if client["preparer"]["billing_arrangement"] == 1 else 100

# Filing timeline score
from datetime import datetime, timedelta
fiscal_end = datetime.strptime(client["fiscal_year_end"], "%Y-%m-%d")
filing_deadline = fiscal_end + timedelta(days=18 * 30)
days_remaining = (filing_deadline - datetime.now()).days
filing_score = min(100, max(0, days_remaining / 5.4))  # 540 days = 100

categories = ["Eligibility", "Expenditures", "Documentation", "Narratives", "Preparer Risk", "Filing Timeline"]
values = [
    subscores["eligibility"],
    subscores["expenditure"],
    subscores["documentation"],
    narrative_score,
    preparer_score,
    round(filing_score),
]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=values + [values[0]],
    theta=categories + [categories[0]],
    fill="toself",
    fillcolor="rgba(0, 102, 204, 0.2)",
    line=dict(color="#0066CC", width=2),
    name="Current Score",
))
fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100]),
    ),
    showlegend=False,
    height=400,
    margin=dict(t=40, b=40, l=60, r=60),
)
st.plotly_chart(fig, use_container_width=True)

# Score table
score_df = pd.DataFrame({
    "Category": categories,
    "Score": values,
    "Status": ["🟢 Good" if v >= 70 else "🟡 Moderate" if v >= 40 else "🔴 Poor" for v in values],
})
st.dataframe(score_df, use_container_width=True, hide_index=True)

st.divider()

# --- CRA Audit Risk Factors ---
st.subheader("CRA Audit Risk Factors")

risk_factors = [
    ("⚠️", "Contingency fee preparer (elevated audit rate per CRA 2022 warnings)", "MEDIUM"),
    ("⚠️", "Ineligible project included (P003 — routine development claimed as SR&ED)", "HIGH"),
    ("⚠️", "Documentation gap on otherwise-eligible project (P002 — 80 days)", "HIGH"),
    ("⚠️", "Ineligible expenditures (office supplies $1,200, non-SR&ED contract $45,000)", "MEDIUM"),
    ("✅", "Not first-time claimant (lower risk profile)", "LOW"),
    ("✅", f"Filing well within 18-month deadline ({days_remaining} days remaining)", "LOW"),
]

for icon, description, severity in risk_factors:
    if icon == "⚠️":
        st.warning(f"{icon} **[{severity}]** {description}")
    else:
        st.success(f"{icon} **[{severity}]** {description}")

st.divider()

# --- Prioritized Remediation Plan ---
st.subheader("Prioritized Remediation Plan")

remediation_data = [
    {
        "Priority": "1",
        "Action": "Remove Project P003 entirely from claim",
        "Impact": "HIGH — eliminates most significant audit trigger",
        "Effort": "LOW",
    },
    {
        "Priority": "2",
        "Action": "Remove $1,200 office supplies from materials",
        "Impact": "MEDIUM — removes ineligible expenditure",
        "Effort": "LOW",
    },
    {
        "Priority": "3",
        "Action": "Prepare documentation memo for P002 gap period",
        "Impact": "HIGH — preempts CRA reviewer question",
        "Effort": "MEDIUM",
    },
    {
        "Priority": "4",
        "Action": "Recalculate PPA base excluding P003 salaries",
        "Impact": "MEDIUM — ensures accurate proxy amount",
        "Effort": "LOW",
    },
    {
        "Priority": "5",
        "Action": "Consider preparer arrangement discussion",
        "Impact": "LOW — contingency fee is legal but flagged",
        "Effort": "N/A",
    },
    {
        "Priority": "6",
        "Action": "Add photos/videos to evidence for P001/P002",
        "Impact": "LOW — nice-to-have, not required",
        "Effort": "LOW",
    },
]

df_remediation = pd.DataFrame(remediation_data)
st.dataframe(df_remediation, use_container_width=True, hide_index=True)

st.divider()

# --- Before/After Comparison ---
st.subheader("Before/After Comparison Summary")

uncorrected = calculate_uncorrected_expenditures(expenditures)
corrected = calculate_corrected_expenditures(expenditures)

itc_before = round(uncorrected["total"] * ITC_CCPC_ENHANCED_RATE)
itc_after = round(corrected["total"] * ITC_CCPC_ENHANCED_RATE)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Metric")
    st.markdown("Claim Amount")
    st.markdown("Estimated Federal ITC")
    st.markdown("Audit Risk Level")
    st.markdown("Expected Outcome")

with col2:
    st.markdown("### Before Corrections")
    st.markdown(f"**{fmt_currency(uncorrected['total'])}**")
    st.markdown(f"**{fmt_currency(itc_before)}**")
    st.markdown("🔴 **HIGH**")
    st.markdown("Likely partial or full denial")

with col3:
    st.markdown("### After Corrections")
    st.markdown(f"**{fmt_currency(corrected['total'])}**")
    st.markdown(f"**{fmt_currency(itc_after)}**")
    st.markdown("🟢 **LOW**")
    st.markdown("High probability of full approval")

st.divider()

# --- Downloadable Report ---
st.subheader("Download Report")

report_text = f"""IAM-AUDIT SR&ED CLAIM READINESS REPORT
{'='*50}
Client: {client['company_name']}
Business Number: {client['business_number']}
Fiscal Year End: {client['fiscal_year_end']}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

OVERALL READINESS SCORE: {overall_score}/100 ({'HIGH RISK' if overall_score <= 40 else 'MEDIUM RISK' if overall_score <= 70 else 'LOW RISK'})

SCORE BREAKDOWN:
- Eligibility: {subscores['eligibility']}/100
- Expenditure Accuracy: {subscores['expenditure']}/100
- Documentation: {subscores['documentation']}/100
- Form Completeness: {subscores['form']}/100

ISSUES IDENTIFIED:
"""

issues = get_all_issues(projects, expenditures, documentation, form_data, client)
for i, issue in enumerate(issues, 1):
    report_text += f"\n{i}. [{issue['severity']}] {issue['issue']}"
    report_text += f"\n   Remediation: {issue['remediation']}\n"

report_text += f"""
EXPENDITURE COMPARISON:
{'='*50}
                    As Filed        Corrected       Delta
Salaries:           {fmt_currency(uncorrected['salaries']):>15} {fmt_currency(corrected['salaries']):>15} {fmt_currency(corrected['salaries'] - uncorrected['salaries']):>15}
Materials:          {fmt_currency(uncorrected['materials']):>15} {fmt_currency(corrected['materials']):>15} {fmt_currency(corrected['materials'] - uncorrected['materials']):>15}
Contracts:          {fmt_currency(uncorrected['contracts']):>15} {fmt_currency(corrected['contracts']):>15} {fmt_currency(corrected['contracts'] - uncorrected['contracts']):>15}
PPA:                {fmt_currency(uncorrected['ppa']):>15} {fmt_currency(corrected['ppa']):>15} {fmt_currency(corrected['ppa'] - uncorrected['ppa']):>15}
Total:              {fmt_currency(uncorrected['total']):>15} {fmt_currency(corrected['total']):>15} {fmt_currency(corrected['total'] - uncorrected['total']):>15}

ESTIMATED ITC:
Federal (35%):      {fmt_currency(itc_before):>15} {fmt_currency(itc_after):>15}
Audit Risk:         {'HIGH':>15} {'LOW':>15}

REMEDIATION PLAN:
"""

for item in remediation_data:
    report_text += f"\n{item['Priority']}. {item['Action']} (Impact: {item['Impact']}, Effort: {item['Effort']})"

report_text += "\n\n---\nGenerated by IAM-Audit SR&ED Readiness Scanner (POC Demo)\n"

st.download_button(
    label="Download Full Report (TXT)",
    data=report_text,
    file_name=f"sred_readiness_report_{client['company_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
    mime="text/plain",
)
