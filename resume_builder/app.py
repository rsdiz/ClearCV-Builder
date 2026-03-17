"""Application entrypoint and page shell."""

import streamlit as st

from .data import init_session_state
from .ui import render_main_area, render_sidebar


def main():
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="ATS Resume Builder",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; }
        div[data-testid="stSidebar"] button {
            background: transparent;
            border: none;
            text-align: left;
            color: inherit;
            padding: 8px 12px;
            border-radius: 6px;
        }
        div[data-testid="stSidebar"] button:hover {
            background: rgba(26,108,240,0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_session_state()
    render_sidebar()
    render_main_area()
