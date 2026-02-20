from __future__ import annotations

import runpy
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
CPA_DIR = BASE_DIR / "cpa-inspection-2 2"
CPA_APP = CPA_DIR / "app.py"
SRED_DIR = BASE_DIR / "sr&ed 2" / "sred_scanner"
SRED_PAGES_DIR = SRED_DIR / "pages"

SRED_PAGES = {
    "Overview": None,
    "Dashboard": SRED_PAGES_DIR / "1_Dashboard.py",
    "Project Eligibility": SRED_PAGES_DIR / "2_Project_Eligibility.py",
    "Expenditures": SRED_PAGES_DIR / "3_Expenditures.py",
    "Documentation": SRED_PAGES_DIR / "4_Documentation.py",
    "Form T661 Review": SRED_PAGES_DIR / "5_Form_T661_Review.py",
    "Risk Report": SRED_PAGES_DIR / "6_Risk_Report.py",
    "ITC Calculator": SRED_PAGES_DIR / "7_ITC_Calculator.py",
}


@contextmanager
def _push_sys_paths(paths: list[Path]):
    inserted: list[str] = []
    for path in reversed(paths):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
            inserted.append(path_str)
    try:
        yield
    finally:
        for path_str in inserted:
            while path_str in sys.path:
                sys.path.remove(path_str)


@contextmanager
def _patch_set_page_config():
    original = st.set_page_config
    st.set_page_config = lambda *args, **kwargs: None
    try:
        yield
    finally:
        st.set_page_config = original


def _run_script(script: Path, module_name: str, sys_paths: list[Path], patch_page_config: bool = False):
    if not script.exists():
        st.error(f"Missing script: `{script}`")
        return

    with _push_sys_paths(sys_paths):
        if patch_page_config:
            with _patch_set_page_config():
                runpy.run_path(str(script), run_name=module_name)
        else:
            runpy.run_path(str(script), run_name=module_name)


def _render_sred_overview():
    client = st.session_state.client_profile
    st.title("🔍 IAM-Audit: SR&ED Claim Readiness Scanner")
    st.markdown("---")
    st.markdown(
        """
Welcome to the **IAM-Audit SR&ED Readiness Scanner**. This tool analyzes SR&ED claims
against CRA rules and identifies compliance issues before filing.

Use the SR&ED section selector in the sidebar to explore:

| Page | Purpose |
|------|---------|
| **Dashboard** | Executive summary with overall readiness score |
| **Project Eligibility** | Five-question test per project |
| **Expenditures** | T661 Parts 3-4 expenditure analysis |
| **Documentation** | Evidence trail audit |
| **Form T661 Review** | Full form completeness check (all 10 parts) |
| **Risk Report** | Final risk score + remediation plan |
| **ITC Calculator** | Federal + provincial ITC estimate |
        """
    )
    st.info(
        f"Client: {client['company_name']} | Fiscal Year: {client['fiscal_year_end'][:4]} | "
        f"Projects: {len(st.session_state.projects)}"
    )


def _render_sred_sidebar_and_get_page() -> str:
    from utils.data_loader import ensure_data_loaded

    ensure_data_loaded()
    client = st.session_state.client_profile

    fiscal_end = datetime.strptime(client["fiscal_year_end"], "%Y-%m-%d")
    filing_deadline = fiscal_end + timedelta(days=18 * 30)
    days_remaining = (filing_deadline - datetime.now()).days

    with st.sidebar:
        st.markdown("## 🔍 IAM-Audit")
        st.markdown("**SR&ED Readiness Scanner**")
        st.divider()
        st.markdown(f"**Company:** {client['company_name']}")
        st.markdown(f"**BN:** {client['business_number']}")
        st.markdown(f"**Fiscal Year:** {client['fiscal_year_end'][:4]}")
        st.markdown(f"**Type:** {client['corporation_type']}")
        st.markdown(f"**Province:** {client['province']}")
        st.divider()
        st.markdown(f"**Filing Deadline:** {filing_deadline.strftime('%B %d, %Y')}")
        if days_remaining > 180:
            st.success(f"**{days_remaining} days remaining**")
        elif days_remaining > 90:
            st.warning(f"**{days_remaining} days remaining**")
        else:
            st.error(f"**{days_remaining} days remaining**")
        st.divider()
        preparer = client["preparer"]
        st.markdown(f"**Preparer:** {preparer['contact_name']}")
        st.markdown(f"*{preparer['name']}*")
        if preparer["billing_arrangement"] == 1:
            st.error(f"⚠️ Contingency Fee ({preparer['fee_percentage']}%)")
        st.divider()
        return st.selectbox("SR&ED Section", list(SRED_PAGES.keys()), index=0)


def _render_sred():
    with _push_sys_paths([SRED_DIR]):
        selected_page = _render_sred_sidebar_and_get_page()

    page_script = SRED_PAGES[selected_page]
    if page_script is None:
        _render_sred_overview()
        return

    _run_script(
        script=page_script,
        module_name=f"sred_{page_script.stem}",
        sys_paths=[SRED_DIR, SRED_PAGES_DIR],
    )


def _render_cpa():
    _run_script(
        script=CPA_APP,
        module_name="cpa_inspection_embedded",
        sys_paths=[CPA_DIR],
        patch_page_config=True,
    )


def main():
    st.set_page_config(
        page_title="IAM-Audit Unified Scanner",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    with st.sidebar:
        st.markdown("## 🧭 IAM-Audit Suite")
        mode = st.radio(
            "Functionality",
            [
                "CPA Practice Inspection",
                "SR&ED Claim Readiness",
            ],
            index=0,
        )
        st.divider()

    if mode == "CPA Practice Inspection":
        _render_cpa()
    else:
        _render_sred()


if __name__ == "__main__":
    main()
