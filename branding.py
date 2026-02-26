from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Brand:
    slug: str
    display_name: str
    tagline: str


@dataclass(frozen=True)
class Palette:
    primary_blue: str
    deep_blue: str
    surface_blue: str
    surface_blue_alt: str
    border_soft: str
    text_primary: str
    text_muted: str
    status_success: str
    status_success_bg: str
    status_warning: str
    status_warning_bg: str
    status_critical: str
    status_critical_bg: str
    status_info: str
    status_info_bg: str


BRAND = Brand(
    slug="verifiable-accounting",
    display_name="Verifiable Accounting",
    tagline="Interpretive AI for Accounting & Assurance",
)

PALETTE = Palette(
    primary_blue="#5B9BD5",
    deep_blue="#2F6EA3",
    surface_blue="#ECF4FF",
    surface_blue_alt="#F7FAFF",
    border_soft="#D6E4F5",
    text_primary="#16324F",
    text_muted="#5D7692",
    status_success="#5B9E85",
    status_success_bg="#ECF8F3",
    status_warning="#C7A56A",
    status_warning_bg="#FFF8E9",
    status_critical="#C4838E",
    status_critical_bg="#FDEFF2",
    status_info="#5E8DB4",
    status_info_bg="#EDF4FB",
)


def powered_by_text() -> str:
    return f"Powered by {BRAND.display_name} • {BRAND.tagline}"


def powered_by_markdown() -> str:
    return f"Powered by **{BRAND.display_name}** • {BRAND.tagline}"


def sred_header_title() -> str:
    return f"🔍 {BRAND.display_name}: SR&ED Claim Readiness Scanner"


def apply_enterprise_theme() -> None:
    import streamlit as st

    st.markdown(
        f"""
<style>
.stApp {{
  background:
    radial-gradient(1200px 500px at -15% -10%, #E6F2FF 0%, #F7FBFF 50%, #F3F8FF 100%);
  color: {PALETTE.text_primary};
  --red-70: {PALETTE.status_critical};
  --red-80: {PALETTE.status_critical};
  --red-90: {PALETTE.status_critical_bg};
  --yellow-70: {PALETTE.status_warning};
  --yellow-80: {PALETTE.status_warning};
  --yellow-90: {PALETTE.status_warning_bg};
  --orange-70: {PALETTE.status_warning};
  --orange-80: {PALETTE.status_warning};
  --orange-90: {PALETTE.status_warning_bg};
}}

[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #EAF3FF 0%, #F6FAFF 100%);
  border-right: 1px solid {PALETTE.border_soft};
}}

[data-testid="stMetric"] {{
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid {PALETTE.border_soft};
  border-radius: 12px;
  padding: 0.6rem 0.75rem;
}}

div[data-testid="stExpander"] > details {{
  border: 1px solid {PALETTE.border_soft};
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
}}

div[data-testid="stAlert"] {{
  border-radius: 12px;
}}

.stButton > button,
.stDownloadButton > button {{
  border-radius: 10px;
  border: 1px solid {PALETTE.border_soft};
}}
</style>
        """,
        unsafe_allow_html=True,
    )
