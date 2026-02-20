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

# Calculate scores
overall_score, subscores = calculate_overall_score(projects, expenditures, documentation, form_data)

# Determine color
if overall_score <= 40:
    score_color = "#FF4B4B"
    score_label = "HIGH RISK"
elif overall_score <= 70:
    score_color = "#FFA500"
    score_label = "MEDIUM RISK"
else:
    score_color = "#00CC66"
    score_label = "LOW RISK"

st.header("Executive Dashboard")

# Overall Readiness Score Gauge
col_gauge, col_metrics = st.columns([1, 2])

with col_gauge:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=overall_score,
        title={"text": "Overall Readiness Score", "font": {"size": 20}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": score_color},
            "steps": [
                {"range": [0, 40], "color": "#FFE0E0"},
                {"range": [40, 70], "color": "#FFF3E0"},
                {"range": [70, 100], "color": "#E0FFE0"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": overall_score,
            },
        },
    ))
    fig.update_layout(height=300, margin=dict(t=60, b=20, l=30, r=30))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"<h3 style='text-align: center; color: {score_color};'>{score_label}</h3>", unsafe_allow_html=True)

with col_metrics:
    st.subheader("Score Breakdown")
    sb_col1, sb_col2 = st.columns(2)
    with sb_col1:
        st.metric("Eligibility (35%)", f"{subscores['eligibility']}/100")
        st.metric("Expenditure Accuracy (25%)", f"{subscores['expenditure']}/100")
    with sb_col2:
        st.metric("Documentation (25%)", f"{subscores['documentation']}/100")
        st.metric("Form Completeness (15%)", f"{subscores['form']}/100")

st.divider()

# Four metric cards
st.subheader("Key Metrics")
m1, m2, m3, m4 = st.columns(4)

# Count eligible projects
eligible_count = sum(1 for p in projects if p["eligibility_strength"] != "INELIGIBLE")
with m1:
    if eligible_count == len(projects):
        st.success(f"**Projects Eligible**\n\n{eligible_count} of {len(projects)}")
    else:
        st.warning(f"**Projects Eligible**\n\n{eligible_count} of {len(projects)}")

# Count expenditure issues
exp_issues = len(expenditures.get("deliberate_errors", []))
with m2:
    if exp_issues > 0:
        st.error(f"**Expenditure Issues**\n\n{exp_issues} found")
    else:
        st.success(f"**Expenditure Issues**\n\nNone found")

# Documentation gaps
doc_gaps = sum(1 for item in documentation["evidence_items"] if item.get("gap_flag"))
with m3:
    if doc_gaps > 0:
        st.warning(f"**Documentation Gaps**\n\n{doc_gaps} critical")
    else:
        st.success(f"**Documentation Gaps**\n\nNone found")

# Form T661 status
parts = form_data["parts_status"]
complete_parts = sum(1 for p in parts.values() if p["status"] == "COMPLETE")
with m4:
    if complete_parts == len(parts):
        st.success(f"**Form T661 Status**\n\n{complete_parts} of {len(parts)} parts ready")
    else:
        st.warning(f"**Form T661 Status**\n\n{complete_parts} of {len(parts)} parts ready")

st.divider()

# Issues Summary Table
st.subheader("Issues Summary")
issues = get_all_issues(projects, expenditures, documentation, form_data, client)

if issues:
    issue_data = []
    for issue in issues:
        severity_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(issue["severity"], "⚪")
        issue_data.append({
            "Severity": f"{severity_emoji} {issue['severity']}",
            "Category": issue["category"],
            "Issue": issue["issue"],
            "Project": issue["project"],
            "Remediation": issue["remediation"],
        })

    df_issues = pd.DataFrame(issue_data)
    st.dataframe(df_issues, use_container_width=True, hide_index=True)
else:
    st.success("No issues found!")

st.divider()

# Estimated ITC Impact
st.subheader("Estimated ITC Impact")

uncorrected = calculate_uncorrected_expenditures(expenditures)
corrected = calculate_corrected_expenditures(expenditures)

col_before, col_after = st.columns(2)

with col_before:
    st.markdown("### As Filed (with errors)")
    st.metric("Total Qualified Expenditures", fmt_currency(uncorrected["total"]))
    itc_before = round(uncorrected["total"] * ITC_CCPC_ENHANCED_RATE)
    st.metric("Estimated Federal ITC (35%)", fmt_currency(itc_before))
    st.error("**HIGH AUDIT RISK** — Includes ineligible project and expenditures")

with col_after:
    st.markdown("### Corrected (recommended)")
    st.metric(
        "Total Qualified Expenditures",
        fmt_currency(corrected["total"]),
        delta=fmt_currency(corrected["total"] - uncorrected["total"]),
    )
    itc_after = round(corrected["total"] * ITC_CCPC_ENHANCED_RATE)
    st.metric(
        "Estimated Federal ITC (35%)",
        fmt_currency(itc_after),
        delta=fmt_currency(itc_after - itc_before),
    )
    st.success("**LOW AUDIT RISK** — Clean claim, defensible if reviewed")

st.info(
    "**Key Insight:** Removing the ineligible project reduces the claim by "
    f"{fmt_currency(uncorrected['total'] - corrected['total'])}, but eliminates audit risk. "
    "The expected value of the corrected claim is higher because the uncorrected claim "
    "has a high probability of full denial upon CRA review."
)
