"""
Streamlit UI helpers — shared styling and reusable components.

Keeps ``app.py`` clean by centralising the dark theme CSS, metric
cards, section headers, loading spinners, etc.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------------
# Dark theme CSS
# ---------------------------------------------------------------------------
DARK_CSS = """
<style>
/* ----- Base ----- */
:root {
    --bg-primary: #0e1117;
    --bg-secondary: #161b22;
    --bg-card: #1b2230;
    --bg-hover: #242c3b;
    --border: #2a323f;
    --text-primary: #e8eef5;
    --text-secondary: #9aa6b2;
    --accent-cyan: #00d2ff;
    --accent-purple: #7c4dff;
    --accent-green: #00e676;
    --accent-orange: #ffab40;
    --accent-pink: #ff4081;
    --accent-red: #ff5252;
}

.stApp {
    background: linear-gradient(135deg, #0a0e14 0%, #0e1117 50%, #131923 100%);
    color: var(--text-primary);
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ----- Sidebar ----- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080c12 0%, #0e1117 60%, #111720 100%);
    border-right: 1px solid #1e2733;
    min-width: 260px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--accent-cyan);
}

/* ----- Sidebar hide default radio widget ----- */
section[data-testid="stSidebar"] [data-testid="stRadio"] {
    display: none !important;
}

/* ----- Sidebar nav buttons ----- */
.nav-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    padding: 11px 16px;
    margin-bottom: 4px;
    border-radius: 10px;
    border: 1px solid transparent;
    background: transparent;
    color: #9aa6b2;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s ease;
    letter-spacing: 0.01em;
    line-height: 1.2;
}
.nav-btn:hover {
    background: rgba(0, 210, 255, 0.08);
    border-color: rgba(0, 210, 255, 0.2);
    color: #e8eef5;
    transform: translateX(3px);
}
.nav-btn.active {
    background: linear-gradient(135deg, rgba(0,210,255,0.18) 0%, rgba(124,77,255,0.18) 100%);
    border-color: rgba(0, 210, 255, 0.45);
    color: #ffffff;
    font-weight: 700;
    box-shadow: 0 2px 12px rgba(0, 210, 255, 0.12);
}
.nav-btn.active .nav-icon {
    filter: drop-shadow(0 0 6px rgba(0, 210, 255, 0.7));
}
.nav-icon {
    font-size: 1.15rem;
    min-width: 22px;
    text-align: center;
}
.nav-label {
    flex: 1;
}
.nav-indicator {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent-cyan);
    box-shadow: 0 0 6px rgba(0,210,255,0.8);
    flex-shrink: 0;
}

/* ----- Sidebar section label ----- */
.sidebar-section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4a5568;
    padding: 12px 16px 6px 16px;
    margin-bottom: 2px;
}

/* ----- Status badge ----- */
.status-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 16px;
    border-radius: 8px;
    margin-bottom: 4px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    font-size: 0.82rem;
    color: #9aa6b2;
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.status-dot.ok { background: #00e676; box-shadow: 0 0 5px rgba(0,230,118,0.6); }
.status-dot.warn { background: #ffab40; box-shadow: 0 0 5px rgba(255,171,64,0.6); }

/* ----- Headers ----- */
h1, h2, h3, h4 {
    color: #00d2ff !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

h1 code, h2 code, h3 code, h4 code {
    background: rgba(0,210,255,0.15) !important;
    color: #00d2ff !important;
    padding: 2px 8px !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', 'Consolas', monospace !important;
    font-size: 0.9em !important;
}

/* ----- Metric cards ----- */
div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 22px rgba(0, 210, 255, 0.15);
    border-color: var(--accent-cyan);
}
div[data-testid="stMetric"] label {
    color: var(--text-secondary) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--accent-cyan) !important;
    font-size: 1.7rem !important;
    font-weight: 700;
}

/* ----- Buttons ----- */
.stButton > button {
    background: linear-gradient(135deg, #00d2ff 0%, #7c4dff 100%) !important;
    color: #0a0e14 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(0, 210, 255, 0.35) !important;
}
.stButton > button:active {
    transform: translateY(0);
}

/* ----- Inputs ----- */
.stTextInput > div > input,
.stNumberInput > div > input,
.stSelectbox > div > div,
.stTextArea > div > textarea {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}
.stTextInput > div > input:focus,
.stNumberInput > div > input:focus,
.stSelectbox > div > div:focus,
.stTextArea > div > textarea:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 2px rgba(0, 210, 255, 0.2) !important;
}

/* ----- Sliders ----- */
.stSlider > div > div > div > div {
    background: var(--accent-cyan) !important;
}

/* ----- Tabs ----- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--bg-secondary);
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00d2ff 0%, #7c4dff 100%) !important;
    color: #0a0e14 !important;
}

/* ----- Dataframes / tables ----- */
.dataframe, .stDataFrame, .stTable {
    background: var(--bg-card) !important;
    border-radius: 10px;
    overflow: hidden;
}
table.dataframe tr, table.dataframe th, table.dataframe td {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
}

/* ----- Cards / containers ----- */
.custom-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 16px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    transition: all 0.25s ease;
}
.custom-card:hover {
    border-color: var(--accent-cyan);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 210, 255, 0.12);
}
.custom-card h3 {
    margin-top: 0;
    color: var(--accent-cyan) !important;
    -webkit-text-fill-color: var(--accent-cyan) !important;
}

.pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 6px;
    background: rgba(0, 210, 255, 0.15);
    color: var(--accent-cyan);
    border: 1px solid rgba(0, 210, 255, 0.3);
}
.pill.purple { background: rgba(124, 77, 255, 0.15); color: var(--accent-purple); border-color: rgba(124, 77, 255, 0.3); }
.pill.green  { background: rgba(0, 230, 118, 0.15); color: var(--accent-green);  border-color: rgba(0, 230, 118, 0.3); }
.pill.orange { background: rgba(255, 171, 64, 0.15); color: var(--accent-orange); border-color: rgba(255, 171, 64, 0.3); }
.pill.pink   { background: rgba(255, 64, 129, 0.15); color: var(--accent-pink);   border-color: rgba(255, 64, 129, 0.3); }

/* ----- Divider ----- */
hr {
    border-color: var(--border) !important;
    margin: 24px 0 !important;
}

/* ----- Footer ----- */
.app-footer {
    margin-top: 48px;
    padding: 20px 0;
    border-top: 1px solid var(--border);
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.85rem;
}

/* ----- Spinner ----- */
.stSpinner > div {
    border-top-color: var(--accent-cyan) !important;
}

/* ----- Code blocks ----- */
.stCodeBlock {
    border-radius: 10px;
    overflow: hidden;
}

/* ----- Hide streamlit branding ----- */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* ----- Animated gradient bar ----- */
.gradient-bar {
    height: 4px;
    background: linear-gradient(90deg, #00d2ff 0%, #7c4dff 50%, #00e676 100%);
    border-radius: 2px;
    margin-bottom: 18px;
}
</style>
"""


def apply_dark_theme() -> None:
    """Inject the dark theme CSS into the Streamlit app."""
    st.markdown(DARK_CSS, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """Render a styled section header with optional subtitle."""
    st.markdown('<div class="gradient-bar"></div>', unsafe_allow_html=True)
    if icon:
        st.markdown(f"## {icon}  {title}")
    else:
        st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<p style='color:#9aa6b2;margin-top:-8px;'>{subtitle}</p>",
                    unsafe_allow_html=True)


def metric_card(label: str, value: Any, delta: str = "", color: str = "#00d2ff") -> None:
    """Render a single metric value as a styled card."""
    color_map = {
        "cyan": "#00d2ff",
        "purple": "#7c4dff",
        "green": "#00e676",
        "orange": "#ffab40",
        "pink": "#ff4081",
    }
    c = color_map.get(color, color)
    st.markdown(
        f"""
        <div class='custom-card' style='text-align:center;'>
            <div style='color:#9aa6b2;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;'>{label}</div>
            <div style='color:{c};font-size:2.1rem;font-weight:700;margin-top:6px;'>{value}</div>
            {f"<div style='color:#9aa6b2;font-size:0.8rem;margin-top:4px;'>{delta}</div>" if delta else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str, color: str = "cyan") -> None:
    """Render a custom titled card."""
    color_map = {
        "cyan": "#00d2ff", "purple": "#7c4dff", "green": "#00e676",
        "orange": "#ffab40", "pink": "#ff4081", "red": "#ff5252",
    }
    c = color_map.get(color, color)
    st.markdown(
        f"""
        <div class='custom-card'>
            <h3 style='color:{c};margin-top:0;'>{title}</h3>
            <div style='color:#e8eef5;line-height:1.6;'>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(text: str, color: str = "cyan") -> str:
    """Return HTML for a small pill badge."""
    return f"<span class='pill {color}'>{text}</span>"


def footer() -> None:
    """Render a small footer."""
    st.markdown(
        "<div class='app-footer'>"
        "Customer Segmentation & Intelligent Classification System  •  "
        "Built with ❤️ using Python, scikit-learn & Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )
