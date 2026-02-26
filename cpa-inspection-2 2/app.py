import streamlit as st
import pandas as pd
from datetime import date, datetime
from pathlib import Path
import sys

from engine.scanner import run_scan
from engine.report import generate_report_text, generate_csv_rows

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from branding import PALETTE, apply_enterprise_theme, powered_by_markdown

st.set_page_config(
    page_title="CPA Practice Inspection Readiness Scanner",
    page_icon="\U0001f4cb",
    layout="wide",
)
apply_enterprise_theme()

# --- Run scan (cached) ---
@st.cache_data
def get_scan_results():
    return run_scan()

result = get_scan_results()

# --- Sidebar ---
st.sidebar.markdown("### \U0001f4cb CPA Practice Inspection\n### Readiness Scanner")
st.sidebar.caption(powered_by_markdown())
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    [
        "\U0001f3e0 Dashboard",
        "\U0001f3e2 Firm-Level Scan",
        "\U0001f4c2 Engagement Files",
        "\U0001f4ca Gap Report",
        "\U0001f517 Evidence Graph",
        "\U0001f4e4 Generate Report",
    ],
)

st.sidebar.divider()
if st.sidebar.button("\U0001f504 Refresh Scan", use_container_width=True):
    get_scan_results.clear()
    st.rerun()
