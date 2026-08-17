import hashlib
import json
from pathlib import Path
import streamlit as st
from config import BASE_DIR
from utils.theme import render_section_header

USERS_FILE = BASE_DIR / "users.json"

DEFAULT_USERS = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "Admin",
        "name": "System Administrator"
    },
    "analyst": {
        "password_hash": hashlib.sha256("analyst123".encode()).hexdigest(),
        "role": "Analyst",
        "name": "Lead Data Scientist"
    },
    "viewer": {
        "password_hash": hashlib.sha256("viewer123".encode()).hexdigest(),
        "role": "Viewer",
        "name": "Business Stakeholder"
    }
}


def load_users():
    if not USERS_FILE.exists():
        save_users(DEFAULT_USERS)
        return DEFAULT_USERS
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_USERS


def save_users(users_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users_dict, f, indent=4)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username, password):
    users = load_users()
    username = username.strip().lower()
    if username in users:
        if users[username]["password_hash"] == hash_password(password):
            return True, users[username]
    return False, None


def register_user(username, password, name, role="Analyst"):
    users = load_users()
    username = username.strip().lower()
    if username in users:
        return False, "Username already exists."
    
    users[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "name": name
    }
    save_users(users)
    return True, "User registered successfully!"


def render_auth_ui():
    if st.session_state.get("authenticated", False):
        user = st.session_state.get("user", {})
        
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.5rem;">🟢</span>
                <div>
                    <strong style="color: #34D399; font-size: 1.05rem;">Authenticated Session Active</strong>
                    <div style="font-size: 0.88rem; color: #94A3B8;">Operator: <strong>{user.get('name', 'User')}</strong> &bull; Access Role: <code>{user.get('role', 'Analyst')}</code></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🚪 Sign Out", key="logout_btn", type="secondary"):
                st.session_state["authenticated"] = False
                st.session_state["user"] = None
                st.rerun()
        return True

    render_section_header("🔐 Enterprise Authentication & Access Control", "Sign in to authenticate into the Machine Learning & Interpretability Platform", icon="🔒")

    col_main, col_info = st.columns([6, 4])
    
    with col_main:
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Register New Account"])
        
        with tab1:
            st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username", value="analyst", placeholder="Enter username")
                password = st.text_input("Password", type="password", value="analyst123", placeholder="Enter password")
                submit = st.form_submit_button("Authenticate & Enter Workspace", type="primary", use_container_width=True)
                
                if submit:
                    success, user_info = authenticate(username, password)
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user_info
                        st.toast(f"Welcome back, {user_info['name']}!", icon="🚀")
                        st.rerun()
                    else:
                        st.error("❌ Authentication failed. Invalid username or password.")
                        
        with tab2:
            st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
            with st.form("register_form"):
                new_user = st.text_input("Username", placeholder="e.g. jsmith")
                new_name = st.text_input("Full Name", placeholder="e.g. John Smith")
                new_pass = st.text_input("Password", type="password", placeholder="Set strong password")
                new_role = st.selectbox("Assign Access Role", ["Analyst", "Viewer", "Admin"])
                reg_submit = st.form_submit_button("Create Platform User", type="primary", use_container_width=True)
                
                if reg_submit:
                    if not new_user or not new_pass or not new_name:
                        st.warning("⚠️ Please complete all registration fields.")
                    else:
                        success, msg = register_user(new_user, new_pass, new_name, new_role)
                        if success:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
                            
    with col_info:
        st.markdown("""
        <div class="glass-card" style="margin-top: 28px;">
            <h4 style="margin: 0 0 12px 0; color: #818CF8;">💡 Demo Access Accounts</h4>
            <p style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 14px;">Use pre-configured roles to test granular authorization levels across the pipeline:</p>
            
            <div style="background: rgba(99, 102, 241, 0.1); border-left: 3px solid #6366F1; border-radius: 6px; padding: 10px; margin-bottom: 8px;">
                <div style="font-weight: 600; font-size: 0.9rem;">Lead Data Scientist (Analyst)</div>
                <div style="font-size: 0.82rem; color: #CBD5E1;"><code>analyst</code> / <code>analyst123</code></div>
            </div>
            
            <div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10B981; border-radius: 6px; padding: 10px; margin-bottom: 8px;">
                <div style="font-weight: 600; font-size: 0.9rem;">System Administrator (Admin)</div>
                <div style="font-size: 0.82rem; color: #CBD5E1;"><code>admin</code> / <code>admin123</code></div>
            </div>
            
            <div style="background: rgba(6, 182, 212, 0.1); border-left: 3px solid #06B6D4; border-radius: 6px; padding: 10px;">
                <div style="font-weight: 600; font-size: 0.9rem;">Business Executive (Viewer)</div>
                <div style="font-size: 0.82rem; color: #CBD5E1;"><code>viewer</code> / <code>viewer123</code></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    return st.session_state.get("authenticated", False)
