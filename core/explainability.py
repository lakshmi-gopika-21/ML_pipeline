import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from utils.theme import render_section_header

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


def compute_shap_explanations(model, X_sample: pd.DataFrame):
    if not SHAP_AVAILABLE:
        return None, None
    try:
        explainer = shap.Explainer(model, X_sample)
        shap_values = explainer(X_sample)
        return explainer, shap_values
    except Exception as e:
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample)
            return explainer, shap_values
        except Exception:
            return None, None


def render_explainability_ui():
    render_section_header("🔍 Stage 7: SHAP & Interpretability Suite", "Uncover global feature importances, SHAP marginal contributions, and Partial Dependence Curves", icon="🔍")
    
    frozen_model = st.session_state.get("frozen_predictive_model")
    frozen_name = st.session_state.get("frozen_predictive_name", "Predictive Model")
    val_df = st.session_state.get("val_df")
    target_col = st.session_state.get("target_col", "Churn")
    
    if frozen_model is None or val_df is None:
        st.warning("⚠️ No frozen predictive model available. Please complete Stage 5 (Predictive ML Path) first.")
        return
        
    X_val = val_df.drop(columns=[target_col])
    theme_plotly = "plotly_dark" if st.session_state.get("theme", "Dark") == "Dark" else "plotly_white"

    tab1, tab2, tab3 = st.tabs([
        "🏆 Global Feature Importances",
        "🐝 SHAP Summary & Beeswarm",
        "📈 Partial Dependence Plots (PDP)"
    ])
    
    with tab1:
        st.markdown(f"##### Global Feature Importances — `{frozen_name}`")
        if hasattr(frozen_model, "feature_importances_"):
            importances = frozen_model.feature_importances_
            fi_df = pd.DataFrame({"Feature": X_val.columns, "Importance": importances}).sort_values("Importance", ascending=True)
            
            fig_fi = px.bar(
                fi_df,
                x="Importance",
                y="Feature",
                orientation="h",
                title=f"Feature Importances ({frozen_name})",
                color="Importance",
                color_continuous_scale="Viridis"
            )
            fig_fi.update_layout(template=theme_plotly, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_fi, use_container_width=True)
        elif hasattr(frozen_model, "coef_"):
            coefs = np.abs(frozen_model.coef_)
            fi_df = pd.DataFrame({"Feature": X_val.columns, "Absolute Coefficient": coefs}).sort_values("Absolute Coefficient", ascending=True)
            fig_coef = px.bar(fi_df, x="Absolute Coefficient", y="Feature", orientation="h", title=f"Absolute Coefficients ({frozen_name})")
            fig_coef.update_layout(template=theme_plotly, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_coef, use_container_width=True)
        else:
            st.info("Selected model architecture does not expose native feature importance weights.")

    with tab2:
        st.markdown("##### SHAP Marginal Impact Summary")
        if not SHAP_AVAILABLE:
            st.warning("💡 Package `shap` is not installed. You can run `pip install shap` to activate beeswarm plots.")
        else:
            if st.button("⚡ Calculate SHAP Values on Validation Sample", type="primary", use_container_width=True):
                with st.spinner("Computing SHAP marginal value attributions..."):
                    sample_size = min(200, len(X_val))
                    X_sample = X_val.sample(sample_size, random_state=42)
                    explainer, shap_vals = compute_shap_explanations(frozen_model, X_sample)
                    st.session_state["shap_explainer"] = explainer
                    st.session_state["shap_values"] = shap_vals
                    st.session_state["shap_sample"] = X_sample
                    st.toast("SHAP calculation complete!", icon="🐝")
                
        shap_vals = st.session_state.get("shap_values")
        X_sample = st.session_state.get("shap_sample")
        
        if shap_vals is not None and X_sample is not None:
            fig, ax = plt.subplots(figsize=(10, 6))
            if hasattr(shap_vals, "values"):
                shap.summary_plot(shap_vals.values, X_sample, show=False)
            else:
                shap.summary_plot(shap_vals, X_sample, show=False)
            st.pyplot(fig)
            plt.close(fig)

    with tab3:
        st.markdown("##### Partial Dependence Curves (PDP)")
        st.info("Inspect non-linear effect of a selected feature holding all other variables constant at their mean.")
        selected_pdp_feat = st.selectbox("Select Feature for PDP Curve", options=list(X_val.columns), index=0)
        
        feat_vals = np.linspace(X_val[selected_pdp_feat].min(), X_val[selected_pdp_feat].max(), 50)
        pdp_y = []
        X_mean = X_val.mean().to_dict()
        
        for val in feat_vals:
            X_temp = pd.DataFrame([X_mean] * len(feat_vals))
            X_temp[selected_pdp_feat] = val
            pred = frozen_model.predict(X_temp).mean()
            pdp_y.append(pred)
            
        fig_pdp = px.line(
            x=feat_vals,
            y=pdp_y,
            labels={"x": selected_pdp_feat, "y": f"Predicted {target_col}"},
            title=f"Partial Dependence — {selected_pdp_feat}"
        )
        fig_pdp.update_layout(template=theme_plotly, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pdp, use_container_width=True)
