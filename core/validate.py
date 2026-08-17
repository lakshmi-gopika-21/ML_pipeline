import pandas as pd
import numpy as np
import streamlit as st
from utils.state import set_approval_gate, is_gate_approved
from utils.theme import render_section_header, render_approval_banner


def validate_dataframe(df: pd.DataFrame):
    report = {
        "num_rows": len(df),
        "num_cols": len(df.columns),
        "duplicates": int(df.duplicated().sum()),
        "missing_summary": {},
        "data_types": {},
        "constant_cols": [],
        "high_cardinality_cols": []
    }
    
    for col in df.columns:
        n_missing = int(df[col].isna().sum())
        pct_missing = (n_missing / len(df)) * 100
        report["missing_summary"][col] = {
            "count": n_missing,
            "percentage": round(pct_missing, 2)
        }
        report["data_types"][col] = str(df[col].dtype)
        
        if df[col].nunique() == 1:
            report["constant_cols"].append(col)
        elif df[col].dtype == "object" and df[col].nunique() > 50:
            report["high_cardinality_cols"].append(col)
            
    return report


def render_validation_ui():
    render_section_header("🛡️ Stage 2: Data Audit & Target Gate", "Inspect schema health, audit missingness, and enforce human target selection", icon="🛡️")
    
    df = st.session_state.get("raw_df")
    if df is None:
        st.warning("⚠️ No dataset loaded. Please navigate to Stage 1 (Data Ingestion) to initialize raw data.")
        return
    
    val_report = validate_dataframe(df)
    is_approved = is_gate_approved("validation")
    
    render_approval_banner("Variable Selection & Imputation Gate", "Confirm target variable (Y), feature matrix (X), and missingness handling strategy", is_approved=is_approved)
    
    st.markdown("##### 🔍 Data Quality Audit Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows Audit", f"{val_report['num_rows']:,}")
    c2.metric("Columns Audit", val_report['num_cols'])
    c3.metric("Duplicate Rows", val_report['duplicates'], delta="Clean" if val_report['duplicates'] == 0 else f"-{val_report['duplicates']}")
    
    missing_cols_count = sum(1 for v in val_report["missing_summary"].values() if v["count"] > 0)
    c4.metric("Columns with Missing Values", missing_cols_count)
    
    with st.expander("📋 View Column Data Types & Missingness Matrix", expanded=False):
        missing_df = pd.DataFrame([
            {
                "Column": col,
                "Data Type": val_report["data_types"][col],
                "Missing Count": val_report["missing_summary"][col]["count"],
                "Missing %": f"{val_report['missing_summary'][col]['percentage']}%"
            }
            for col in df.columns
        ])
        st.dataframe(missing_df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("##### 🚦 Human Intervention: Target & Feature Gate")
    
    all_cols = list(df.columns)
    default_target = "median_house_value" if "median_house_value" in all_cols else all_cols[-1]
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        target_col = st.selectbox(
            "Select Target Variable (Y)",
            options=all_cols,
            index=all_cols.index(default_target) if default_target in all_cols else len(all_cols) - 1
        )
    
    feature_candidates = [c for c in all_cols if c != target_col]
    
    with col_t2:
        selected_features = st.multiselect(
            "Select Feature Matrix Columns (X)",
            options=feature_candidates,
            default=feature_candidates
        )
        
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        impute_num_strategy = st.selectbox("Numeric Missing Imputer Strategy", ["Median", "Mean", "Drop Rows", "KNN Imputer"])
    with col_s2:
        impute_cat_strategy = st.selectbox("Categorical Missing Imputer Strategy", ["Most Frequent / Mode", "Constant ('Missing')", "Drop Rows"])
        
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    
    approved = st.button("🔒 Approve Selection & Advance Pipeline Gate", type="primary", use_container_width=True)
    
    if approved:
        st.session_state["target_col"] = target_col
        st.session_state["selected_features"] = selected_features
        st.session_state["impute_num_strategy"] = impute_num_strategy
        st.session_state["impute_cat_strategy"] = impute_cat_strategy
        set_approval_gate("validation", True)
        st.success("✅ Variable selection and validation strategy approved!")
        st.toast("Validation Gate Locked & Approved!", icon="✅")
        st.rerun()
