import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import ensure_data_loaded

ensure_data_loaded()

documentation = st.session_state.documentation
projects = st.session_state.projects

st.header("Documentation & Evidence Trail Audit")
st.markdown("CRA's primary review focus is contemporaneous documentation. "
            "This page audits the evidence trail against CRA expectations.")

st.divider()

# --- Timeline Visualization ---
st.subheader("Evidence Timeline")

# Build timeline data
timeline_items = []
project_colors = {"P001": "#0066CC", "P002": "#00CC66", "P003": "#FF4B4B"}
type_symbols = {
    "project_initiation_record": "diamond",
    "literature_review": "square",
    "lab_notebook": "circle",
    "test_data": "triangle-up",
    "technical_report": "star",
    "source_code": "hexagon",
    "timesheets": "cross",
    "feasibility_report": "diamond",
    "project_plan": "square",
    "jira_tickets": "pentagon",
}

fig = go.Figure()

# Add gap highlight for P002
fig.add_shape(
    type="rect",
    x0="2024-06-15", x1="2024-09-03",
    y0=-0.5, y1=2.5,
    fillcolor="rgba(255, 75, 75, 0.15)",
    line=dict(color="red", width=2, dash="dash"),
)
fig.add_annotation(
    x="2024-07-24", y=2.3,
    text="⚠️ 80-Day Documentation Gap (P002)",
    showarrow=False,
    font=dict(color="red", size=12, family="Arial Black"),
)

project_y = {"P001": 0, "P002": 1, "P003": 2}

for item in documentation["evidence_items"]:
    pid = item["project"]
    y = project_y.get(pid, 0)

    # Parse date
    if "date" in item:
        x_date = item["date"]
        hover_date = item["date"]
    elif "date_range" in item:
        dates = item["date_range"].split(" to ")
        x_date = dates[0]
        hover_date = item["date_range"]
    else:
        continue

    symbol = type_symbols.get(item["type"], "circle")
    color = project_colors.get(pid, "#888888")

    # Flag items
    flag_text = ""
    if item.get("gap_flag"):
        flag_text = " ⚠️ GAP"
        color = "#FF4B4B"
    if item.get("flag"):
        flag_text = " ⚠️ FLAG"
        color = "#FFA500"

    fig.add_trace(go.Scatter(
        x=[x_date],
        y=[y],
        mode="markers",
        marker=dict(size=14, color=color, symbol=symbol, line=dict(width=1, color="white")),
        name=f"{pid}: {item['type']}",
        hovertext=f"<b>{item['title']}</b><br>Date: {hover_date}<br>Format: {item['format']}{flag_text}",
        hoverinfo="text",
        showlegend=False,
    ))

fig.update_layout(
    height=300,
    xaxis=dict(title="2024", range=["2024-01-01", "2024-12-31"]),
    yaxis=dict(
        tickvals=[0, 1, 2],
        ticktext=["P001: Sensor Fusion", "P002: Anomaly Detection", "P003: GraphQL Migration"],
        range=[-0.5, 2.5],
    ),
    margin=dict(t=30, b=40, l=200, r=30),
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Evidence Checklist ---
st.subheader("Evidence Checklist (T661 Lines 270-282)")

checklist = documentation["t661_evidence_checklist"]

checklist_display = {
    "line_270_lab_notebooks": "270 — Lab notebooks",
    "line_272_project_planning_docs": "272 — Project planning docs",
    "line_274_design_docs": "274 — Design/system architecture",
    "line_276_test_protocols_data": "276 — Test protocols/data",
    "line_278_photographs_videos": "278 — Photos/videos",
    "line_280_contracts_invoices": "280 — Contracts/invoices",
    "line_282_other": "282 — Other records",
}

def format_check(val):
    if val is True:
        return "✅"
    elif val == "partial":
        return "⚠️ Partial"
    elif val == "wrong_type":
        return "⚠️ Wrong type"
    elif val is False:
        return "❌ None"
    return str(val)

check_data = []
for key, label in checklist_display.items():
    row = {"Line": label}
    project_vals = checklist.get(key, {})
    row["P001"] = format_check(project_vals.get("P001"))
    row["P002"] = format_check(project_vals.get("P002"))
    row["P003"] = format_check(project_vals.get("P003"))
    check_data.append(row)

df_check = pd.DataFrame(check_data)
st.dataframe(df_check, use_container_width=True, hide_index=True)

st.divider()

# --- P002 Documentation Gap Deep Dive ---
st.subheader("P002 Documentation Gap — Deep Dive")

st.error(
    "**80-Day Documentation Gap Detected**\n\n"
    "**Period:** June 15, 2024 to September 3, 2024\n\n"
    "**Cause:** Team lead on parental leave. No delegate assigned for documentation.\n\n"
    "**Impact:** Lab notebook entries (Confluence: CloudAnomaly-R&D Space) suspended for 80 days. "
    "89 entries before gap, 67 entries after resumption."
)

st.warning(
    "**Note:** Git commits continued during the gap period — code exists but no experimental "
    "rationale was recorded. The Git repo (novatech/cloud-anomaly-gnn) shows 412 total commits "
    "spanning the entire project period, indicating active development without corresponding "
    "SR&ED documentation."
)

with st.expander("CRA Guidance on Documentation Gaps"):
    st.markdown(
        "While contemporaneous documentation is not a statutory requirement "
        "(*Abeilles v. The Queen*, 2014 TCC 313), it is CRA's primary review focus. "
        "CRA Guidelines on Eligibility (2021), Section 6 states:\n\n"
        "> *'The claimant should be able to demonstrate that a systematic investigation "
        "or search was carried out by providing evidence that was recorded as the work progressed.'*\n\n"
        "**Risk Assessment:** CRA reviewer will likely request an explanation for the gap. "
        "An 80-day gap on an otherwise strong project weakens the claim for that period.\n\n"
        "**Recommendation:** Prepare a retrospective memo reconstructing the experimental approach "
        "during the gap period using:\n"
        "- Git commit messages and code review comments\n"
        "- Pull request descriptions\n"
        "- Slack/Teams messages (if available)\n"
        "- Calendar invites for team meetings\n\n"
        "This memo should be clearly labeled as a retrospective reconstruction, not presented "
        "as contemporaneous documentation."
    )

st.divider()

# --- P003 Documentation Failure ---
st.subheader("P003 Documentation Assessment")

st.error(
    "**Documentation Inadequate for SR&ED Claim**\n\n"
    "Project P003 documentation consists entirely of standard software engineering artifacts:\n\n"
    "- **Confluence page:** Standard project plan (not an SR&ED PIR). No hypotheses, no uncertainty analysis.\n"
    "- **Jira tickets:** 47 standard development stories. No experimental design or hypothesis tracking.\n"
    "- **Timesheets:** Standard time entries (not SR&ED-specific allocation).\n\n"
    "**Assessment:** No SR&ED-type records exist for this project. There are no records of hypotheses "
    "formulated, experiments conducted, or technological uncertainties investigated. This is consistent "
    "with the project's ineligibility — it was standard development work documented as such."
)
