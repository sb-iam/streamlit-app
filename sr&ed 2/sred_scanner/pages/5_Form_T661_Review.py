import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import ensure_data_loaded

ensure_data_loaded()

form_data = st.session_state.t661_form

st.header("Form T661 Completeness Review")
st.markdown(f"**Form Version:** {form_data['form_version']}")
st.markdown("Review of all 10 parts of Form T661 with completeness status and identified issues.")

st.divider()

parts_config = [
    {
        "key": "part_1_general_info",
        "number": 1,
        "title": "General Information",
        "description": "Corporation name, business number, tax year, province, first-time claimant status.",
    },
    {
        "key": "part_2_project_info",
        "number": 2,
        "title": "Project Information",
        "description": "Per-project narratives (Lines 242, 244, 246), five-question test results, personnel evidence.",
    },
    {
        "key": "part_3_expenditures",
        "number": 3,
        "title": "Expenditure Calculation",
        "description": "Salaries (Line 300), materials (Line 360), contracts (Line 370), total SR&ED expenditures.",
    },
    {
        "key": "part_4_qualified_expenditures",
        "number": 4,
        "title": "Qualified Expenditures for ITC",
        "description": "Calculation of expenditures that qualify for Investment Tax Credit.",
    },
    {
        "key": "part_5_ppa",
        "number": 5,
        "title": "Prescribed Proxy Amount (PPA)",
        "description": "Proxy method calculation: 55% of eligible salary base.",
    },
    {
        "key": "part_6_per_project_breakdown",
        "number": 6,
        "title": "Per-Project Breakdown",
        "description": "Expenditure allocation by project.",
    },
    {
        "key": "part_7_statistical_info",
        "number": 7,
        "title": "Statistical Information",
        "description": "R&D personnel count, total SR&ED expenditures, industry classification.",
    },
    {
        "key": "part_8_checklist",
        "number": 8,
        "title": "Supporting Evidence Checklist",
        "description": "Evidence checklist (Lines 270-282): lab notebooks, planning docs, test data, etc.",
    },
    {
        "key": "part_9_preparer",
        "number": 9,
        "title": "Preparer Disclosure",
        "description": "Third-party preparer information, billing arrangement, fee percentage.",
    },
    {
        "key": "part_10_certification",
        "number": 10,
        "title": "Certification",
        "description": "Officer certification that information is correct and complete.",
    },
]

status_badges = {
    "COMPLETE": ("✅", "success"),
    "ISSUES_FOUND": ("❌", "error"),
    "INCOMPLETE": ("⚠️", "warning"),
    "WARNING": ("⚠️", "warning"),
    "NOT_CALCULATED": ("⏸️", "info"),
    "NOT_SIGNED": ("⏸️", "info"),
}

# Summary table
st.subheader("Status Overview")

col_headers = st.columns([1, 3, 2, 4])
col_headers[0].markdown("**Part**")
col_headers[1].markdown("**Title**")
col_headers[2].markdown("**Status**")
col_headers[3].markdown("**Key Issues**")

for pc in parts_config:
    part_data = form_data["parts_status"].get(pc["key"], {})
    status = part_data.get("status", "UNKNOWN")
    emoji, _ = status_badges.get(status, ("❓", "info"))
    issues = part_data.get("issues", [])
    issue_summary = issues[0][:60] + "..." if issues else "None"

    cols = st.columns([1, 3, 2, 4])
    cols[0].markdown(f"**{pc['number']}**")
    cols[1].markdown(pc["title"])
    cols[2].markdown(f"{emoji} {status.replace('_', ' ')}")
    cols[3].markdown(issue_summary)

st.divider()

# Detailed expanders
st.subheader("Detailed Review")

for pc in parts_config:
    part_data = form_data["parts_status"].get(pc["key"], {})
    status = part_data.get("status", "UNKNOWN")
    emoji, badge_type = status_badges.get(status, ("❓", "info"))
    issues = part_data.get("issues", [])

    with st.expander(f"Part {pc['number']}: {pc['title']} — {emoji} {status.replace('_', ' ')}"):
        st.markdown(f"*{pc['description']}*")
        st.divider()

        # Show status
        badge_fn = {"success": st.success, "error": st.error, "warning": st.warning, "info": st.info}
        badge_fn.get(badge_type, st.info)(f"**Status:** {status.replace('_', ' ')}")

        # Show line values if available
        lines = part_data.get("lines", {})
        if lines:
            st.markdown("**Field Values:**")
            for line_key, line_val in lines.items():
                st.markdown(f"- **{line_key}:** {line_val}")

        # Show section details
        for key in ["section_a_method", "section_a_fields"]:
            if key in part_data:
                st.markdown(f"**{key.replace('_', ' ').title()}:** {part_data[key]}")

        # Section B details
        if "section_b_three_questions" in part_data:
            st.markdown("**Section B — Three Questions (per project):**")
            for pid, results in part_data["section_b_three_questions"].items():
                line_results = " | ".join(f"{k}: {v}" for k, v in results.items())
                st.markdown(f"- **{pid}:** {line_results}")

        if "section_c_personnel_evidence" in part_data:
            st.markdown("**Section C — Personnel Evidence:**")
            for pid, status_text in part_data["section_c_personnel_evidence"].items():
                st.markdown(f"- **{pid}:** {status_text}")

        # Section B summary for Part 3
        if "section_b_summary" in part_data:
            st.markdown("**Section B — Expenditure Summary:**")
            for k, v in part_data["section_b_summary"].items():
                st.markdown(f"- **{k}:** ${v:,}")

        # PPA details
        if "proxy_base_before_corrections" in part_data:
            st.markdown(f"**PPA Base (before corrections):** ${part_data['proxy_base_before_corrections']:,}")
            st.markdown(f"**PPA Amount (before corrections):** ${part_data['proxy_amount_before_corrections']:,}")

        # Preparer details
        if "preparer_name" in part_data:
            st.markdown(f"**Preparer:** {part_data['preparer_name']} (BN: {part_data['preparer_bn']})")
            st.markdown(f"**Billing Arrangement:** Code {part_data['billing_arrangement_code']} — {part_data['billing_arrangement_text']}")
            st.markdown(f"**Fee:** {part_data['fee_percentage']}%")

        # Note
        if "note" in part_data:
            st.info(part_data["note"])

        # Issues
        if issues:
            st.markdown("**Issues Found:**")
            for issue in issues:
                st.error(f"- {issue}")
        else:
            st.success("No issues found for this part.")
