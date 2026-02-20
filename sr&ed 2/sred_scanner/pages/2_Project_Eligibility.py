import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.rules import FIVE_QUESTIONS
from utils.constants import LINE_242_WORD_LIMIT, LINE_244_WORD_LIMIT, LINE_246_WORD_LIMIT
from utils.data_loader import ensure_data_loaded

ensure_data_loaded()

projects = st.session_state.projects

st.header("Project Eligibility Analysis")
st.markdown("Each project is evaluated against the CRA **Five-Question Eligibility Test** "
            "(Northwest Hydraulic Consultants Ltd. v. The Queen, 1998).")

tabs = st.tabs([f"{p['project_id']}: {p['title'][:40]}..." for p in projects])

for idx, (tab, project) in enumerate(zip(tabs, projects)):
    with tab:
        # Project header
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Field of Science:** {project['field_of_science']}")
            st.markdown(f"**Code:** {project['field_of_science_code']}")
        with col2:
            st.markdown(f"**Start:** {project['start_date']}")
            st.markdown(f"**End:** {project['end_date']}")
        with col3:
            st.markdown(f"**Status:** {project['status'].capitalize()}")
            st.markdown(f"**Keywords:** {', '.join(project['keyword_codes'])}")

        st.divider()

        # Five-Question Test
        st.subheader("Five-Question Eligibility Test")
        fqt = project["five_question_test"]

        passed_count = 0
        for q in FIVE_QUESTIONS:
            result = fqt.get(q["key"], False)
            evidence = fqt.get(q["evidence_key"], "No evidence provided")

            if result:
                passed_count += 1
                icon = "✅"
            else:
                icon = "❌"

            with st.expander(f"{icon} {q['id']}: {q['question'][:80]}..."):
                st.markdown(f"**Full Question:** {q['question']}")
                st.markdown(f"**Result:** {'PASS' if result else 'FAIL'}")
                st.markdown(f"**Evidence:** {evidence}")
                st.caption(f"Source: {q['source']}")

        # Verdict
        st.divider()
        strength = project["eligibility_strength"]
        if strength == "STRONG":
            st.success(f"**VERDICT: ELIGIBLE** ({passed_count}/5 questions passed)")
        elif strength == "MEDIUM":
            st.warning(f"**VERDICT: ELIGIBLE WITH RISK** ({passed_count}/5 questions passed — documentation gap on Q5)")
        else:
            st.error(f"**VERDICT: INELIGIBLE** ({passed_count}/5 questions passed)")

        # P003 educational callout
        if project["project_id"] == "P003":
            st.error(
                "**Why This Project Fails:** REST-to-GraphQL migration using vendor-published guides "
                "is *standard practice*, not SR&ED. CRA distinguishes between *technological uncertainty* "
                "(solution/method unknown) and *technical problems* (existing knowledge sufficient). "
                "Complexity, novelty of application, or business value do not qualify. "
                "See CRA Guidelines on Eligibility (August 2021), Section 2.1.1."
            )

        st.divider()

        # Narrative Analysis
        st.subheader("Narrative Analysis (T661 Part 2, Section B)")

        narratives = [
            ("Line 242 — Scientific/Technological Advancement", project["line_242_word_count"], LINE_242_WORD_LIMIT),
            ("Line 244 — Technological Uncertainty", project["line_244_word_count"], LINE_244_WORD_LIMIT),
            ("Line 246 — Work Performed", project["line_246_word_count"], LINE_246_WORD_LIMIT),
        ]

        for label, wc, limit in narratives:
            pct = wc / limit
            col_label, col_bar = st.columns([1, 2])
            with col_label:
                st.markdown(f"**{label}**")
                st.markdown(f"{wc} / {limit} words ({pct:.0%})")
            with col_bar:
                if pct < 0.5:
                    st.progress(pct, text=f"⚠️ Under 50% — too brief")
                elif pct < 0.75:
                    st.progress(pct, text="Adequate length")
                else:
                    st.progress(min(pct, 1.0), text="Good length")

            if pct < 0.5:
                st.warning(
                    f"**Flag:** Narrative is only {pct:.0%} of the allowed length. "
                    "CRA reviewers expect detailed descriptions demonstrating SR&ED eligibility. "
                    "Short narratives may trigger additional scrutiny."
                )

        # Quality indicators
        if project["project_id"] != "P003":
            narrative_text = (
                project.get("line_242_scientific_technological_advancement", "") + " " +
                project.get("line_244_technological_uncertainty", "") + " " +
                project.get("line_246_work_performed", "")
            ).lower()

            quality_keywords = {
                "hypothesis": "Hypotheses mentioned",
                "experiment": "Experiments referenced",
                "systematic": "Systematic approach described",
                "uncertainty": "Uncertainty articulated",
                "advancement": "Advancement claimed",
                "measured": "Measurements cited",
                "documented": "Documentation referenced",
            }

            st.markdown("**Quality Indicators:**")
            for kw, label in quality_keywords.items():
                if kw in narrative_text:
                    st.markdown(f"  ✅ {label}")
                else:
                    st.markdown(f"  ⬜ {label}")

        # Personnel summary
        st.divider()
        st.subheader("Personnel")
        for person in project["personnel"]:
            role_info = f"**{person['name']}** — {person['role']}"
            if person.get("is_contractor"):
                role_info += f" | Contract: ${person['contract_value']:,}"
            else:
                pct_alloc = person["hours_sred"] / person["hours_total"] * 100
                role_info += f" | {person['hours_sred']}h / {person['hours_total']}h ({pct_alloc:.0f}% SR&ED)"
            if person.get("is_specified_employee"):
                role_info += " | ⚠️ **Specified Employee** (>10% shareholder)"
            st.markdown(role_info)
