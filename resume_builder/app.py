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
        .stApp {
            background:
                radial-gradient(circle at 12% 18%, rgba(56, 189, 248, 0.16), transparent 24%),
                radial-gradient(circle at 88% 12%, rgba(45, 212, 191, 0.12), transparent 22%),
                radial-gradient(circle at 50% 100%, rgba(59, 130, 246, 0.14), transparent 32%),
                linear-gradient(180deg, #04111f 0%, #071829 42%, #030b15 100%);
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1320px;
        }
        :root {
            --clearcv-accent: #59d8ff;
            --clearcv-accent-strong: #8cf0ff;
            --clearcv-accent-soft: rgba(89, 216, 255, 0.18);
            --clearcv-surface: rgba(8, 18, 32, 0.76);
            --clearcv-surface-strong: rgba(10, 23, 39, 0.9);
            --clearcv-surface-active: rgba(16, 37, 59, 0.96);
            --clearcv-border: rgba(111, 214, 255, 0.18);
            --clearcv-text: #e8f7ff;
            --clearcv-muted: #91adc5;
            --clearcv-progress: rgba(6, 19, 33, 0.96);
            --clearcv-progress-muted: rgba(204, 240, 255, 0.7);
            --clearcv-badge-empty-bg: rgba(120, 145, 170, 0.16);
            --clearcv-badge-empty-text: #d2e7f6;
            --clearcv-pill-bg: rgba(35, 111, 150, 0.24);
            --clearcv-pill-text: #92ecff;
            --clearcv-shadow: 0 24px 60px rgba(1, 8, 15, 0.45);
            --clearcv-input-bg: rgba(4, 13, 24, 0.88);
            --clearcv-grid: rgba(120, 202, 235, 0.07);
        }
        [data-theme="dark"] {
            --clearcv-surface: rgba(8, 18, 32, 0.74);
            --clearcv-surface-strong: rgba(10, 23, 39, 0.92);
            --clearcv-surface-active: rgba(15, 35, 55, 0.98);
            --clearcv-border: rgba(111, 214, 255, 0.2);
            --clearcv-input-bg: rgba(4, 13, 24, 0.9);
        }
        [data-theme="light"] {
            --clearcv-surface: rgba(236, 248, 255, 0.8);
            --clearcv-surface-strong: rgba(245, 251, 255, 0.92);
            --clearcv-surface-active: rgba(224, 244, 255, 0.96);
            --clearcv-border: rgba(14, 112, 160, 0.18);
            --clearcv-text: #082235;
            --clearcv-muted: #4d6980;
            --clearcv-progress: rgba(6, 28, 48, 0.92);
            --clearcv-progress-muted: rgba(224, 245, 255, 0.78);
            --clearcv-badge-empty-bg: rgba(150, 184, 208, 0.22);
            --clearcv-badge-empty-text: #27475e;
            --clearcv-pill-bg: rgba(35, 111, 150, 0.12);
            --clearcv-pill-text: #0e698f;
            --clearcv-shadow: 0 24px 60px rgba(20, 66, 99, 0.16);
            --clearcv-input-bg: rgba(255, 255, 255, 0.88);
            --clearcv-grid: rgba(14, 112, 160, 0.06);
        }
        h1, h2, h3, h4, .stMarkdown p, .stCaption {
            color: var(--clearcv-text);
        }
        div[data-testid="stAppViewContainer"] > .main {
            background-image:
                linear-gradient(var(--clearcv-grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--clearcv-grid) 1px, transparent 1px);
            background-size: 72px 72px;
        }
        div[data-testid="stHeader"] {
            background: transparent;
        }
        div[data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, rgba(89, 216, 255, 0.16), transparent 34%),
                linear-gradient(180deg, rgba(5, 15, 26, 0.96) 0%, rgba(4, 11, 20, 0.98) 100%);
            border-right: 1px solid var(--clearcv-border);
        }
        div[data-testid="stSidebar"] > div:first-child {
            background-image:
                linear-gradient(var(--clearcv-grid) 1px, transparent 1px),
                linear-gradient(90deg, var(--clearcv-grid) 1px, transparent 1px);
            background-size: 62px 62px;
        }
        div[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        div[data-testid="stSidebar"] label,
        div[data-testid="stSidebar"] .stCaption {
            color: var(--clearcv-text);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(180deg, var(--clearcv-surface) 0%, var(--clearcv-surface-strong) 100%);
            border: 1px solid var(--clearcv-border);
            border-radius: 22px;
            box-shadow: var(--clearcv-shadow);
            backdrop-filter: blur(18px);
        }
        div[data-testid="stForm"] {
            background: linear-gradient(180deg, rgba(8, 18, 32, 0.42) 0%, rgba(8, 18, 32, 0.24) 100%);
            border: 1px solid var(--clearcv-border);
            border-radius: 22px;
            padding: 1rem 1rem 0.3rem;
            backdrop-filter: blur(16px);
        }
        details[data-testid="stExpander"] {
            background: linear-gradient(180deg, rgba(8, 18, 32, 0.5) 0%, rgba(8, 18, 32, 0.22) 100%);
            border: 1px solid var(--clearcv-border);
            border-radius: 20px;
            overflow: hidden;
        }
        details[data-testid="stExpander"] summary {
            background: rgba(89, 216, 255, 0.05);
        }
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        .stTextInput input,
        .stTextArea textarea {
            background: var(--clearcv-input-bg) !important;
            border: 1px solid var(--clearcv-border) !important;
            color: var(--clearcv-text) !important;
            border-radius: 16px !important;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
        }
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: var(--clearcv-muted) !important;
        }
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        .stTextArea textarea:focus,
        .stTextInput input:focus {
            border-color: var(--clearcv-accent) !important;
            box-shadow: 0 0 0 1px var(--clearcv-accent), 0 0 0 6px rgba(89, 216, 255, 0.08) !important;
        }
        .stButton button,
        .stDownloadButton button {
            border-radius: 14px;
            border: 1px solid var(--clearcv-border);
            background: linear-gradient(180deg, rgba(9, 24, 40, 0.96) 0%, rgba(6, 16, 29, 0.96) 100%);
            color: var(--clearcv-text);
            font-weight: 600;
            letter-spacing: 0.01em;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
        }
        .stButton button:hover,
        .stDownloadButton button:hover {
            border-color: rgba(140, 240, 255, 0.38);
            color: var(--clearcv-accent-strong);
            transform: translateY(-1px);
        }
        .stButton button[kind="primary"],
        .stDownloadButton button[kind="primary"] {
            background: linear-gradient(135deg, #35d7ff 0%, #1f8fff 50%, #62f4d6 100%);
            color: #02101a;
            border: none;
            box-shadow: 0 16px 32px rgba(53, 215, 255, 0.24);
        }
        .stButton button[kind="primary"]:hover,
        .stDownloadButton button[kind="primary"]:hover {
            color: #02101a;
            filter: brightness(1.04);
        }
        div[data-testid="stSidebar"] .stButton button,
        div[data-testid="stSidebar"] .stDownloadButton button {
            text-align: left;
            padding: 0.72rem 0.84rem;
        }
        div[data-testid="stProgressBar"] > div > div {
            background: linear-gradient(90deg, #35d7ff 0%, #1f8fff 55%, #62f4d6 100%);
        }
        .clearcv-shell {
            position: relative;
            overflow: hidden;
            padding: 1.35rem 1.5rem;
            border-radius: 26px;
            border: 1px solid var(--clearcv-border);
            background:
                radial-gradient(circle at top right, rgba(98, 244, 214, 0.14), transparent 28%),
                linear-gradient(140deg, rgba(7, 24, 39, 0.94) 0%, rgba(6, 17, 30, 0.88) 100%);
            box-shadow: var(--clearcv-shadow);
            margin-bottom: 1rem;
        }
        .clearcv-shell::after {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.05) 48%, transparent 100%);
            transform: translateX(-100%);
            animation: clearcv-scan 9s linear infinite;
            pointer-events: none;
        }
        @keyframes clearcv-scan {
            to { transform: translateX(100%); }
        }
        .clearcv-shell-kicker,
        .clearcv-panel-kicker,
        .clearcv-stat-label,
        .clearcv-sidebar-kicker {
            color: var(--clearcv-muted);
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.72rem;
            margin: 0;
        }
        .clearcv-shell h1,
        .clearcv-panel-title,
        .clearcv-sidebar-title {
            margin: 0.2rem 0 0 0;
            color: var(--clearcv-text);
        }
        .clearcv-shell-grid,
        .clearcv-sidebar-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 0.8rem;
            margin-top: 1.1rem;
        }
        .clearcv-stat,
        .clearcv-sidebar-chip {
            border: 1px solid var(--clearcv-border);
            border-radius: 18px;
            padding: 0.85rem 0.95rem;
            background: rgba(89, 216, 255, 0.05);
            backdrop-filter: blur(14px);
        }
        .clearcv-stat-value,
        .clearcv-sidebar-chip strong {
            display: block;
            color: var(--clearcv-accent-strong);
            font-size: 1.1rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }
        .clearcv-panel-intro,
        .clearcv-sidebar-panel,
        .clearcv-preview-panel {
            padding: 1rem 1.1rem;
            border-radius: 22px;
            border: 1px solid var(--clearcv-border);
            background: linear-gradient(180deg, rgba(10, 23, 39, 0.82) 0%, rgba(7, 18, 30, 0.72) 100%);
            box-shadow: var(--clearcv-shadow);
            backdrop-filter: blur(18px);
            margin-bottom: 0.9rem;
        }
        .clearcv-panel-copy,
        .clearcv-sidebar-copy {
            color: var(--clearcv-muted);
            margin: 0.35rem 0 0 0;
            font-size: 0.95rem;
            line-height: 1.55;
        }
        .clearcv-preview-panel ul {
            margin: 0.4rem 0 0 1rem;
        }
        .clearcv-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, var(--clearcv-border) 15%, var(--clearcv-border) 85%, transparent 100%);
            margin: 0.85rem 0 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_session_state()
    render_sidebar()
    render_main_area()
