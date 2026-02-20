import streamlit as st
import json
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def load_json(filename):
    with open(os.path.join(BASE_DIR, "data", filename), "r") as f:
        return json.load(f)


def ensure_data_loaded():
    """Load all data files into session state if not already loaded."""
    if "data_loaded" not in st.session_state:
        st.session_state.client_profile = load_json("client_profile.json")
        st.session_state.projects = load_json("projects.json")
        st.session_state.expenditures = load_json("expenditures.json")
        st.session_state.documentation = load_json("documentation_log.json")
        st.session_state.t661_form = load_json("t661_form_data.json")
        st.session_state.data_loaded = True
