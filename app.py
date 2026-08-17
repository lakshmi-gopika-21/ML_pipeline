import sys
from pathlib import Path
import streamlit as st

# Ensure app root is in sys.path
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from config import PIPELINE_STAGES
from utils.state import init_session_state
from utils.theme import apply_theme, render_theme_toggle, render_hero_banner
from auth import render_auth_ui
from project_manager import render_project_manager_ui, load_project_meta
from core.ingest import render_ingestion_ui
from core.validate import render_validation_ui
from core.eda import render_eda_ui
from core.preprocess import render_preprocessing_ui
from core.predictive_pipeline import render_predictive_ui
from core.inferential_pipeline import render_inferential_ui
from core.explainability import render_explainability_ui
from core.evaluator import render_evaluator_ui
from core.reporter import render_reporter_ui
from ai_assistant.groq_chat import render_ai_chat_ui


def main():
    st.set_page_config(
        page_title="AI-Assisted ML & Interpretability Platform",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    apply_theme()
    
    # Active state metadata
    active_proj_id = st.session_state.get("active_project_id", "PRJ-CA-HOUSING-01")
    user = st.session_state.get("user", {})
    user_role = user.get("role", "Analyst") if user else None
    
    # Top Control Bar (Hero Header + Theme Switcher)
    col_header, col_theme = st.columns([8, 2])
    with col_header:
        render_hero_banner(
            title="AI-Assisted Data Science & ML Platform",
            subtitle="End-to-End Predictive Machine Learning & Econometric Interpretability Engine",
            active_project=active_proj_id,
            role=user_role
        )
    with col_theme:
        st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 🎨 Display Theme")
        render_theme_toggle()
        
    # Authentication Gate
    authenticated = render_auth_ui()
    if not authenticated:
        st.warning("⚠️ Access Restricted: Please sign in above to proceed into the Data Science Platform.")
        st.stop()
        
    # Sidebar Navigation Header
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px 0 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
        <div style="font-size: 1.8rem; margin-bottom: 4px;">🧠 <strong>ANTIGRAVITY</strong></div>
        <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.1em;">Pipeline Control Center</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    
    # Pipeline Navigation Radio
    stage_keys = [s[0] for s in PIPELINE_STAGES]
    stage_labels = [s[1] for s in PIPELINE_STAGES]
    
    current_stage_key = st.session_state.get("active_stage", "projects")
    current_index = stage_keys.index(current_stage_key) if current_stage_key in stage_keys else 1
    
    selected_stage_label = st.sidebar.radio(
        "Navigation Stages",
        options=stage_labels,
        index=current_index,
        key="stage_radio",
        label_visibility="collapsed"
    )
    
    selected_stage_key = stage_keys[stage_labels.index(selected_stage_label)]
    if selected_stage_key != current_stage_key:
        st.session_state["active_stage"] = selected_stage_key
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 12px; font-size: 0.82rem;">
        <div>📁 Active Project: <strong>{active_proj_id}</strong></div>
        <div>👤 Operator: <strong>{user.get('name', 'Analyst')}</strong></div>
        <div style="margin-top: 6px; color: #10B981; font-weight: 600;">🟢 Pipeline Status: Ready</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<div style='padding-top: 8px;'></div>", unsafe_allow_html=True)
    st.sidebar.caption("© 2026 Antigravity AI Machine Learning Framework")
    
    # Render Selected Pipeline Stage
    if selected_stage_key == "auth":
        st.success("You are fully authenticated into the environment!")
    elif selected_stage_key == "projects":
        render_project_manager_ui()
    elif selected_stage_key == "ingestion":
        render_ingestion_ui()
    elif selected_stage_key == "validation":
        render_validation_ui()
    elif selected_stage_key == "eda":
        render_eda_ui()
    elif selected_stage_key == "preprocessing":
        render_preprocessing_ui()
    elif selected_stage_key == "predictive":
        render_predictive_ui()
    elif selected_stage_key == "inferential":
        render_inferential_ui()
    elif selected_stage_key == "explainability":
        render_explainability_ui()
    elif selected_stage_key == "comparison":
        render_evaluator_ui()
    elif selected_stage_key == "reports":
        render_reporter_ui()
    elif selected_stage_key == "ai_chat":
        render_ai_chat_ui()


if __name__ == "__main__":
    main()