st.sidebar.divider()
st.sidebar.markdown(f"**Firm:** {result.firm_name}")
st.sidebar.markdown(f"**License:** {result.license_number}")
st.sidebar.markdown(f"**Jurisdiction:** {result.jurisdiction}")
inspection_date = datetime.strptime(result.next_inspection_due, "%Y-%m-%d").date()
days_until = (inspection_date - date.today()).days
if days_until > 0:
    st.sidebar.markdown(f"**Next Inspection:** {result.next_inspection_due}")
    st.sidebar.markdown(
        f"**Days Until:** <span style='color:{PALETTE.status_warning}; font-weight:600;'>{days_until} days</span>",
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown(
        f"**Inspection:** <span style='color:{PALETTE.status_critical}; font-weight:700;'>OVERDUE</span>",
        unsafe_allow_html=True,
    )


# ============================================================
# Page 1: Dashboard
# ============================================================
if page == "\U0001f3e0 Dashboard":
    st.title("\U0001f4cb CPA Practice Inspection Readiness Scanner")
    st.caption(powered_by_markdown())

    # Firm info bar
    col_firm = st.columns(3)
    col_firm[0].markdown(f"**Firm:** {result.firm_name}")
    col_firm[1].markdown(f"**License:** {result.license_number}")
    if days_until > 0:
        col_firm[2].markdown(
            f"**Inspection in:** <span style='color:{PALETTE.status_warning}; font-weight:700;'>{days_until} days</span> "
            f"({result.next_inspection_due})",
            unsafe_allow_html=True,
        )
    else:
        col_firm[2].markdown(
            f"**Inspection:** <span style='color:{PALETTE.status_critical}; font-weight:700;'>OVERDUE</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    # Big score + metrics
    score_col, metrics_col = st.columns([1, 2])

    with score_col:
        # Readiness score
        score = result.readiness_score
        if score >= 80:
            score_color = PALETTE.status_success
        elif score >= 60:
            score_color = PALETTE.status_warning
        else:
            score_color = PALETTE.status_critical
        st.markdown(
            f"<div style='text-align:center; padding: 20px;'>"
            f"<div style='font-size: 72px; font-weight: bold; color: {score_color};'>{score}%</div>"
            f"<div style='font-size: 18px; color: {PALETTE.text_muted};'>Readiness Score</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='text-align:center; padding: 10px;'>"
            f"<div style='font-size: 14px;'>Predicted Outcome</div>"
            f"<div style='font-size: 16px; font-weight: bold; color: {score_color};'>{result.predicted_outcome}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with metrics_col:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Assertions Checked", result.total_assertions)
        m2.metric("Critical Gaps", result.critical_count, delta=f"{result.critical_count} found", delta_color="inverse")
        m3.metric("Warnings", result.warning_count, delta=f"{result.warning_count} found", delta_color="inverse")
        m4.metric("Files Scanned", result.files_scanned)

    st.divider()

    # Component traffic lights
    st.subheader("CSQM 1 Component Status")
    comp_cols = st.columns(len(result.components))
    for i, comp in enumerate(result.components):
        with comp_cols[i]:
            if comp.status == "pass":
                icon = "\u2705"
                color = PALETTE.status_success
            elif comp.status == "warning":
                icon = "\u26a0\ufe0f"
                color = PALETTE.status_warning
            else:
                icon = "\u274c"
                color = PALETTE.status_critical

            st.markdown(
                f"<div style='text-align:center; padding: 10px; border-radius: 8px; "
                f"border: 2px solid {color};'>"
                f"<div style='font-size: 28px;'>{icon}</div>"
                f"<div style='font-size: 12px; font-weight: bold;'>{comp.name}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.divider()

    # Call to action
    if result.critical_count > 0:
        st.error(
            f"\u274c **{result.critical_count} critical item{'s' if result.critical_count != 1 else ''} "
            f"need attention before your inspection.** "
            f"Go to the Gap Report for a prioritized fix list."
        )
    elif result.warning_count > 0:
        st.warning(
            f"\u26a0\ufe0f {result.warning_count} warning{'s' if result.warning_count != 1 else ''} found. "
            f"Review the Gap Report before your inspection."
        )
    else:
        st.success("\u2705 Your firm appears ready for inspection!")


# ============================================================
# Page 2: Firm-Level Scan
# ============================================================
elif page == "\U0001f3e2 Firm-Level Scan":
    st.title("\U0001f3e2 Firm-Level Scan Results")
    st.caption("CSQM 1 component-by-component review of your firm's quality management system")

    for comp in result.components:
        if comp.status == "pass":
            icon = "\u2705"
        elif comp.status == "warning":
            icon = "\u26a0\ufe0f"
        else:
            icon = "\u274c"

        with st.expander(
            f"{icon} **{comp.name}** — {comp.critical_count} critical, {comp.warning_count} warnings",
            expanded=(comp.status == "critical"),
        ):
            st.caption(comp.description)

            if not comp.findings:
                st.success("\u2705 All checks passed. No issues found.")
            else:
                for f in comp.findings:
                    if f.severity == "critical":
                        st.markdown(f"\u274c **{f.rule_id}: {f.description}**")
                        st.error(f"**The inspector will flag this:** {f.issue}")
                    elif f.severity == "warning":
                        st.markdown(f"\u26a0\ufe0f **{f.rule_id}: {f.description}**")
                        st.warning(f"{f.issue}")
                    else:
                        st.markdown(f"\u2139\ufe0f **{f.rule_id}: {f.description}**")
                        st.info(f"{f.issue}")

                    st.markdown(f"**Fix this:** {f.remediation}")
                    st.caption(f"Estimated time: {f.estimated_fix_time}")
                    st.markdown("---")


# ============================================================
# Page 3: Engagement Files
# ============================================================
elif page == "\U0001f4c2 Engagement Files":
    st.title("\U0001f4c2 Engagement File Review")
    st.caption("Review each client engagement file the inspector may select")

    # File selector
    file_options = []
    for fr in result.file_results:
        if fr.overall_status == "fail":
            icon = "\u274c"
        elif fr.overall_status == "pass_with_warning":
            icon = "\u26a0\ufe0f"
        else:
            icon = "\u2705"
        file_options.append(f"{icon} {fr.client_name} ({fr.file_id})")

    selected_idx = st.selectbox(
        "Select engagement file",
        range(len(file_options)),
        format_func=lambda i: file_options[i],
    )

    fr = result.file_results[selected_idx]

    # File header
    st.divider()
    h1, h2, h3 = st.columns(3)
    h1.markdown(f"**Client:** {fr.client_name}")
    h2.markdown(f"**Type:** {fr.engagement_type.title()} ({fr.standard})")
    h3.markdown(f"**Status:** {'**FAIL**' if fr.overall_status == 'fail' else fr.overall_status.upper()}")

    h4, h5, h6 = st.columns(3)
    h4.markdown(f"**Partner:** {fr.engagement_partner}")
    h5.markdown(f"**Prepared by:** {fr.prepared_by}")
    h6.metric("Assertions", f"{fr.assertions_passed}/{fr.assertions_total}")

    if fr.overall_status == "fail":
        st.error(
            f"\u274c **This file has significant deficiencies.** "
            f"The inspector will likely flag this file for re-performance or a significant finding."
        )

    st.divider()

    # Checklist view — load the raw file data for the detail view
    from engine.scanner import load_engagement_files
    engagement_files = load_engagement_files()
    raw_file = engagement_files[selected_idx]
    checks = raw_file.get("checks", {})

    st.subheader("Inspection Checklist")

    for check_name, check_data in checks.items():
        display_name = check_name.replace("_", " ").title()
        status = check_data.get("status", "ok")

        if status == "ok":
            st.markdown(f"\u2705 **{display_name}** — Pass")
        elif status == "warning":
            st.markdown(f"\u26a0\ufe0f **{display_name}** — Warning")
            issue = check_data.get("issue", "")
            if issue:
                st.warning(issue)
        elif status == "critical":
            st.markdown(f"\u274c **{display_name}** — Critical")
            issue = check_data.get("issue", "")
            issues_list = check_data.get("issues", [])
            if issues_list:
                for iss in issues_list:
                    st.error(iss)
            elif issue:
                st.error(issue)
        elif status == "pending":
            st.markdown(f"\u2139\ufe0f **{display_name}** — Pending")
            issue = check_data.get("issue", "")
            if issue:
                st.info(issue)

        # Side-by-side: what file has vs. what inspector expects
        if status in ("critical", "warning"):
            with st.expander(f"Details: What the inspector expects for {display_name}"):
                col_has, col_expects = st.columns(2)
                with col_has:
                    st.markdown("**What your file has:**")
                    for k, v in check_data.items():
                        if k in ("status", "issue", "issues"):
                            continue
                        if isinstance(v, bool):
                            icon = "\u2705" if v else "\u274c"
                            st.markdown(f"- {icon} {k.replace('_', ' ').title()}")
                with col_expects:
                    st.markdown("**What the inspector expects:**")
                    for k, v in check_data.items():
                        if k in ("status", "issue", "issues"):
                            continue
                        if isinstance(v, bool):
                            st.markdown(f"- \u2705 {k.replace('_', ' ').title()}")

    st.divider()

    # Findings for this file
    if fr.findings:
        st.subheader("Findings for This File")
        for f in fr.findings:
            if f.severity == "critical":
                st.error(f"\u274c **{f.rule_id}:** {f.issue}")
            elif f.severity == "warning":
                st.warning(f"\u26a0\ufe0f **{f.rule_id}:** {f.issue}")
            else:
                st.info(f"\u2139\ufe0f **{f.rule_id}:** {f.issue}")
            st.markdown(f"**Fix:** {f.remediation} (Est. {f.estimated_fix_time})")


# ============================================================
# Page 4: Gap Report
# ============================================================
elif page == "\U0001f4ca Gap Report":
    st.title("\U0001f4ca Gap Report")
    st.caption("Prioritized list of all findings — fix these before your inspection")

    # Summary
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Findings", len(result.all_findings))
    s2.metric("\u274c Critical", result.critical_count)
    s3.metric("\u26a0\ufe0f Warnings", result.warning_count)
    s4.metric("\u2139\ufe0f Info", result.info_count)

    st.divider()

    # Predicted outcomes
    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown("**If unfixed:**")
        if result.critical_count > 0:
            st.error(f"\u274c Predicted: **{result.predicted_outcome}**")
        elif result.warning_count > 3:
            st.warning(f"\u26a0\ufe0f Predicted: **{result.predicted_outcome}**")
        else:
            st.success(f"\u2705 Predicted: **{result.predicted_outcome}**")
    with col_after:
        st.markdown("**If all critical items fixed:**")
        if result.post_fix_outcome == "Meets Requirements":
            st.success(f"\u2705 Predicted: **{result.post_fix_outcome}** ({result.post_fix_score}%)")
        else:
            st.warning(f"\u26a0\ufe0f Predicted: **{result.post_fix_outcome}** ({result.post_fix_score}%)")

    st.divider()

    # Findings grouped by severity
    critical_findings = [f for f in result.all_findings if f.severity == "critical"]
    warning_findings = [f for f in result.all_findings if f.severity == "warning"]
    info_findings = [f for f in result.all_findings if f.severity == "info"]

    priority = 1

    if critical_findings:
        st.subheader("\u274c Critical — Must fix before inspection")
        for f in critical_findings:
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{priority}. [{f.rule_id}] {f.description}**")
                    st.markdown(f"*Location:* {f.location} | *Component:* {f.component}")
                    st.error(f"**The inspector will flag this:** {f.issue}")
                    st.markdown(f"**Fix:** {f.remediation}")
                with c2:
                    st.metric("Est. Time", f.estimated_fix_time)
                st.markdown("---")
                priority += 1

    if warning_findings:
        st.subheader("\u26a0\ufe0f Warnings — Should fix before inspection")
        for f in warning_findings:
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{priority}. [{f.rule_id}] {f.description}**")
                    st.markdown(f"*Location:* {f.location} | *Component:* {f.component}")
                    st.warning(f"{f.issue}")
                    st.markdown(f"**Fix:** {f.remediation}")
                with c2:
                    st.metric("Est. Time", f.estimated_fix_time)
                st.markdown("---")
                priority += 1

    if info_findings:
        st.subheader("\u2139\ufe0f Info — For your awareness")
        for f in info_findings:
            with st.container():
                st.markdown(f"**{priority}. [{f.rule_id}] {f.description}**")
                st.markdown(f"*Location:* {f.location}")
                st.info(f"{f.issue}")
                st.markdown(f"**Fix:** {f.remediation} (Est. {f.estimated_fix_time})")
                st.markdown("---")
                priority += 1

    st.divider()

    # Export
    csv_rows = generate_csv_rows(result)
    df = pd.DataFrame(csv_rows)
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="\U0001f4e5 Export Gap Report as CSV",
        data=csv_data,
        file_name=f"gap_report_{result.firm_name.replace(' ', '_')}_{date.today().isoformat()}.csv",
        mime="text/csv",
    )


# ============================================================
# Page 5: Evidence Graph
# ============================================================
elif page == "\U0001f517 Evidence Graph":
    st.title("\U0001f517 Evidence Chain Visualization")
    st.caption("How your documents link to CPA inspection requirements")

    # Build evidence graph data
    st.subheader("Document-to-Requirement Mapping")

    # Firm-level documents
    firm_docs_map = {
        "SoQM Manual": ["GOV-01", "GOV-02", "GOV-03", "RES-02"],
        "Independence Declarations": ["ETH-01", "ETH-02"],
        "Conflict Register": ["ETH-03"],
        "Client Acceptance Forms": ["ACC-01", "ACC-02", "ACC-03"],
        "CPD Records": ["RES-01"],
        "Policy Distribution Log": ["COM-01", "COM-02"],
        "Complaints Procedure": ["COM-03"],
        "Monitoring Log": ["MON-01", "MON-02", "MON-03"],
        "SoQM Evaluation": ["MON-04"],
        "Remediation Log": ["MON-05", "MON-06"],
        "Governance Policies": ["GOV-01", "GOV-02", "GOV-03"],
    }

    # Identify broken chains
    broken_rules = set()
    for f in result.all_findings:
        if f.severity in ("critical", "warning"):
            broken_rules.add(f.rule_id)

    # Build graphviz
    dot_lines = [
        "digraph evidence {",
        '  rankdir=LR;',
        '  node [shape=box, style=filled, fontsize=10];',
        '',
        '  // Documents',
        '  subgraph cluster_docs {',
        '    label="Documents";',
        '    style=dashed;',
        f'    color="{PALETTE.border_soft}";',
        f'    fontcolor="{PALETTE.text_muted}";',
    ]

    for doc in firm_docs_map:
        safe = doc.replace(" ", "_").replace("&", "and")
        dot_lines.append(
            f'    {safe} [label="{doc}", fillcolor="{PALETTE.surface_blue}", fontcolor="{PALETTE.text_primary}"];'
        )

    dot_lines.append("  }")
    dot_lines.append("")
    dot_lines.append("  // Requirements")
    dot_lines.append("  subgraph cluster_reqs {")
    dot_lines.append('    label="Requirements";')
    dot_lines.append('    style=dashed;')
    dot_lines.append(f'    color="{PALETTE.border_soft}";')
    dot_lines.append(f'    fontcolor="{PALETTE.text_muted}";')

    all_rules = set()
    for rules in firm_docs_map.values():
        all_rules.update(rules)

    for rule in sorted(all_rules):
        if rule in broken_rules:
            dot_lines.append(
                f'    {rule} [label="{rule}", fillcolor="{PALETTE.status_critical_bg}", fontcolor="{PALETTE.status_critical}"];'
            )
        else:
            dot_lines.append(
                f'    {rule} [label="{rule}", fillcolor="{PALETTE.status_success_bg}", fontcolor="{PALETTE.status_success}"];'
            )

    dot_lines.append("  }")
    dot_lines.append("")
    dot_lines.append("  // Edges")

    for doc, rules in firm_docs_map.items():
        safe = doc.replace(" ", "_").replace("&", "and")
        for rule in rules:
            if rule in broken_rules:
                dot_lines.append(f'  {safe} -> {rule} [color="{PALETTE.status_critical}", penwidth=2];')
            else:
                dot_lines.append(f'  {safe} -> {rule} [color="{PALETTE.status_success}"];')

    dot_lines.append("}")
    dot_source = "\n".join(dot_lines)

    st.graphviz_chart(dot_source)

    st.divider()

    # Summary table
    st.subheader("Evidence Chain Summary")

    total_links = sum(len(rules) for rules in firm_docs_map.values())
    broken_links = sum(
        1 for rules in firm_docs_map.values() for r in rules if r in broken_rules
    )
    connected = total_links - broken_links

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Evidence Links", total_links)
    c2.metric("Connected (Pass)", connected)
    c3.metric("Broken (Fail/Warn)", broken_links, delta=f"{broken_links} issues", delta_color="inverse")

    st.divider()

    # Legend
    st.markdown(
        "**Legend:** "
        f"<span style='color:{PALETTE.status_success}; font-weight:600;'>Green</span> = Evidence chain intact "
        f"(requirement met) | "
        f"<span style='color:{PALETTE.status_critical}; font-weight:600;'>Rose</span> = Evidence chain broken (gap found)",
        unsafe_allow_html=True,
    )


# ============================================================
# Page 6: Generate Report
# ============================================================
elif page == "\U0001f4e4 Generate Report":
    st.title("\U0001f4e4 Inspection Readiness Report")
    st.caption("Generate and download your inspection readiness report")

    if st.button("Generate Report", type="primary"):
        with st.status("Generating inspection readiness report...", expanded=True) as status:
            st.write("Loading firm documents...")
            st.write("Scanning firm-level controls...")
            st.write("Scanning engagement files...")
            st.write("Calculating readiness score...")
            st.write("Building remediation plan...")
            status.update(label="Report generated!", state="complete")

    report_text = generate_report_text(result)

    st.divider()

    # Display formatted report
    st.text(report_text)

    st.divider()

    # Download buttons
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="\U0001f4c4 Download Report (TXT)",
            data=report_text,
            file_name=f"inspection_readiness_{result.firm_name.replace(' ', '_')}_{date.today().isoformat()}.txt",
            mime="text/plain",
        )
    with col_dl2:
        csv_rows = generate_csv_rows(result)
        df = pd.DataFrame(csv_rows)
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="\U0001f4ca Download Findings (CSV)",
            data=csv_data,
            file_name=f"findings_{result.firm_name.replace(' ', '_')}_{date.today().isoformat()}.csv",
            mime="text/csv",
        )

    st.divider()

    # Pitch — computed from actual findings
    st.markdown("---")
    st.markdown(
        f"**Fix those {result.critical_count} critical items** "
        f"(estimated **{result.estimated_fix_hours} hours** of work), run the scan again, "
        f"and your score goes from **{result.readiness_score}%** to **{result.post_fix_score}%**. "
        f"Predicted outcome: **{result.post_fix_outcome}**."
    )
