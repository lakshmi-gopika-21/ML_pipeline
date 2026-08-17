import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.theme import render_section_header


def render_eda_ui():
    render_section_header("📊 Stage 3: Interactive Exploratory Data Analysis", "Analyze empirical distributions, feature correlations, non-linearities, and spatial patterns", icon="📊")
    
    df = st.session_state.get("raw_df")
    target_col = st.session_state.get("target_col", "median_house_value")
    
    if df is None:
        st.warning("⚠️ No dataset loaded. Please complete Stage 1 (Data Ingestion) first.")
        return

    theme_plotly = "plotly_dark" if st.session_state.get("theme", "Dark") == "Dark" else "plotly_white"

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Summary Stats & Distributions",
        "🔥 Correlation & Multicollinearity",
        "🎯 Feature vs Target Relationships",
        "🗺️ Geospatial & Missingness Maps"
    ])
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    with tab1:
        st.markdown("##### Numeric Feature Summary Statistics")
        st.dataframe(df.describe().T, use_container_width=True)
        
        st.markdown("##### Distribution Analysis")
        selected_dist_col = st.selectbox("Select Column for Distribution Analysis", options=numeric_cols, index=0)
        
        fig_hist = px.histogram(
            df,
            x=selected_dist_col,
            marginal="box",
            title=f"Distribution & Boxplot — {selected_dist_col}",
            color_discrete_sequence=["#6366F1"]
        )
        fig_hist.update_layout(template=theme_plotly, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with tab2:
        st.markdown("##### Pearson Correlation Matrix")
        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            fig_corr = px.imshow(
                corr,
                text_auto=".2f",
                color_continuous_scale="Viridis",
                title="Multicollinearity & Correlation Matrix"
            )
            fig_corr.update_layout(template=theme_plotly, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Insufficient numeric columns for correlation matrix.")

    with tab3:
        st.markdown(f"##### Feature Scatter Analysis vs Target (`{target_col}`)")
        feat_for_scatter = [c for c in numeric_cols if c != target_col]
        if feat_for_scatter:
            col_x, col_c = st.columns([1, 1])
            with col_x:
                selected_feat = st.selectbox("X-Axis Feature", options=feat_for_scatter, index=0)
            with col_c:
                color_by = st.selectbox("Color Segment (Optional)", options=["None"] + categorical_cols)
            
            fig_scatter = px.scatter(
                df,
                x=selected_feat,
                y=target_col,
                color=None if color_by == "None" else color_by,
                opacity=0.6,
                trendline="ols",
                title=f"{selected_feat} vs {target_col} (with OLS Trendline)"
            )
            fig_scatter.update_layout(template=theme_plotly, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_scatter, use_container_width=True)
            
    with tab4:
        col_g1, col_g2 = st.columns([1, 1])
        
        with col_g1:
            st.markdown("##### Geospatial Scatter Map")
            if "longitude" in df.columns and "latitude" in df.columns:
                fig_geo = px.scatter(
                    df,
                    x="longitude",
                    y="latitude",
                    color=target_col if target_col in df.columns else None,
                    size="population" if "population" in df.columns else None,
                    color_continuous_scale="Jet",
                    title="Geographic Location vs Target Value",
                    opacity=0.5
                )
                fig_geo.update_layout(template=theme_plotly, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_geo, use_container_width=True)
            else:
                st.info("No spatial coordinates (`longitude`, `latitude`) detected.")
                
        with col_g2:
            st.markdown("##### Missing Data Heatmap Matrix")
            missing_matrix = df.isna()
            fig_miss = px.imshow(
                missing_matrix.T,
                labels=dict(x="Record Index", y="Feature Name"),
                title="Missing Value Pattern Heatmap",
                color_continuous_scale=["#10B981", "#EF4444"]
            )
            fig_miss.update_layout(template=theme_plotly, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_miss, use_container_width=True)
