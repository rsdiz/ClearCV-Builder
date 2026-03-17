"""Application entrypoint and page shell."""

import streamlit as st

from .data import init_session_state
from .ui import render_main_area, render_sidebar


def main():
    """Run the Streamlit application."""
    st.set_page_config(
        page_title="ClearCV Builder",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; }
        :root {
            --clearcv-accent: #1a6cf0;
            --clearcv-accent-strong: #0f4fc2;
            --clearcv-accent-soft: rgba(26,108,240,0.14);
            --clearcv-surface: rgba(255,255,255,0.78);
            --clearcv-surface-strong: rgba(255,255,255,0.92);
            --clearcv-surface-active: #f4f8ff;
            --clearcv-border: rgba(18,32,51,0.12);
            --clearcv-text: #122033;
            --clearcv-muted: #5f6b7a;
            --clearcv-progress: #122033;
            --clearcv-progress-muted: rgba(255,255,255,0.78);
            --clearcv-badge-empty-bg: #cbd5e1;
            --clearcv-badge-empty-text: #334155;
            --clearcv-pill-bg: #e8f0fe;
            --clearcv-pill-text: #1a6cf0;
        }
        [data-theme="dark"] {
            --clearcv-accent: #7ab2ff;
            --clearcv-accent-strong: #a9ccff;
            --clearcv-accent-soft: rgba(122,178,255,0.18);
            --clearcv-surface: rgba(15,23,42,0.72);
            --clearcv-surface-strong: rgba(15,23,42,0.86);
            --clearcv-surface-active: rgba(32,46,74,0.88);
            --clearcv-border: rgba(148,163,184,0.22);
            --clearcv-text: #f8fafc;
            --clearcv-muted: #cbd5e1;
            --clearcv-progress: #0f172a;
            --clearcv-progress-muted: rgba(255,255,255,0.72);
            --clearcv-badge-empty-bg: rgba(148,163,184,0.22);
            --clearcv-badge-empty-text: #e2e8f0;
            --clearcv-pill-bg: rgba(59,130,246,0.18);
            --clearcv-pill-text: #bfdbfe;
        }
        div[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, var(--clearcv-accent-soft), transparent 34%),
                linear-gradient(180deg, var(--clearcv-surface) 0%, var(--clearcv-surface-strong) 100%);
        }
        div[data-testid="stSidebar"] .stButton button,
        div[data-testid="stSidebar"] .stDownloadButton button {
            background: var(--clearcv-surface-strong);
            border: 1px solid var(--clearcv-border);
            text-align: left;
            color: var(--clearcv-text);
            padding: 0.65rem 0.8rem;
            border-radius: 12px;
            font-weight: 600;
            box-shadow: 0 8px 24px rgba(18,32,51,0.10);
        }
        div[data-testid="stSidebar"] .stButton button:hover,
        div[data-testid="stSidebar"] .stDownloadButton button:hover {
            border-color: var(--clearcv-accent-soft);
            color: var(--clearcv-accent-strong);
            background: var(--clearcv-surface);
        }
        div[data-testid="stSidebar"] .stButton button[kind="primary"] {
            background: var(--clearcv-accent);
            border-color: transparent;
            color: white;
        }
        div[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
            background: var(--clearcv-accent-strong);
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_session_state()
    render_sidebar()
    render_main_area()
