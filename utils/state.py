import streamlit as st


def init_session_state():
    defaults = {
        "authenticated": False,
        "user": None,
        "theme": "Dark",
        "active_project_id": "PRJ-TELCO-CHURN-01",
        "active_stage": "ingestion",
        "raw_df": None,
        "processed_df": None,
        "train_df": None,
        "val_df": None,
        "test_df": None,
        "target_col": "Churn",
        "selected_features": [],
        "feature_engineering_approved": False,
        "engineered_df": None,
        "scaled_train": None,
        "scaled_val": None,
        "scaled_test": None,
        "predictive_models": {},
        "frozen_predictive_model": None,
        "predictive_metrics": {},
        "vif_threshold": 5.0,
        "vif_history": [],
        "vif_accepted_cols": [],
        "ols_model": None,
        "reset_result": None,
        "gam_model": None,
        "inferential_selected_model": None,
        "inferential_metrics": {},
        "shap_values": None,
        "shap_explainer": None,
        "approval_gates": {
            "validation": False,
            "preprocessing": False,
            "predictive": False,
            "inferential": False
        },
        "chat_history": []
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def set_approval_gate(stage: str, approved: bool = True):
    if "approval_gates" not in st.session_state:
        st.session_state["approval_gates"] = {}
    st.session_state["approval_gates"][stage] = approved


def is_gate_approved(stage: str) -> bool:
    return st.session_state.get("approval_gates", {}).get(stage, False)
