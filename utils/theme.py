import streamlit as st
from config import DARK_THEME, LIGHT_THEME


def apply_theme():
    theme = st.session_state.get("theme", "Dark")
    colors = DARK_THEME if theme == "Dark" else LIGHT_THEME
    
    is_dark = theme == "Dark"
    
    bg_gradient = "radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.08) 0%, transparent 40%), radial-gradient(circle at 85% 85%, rgba(6, 182, 212, 0.08) 0%, transparent 40%)" if is_dark else "radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.04) 0%, transparent 40%), radial-gradient(circle at 85% 85%, rgba(6, 182, 212, 0.04) 0%, transparent 40%)"
    
    css = f"""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Root & Main Layout */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: {colors["bg"]};
        background-image: {bg_gradient};
        background-attachment: fixed;
        color: {colors["text"]};
    }}
    
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {"#0D1322" if is_dark else "#F1F5F9"} !important;
        border-right: 1px solid {colors["border"]} !important;
        padding-top: 1rem;
    }}
    
    [data-testid="stSidebar"] .stRadio > label {{
        font-weight: 600;
        letter-spacing: 0.02em;
    }}
    
    /* Modern Radio Group in Sidebar */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {{
        background: {"rgba(255, 255, 255, 0.03)" if is_dark else "rgba(0, 0, 0, 0.02)"};
        border: 1px solid {colors["border"]};
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }}
    
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
        border-color: {colors["accent_primary"]};
        background: {"rgba(99, 102, 241, 0.1)" if is_dark else "rgba(79, 70, 229, 0.06)"};
        transform: translateX(3px);
    }}
    
    [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {{
        background: {"linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(6, 182, 212, 0.15))" if is_dark else "linear-gradient(135deg, rgba(79, 70, 229, 0.12), rgba(8, 145, 178, 0.08))"};
        border-color: {colors["accent_primary"]};
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.2);
    }}
    
    /* Main Content Container Cards */
    .glass-card {{
        background: {colors["card_bg"]};
        border: 1px solid {colors["border"]};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: {colors["shadow"]};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        transition: all 0.3s ease;
    }}
    
    .glass-card:hover {{
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
    }}
    
    .hero-container {{
        background: {"linear-gradient(135deg, rgba(17, 24, 39, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%)" if is_dark else "linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%)"};
        border: 1px solid {"rgba(99, 102, 241, 0.3)" if is_dark else "rgba(79, 70, 229, 0.2)"};
        border-radius: 20px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(20px);
    }}

    .hero-title {{
        background: linear-gradient(135deg, #818CF8 0%, #38BDF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.1rem;
        letter-spacing: -0.02em;
        margin: 0;
    }}
    
    /* Streamlit Metric Overrides */
    [data-testid="stMetric"] {{
        background: {colors["card_bg"]};
        border: 1px solid {colors["border"]};
        border-top: 3px solid {colors["accent_primary"]};
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: {colors["shadow"]};
        transition: all 0.25s ease;
    }}
    
    [data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        border-color: {colors["accent_primary"]};
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2);
    }}
    
    [data-testid="stMetricValue"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 1.8rem !important;
        color: {colors["text"]};
    }}
    
    [data-testid="stMetricLabel"] {{
        font-weight: 600;
        font-size: 0.88rem;
        color: {colors["text_muted"]};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    /* Tabs Styling */
    [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {"rgba(15, 23, 42, 0.6)" if is_dark else "rgba(241, 245, 249, 0.8)"};
        padding: 6px;
        border-radius: 14px;
        border: 1px solid {colors["border"]};
    }}
    
    [data-baseweb="tab"] {{
        height: 42px;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: {colors["text_muted"]} !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease !important;
        padding: 0 18px !important;
    }}
    
    [data-baseweb="tab"][aria-selected="true"] {{
        background: {"linear-gradient(135deg, #4F46E5, #0891B2)" if is_dark else "#FFFFFF"} !important;
        color: #FFFFFF !important;
        border-color: {colors["accent_primary"]} !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
    }}
    
    /* Custom Primary & Secondary Buttons */
    .stButton > button {{
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.01em;
        padding: 8px 20px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid {colors["border"]};
    }}
    
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 50%, #06B6D4 100%);
        color: #FFFFFF;
        border: none;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
    }}
    
    .stButton > button[kind="primary"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.5);
    }}
    
    .stButton > button[kind="secondary"] {{
        background: {"rgba(30, 41, 59, 0.7)" if is_dark else "#FFFFFF"};
        color: {colors["text"]};
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        border-color: {colors["accent_primary"]};
        color: {colors["accent_primary"]};
        transform: translateY(-1px);
    }}
    
    /* Alert Callout Containers */
    .stAlert {{
        border-radius: 12px !important;
        border: 1px solid {colors["border"]} !important;
        backdrop-filter: blur(10px);
    }}
    
    /* Badges & Pills */
    .badge-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }}
    
    .badge-primary {{
        background: rgba(99, 102, 241, 0.15);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }}
    
    .badge-success {{
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }}
    
    .badge-warning {{
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }}

    .badge-info {{
        background: rgba(6, 182, 212, 0.15);
        color: #22D3EE;
        border: 1px solid rgba(6, 182, 212, 0.4);
    }}
    
    /* Approval Gate Card */
    .approval-gate-card {{
        background: {"linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%)" if is_dark else "linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(6, 182, 212, 0.08) 100%)"};
        border: 1px solid {colors["accent_primary"]};
        border-radius: 14px;
        padding: 18px 22px;
        margin: 18px 0;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.15);
    }}
    
    /* Inputs & Selectboxes */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{
        border-radius: 10px !important;
        border: 1px solid {colors["border"]} !important;
        background-color: {"rgba(15, 23, 42, 0.6)" if is_dark else "#FFFFFF"} !important;
    }}
    
    /* Dataframe wrapper styling */
    [data-testid="stDataFrame"] {{
        border: 1px solid {colors["border"]};
        border-radius: 14px;
        overflow: hidden;
        box-shadow: {colors["shadow"]};
    }}
    
    /* Code Blocks */
    code {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
        border-radius: 6px !important;
        padding: 2px 6px !important;
        background: {"rgba(15, 23, 42, 0.8)" if is_dark else "rgba(241, 245, 249, 0.9)"} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_theme_toggle():
    current_theme = st.session_state.get("theme", "Dark")
    new_theme = st.radio(
        "Theme",
        options=["Dark", "Light"],
        index=0 if current_theme == "Dark" else 1,
        horizontal=True,
        key="theme_radio",
        label_visibility="collapsed"
    )
    if new_theme != current_theme:
        st.session_state["theme"] = new_theme
        st.rerun()


def render_hero_banner(title: str, subtitle: str, active_project: str = None, role: str = None):
    project_badge = f'<span class="badge-pill badge-primary">📁 {active_project}</span>' if active_project else ""
    role_badge = f'<span class="badge-pill badge-info">👤 {role}</span>' if role else ""
    
    html = f"""
    <div class="hero-container">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
                    <span style="font-size: 2.2rem;">🧠</span>
                    <h1 class="hero-title">{title}</h1>
                </div>
                <p style="margin: 0; color: #94A3B8; font-size: 0.98rem; font-weight: 500;">{subtitle}</p>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                {project_badge}
                {role_badge}
                <span class="badge-pill badge-success">⚡ v2.5 Online</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str = None, icon: str = None):
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 8px;">{icon}</span>' if icon else ""
    sub_html = f'<p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9rem;">{subtitle}</p>' if subtitle else ""
    
    html = f"""
    <div style="margin-top: 15px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
        <div style="display: flex; align-items: center;">
            {icon_html}
            <h3 style="margin: 0; font-weight: 700; font-size: 1.35rem; letter-spacing: -0.01em;">{title}</h3>
        </div>
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_approval_banner(stage_title: str, description: str, is_approved: bool = False):
    status_class = "badge-success" if is_approved else "badge-warning"
    status_text = "APPROVED & LOCKED" if is_approved else "PENDING HUMAN DECISION"
    icon = "✅" if is_approved else "🚦"
    
    html = f"""
    <div class="approval-gate-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.4rem;">{icon}</span>
                <div>
                    <strong style="font-size: 1.05rem;">Human Approval Gate — {stage_title}</strong>
                    <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #94A3B8;">{description}</p>
                </div>
            </div>
            <span class="badge-pill {status_class}">{status_text}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
