import os
import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from core.model_basket import PREDICTIVE_MODEL_BASKET, calculate_metrics
from config import MODELS_DIR
from utils.state import set_approval_gate, is_gate_approved
from utils.theme import render_section_header, render_approval_banner


def train_and_eval_predictive_model(model_name: str, train_df: pd.DataFrame, val_df: pd.DataFrame, target_col: str, custom_params: dict = None):
    model_info = PREDICTIVE_MODEL_BASKET[model_name]
    cls = model_info["class"]
    params = custom_params if custom_params is not None else model_info["params"]
    
    model = cls(**params)
    
    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]
    
    X_val = val_df.drop(columns=[target_col])
    y_val = val_df[target_col]
    
    # Train
    model.fit(X_train, y_train)
    
    # Predictions
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)
    
    train_metrics = calculate_metrics(y_train, y_train_pred)
    val_metrics = calculate_metrics(y_val, y_val_pred)
    
    return {
        "model_name": model_name,
        "model": model,
        "train_metrics": train_metrics,
        "val_metrics": val_metrics,
        "y_val_true": y_val,
        "y_val_pred": y_val_pred
    }


def render_predictive_ui():
    render_section_header("🤖 Stage 5: Predictive ML Model Basket (Black-Box Path)", "Benchmark algorithms from the predictive zoo, evaluate validation metrics, and freeze top model", icon="🤖")
    
    train_df = st.session_state.get("train_df")
    val_df = st.session_state.get("val_df")
    test_df = st.session_state.get("test_df")
    target_col = st.session_state.get("target_col", "median_house_value")
    
    if train_df is None or val_df is None:
        st.warning("⚠️ Data splits not available. Please complete Stage 4 (Preprocessing) first.")
        return

    is_approved = is_gate_approved("predictive")
    render_approval_banner("Predictive Basket Benchmark & Model Freeze", "Train candidate ML models, rank validation metrics, and lock top predictor for untouched test evaluation", is_approved=is_approved)

    st.markdown("##### 1. Predictive Algorithm Selection")
    selected_models = st.multiselect(
        "Choose Predictive Models to Train & Benchmark",
        options=list(PREDICTIVE_MODEL_BASKET.keys()),
        default=["Random Forest Regressor", "Gradient Boosting Regressor", "SGD Regressor (Gradient Descent)"]
    )
    
    st.markdown("<div style='padding-top: 6px;'></div>", unsafe_allow_html=True)
    run_train = st.button("🚀 Train & Benchmark Selected Models", type="primary", use_container_width=True)
    
    if run_train or "predictive_results" in st.session_state:
        if run_train:
            results = {}
            with st.spinner("Training models across training split & scoring validation set..."):
                for m_name in selected_models:
                    res = train_and_eval_predictive_model(m_name, train_df, val_df, target_col)
                    results[m_name] = res
                st.session_state["predictive_results"] = results
                st.toast("Model Basket Benchmark Complete!", icon="🏆")
                
        results = st.session_state.get("predictive_results", {})
        
        if results:
            st.markdown("---")
            st.markdown("##### 🏆 Validation Leaderboard Matrix")
            leaderboard_data = []
            for m_name, res in results.items():
                vm = res["val_metrics"]
                tm = res["train_metrics"]
                leaderboard_data.append({
                    "Model": m_name,
                    "Val RMSE ($)": f"${vm['rmse']:,.2f}",
                    "Val MAE ($)": f"${vm['mae']:,.2f}",
                    "Val R²": f"{vm['r2']:.4f}",
                    "Train R²": f"{tm['r2']:.4f}"
                })
            
            lead_df = pd.DataFrame(leaderboard_data).sort_values(by="Val R²", ascending=False)
            st.dataframe(lead_df, use_container_width=True)
            
            best_model_name = lead_df.iloc[0]["Model"]
            st.markdown("##### 🧊 Select Model to Freeze for Test Set Evaluation")
            col_sel, col_act = st.columns([2, 1])
            with col_sel:
                frozen_name = st.selectbox("Model Candidate", options=list(results.keys()), index=list(results.keys()).index(best_model_name))
            with col_act:
                st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
                freeze_btn = st.button("🧊 Freeze & Evaluate Test Set", type="secondary", use_container_width=True)
                
            if freeze_btn:
                frozen_res = results[frozen_name]
                frozen_model = frozen_res["model"]
                
                X_test = test_df.drop(columns=[target_col])
                y_test = test_df[target_col]
                
                y_test_pred = frozen_model.predict(X_test)
                test_metrics = calculate_metrics(y_test, y_test_pred)
                
                st.session_state["frozen_predictive_model"] = frozen_model
                st.session_state["frozen_predictive_name"] = frozen_name
                st.session_state["predictive_test_metrics"] = test_metrics
                
                model_save_path = MODELS_DIR / ("frozen_sgd_regressor.joblib" if "SGD" in frozen_name else "frozen_predictive_model.joblib")
                joblib.dump(frozen_model, model_save_path)
                
                set_approval_gate("predictive", True)
                st.success(f"🏆 `{frozen_name}` frozen and saved to artifact store!")
                st.toast("Predictive Model Gate Approved!", icon="🎯")
                st.rerun()
                
            test_metrics = st.session_state.get("predictive_test_metrics")
            if test_metrics:
                st.markdown("---")
                st.markdown("##### 🧪 Untouched Out-of-Sample Test Evaluation")
                tm1, tm2, tm3 = st.columns(3)
                tm1.metric("Test RMSE", f"${test_metrics['rmse']:,.2f}")
                tm2.metric("Test MAE", f"${test_metrics['mae']:,.2f}")
                tm3.metric("Test R² Score", f"{test_metrics['r2']:.4f}")
                
                frozen_name = st.session_state.get("frozen_predictive_name", "Predictive Model")
                frozen_model = st.session_state.get("frozen_predictive_model")
                X_val = val_df.drop(columns=[target_col])
                y_val = val_df[target_col]
                y_val_pred = frozen_model.predict(X_val)
                
                theme_plotly = "plotly_dark" if st.session_state.get("theme", "Dark") == "Dark" else "plotly_white"
                
                fig_pv = px.scatter(
                    x=y_val,
                    y=y_val_pred,
                    labels={"x": "Actual Target", "y": "Predicted Target"},
                    title=f"Actual vs Predicted — {frozen_name} (Validation Set)",
                    opacity=0.5
                )
                fig_pv.add_trace(go.Scatter(x=[y_val.min(), y_val.max()], y=[y_val.min(), y_val.max()], mode="lines", name="Ideal 1:1 Line", line=dict(color="#EF4444", dash="dash")))
                fig_pv.update_layout(template=theme_plotly, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_pv, use_container_width=True)
