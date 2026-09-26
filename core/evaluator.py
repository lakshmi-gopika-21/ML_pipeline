import pandas as pd
import streamlit as st
from utils.theme import render_section_header


def render_evaluator_ui():
    render_section_header("⚖️ Stage 8: Cross-Window Model Comparison Scorecard", "Evaluate black-box predictive capability vs inferential econometric model clarity", icon="⚖️")
    
    frozen_pred_name = st.session_state.get("frozen_predictive_name", "Predictive Model")
    pred_test_m = st.session_state.get("predictive_test_metrics")
    
    inf_test_m = st.session_state.get("inferential_test_metrics")
    
    if pred_test_m is None and inf_test_m is None:
        st.warning("⚠️ No frozen models evaluated yet. Please complete Stage 5 and Stage 6 first.")
        return
        
    st.markdown("##### Integrated Multi-Dimensional Decision Matrix")
    
    comp_rows = []
    
    if pred_test_m:
        comp_rows.append({
            "Model Name": f"Predictive: {frozen_pred_name}",
            "Analytical Purpose": "Out-of-sample Prediction",
            "Test Accuracy": f"{pred_test_m['accuracy']:.3f}",
            "Test Recall": f"{pred_test_m['recall']:.3f}",
            "Test ROC-AUC": f"{pred_test_m['roc_auc']:.3f}",
            "Inferential Capability": "Limited (Black-Box)",
            "Decision Support Suitability": "Automated Real-Time Ingestion"
        })
        
    if inf_test_m:
        comp_rows.append({
            "Model Name": "Inferential: Selected Model",
            "Analytical Purpose": "Interpretation",
            "Test Accuracy": f"{inf_test_m.get('accuracy', 0):.3f}",
            "Test Recall": f"{inf_test_m.get('recall', 0):.3f}",
            "Test ROC-AUC": f"{inf_test_m.get('roc_auc', 0):.3f}",
            "Inferential Capability": "High (Coefficients & risk drivers)",
            "Decision Support Suitability": "Retention Strategy"
        })
        
    comp_df = pd.DataFrame(comp_rows)
    st.dataframe(comp_df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("##### 🎯 Executive Decision Recommendation")
    
    if pred_test_m:
        st.success(
            f"Deploy `{frozen_pred_name}` for retention prioritization. "
            "Use recall and ROC-AUC to monitor customer-risk coverage."
        )
