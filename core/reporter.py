import time
import pandas as pd
import streamlit as st
from config import RESULTS_DIR
from utils.theme import render_section_header


def generate_markdown_report(project_meta: dict) -> str:
    target_col = st.session_state.get("target_col", "median_house_value")
    pred_test_m = st.session_state.get("predictive_test_metrics", {})
    inf_test_m = st.session_state.get("inferential_test_metrics", {})
    vif_accepted = st.session_state.get("vif_accepted_cols", [])
    reset_res = st.session_state.get("reset_result", {})
    
    lines = []
    lines.append(f"# Executive Machine Learning & Econometric Pipeline Report")
    lines.append(f"**Project Identifier**: `{project_meta.get('id', 'PRJ-CA-HOUSING-01')}`  ")
    lines.append(f"**Project Name**: {project_meta.get('name', 'California Housing Price Prediction')}  ")
    lines.append(f"**Generated On**: {time.strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Target Variable**: `{target_col}`\n")
    
    lines.append("## 1. Executive Summary")
    lines.append("This report presents the end-to-end Machine Learning pipeline results combining a Predictive Black-Box analytical window with a Parallel Econometric Inferential window.")
    lines.append("")
    
    lines.append("## 2. Predictive Analytical Window (Black-Box ML)")
    if pred_test_m:
        lines.append(f"- **Frozen Predictive Model**: `{st.session_state.get('frozen_predictive_name', 'N/A')}`")
        lines.append(f"- **Untouched Test RMSE**: ${pred_test_m.get('rmse', 0):,.2f}")
        lines.append(f"- **Untouched Test MAE**: ${pred_test_m.get('mae', 0):,.2f}")
        lines.append(f"- **Untouched Test R²**: {pred_test_m.get('r2', 0):.4f}")
    else:
        lines.append("Predictive model not yet frozen or evaluated.")
    lines.append("")
    
    lines.append("## 3. Inferential & Econometric Analytics Window")
    lines.append(f"- **VIF Threshold**: `{st.session_state.get('vif_threshold', 5.0)}`")
    lines.append(f"- **VIF-Accepted Features ({len(vif_accepted)})**: `{vif_accepted}`")
    if reset_res:
        lines.append(f"- **Ramsey RESET Test F-Statistic**: {reset_res.get('f_statistic', 0):.4f}")
        lines.append(f"- **Ramsey RESET Test p-value**: {reset_res.get('p_value', 0):.4e}")
        lines.append(f"- **Linear Specification Accepted?**: {'Yes' if reset_res.get('passed') else 'No (Non-linear/GAM required)'}")
    if inf_test_m:
        lines.append(f"- **Inferential Test RMSE**: ${inf_test_m.get('rmse', 0):,.2f}")
        lines.append(f"- **Inferential Test R²**: {inf_test_m.get('r2', 0):.4f}")
    lines.append("")
    
    lines.append("## 4. Managerial Recommendation")
    lines.append("For automated pricing API endpoints, deploy the high-capacity Predictive Model. For regulatory compliance, policy strategy, and stakeholder transparency, utilize the Parallel Inferential Model.")
    
    return "\n".join(lines)


def render_reporter_ui():
    render_section_header("📄 Stage 9: Automated Executive Reports & Deck Generator", "Export markdown audit documents and slide deck previews for executive review", icon="📄")
    
    project_meta = st.session_state.get("active_project_meta", {"id": "PRJ-CA-HOUSING-01", "name": "California Housing Prediction"})
    
    tab1, tab2 = st.tabs(["📝 Markdown Report Exporter", "📊 Presentation Slide Deck Preview"])
    
    with tab1:
        report_md = generate_markdown_report(project_meta)
        
        st.download_button(
            "📥 Export Executive Markdown Report (.md)",
            data=report_md,
            file_name=f"{project_meta.get('id')}_Executive_Report.md",
            mime="text/markdown",
            type="primary",
            use_container_width=True
        )
        
        st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown(report_md)
        
    with tab2:
        st.markdown("##### Executive Presentation Slide Deck (6-Slide Framework)")
        
        slides = [
            ("Slide 1: Executive Overview & Business Objective", "Predicting California Median House Prices with dual accuracy and interpretability paths."),
            ("Slide 2: Data Ingestion & Preprocessing Audit", "Leakage-safe train/val/test partitions, median imputations, and domain ratio features."),
            ("Slide 3: Predictive ML Performance Leaderboard", "Benchmark of Random Forest, GBDT, and Neural Nets evaluated on untouched test set."),
            ("Slide 4: Inferential Econometrics & VIF Diagnostics", "Iterative VIF variable elimination, Ramsey RESET specification test, and HC3 robust standard errors."),
            ("Slide 5: Model Interpretability & SHAP Values", "Global feature importances, SHAP beeswarm marginal attributions, and partial dependence curves."),
            ("Slide 6: Dual Deployment Strategy & Recommendations", "Deployment architecture for automated API ingestion alongside executive policy reporting.")
        ]
        
        for title, desc in slides:
            st.markdown(f"""
            <div class="glass-card" style="margin-bottom: 12px; padding: 16px;">
                <h4 style="margin: 0; color: #818CF8; font-size: 1.05rem;">{title}</h4>
                <p style="margin: 4px 0 0 0; color: #CBD5E1; font-size: 0.88rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
