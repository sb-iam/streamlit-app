import streamlit as st
import sys
import os
from datetime import datetime, timedelta

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from branding import BRAND, apply_enterprise_theme, powered_by_markdown, sred_header_title

st.set_page_config(
    page_title=f"{BRAND.display_name} | SR&ED Readiness Scanner",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_enterprise_theme()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.data_loader import ensure_data_loaded

ensure_data_loaded()

# Sidebar
client = st.session_state.client_profile
fiscal_end = datetime.strptime(client["fiscal_year_end"], "%Y-%m-%d")
filing_deadline = fiscal_end + timedelta(days=18 * 30)  # ~18 months
days_remaining = (filing_deadline - datetime.now()).days

with st.sidebar:
    st.markdown(f"## 🔍 {BRAND.display_name}")
    st.markdown("**SR&ED Readiness Scanner**")
    st.caption(powered_by_markdown())
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

# Main page content
st.title(sred_header_title())
st.markdown("---")
st.markdown("""
Welcome to the **{brand} SR&ED Readiness Scanner**. This tool analyzes SR&ED claims
against CRA rules and identifies compliance issues before filing.

**Navigate using the sidebar** to explore:

| Page | Purpose |
|------|---------|
| **Dashboard** | Executive summary with overall readiness score |
| **Project Eligibility** | Five-question test per project |
| **Expenditures** | T661 Parts 3-4 expenditure analysis |
| **Documentation** | Evidence trail audit |
| **Form T661 Review** | Full form completeness check (all 10 parts) |
| **Risk Report** | Final risk score + remediation plan |
| **ITC Calculator** | Federal + provincial ITC estimate |

---
**Client:** {company} | **Fiscal Year:** {fy} | **Projects:** {n_proj}
""".format(
    brand=BRAND.display_name,
    company=client["company_name"],
    fy=client["fiscal_year_end"][:4],
    n_proj=len(st.session_state.projects),
))

st.info("Select a page from the sidebar to begin your SR&ED claim review.")
