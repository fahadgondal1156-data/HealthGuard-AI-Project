from __future__ import annotations

import html
import os
import time
from datetime import datetime
from typing import Any, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# =============================================================================
# HealthGuard-AI Premium Dashboard — Final v3.0
# =============================================================================
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("DASHBOARD_REQUEST_TIMEOUT", "20"))

st.set_page_config(
    page_title="HealthGuard-AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Theme / CSS
# -----------------------------------------------------------------------------
GLOBAL_CSS = r"""
<style>
:root {
  --hg-bg: #f4f7fb;
  --hg-surface: #ffffff;
  --hg-surface-2: #f8fbff;
  --hg-text: #172033;
  --hg-muted: #6f7b91;
  --hg-primary: #1167d8;
  --hg-primary-2: #00a6c7;
  --hg-accent: #6f5bf6;
  --hg-success: #1aa981;
  --hg-warning: #f0a43a;
  --hg-danger: #e05260;
  --hg-border: #e4eaf2;
  --hg-shadow: 0 14px 35px rgba(20, 48, 86, .09);
  --hg-radius: 18px;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--hg-bg);
  color: var(--hg-text);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { right: 1rem; }
#MainMenu, footer { visibility: hidden; }

.block-container {
  max-width: 1580px;
  padding-top: 1.15rem;
  padding-bottom: 2.75rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0c1f38 0%, #102b4c 58%, #0d223c 100%);
  border-right: 0;
}
[data-testid="stSidebar"] * { color: #edf5ff; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #dbe8f8; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.11); }
[data-testid="stSidebar"] .stButton > button {
  background: linear-gradient(180deg, rgba(34,79,121,.86), rgba(21,57,94,.88)) !important;
  color: #edf7ff !important;
  border: 1px solid rgba(126,190,255,.18) !important;
  box-shadow: 0 8px 18px rgba(2,13,27,.16) !important;
  min-height: 44px !important;
  justify-content: flex-start !important;
  padding-left: .9rem !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: linear-gradient(135deg, #1268d8, #0d91ba 65%, #554ed8) !important;
  color: #ffffff !important;
  border-color: rgba(132,211,255,.55) !important;
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(0,114,218,.24) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: linear-gradient(135deg,#1675e7,#0ca8c8 64%,#6758ef) !important;
  color:#fff !important;
  border-color:rgba(173,231,255,.55) !important;
  box-shadow:0 11px 26px rgba(16,119,220,.28) !important;
}
[data-testid="stSidebar"] .stButton > button:disabled {
  opacity:.55 !important;
}

.hg-side-brand {
  display:flex; gap:.75rem; align-items:center; padding:.4rem .15rem .85rem .15rem;
}
.hg-side-logo {
  width:42px; height:42px; border-radius:13px; display:grid; place-items:center;
  background:linear-gradient(135deg,#20b9d9,#2267e8 55%,#765af6);
  box-shadow:0 8px 22px rgba(0,157,255,.30); font-size:21px;
}
.hg-side-title { font-size:1.08rem; font-weight:800; letter-spacing:-.02em; }
.hg-side-sub { font-size:.76rem; opacity:.72; margin-top:1px; }
.hg-status-pill {
  display:inline-flex; align-items:center; gap:.45rem; padding:.38rem .7rem;
  border-radius:999px; background:rgba(62,215,164,.13); border:1px solid rgba(62,215,164,.22);
  color:#bff7df !important; font-size:.78rem; font-weight:700;
}
.hg-status-dot { width:8px; height:8px; border-radius:50%; background:#31d59a; box-shadow:0 0 0 5px rgba(49,213,154,.12); }

/* Top navigation */
.hg-topbrand { padding-top:.12rem; }
.hg-topbrand h2 { margin:0; font-size:1.36rem; letter-spacing:-.035em; }
.hg-topbrand p { margin:.1rem 0 0; color:var(--hg-muted); font-size:.80rem; }

/* Cards */
.hg-panel, .hg-kpi, .hg-empty, .hg-activity-item {
  background:var(--hg-surface);
  border:1px solid var(--hg-border);
  border-radius:var(--hg-radius);
  box-shadow:var(--hg-shadow);
}
.hg-panel { padding:1.15rem 1.25rem; margin:.35rem 0 1rem 0; }
.hg-kpi { padding:1rem 1.05rem; min-height:116px; position:relative; overflow:hidden; }
.hg-kpi:after {
  content:""; position:absolute; width:92px; height:92px; right:-32px; top:-34px;
  border-radius:50%; background:linear-gradient(135deg,rgba(17,103,216,.10),rgba(111,91,246,.12));
}
.hg-kpi-label { color:var(--hg-muted); font-size:.76rem; text-transform:uppercase; letter-spacing:.055em; font-weight:750; }
.hg-kpi-value { color:var(--hg-text); font-weight:850; font-size:1.72rem; margin-top:.35rem; letter-spacing:-.035em; }
.hg-kpi-foot { color:var(--hg-muted); font-size:.77rem; margin-top:.2rem; }
.hg-kpi-icon { position:absolute; right:15px; bottom:12px; font-size:1.35rem; opacity:.68; }

.hg-section-title { font-size:1.08rem; font-weight:820; margin:.2rem 0 .2rem; letter-spacing:-.02em; }
.hg-section-sub { color:var(--hg-muted); font-size:.82rem; margin-bottom:.65rem; }
.hg-chip {
  display:inline-flex; padding:.32rem .62rem; border-radius:999px; border:1px solid var(--hg-border);
  font-size:.72rem; font-weight:750; background:#f7f9fc; color:#43506a; margin-right:.35rem;
}
.hg-risk-low { background:#eafaf4; color:#167a5d; border-color:#c9f0e3; }
.hg-risk-moderate { background:#fff7e8; color:#9a6816; border-color:#f5dfae; }
.hg-risk-high { background:#fff0eb; color:#b65c32; border-color:#f4caba; }
.hg-risk-critical { background:#ffedf0; color:#b9384e; border-color:#f4c2cb; }

.hg-activity-item { padding:.72rem .85rem; margin:.45rem 0; box-shadow:none; }
.hg-activity-main { font-weight:720; font-size:.86rem; }
.hg-activity-meta { color:var(--hg-muted); font-size:.73rem; margin-top:.18rem; }

.hg-empty { padding:1.35rem; text-align:center; box-shadow:none; border-style:dashed; }
.hg-empty-icon { font-size:2.1rem; }
.hg-empty-title { font-weight:800; margin-top:.35rem; }
.hg-empty-text { color:var(--hg-muted); font-size:.83rem; margin-top:.2rem; }

/* Inputs */
[data-testid="stForm"] {
  background:#fff; border:1px solid #e5ebf3; border-radius:18px; padding:1rem;
  box-shadow:0 10px 28px rgba(25,49,82,.06);
}
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
  border-radius:12px !important;
  border-color:#dce5ef !important;
  min-height:44px;
}
[data-testid="stTextInput"] input:focus {
  border-color:#3e86e8 !important;
  box-shadow:0 0 0 3px rgba(17,103,216,.10) !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius:12px !important;
  border:1px solid #d7e2ef !important;
  min-height:42px;
  font-weight:760 !important;
  transition:all .18s ease !important;
  background:linear-gradient(180deg,#ffffff 0%,#f7fbff 100%) !important;
  color:#173b63 !important;
  box-shadow:0 5px 15px rgba(28,55,90,.05);
}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
  border-color:#6da8e9 !important;
  color:#075dbf !important;
  background:#edf6ff !important;
  transform:translateY(-1px);
  box-shadow:0 9px 22px rgba(25,76,139,.11);
}
button[kind="primary"] {
  color:#fff !important;
  border:0 !important;
  background:linear-gradient(135deg,#1268d8,#0aa4c3 62%,#6558e8) !important;
  box-shadow:0 9px 25px rgba(17,103,216,.25) !important;
}
button[kind="primary"]:hover { color:#fff !important; filter:brightness(1.03); }

/* Tabs / radio */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:.45rem; }
[data-testid="stTabs"] button { border-radius:10px 10px 0 0; }

/* Dataframes */
[data-testid="stDataFrame"] { border:1px solid var(--hg-border); border-radius:14px; overflow:hidden; }

/* Login */
.hg-login-hero {
  position:relative; min-height:calc(100vh - 3.2rem); border-radius:30px; overflow:hidden; padding:clamp(2rem,3.2vw,4.2rem);
  color:#fff; box-shadow:0 28px 70px rgba(17,45,81,.22);
  background:
    radial-gradient(circle at 80% 15%, rgba(110,96,255,.45) 0, transparent 26%),
    radial-gradient(circle at 18% 82%, rgba(0,202,209,.28) 0, transparent 28%),
    linear-gradient(145deg,#071b31 0%,#0d3157 46%,#113a68 70%,#1a2f6b 100%);
}
.hg-login-grid {
  position:absolute; inset:0; opacity:.16;
  background-image:
    linear-gradient(rgba(255,255,255,.18) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.18) 1px, transparent 1px);
  background-size:38px 38px;
  mask-image:linear-gradient(to bottom right,black,transparent 82%);
}
.hg-login-orb { position:absolute; border-radius:50%; filter:blur(.2px); border:1px solid rgba(255,255,255,.22); }
.hg-login-orb.o1 { width:190px;height:190px;right:-42px;top:96px;background:rgba(22,174,227,.09); }
.hg-login-orb.o2 { width:95px;height:95px;right:154px;top:54px;background:rgba(133,97,255,.11); }
.hg-login-ecg {
  position:absolute; left:0; right:0; bottom:145px; height:120px; opacity:.52;
}
.hg-login-net { position:absolute; right:28px; top:30px; width:300px; height:250px; opacity:.32; }
.hg-hero-badge {
  display:inline-flex; align-items:center; gap:.5rem; padding:.45rem .72rem; border-radius:999px;
  border:1px solid rgba(255,255,255,.18); background:rgba(255,255,255,.08); backdrop-filter:blur(10px);
  font-size:.75rem; font-weight:760;
}
.hg-hero-title { margin-top:clamp(4rem,10vh,8rem); font-size:clamp(3rem,4.3vw,5rem); line-height:1.01; letter-spacing:-.06em; font-weight:860; max-width:760px; }
.hg-hero-copy { max-width:660px; font-size:clamp(.95rem,1vw,1.14rem); line-height:1.72; color:rgba(235,246,255,.86); margin-top:1.2rem; }
.hg-hero-stats { display:flex; gap:.75rem; margin-top:2rem; flex-wrap:wrap; }
.hg-hero-stat { padding:.72rem .9rem; border-radius:15px; background:rgba(255,255,255,.075); border:1px solid rgba(255,255,255,.13); min-width:135px; }
.hg-hero-stat strong { display:block; font-size:1.08rem; }
.hg-hero-stat span { font-size:.7rem; color:rgba(235,246,255,.70); }
.hg-login-card {
  background:rgba(255,255,255,.96); border:1px solid #e2eaf3; border-radius:26px;
  padding:1.55rem 1.6rem 1rem; max-width:540px; margin:clamp(3rem,18vh,12rem) auto 0;
  box-shadow:0 26px 70px rgba(25,49,82,.16); backdrop-filter:blur(12px);
}
.hg-login-mark { display:flex; align-items:center; gap:.7rem; margin-bottom:.65rem; }
.hg-login-logo { width:48px;height:48px;border-radius:15px;display:grid;place-items:center;color:#fff;font-size:23px;background:linear-gradient(135deg,#18b3d3,#1e6ee6 55%,#705cf6);box-shadow:0 9px 25px rgba(23,113,220,.25); }
.hg-login-title { font-size:1.35rem; font-weight:850; letter-spacing:-.03em; }
.hg-login-sub { color:var(--hg-muted); font-size:.8rem; }

/* Responsive */
@media (min-width: 1650px) {
  .hg-login-card { max-width:590px; margin-top:20vh; }
  .hg-login-hero { min-height:calc(100vh - 4rem); }
}
@media (max-width: 1100px) {
  .hg-login-card { margin-top:7vh; }
  .hg-hero-title { margin-top:4.3rem; }
}
@media (max-width: 900px) {
  .block-container { padding-left:.85rem; padding-right:.85rem; }
  .hg-login-hero { min-height:500px; border-radius:22px; }
  .hg-hero-title { font-size:2.45rem; margin-top:3.25rem; }
  .hg-login-card { margin:1rem auto 0; max-width:100%; }
  .hg-kpi { min-height:104px; }
}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

RISK_COLORS = {
    "low": "#1aa981",
    "moderate": "#f0a43a",
    "high": "#ed7f46",
    "critical": "#e05260",
    "unknown": "#8a96aa",
}
NAV_OPTIONS = ["Overview", "Patients", "Alerts", "AI Analytics", "Security", "System"]
NAV_ICONS = {
    "Overview": "⌂",
    "Patients": "♡",
    "Alerts": "⚠",
    "AI Analytics": "◈",
    "Security": "⌁",
    "System": "⚙",
}

# -----------------------------------------------------------------------------
# Session / auth helpers
# -----------------------------------------------------------------------------
def ensure_state() -> None:
    defaults = {
        "token": None,
        "role": None,
        "username": None,
        "page": "Overview",
        "global_search": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def clear_auth() -> None:
    for key in ("token", "role", "username"):
        st.session_state[key] = None
    st.session_state["page"] = "Overview"


def auth_headers() -> dict[str, str]:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def role_allows(*roles: str) -> bool:
    return st.session_state.get("role") in roles


def navigate(page: str) -> None:
    if page in NAV_OPTIONS:
        st.session_state["page"] = page
        st.session_state["nav_workspace"] = page


ensure_state()

# -----------------------------------------------------------------------------
# API helpers
# -----------------------------------------------------------------------------
def api_request(
    method: str,
    path: str,
    *,
    show_error: bool = True,
    timeout: Optional[int] = None,
    **kwargs: Any,
) -> Optional[Any]:
    headers = kwargs.pop("headers", {}) or {}
    headers.update(auth_headers())
    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{path}",
            headers=headers,
            timeout=timeout or REQUEST_TIMEOUT,
            **kwargs,
        )
    except requests.exceptions.Timeout:
        if show_error:
            st.error("HealthGuard-AI API request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        if show_error:
            st.error(f"Cannot reach HealthGuard-AI API at {API_BASE_URL}.")
        return None
    except requests.RequestException as exc:
        if show_error:
            st.error(f"API request failed: {exc}")
        return None

    if response.status_code == 401:
        if st.session_state.get("token"):
            clear_auth()
            st.warning("Your session expired. Please sign in again.")
            st.rerun()
        if show_error:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            st.error(f"Authentication failed: {detail}")
        return None

    if response.status_code == 403:
        if show_error:
            st.warning("Your current role does not have permission for this action.")
        return None

    if not response.ok:
        if show_error:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            st.error(f"API HTTP {response.status_code}: {detail}")
        return None

    if not response.content:
        return {}
    try:
        return response.json()
    except ValueError:
        return response.text


def api_health() -> tuple[bool, str, Optional[float]]:
    started = time.perf_counter()
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        latency = (time.perf_counter() - started) * 1000
        if response.ok:
            data = response.json()
            return True, data.get("service", "HealthGuard-AI"), latency
        return False, f"HTTP {response.status_code}", latency
    except requests.RequestException as exc:
        return False, str(exc), None


# -----------------------------------------------------------------------------
# Formatting / rendering helpers
# -----------------------------------------------------------------------------
def fmt_float(value: Any, digits: int = 3) -> str:
    try:
        if value is None or pd.isna(value):
            return "—"
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "—"


def fmt_percent(value: Any, digits: int = 1) -> str:
    try:
        if value is None or pd.isna(value):
            return "—"
        return f"{float(value):.{digits}%}"
    except (TypeError, ValueError):
        return "—"


def safe_text(value: Any) -> str:
    return html.escape("—" if value is None else str(value))



def pretty_model_name(value: Any) -> str:
    raw = str(value or "Unknown").replace("_", " ").strip()
    known = {"xgboost": "XGBoost", "random forest": "Random Forest", "logistic": "Logistic Regression", "logistic regression": "Logistic Regression"}
    return known.get(raw.lower(), raw.title())

def kpi_card(label: str, value: Any, foot: str = "", icon: str = "•") -> None:
    st.markdown(
        f"""
        <div class="hg-kpi">
          <div class="hg-kpi-label">{safe_text(label)}</div>
          <div class="hg-kpi-value">{safe_text(value)}</div>
          <div class="hg-kpi-foot">{safe_text(foot)}</div>
          <div class="hg-kpi-icon">{icon}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, text: str) -> None:
    st.markdown(
        f"""
        <div class="hg-empty">
          <div class="hg-empty-icon">{icon}</div>
          <div class="hg-empty-title">{safe_text(title)}</div>
          <div class="hg-empty-text">{safe_text(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_chip(band: Any) -> str:
    band_str = str(band or "unknown").lower()
    css = f"hg-risk-{band_str}" if band_str in {"low", "moderate", "high", "critical"} else ""
    return f'<span class="hg-chip {css}">{html.escape(band_str.upper())}</span>'


def section_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="hg-section-title">{safe_text(title)}</div>'
        + (f'<div class="hg-section-sub">{safe_text(subtitle)}</div>' if subtitle else ""),
        unsafe_allow_html=True,
    )


def styled_plot(fig: go.Figure, height: int = 330) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=18, r=18, t=52, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#33405a"),
        title_font=dict(size=15, color="#172033"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#edf1f6", zeroline=False)
    return fig


def activity_feed(events: list[dict[str, Any]], limit: int = 6) -> None:
    if not events:
        empty_state("◎", "No recent activity", "Audit events will appear here as users interact with the platform.")
        return
    for event in events[:limit]:
        action = safe_text(event.get("action", "EVENT"))
        actor = safe_text(event.get("actor", "system"))
        resource = safe_text(event.get("resource", ""))
        result = safe_text(event.get("result", "success"))
        when = safe_text(event.get("time", ""))
        suffix = f" • {resource}" if resource and resource != "—" else ""
        st.markdown(
            f"""
            <div class="hg-activity-item">
              <div class="hg-activity-main">{action}</div>
              <div class="hg-activity-meta">{actor}{suffix} · {result} · {when}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def login_screen() -> None:
    # Hide sidebar while unauthenticated.
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display:none !important;}
        [data-testid="stAppViewContainer"] > .main {margin-left:0 !important;}
        [data-testid="stAppViewContainer"] {
          background:
            radial-gradient(circle at 88% 9%, rgba(77,125,255,.12), transparent 23%),
            radial-gradient(circle at 10% 88%, rgba(0,188,194,.09), transparent 28%),
            #f2f6fb !important;
        }
        [data-testid="stAppViewContainer"] .block-container {
          max-width:none !important;
          width:100% !important;
          padding:1.6rem clamp(1rem,3vw,4rem) !important;
          margin:0 !important;
          min-height:100vh !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.markdown(
            """
            <div class="hg-login-hero">
              <div class="hg-login-grid"></div>
              <div class="hg-login-orb o1"></div>
              <div class="hg-login-orb o2"></div>
              <div class="hg-hero-badge">✦ Secure AI-assisted patient monitoring</div>
              <svg class="hg-login-net" viewBox="0 0 300 250" xmlns="http://www.w3.org/2000/svg">
                <g stroke="#87e8ff" stroke-width="1.2" opacity=".65">
                  <path d="M35 55 L110 30 L168 78 L247 48 M35 55 L80 132 L168 78 L210 150 L265 202 M80 132 L42 205 M80 132 L150 198 L210 150 M110 30 L150 198 M168 78 L265 202"/>
                </g>
                <g fill="#b7f6ff" stroke="#ffffff" stroke-width="1">
                  <circle cx="35" cy="55" r="7"/><circle cx="110" cy="30" r="6"/><circle cx="168" cy="78" r="9"/>
                  <circle cx="247" cy="48" r="6"/><circle cx="80" cy="132" r="8"/><circle cx="210" cy="150" r="7"/>
                  <circle cx="42" cy="205" r="5"/><circle cx="150" cy="198" r="8"/><circle cx="265" cy="202" r="6"/>
                </g>
              </svg>
              <div class="hg-hero-title">Clinical intelligence,<br/>made explainable.</div>
              <div class="hg-hero-copy">
                HealthGuard-AI unifies remote physiological monitoring, personalized risk estimation,
                anomaly detection, explainable AI, alerts, and security auditing in one research platform.
              </div>
              <div class="hg-hero-stats">
                <div class="hg-hero-stat"><strong>24 / 48 h</strong><span>Early-warning horizons</span></div>
                <div class="hg-hero-stat"><strong>XAI</strong><span>Explainable predictions</span></div>
                <div class="hg-hero-stat"><strong>RBAC</strong><span>Secure clinical access</span></div>
              </div>
              <svg class="hg-login-ecg" viewBox="0 0 1200 160" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
                <defs><linearGradient id="ecg" x1="0" x2="1"><stop stop-color="#4af0d1"/><stop offset=".55" stop-color="#57c8ff"/><stop offset="1" stop-color="#9a86ff"/></linearGradient></defs>
                <path d="M0 92 L150 92 L195 92 L220 74 L245 111 L274 22 L302 130 L336 92 L450 92 L485 92 L510 72 L536 112 L564 31 L592 126 L625 92 L760 92 L795 92 L821 70 L850 111 L880 25 L907 131 L942 92 L1200 92" fill="none" stroke="url(#ecg)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="hg-login-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="hg-login-mark">
              <div class="hg-login-logo">🛡</div>
              <div><div class="hg-login-title">HealthGuard-AI</div><div class="hg-login-sub">Secure research workspace</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### Welcome back")
        st.caption("Sign in to access patient monitoring, AI analytics, and security operations.")
        with st.form("hg_login_form", clear_on_submit=False):
            username = st.text_input("Username", value="healthguard", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign in securely", type="primary", use_container_width=True)
        if submitted:
            username = username.strip()
            if not username or not password:
                st.error("Enter both username and password.")
            else:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        json={"username": username, "password": password},
                        timeout=REQUEST_TIMEOUT,
                    )
                    if response.ok:
                        data = response.json()
                        st.session_state["token"] = data["access_token"]
                        st.session_state["role"] = data.get("role", "")
                        st.session_state["username"] = username
                        st.session_state["page"] = "Overview"
                        st.success("Authentication successful.")
                        st.rerun()
                    else:
                        try:
                            detail = response.json().get("detail", response.text)
                        except Exception:
                            detail = response.text
                        st.error(f"Sign-in failed (HTTP {response.status_code}): {detail}")
                except requests.RequestException as exc:
                    st.error(f"Cannot reach HealthGuard-AI API: {exc}")

        ok, _, latency = api_health()
        status = "Online" if ok else "Unavailable"
        status_color = "#1aa981" if ok else "#e05260"
        latency_text = f" · {latency:.0f} ms" if latency is not None else ""
        st.markdown(
            f'<div style="margin-top:.75rem;padding:.65rem .8rem;border-radius:12px;background:#f7f9fc;border:1px solid #e6ebf2;font-size:.78rem;color:#68758a;">'
            f'<span style="color:{status_color};font-weight:800;">● {status}</span>{latency_text} &nbsp;·&nbsp; Encrypted API session</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Research prototype — not a medical diagnostic device.")


def sidebar_system(metadata: dict[str, Any] | None, api_ok: bool, latency: Optional[float]) -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="hg-side-brand">
              <div class="hg-side-logo">🛡</div>
              <div><div class="hg-side-title">HealthGuard-AI</div><div class="hg-side-sub">Clinical AI Command Center</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if api_ok:
            st.markdown('<div class="hg-status-pill"><span class="hg-status-dot"></span> API operational</div>', unsafe_allow_html=True)
        else:
            st.error("API unavailable")
        st.markdown("&nbsp;", unsafe_allow_html=True)
        st.caption("SESSION")
        st.write(f"**{st.session_state.get('username', '—')}**")
        st.caption(f"Role · {str(st.session_state.get('role', '—')).upper()}")
        if latency is not None:
            st.caption(f"API latency · {latency:.0f} ms")
        st.divider()
        st.caption("AI MODEL")
        if metadata:
            st.write(f"**{pretty_model_name(metadata.get('best_model'))}**")
            st.caption(f"Horizon · {metadata.get('horizon_hours', '—')}h")
            st.caption(f"Threshold · {fmt_float(metadata.get('threshold'), 3)}")
        else:
            st.caption("Model metadata unavailable")
        st.divider()
        st.caption("QUICK ACTIONS")
        current_page = st.session_state.get("page", "Overview")
        st.button("⌂  Overview", key="side_overview", use_container_width=True, type="primary" if current_page == "Overview" else "secondary", on_click=navigate, args=("Overview",))
        st.button("♡  Patient Monitor", key="side_patients", use_container_width=True, type="primary" if current_page == "Patients" else "secondary", on_click=navigate, args=("Patients",))
        if role_allows("admin", "clinician", "auditor"):
            st.button("⚠  Alert Center", key="side_alerts", use_container_width=True, type="primary" if current_page == "Alerts" else "secondary", on_click=navigate, args=("Alerts",))
        st.button("◈  AI Analytics", key="side_ai", use_container_width=True, type="primary" if current_page == "AI Analytics" else "secondary", on_click=navigate, args=("AI Analytics",))
        if role_allows("admin", "auditor"):
            st.button("⌁  Security Audit", key="side_security", use_container_width=True, type="primary" if current_page == "Security" else "secondary", on_click=navigate, args=("Security",))
        st.button("⚙  System", key="side_system", use_container_width=True, type="primary" if current_page == "System" else "secondary", on_click=navigate, args=("System",))
        st.divider()
        st.caption("HealthGuard-AI v3.0 Final UI")
        st.caption("Secure · Explainable · Auditable")


def top_navigation(open_alerts: list[dict[str, Any]], api_ok: bool) -> None:
    c_brand, c_nav, c_search, c_notify, c_user = st.columns([2.15, 1.55, 2.25, .65, .75], gap="small")
    with c_brand:
        st.markdown(
            '<div class="hg-topbrand"><h2>HealthGuard-AI</h2><p>Remote patient intelligence & security</p></div>',
            unsafe_allow_html=True,
        )
    with c_nav:
        current = st.session_state.get("page", "Overview")
        if current not in NAV_OPTIONS:
            current = "Overview"
        selected = st.selectbox(
            "Workspace",
            NAV_OPTIONS,
            index=NAV_OPTIONS.index(current),
            key="nav_workspace",
            label_visibility="collapsed",
            format_func=lambda x: f"{NAV_ICONS[x]}  {x}",
        )
        if selected != st.session_state.get("page"):
            st.session_state["page"] = selected
            st.rerun()
    with c_search:
        st.text_input(
            "Search patients",
            placeholder="Search patient ID…",
            key="global_search",
            label_visibility="collapsed",
        )
    with c_notify:
        with st.popover(f"🔔 {len(open_alerts)}", use_container_width=True):
            st.markdown("**Notifications**")
            if not role_allows("admin", "clinician", "auditor"):
                st.caption("Alert notifications are restricted for this role.")
            elif not open_alerts:
                st.success("No open alerts")
            else:
                for alert in open_alerts[:5]:
                    st.markdown(
                        f"**{safe_text(str(alert.get('severity', 'alert')).upper())}** · {safe_text(alert.get('patient_id'))}  \n"
                        f"<small>{safe_text(alert.get('created_at'))}</small>",
                        unsafe_allow_html=True,
                    )
                st.button("Open Alert Center", key="notify_open_alerts", use_container_width=True, on_click=navigate, args=("Alerts",))
    with c_user:
        with st.popover("👤", use_container_width=True):
            st.markdown(f"**{safe_text(st.session_state.get('username'))}**", unsafe_allow_html=True)
            st.caption(f"Role: {st.session_state.get('role', '—')}")
            st.caption("API: Online" if api_ok else "API: Offline")
            if st.button("Logout", key="profile_logout", use_container_width=True):
                clear_auth()
                st.rerun()

    q1, q2, q3, q4, q5, spacer = st.columns([1, 1, 1, 1, 1, 4], gap="small")
    q1.button("↻ Refresh", key="quick_refresh", use_container_width=True, on_click=lambda: None)
    q2.button("♡ Patients", key="quick_patients", use_container_width=True, on_click=navigate, args=("Patients",))
    if role_allows("admin", "clinician", "auditor"):
        q3.button("⚠ Alerts", key="quick_alerts", use_container_width=True, on_click=navigate, args=("Alerts",))
    else:
        q3.button("⚠ Alerts", key="quick_alerts_disabled", use_container_width=True, disabled=True)
    q4.button("◈ AI Model", key="quick_ai", use_container_width=True, on_click=navigate, args=("AI Analytics",))
    q5.button("⚙ System", key="quick_system", use_container_width=True, on_click=navigate, args=("System",))
    st.divider()


# -----------------------------------------------------------------------------
# Data loading (authenticated)
# -----------------------------------------------------------------------------
if not st.session_state.get("token"):
    login_screen()
    st.stop()

api_ok, api_name, api_latency = api_health()
metadata = api_request("GET", "/model/metadata", show_error=False) or {}
patients = api_request("GET", "/monitoring/patients", show_error=False) or []
alerts: list[dict[str, Any]] = []
if role_allows("admin", "clinician", "auditor"):
    alerts = api_request("GET", "/monitoring/alerts", show_error=False) or []
open_alerts = [a for a in alerts if str(a.get("status", "")).lower() == "open"]
audit_events: list[dict[str, Any]] = []
if role_allows("admin", "auditor"):
    audit_events = api_request("GET", "/security/audit?limit=200", show_error=False) or []

sidebar_system(metadata, api_ok, api_latency)
top_navigation(open_alerts, api_ok)
page = st.session_state.get("page", "Overview")

# -----------------------------------------------------------------------------
# Overview
# -----------------------------------------------------------------------------
if page == "Overview":
    section_header("Clinical Intelligence Overview", "Live operational snapshot of monitored patients, AI risk, alerts, and platform activity.")

    patient_df = pd.DataFrame(patients) if patients else pd.DataFrame()
    if not patient_df.empty and "latest_risk" in patient_df:
        patient_df["latest_risk"] = pd.to_numeric(patient_df["latest_risk"], errors="coerce")
    high_critical = sum(1 for p in patients if str(p.get("risk_band", "")).lower() in {"high", "critical"})
    avg_risk = patient_df["latest_risk"].mean() if not patient_df.empty and "latest_risk" in patient_df else None
    horizon = metadata.get("horizon_hours", "—")
    model_state = "Ready" if metadata else "Unavailable"

    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    with k1: kpi_card("Monitored Patients", len(patients), "Active patient records", "♡")
    with k2: kpi_card("High / Critical", high_critical, "Needs attention", "⚠")
    with k3: kpi_card("Open Alerts", len(open_alerts) if role_allows("admin", "clinician", "auditor") else "—", "Clinical queue", "🔔")
    with k4: kpi_card("Average Risk", fmt_percent(avg_risk, 1), "Latest observations", "◔")
    with k5: kpi_card("Model Horizon", f"{horizon} h" if horizon != "—" else "—", "Early warning", "◈")
    with k6: kpi_card("AI Engine", model_state, metadata.get("best_model", "Research model").replace("_", " ").title() if metadata else "Check model service", "✦")

    left, right = st.columns([1.65, 1], gap="large")
    with left:
        section_header("Patient Risk Distribution", "Current risk segmentation across monitored patients.")
        if not patient_df.empty and "risk_band" in patient_df and patient_df["risk_band"].notna().any():
            counts = patient_df["risk_band"].fillna("unknown").str.lower().value_counts().rename_axis("Risk").reset_index(name="Patients")
            fig = px.bar(
                counts,
                x="Risk",
                y="Patients",
                color="Risk",
                color_discrete_map=RISK_COLORS,
                title="Patients by risk band",
            )
            st.plotly_chart(styled_plot(fig, 335), use_container_width=True, key="overview_risk_bar")
        else:
            empty_state("♡", "No patient observations loaded", "Seed the research database to activate live patient-risk visualizations.")
            st.code("sudo docker compose exec api python scripts/seed_db.py --dataset data/processed/healthguard_24h.csv --limit-per-patient 20", language="bash")

    with right:
        section_header("AI Model Snapshot", "Validated model metadata available from the inference service.")
        if metadata:
            tm = metadata.get("test_metrics") or {}
            m1, m2 = st.columns(2)
            with m1: kpi_card("PR-AUC", fmt_float(tm.get("pr_auc"), 3), "Test set", "◈")
            with m2: kpi_card("AUROC", fmt_float(tm.get("auroc"), 3), "Test set", "◎")
            st.markdown(
                f'<span class="hg-chip">{safe_text(metadata.get("best_model", "model").replace("_", " ").title())}</span>'
                f'<span class="hg-chip">Threshold {safe_text(fmt_float(metadata.get("threshold"), 3))}</span>'
                f'<span class="hg-chip">{safe_text(horizon)}h horizon</span>',
                unsafe_allow_html=True,
            )
            st.progress(min(max(float(tm.get("recall_sensitivity", 0) or 0), 0.0), 1.0), text=f"Sensitivity {fmt_float(tm.get('recall_sensitivity'), 3)}")
            st.progress(min(max(float(tm.get("precision", 0) or 0), 0.0), 1.0), text=f"Precision {fmt_float(tm.get('precision'), 3)}")
        else:
            empty_state("◈", "Model service unavailable", "Check the API model directory and model metadata.")

    c_left, c_right = st.columns([1.35, 1], gap="large")
    with c_left:
        section_header("Highest Current Risk", "Prioritized patients based on latest available AI risk probability.")
        if not patient_df.empty and "latest_risk" in patient_df:
            top = patient_df.sort_values("latest_risk", ascending=False).head(8).copy()
            if st.session_state.get("global_search"):
                query = st.session_state["global_search"].lower().strip()
                top = top[top["patient_id"].astype(str).str.lower().str.contains(query)]
            if not top.empty:
                show = top[[c for c in ["patient_id", "age_group", "sex", "latest_risk", "risk_band"] if c in top.columns]].copy()
                if "latest_risk" in show:
                    show["latest_risk"] = show["latest_risk"].map(lambda x: fmt_percent(x, 1))
                st.dataframe(show, hide_index=True, use_container_width=True)
                st.download_button("Download patient snapshot", show.to_csv(index=False), "healthguard_patient_snapshot.csv", "text/csv", key="overview_export_patients")
            else:
                st.info("No patient matched the current search.")
        else:
            empty_state("⌕", "Patient priority list is empty", "Once patient observations are seeded, the highest-risk records will appear here.")

    with c_right:
        section_header("Recent Activity", "Latest auditable platform actions.")
        if role_allows("admin", "auditor"):
            activity_feed(audit_events, 6)
        else:
            empty_state("⌁", "Audit feed restricted", "Administrator or auditor role is required to view security activity.")

    section_header("Alert Intelligence", "Operational alert mix and the most recent open alerts.")
    a1, a2 = st.columns([1, 1.6], gap="large")
    with a1:
        if alerts:
            adf = pd.DataFrame(alerts)
            severity = adf["severity"].fillna("unknown").str.lower().value_counts().rename_axis("Severity").reset_index(name="Alerts")
            fig = px.pie(severity, names="Severity", values="Alerts", hole=.62, color="Severity", color_discrete_map=RISK_COLORS, title="Alert severity mix")
            st.plotly_chart(styled_plot(fig, 330), use_container_width=True, key="overview_alert_pie")
        elif role_allows("admin", "clinician", "auditor"):
            empty_state("✓", "No alerts stored", "The current alert queue is clear.")
        else:
            empty_state("🔒", "Alert data restricted", "This role cannot access clinical alert details.")
    with a2:
        if open_alerts:
            recent = pd.DataFrame(open_alerts[:12])
            st.dataframe(recent[[c for c in ["id", "patient_id", "created_at", "severity", "status"] if c in recent.columns]], hide_index=True, use_container_width=True)
        elif role_allows("admin", "clinician", "auditor"):
            st.success("No open alerts — monitoring queue is clear.")

# -----------------------------------------------------------------------------
# Patients
# -----------------------------------------------------------------------------
elif page == "Patients":
    section_header("Patient Monitoring", "Longitudinal AI risk, patient-specific context, and model input features.")
    if not patients:
        empty_state("♡", "No patient records loaded", "Seed the database from the prepared HealthGuard research dataset.")
        st.code("sudo docker compose exec api python scripts/seed_db.py --dataset data/processed/healthguard_24h.csv --limit-per-patient 20", language="bash")
    else:
        pmap = {str(p["patient_id"]): p for p in patients}
        options = sorted(pmap.keys())
        search = st.session_state.get("global_search", "").strip().lower()
        if search:
            options = [x for x in options if search in x.lower()] or options
        patient_id = st.selectbox("Patient", options, key="patient_selector")
        pinfo = pmap[patient_id]
        timeline = api_request("GET", f"/monitoring/patients/{patient_id}/timeline", show_error=True) or []

        h1, h2, h3, h4, h5 = st.columns(5, gap="small")
        with h1: kpi_card("Patient", patient_id, "Pseudonymous ID", "♡")
        with h2: kpi_card("Current Risk", fmt_percent(pinfo.get("latest_risk"), 1), "Latest AI probability", "◔")
        with h3: kpi_card("Risk Band", str(pinfo.get("risk_band") or "—").upper(), "Current classification", "⚠")
        with h4: kpi_card("Age Group", pinfo.get("age_group") or "—", "De-identified cohort", "⌁")
        with h5: kpi_card("Sex", pinfo.get("sex") or "—", "Recorded demographic", "◎")

        if not timeline:
            empty_state("◔", "No timeline available", "This patient exists but has no stored model inference readings.")
        else:
            tdf = pd.DataFrame(timeline)
            tdf["observed_at"] = pd.to_datetime(tdf["observed_at"], errors="coerce", utc=True)
            tdf["risk_probability"] = pd.to_numeric(tdf["risk_probability"], errors="coerce")
            tdf = tdf.sort_values("observed_at")
            latest = tdf.iloc[-1]
            tabs = st.tabs(["Risk Overview", "Timeline", "Latest Features", "Observation History"])
            with tabs[0]:
                c1, c2 = st.columns([.8, 1.7], gap="large")
                with c1:
                    value = float(latest.get("risk_probability") or 0)
                    gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=value * 100,
                        number={"suffix": "%", "font": {"size": 42}},
                        title={"text": "Current AI Risk"},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": RISK_COLORS.get(str(latest.get("risk_band", "unknown")).lower(), "#1167d8")},
                            "steps": [
                                {"range": [0, 30], "color": "#eaf8f3"},
                                {"range": [30, 55], "color": "#fff6e4"},
                                {"range": [55, 75], "color": "#fff0e9"},
                                {"range": [75, 100], "color": "#ffebef"},
                            ],
                        },
                    ))
                    st.plotly_chart(styled_plot(gauge, 300), use_container_width=True, key="patient_risk_gauge")
                with c2:
                    fig = px.area(tdf, x="observed_at", y="risk_probability", markers=True, title="Risk probability over time")
                    fig.update_yaxes(tickformat=".0%", range=[0, 1])
                    st.plotly_chart(styled_plot(fig, 300), use_container_width=True, key="patient_area_risk")
            with tabs[1]:
                fig = px.line(tdf, x="observed_at", y="risk_probability", color="risk_band", markers=True, color_discrete_map=RISK_COLORS, title=f"Longitudinal risk — {patient_id}")
                fig.update_yaxes(tickformat=".0%", range=[0, 1])
                st.plotly_chart(styled_plot(fig, 420), use_container_width=True, key="patient_timeline_plot")
            with tabs[2]:
                features = latest.get("features")
                if isinstance(features, dict) and features:
                    fdf = pd.DataFrame([{"Feature": k, "Value": v} for k, v in features.items()])
                    st.dataframe(fdf, hide_index=True, use_container_width=True)
                    numeric = []
                    for k, v in features.items():
                        try:
                            numeric.append((k, float(v)))
                        except (TypeError, ValueError):
                            pass
                    if numeric:
                        ndf = pd.DataFrame(numeric, columns=["Feature", "Value"])
                        ndf["Magnitude"] = ndf["Value"].abs()
                        topn = ndf.nlargest(12, "Magnitude")
                        fig = px.bar(topn.sort_values("Magnitude"), x="Value", y="Feature", orientation="h", title="Largest numeric feature values")
                        st.plotly_chart(styled_plot(fig, 430), use_container_width=True, key="patient_feature_bar")
                else:
                    st.info("No model input features are stored for the latest observation.")
            with tabs[3]:
                show = tdf[["observed_at", "risk_probability", "risk_band"]].copy()
                show["risk_probability"] = show["risk_probability"].map(lambda x: fmt_percent(x, 1))
                st.dataframe(show.sort_values("observed_at", ascending=False), hide_index=True, use_container_width=True)
                st.download_button("Export patient history", show.to_csv(index=False), f"{patient_id}_history.csv", "text/csv", key="patient_export_history")

# -----------------------------------------------------------------------------
# Alerts
# -----------------------------------------------------------------------------
elif page == "Alerts":
    section_header("Alert Command Center", "Prioritize, filter, review, and acknowledge AI-generated monitoring alerts.")
    if not role_allows("admin", "clinician", "auditor"):
        empty_state("🔒", "Alert access restricted", "Your current role does not have permission to view alert records.")
    elif not alerts:
        k1, k2, k3 = st.columns(3)
        with k1: kpi_card("Open Alerts", 0, "Queue status", "✓")
        with k2: kpi_card("Critical", 0, "Highest severity", "⚠")
        with k3: kpi_card("Acknowledged", 0, "Reviewed alerts", "◎")
        empty_state("✓", "No alerts stored", "HealthGuard-AI has no alert records in the current database.")
    else:
        adf = pd.DataFrame(alerts)
        adf["created_at"] = pd.to_datetime(adf["created_at"], errors="coerce", utc=True)
        open_count = int((adf["status"].astype(str).str.lower() == "open").sum())
        ack_count = int((adf["status"].astype(str).str.lower() == "acknowledged").sum())
        critical_count = int((adf["severity"].astype(str).str.lower() == "critical").sum())
        high_count = int((adf["severity"].astype(str).str.lower() == "high").sum())
        k1, k2, k3, k4 = st.columns(4)
        with k1: kpi_card("Open Alerts", open_count, "Needs review", "🔔")
        with k2: kpi_card("Critical", critical_count, "Immediate priority", "⚠")
        with k3: kpi_card("High", high_count, "Elevated risk", "▲")
        with k4: kpi_card("Acknowledged", ack_count, "Reviewed", "✓")

        f1, f2, f3 = st.columns([1, 1, 1.5], gap="small")
        status_opts = ["All"] + sorted(adf["status"].dropna().astype(str).unique().tolist())
        severity_opts = ["All"] + sorted(adf["severity"].dropna().astype(str).unique().tolist())
        selected_status = f1.selectbox("Status", status_opts, key="alert_status_filter")
        selected_severity = f2.selectbox("Severity", severity_opts, key="alert_severity_filter")
        search_alert = f3.text_input("Search patient", placeholder="Patient ID…", key="alert_patient_search")
        filtered = adf.copy()
        if selected_status != "All": filtered = filtered[filtered["status"] == selected_status]
        if selected_severity != "All": filtered = filtered[filtered["severity"] == selected_severity]
        if search_alert.strip(): filtered = filtered[filtered["patient_id"].astype(str).str.contains(search_alert.strip(), case=False, na=False)]

        c1, c2 = st.columns(2, gap="large")
        with c1:
            sev = adf["severity"].fillna("unknown").str.lower().value_counts().rename_axis("Severity").reset_index(name="Alerts")
            fig = px.pie(sev, names="Severity", values="Alerts", hole=.58, color="Severity", color_discrete_map=RISK_COLORS, title="Severity distribution")
            st.plotly_chart(styled_plot(fig, 330), use_container_width=True, key="alerts_severity_pie")
        with c2:
            by_day = adf.dropna(subset=["created_at"]).assign(Day=lambda x: x["created_at"].dt.date).groupby("Day").size().reset_index(name="Alerts")
            fig = px.bar(by_day, x="Day", y="Alerts", title="Alert activity by day")
            st.plotly_chart(styled_plot(fig, 330), use_container_width=True, key="alerts_by_day")

        st.dataframe(filtered, hide_index=True, use_container_width=True)
        st.download_button("Export filtered alerts", filtered.to_csv(index=False), "healthguard_alerts.csv", "text/csv", key="alerts_export")

        if role_allows("admin", "clinician"):
            pending = [a for a in alerts if str(a.get("status", "")).lower() == "open"]
            if pending:
                section_header("Acknowledge Alert", "Mark a reviewed alert as acknowledged while preserving the audit trail.")
                choices = {f"#{a['id']} · {a.get('patient_id')} · {str(a.get('severity', '')).upper()}": a["id"] for a in pending}
                ac1, ac2 = st.columns([3, 1])
                selected = ac1.selectbox("Open alert", list(choices), key="ack_alert_selector")
                if ac2.button("Acknowledge", key="ack_alert_button", type="primary", use_container_width=True):
                    result = api_request("POST", f"/monitoring/alerts/{choices[selected]}/acknowledge")
                    if result is not None:
                        st.success("Alert acknowledged and written to the audit trail.")
                        st.rerun()

# -----------------------------------------------------------------------------
# AI Analytics
# -----------------------------------------------------------------------------
elif page == "AI Analytics":
    section_header("AI Model Intelligence", "Model performance, validation comparison, cohort split, and research metadata.")
    if not metadata:
        empty_state("◈", "Model metadata unavailable", "Verify MODEL_DIR and confirm that trained model artifacts are mounted into the API container.")
    else:
        tm = metadata.get("test_metrics") or {}
        cols = st.columns(6, gap="small")
        labels = [
            ("PR-AUC", tm.get("pr_auc"), "◈"),
            ("AUROC", tm.get("auroc"), "◎"),
            ("Precision", tm.get("precision"), "⌁"),
            ("Sensitivity", tm.get("recall_sensitivity"), "♡"),
            ("F1 Score", tm.get("f1"), "✦"),
            ("Brier", tm.get("brier"), "◔"),
        ]
        for col, (label, value, icon) in zip(cols, labels):
            with col: kpi_card(label, fmt_float(value, 3 if label != "Brier" else 4), "Test performance", icon)

        c1, c2 = st.columns([1.45, 1], gap="large")
        with c1:
            scores = metadata.get("validation_pr_auc_by_model") or {}
            if scores:
                sdf = pd.DataFrame([{"Model": k.replace("_", " ").title(), "PR-AUC": v} for k, v in scores.items()])
                fig = px.bar(sdf.sort_values("PR-AUC"), x="PR-AUC", y="Model", orientation="h", title="Validation PR-AUC by model")
                fig.update_xaxes(range=[0, max(1.0, float(sdf["PR-AUC"].max()) * 1.05)])
                st.plotly_chart(styled_plot(fig, 350), use_container_width=True, key="ai_validation_models")
            else:
                st.info("No validation model comparison is stored in metadata.")
        with c2:
            split = pd.DataFrame({
                "Cohort": ["Train", "Validation", "Test"],
                "Patients": [metadata.get("train_patients", 0), metadata.get("validation_patients", 0), metadata.get("test_patients", 0)],
            })
            fig = px.pie(split, names="Cohort", values="Patients", hole=.62, title="Patient-level split")
            st.plotly_chart(styled_plot(fig, 350), use_container_width=True, key="ai_cohort_split")

        r1, r2 = st.columns([1.35, 1], gap="large")
        with r1:
            metric_names = ["Precision", "Sensitivity", "F1", "AUROC", "PR-AUC"]
            vals = [
                float(tm.get("precision", 0) or 0),
                float(tm.get("recall_sensitivity", 0) or 0),
                float(tm.get("f1", 0) or 0),
                float(tm.get("auroc", 0) or 0),
                float(tm.get("pr_auc", 0) or 0),
            ]
            radar = go.Figure(go.Scatterpolar(r=vals + [vals[0]], theta=metric_names + [metric_names[0]], fill="toself", name="Test metrics"))
            radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False, title="Performance profile")
            st.plotly_chart(styled_plot(radar, 390), use_container_width=True, key="ai_radar")
        with r2:
            section_header("Model Configuration")
            st.markdown(
                f'<div class="hg-panel">'
                f'<b>Best model</b><br>{safe_text(metadata.get("best_model", "—").replace("_", " ").title())}<br><br>'
                f'<b>Prediction horizon</b><br>{safe_text(metadata.get("horizon_hours", "—"))} hours<br><br>'
                f'<b>Decision threshold</b><br>{safe_text(fmt_float(metadata.get("threshold"), 4))}<br><br>'
                f'<b>Features</b><br>{len(metadata.get("features") or [])} engineered inputs'
                f'</div>',
                unsafe_allow_html=True,
            )

        with st.expander("Feature inventory", expanded=False):
            features = metadata.get("features") or []
            if features:
                st.dataframe(pd.DataFrame({"Feature": features}), hide_index=True, use_container_width=True)
        with st.expander("Complete model metadata", expanded=False):
            st.json(metadata)

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------
elif page == "Security":
    section_header("Security & Audit Center", "Role-based access visibility, auditable actions, and security operations insight.")
    if not role_allows("admin", "auditor"):
        empty_state("🔒", "Security audit restricted", "Administrator or auditor privileges are required to view the audit trail.")
    elif not audit_events:
        empty_state("⌁", "No audit events available", "Authentication, patient views, alert reviews, and inference actions will appear here.")
    else:
        sdf = pd.DataFrame(audit_events)
        sdf["time"] = pd.to_datetime(sdf["time"], errors="coerce", utc=True)
        success_count = int((sdf["result"].astype(str).str.lower() == "success").sum()) if "result" in sdf else len(sdf)
        failed_count = int((sdf["result"].astype(str).str.lower() == "failed").sum()) if "result" in sdf else 0
        unique_actors = sdf["actor"].nunique() if "actor" in sdf else 0
        k1, k2, k3, k4 = st.columns(4)
        with k1: kpi_card("Audit Events", len(sdf), "Recent records", "⌁")
        with k2: kpi_card("Successful", success_count, "Recorded outcomes", "✓")
        with k3: kpi_card("Failed", failed_count, "Requires review", "⚠")
        with k4: kpi_card("Actors", unique_actors, "Unique identities", "👤")

        c1, c2 = st.columns(2, gap="large")
        with c1:
            actions = sdf["action"].fillna("UNKNOWN").value_counts().head(12).rename_axis("Action").reset_index(name="Events")
            fig = px.bar(actions.sort_values("Events"), x="Events", y="Action", orientation="h", title="Most frequent audited actions")
            st.plotly_chart(styled_plot(fig, 375), use_container_width=True, key="security_actions")
        with c2:
            actors = sdf["actor"].fillna("system").value_counts().head(10).rename_axis("Actor").reset_index(name="Events")
            fig = px.bar(actors, x="Actor", y="Events", title="Events by actor")
            st.plotly_chart(styled_plot(fig, 375), use_container_width=True, key="security_actors")

        f1, f2, f3 = st.columns(3)
        actor_opts = ["All"] + sorted(sdf["actor"].dropna().astype(str).unique().tolist())
        action_opts = ["All"] + sorted(sdf["action"].dropna().astype(str).unique().tolist())
        actor_filter = f1.selectbox("Actor", actor_opts, key="security_actor_filter")
        action_filter = f2.selectbox("Action", action_opts, key="security_action_filter")
        text_filter = f3.text_input("Search resource", key="security_resource_search", placeholder="Patient, alert, resource…")
        filtered = sdf.copy()
        if actor_filter != "All": filtered = filtered[filtered["actor"] == actor_filter]
        if action_filter != "All": filtered = filtered[filtered["action"] == action_filter]
        if text_filter.strip() and "resource" in filtered:
            filtered = filtered[filtered["resource"].astype(str).str.contains(text_filter.strip(), case=False, na=False)]
        st.dataframe(filtered, hide_index=True, use_container_width=True)
        st.download_button("Export audit log", filtered.to_csv(index=False), "healthguard_audit.csv", "text/csv", key="security_export")

# -----------------------------------------------------------------------------
# System
# -----------------------------------------------------------------------------
elif page == "System":
    section_header("Platform Operations", "Runtime health, API connectivity, model availability, data readiness, and deployment checks.")
    s1, s2, s3, s4 = st.columns(4)
    with s1: kpi_card("API", "ONLINE" if api_ok else "OFFLINE", api_name if api_ok else "Connectivity issue", "●")
    with s2: kpi_card("Latency", f"{api_latency:.0f} ms" if api_latency is not None else "—", "Dashboard → API", "↔")
    with s3: kpi_card("Model", "READY" if metadata else "UNAVAILABLE", metadata.get("best_model", "—").replace("_", " ").title() if metadata else "Check MODEL_DIR", "◈")
    with s4: kpi_card("Patients", len(patients), "Database records", "♡")

    c1, c2 = st.columns([1.15, 1], gap="large")
    with c1:
        section_header("Service Diagnostics")
        diagnostics = pd.DataFrame([
            {"Component": "Dashboard", "Status": "Running", "Endpoint": "Streamlit :8501"},
            {"Component": "FastAPI", "Status": "Online" if api_ok else "Offline", "Endpoint": API_BASE_URL},
            {"Component": "Model", "Status": "Loaded" if metadata else "Unavailable", "Endpoint": "/model/metadata"},
            {"Component": "Patient Store", "Status": "Ready" if patients else "Empty", "Endpoint": "/monitoring/patients"},
            {"Component": "Alert Queue", "Status": f"{len(open_alerts)} open" if role_allows("admin", "clinician", "auditor") else "Restricted", "Endpoint": "/monitoring/alerts"},
        ])
        st.dataframe(diagnostics, hide_index=True, use_container_width=True)
        if st.button("Run live health check", key="system_health_check", type="primary"):
            ok, service, latency = api_health()
            if ok:
                st.success(f"{service} is healthy · {latency:.0f} ms")
            else:
                st.error(f"Health check failed: {service}")
    with c2:
        section_header("Research Readiness")
        checks = [
            ("Authentication & RBAC", True),
            ("API connectivity", api_ok),
            ("Model artifacts", bool(metadata)),
            ("Patient observations", bool(patients)),
            ("Audit trail", bool(audit_events) if role_allows("admin", "auditor") else True),
        ]
        for label, ok in checks:
            icon = "✓" if ok else "○"
            color = "#1aa981" if ok else "#9aa5b5"
            st.markdown(f'<div class="hg-activity-item"><b style="color:{color}">{icon}</b>&nbsp;&nbsp;{safe_text(label)}</div>', unsafe_allow_html=True)
        if not patients:
            st.info("Patient monitoring is ready but the database has not yet been seeded with prepared observations.")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.divider()
st.caption("HealthGuard-AI · Secure explainable remote patient monitoring · Research prototype only — not a medical diagnostic device.")
