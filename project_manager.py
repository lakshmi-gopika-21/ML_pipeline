import json
import time
from pathlib import Path
import yaml
import streamlit as st
from config import BASE_DIR, PROJECTS_DIR, REGISTRY_FILE
from utils.theme import render_section_header


def load_registry():
    if not REGISTRY_FILE.exists():
        default_registry = {
            "recent_projects": [
                {
                    "id": "PRJ-CA-HOUSING-01",
                    "name": "California Housing Price Prediction",
                    "type": "Regression & Interpretability",
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Active",
                    "path": str(PROJECTS_DIR / "PRJ-CA-HOUSING-01")
                }
            ]
        }
        save_registry(default_registry)
        return default_registry
    try:
        with open(REGISTRY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"recent_projects": []}


def save_registry(registry):
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=4)


def create_project(project_id: str, project_name: str, description: str = ""):
    project_dir = PROJECTS_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Auto-generate 9-layer directory structure inside project folder
    subdirs = ["data/raw", "data/processed", "data/splits", "models", "results", "reports", "config"]
    for s in subdirs:
        (project_dir / s).mkdir(parents=True, exist_ok=True)
        
    project_meta = {
        "id": project_id,
        "name": project_name,
        "description": description,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Initialized",
        "target_variable": None,
        "selected_features": [],
        "current_stage": "ingestion"
    }
    
    with open(project_dir / "config" / "project.yaml", "w") as f:
        yaml.dump(project_meta, f)
        
    registry = load_registry()
    existing_ids = [p["id"] for p in registry["recent_projects"]]
    if project_id not in existing_ids:
        registry["recent_projects"].append({
            "id": project_id,
            "name": project_name,
            "type": "ML Pipeline",
            "created_at": project_meta["created_at"],
            "status": "Initialized",
            "path": str(project_dir)
        })
        save_registry(registry)
        
    return project_meta


def load_project_meta(project_id: str):
    project_dir = PROJECTS_DIR / project_id
    config_file = project_dir / "config" / "project.yaml"
    if config_file.exists():
        with open(config_file, "r") as f:
            return yaml.safe_load(f)
    return None


def render_project_manager_ui():
    render_section_header("📁 Project Environment & Global Workspace Registry", "Switch between isolated ML project environments or instantiate a new workspace", icon="📂")
    
    registry = load_registry()
    projects = registry.get("recent_projects", [])
    active_project_id = st.session_state.get("active_project_id", "PRJ-CA-HOUSING-01")
    
    col1, col2 = st.columns([6, 4])
    
    with col1:
        st.markdown("##### 📌 Active Workspace Selector")
        if projects:
            project_options = {p["id"]: f"{p['name']} ({p['id']})" for p in projects}
            selected_id = st.selectbox(
                "Choose Active Project Environment",
                options=list(project_options.keys()),
                format_func=lambda x: project_options[x],
                index=list(project_options.keys()).index(active_project_id) if active_project_id in project_options else 0
            )
            
            if selected_id != active_project_id or "active_project_meta" not in st.session_state:
                st.session_state["active_project_id"] = selected_id
                meta = load_project_meta(selected_id)
                if not meta:
                    meta = create_project(selected_id, project_options[selected_id])
                st.session_state["active_project_meta"] = meta
                st.toast(f"Switched active workspace to `{selected_id}`", icon="🚀")
                
            active_meta = st.session_state.get("active_project_meta", {})
            
            # Active Project Card Summary
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <div>
                        <h4 style="margin: 0; color: #818CF8; font-size: 1.2rem;">{active_meta.get('name', 'N/A')}</h4>
                        <span style="font-size: 0.85rem; color: #94A3B8;">Identifier: <code>{selected_id}</code></span>
                    </div>
                    <span class="badge-pill badge-success">{active_meta.get('status', 'Active')}</span>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px;">
                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 10px;">
                        <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Created At</div>
                        <div style="font-weight: 600; font-size: 0.88rem;">{active_meta.get('created_at', 'N/A')}</div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 10px;">
                        <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Target Variable</div>
                        <div style="font-weight: 600; font-size: 0.88rem; color: #38BDF8;">{active_meta.get('target_variable', 'Not set')}</div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 10px;">
                        <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Pipeline Stage</div>
                        <div style="font-weight: 600; font-size: 0.88rem; color: #FBBF24;">{active_meta.get('current_stage', 'ingestion')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No registered projects found. Use the panel on the right to instantiate a new project.")

    with col2:
        st.markdown("##### ➕ Instantiate New Workspace")
        with st.form("new_project_form"):
            new_id = st.text_input("Project Identifier Code", value=f"PRJ-{int(time.time()) % 10000:04d}")
            new_name = st.text_input("Project Title", value="California Housing Task")
            new_desc = st.text_area("Description / Objective", value="Predicting housing median value with econometrics interpretability", height=70)
            submitted = st.form_submit_button("🚀 Initialize Project Environment", type="primary", use_container_width=True)
            
            if submitted:
                if not new_id or not new_name:
                    st.error("Please specify both Project ID and Title.")
                else:
                    meta = create_project(new_id, new_name, new_desc)
                    st.session_state["active_project_id"] = new_id
                    st.session_state["active_project_meta"] = meta
                    st.success(f"✅ Project `{new_id}` initialized successfully!")
                    st.rerun()

    st.markdown("---")
    st.markdown("##### 🗂️ Global Workspace Registry Table")
    if projects:
        st.dataframe(projects, use_container_width=True)
