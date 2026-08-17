import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
import streamlit as st
from utils.state import set_approval_gate, is_gate_approved
from utils.theme import render_section_header, render_approval_banner
from config import SPLITS_DATA_DIR, PROCESSED_DATA_DIR


def generate_domain_features(df: pd.DataFrame) -> pd.DataFrame:
    df_feat = df.copy()
    cols = df_feat.columns
    
    # California Housing Domain Features
    if "total_rooms" in cols and "households" in cols:
        df_feat["rooms_per_household"] = df_feat["total_rooms"] / (df_feat["households"] + 1e-5)
    if "total_bedrooms" in cols and "total_rooms" in cols:
        df_feat["bedrooms_per_room"] = df_feat["total_bedrooms"] / (df_feat["total_rooms"] + 1e-5)
    if "population" in cols and "households" in cols:
        df_feat["population_per_household"] = df_feat["population"] / (df_feat["households"] + 1e-5)
        
    return df_feat


def preprocess_and_split(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list,
    test_size: float = 0.2,
    val_size: float = 0.2,
    scaling_method: str = "StandardScaler",
    create_domain_features: bool = True
):
    df_proc = df.copy()
    
    if create_domain_features:
        df_proc = generate_domain_features(df_proc)
        
    # Exclude target from features if present
    X_cols = [c for c in df_proc.columns if c != target_col and (c in feature_cols or c in ["rooms_per_household", "bedrooms_per_room", "population_per_household"])]
    
    X = df_proc[X_cols]
    y = df_proc[target_col]
    
    # 1. Split into Train, Validation, Test
    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    val_ratio_relative = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=val_ratio_relative, random_state=42)
    
    # 2. Imputation & Encoding
    num_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X_train.select_dtypes(exclude=[np.number]).columns.tolist()
    
    # Fit imputer on Train only
    if num_cols:
        num_imputer = SimpleImputer(strategy="median")
        X_train_num = pd.DataFrame(num_imputer.fit_transform(X_train[num_cols]), columns=num_cols, index=X_train.index)
        X_val_num = pd.DataFrame(num_imputer.transform(X_val[num_cols]), columns=num_cols, index=X_val.index)
        X_test_num = pd.DataFrame(num_imputer.transform(X_test[num_cols]), columns=num_cols, index=X_test.index)
    else:
        X_train_num, X_val_num, X_test_num = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
    # OneHotEncoding for Categorical
    if cat_cols:
        ohe = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        ohe.fit(X_train[cat_cols])
        ohe_cols = ohe.get_feature_names_out(cat_cols)
        
        X_train_cat = pd.DataFrame(ohe.transform(X_train[cat_cols]), columns=ohe_cols, index=X_train.index)
        X_val_cat = pd.DataFrame(ohe.transform(X_val[cat_cols]), columns=ohe_cols, index=X_val.index)
        X_test_cat = pd.DataFrame(ohe.transform(X_test[cat_cols]), columns=ohe_cols, index=X_test.index)
    else:
        X_train_cat, X_val_cat, X_test_cat = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
    # Combine Imputed Numeric + Encoded Categorical
    X_train_clean = pd.concat([X_train_num, X_train_cat], axis=1)
    X_val_clean = pd.concat([X_val_num, X_val_cat], axis=1)
    X_test_clean = pd.concat([X_test_num, X_test_cat], axis=1)
    
    # 3. Scaling (Fitted on Train only)
    if scaling_method == "StandardScaler":
        scaler = StandardScaler()
    elif scaling_method == "MinMaxScaler":
        scaler = MinMaxScaler()
    elif scaling_method == "RobustScaler":
        scaler = RobustScaler()
    else:
        scaler = None
        
    if scaler:
        X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train_clean), columns=X_train_clean.columns, index=X_train_clean.index)
        X_val_scaled = pd.DataFrame(scaler.transform(X_val_clean), columns=X_val_clean.columns, index=X_val_clean.index)
        X_test_scaled = pd.DataFrame(scaler.transform(X_test_clean), columns=X_test_clean.columns, index=X_test_clean.index)
    else:
        X_train_scaled, X_val_scaled, X_test_scaled = X_train_clean.copy(), X_val_clean.copy(), X_test_clean.copy()
        
    # Create full split dataframes with target
    train_df = X_train_scaled.copy()
    train_df[target_col] = y_train
    
    val_df = X_val_scaled.copy()
    val_df[target_col] = y_val
    
    test_df = X_test_scaled.copy()
    test_df[target_col] = y_test
    
    # Unscaled OLS feature versions for econometric path
    train_ols = pd.concat([X_train_clean, y_train], axis=1)
    val_ols = pd.concat([X_val_clean, y_val], axis=1)
    test_ols = pd.concat([X_test_clean, y_test], axis=1)
    
    return {
        "train": train_df,
        "val": val_df,
        "test": test_df,
        "train_ols": train_ols,
        "val_ols": val_ols,
        "test_ols": test_ols,
        "scaler": scaler,
        "feature_names": list(X_train_clean.columns)
    }


def render_preprocessing_ui():
    render_section_header("🛠️ Stage 4: Preprocessing & Feature Engineering Gate", "Transform raw features, compute domain ratios, apply scalers, and execute data split", icon="🛠️")
    
    df = st.session_state.get("raw_df")
    target_col = st.session_state.get("target_col", "median_house_value")
    selected_features = st.session_state.get("selected_features", [])
    
    if df is None:
        st.warning("⚠️ No dataset loaded. Please complete Stage 1 (Data Ingestion) first.")
        return
        
    is_approved = is_gate_approved("preprocessing")
    render_approval_banner("Feature Transformation & Partition Gate", "Configure scaler, feature engineering, and train/val/test data splits without data leakage", is_approved=is_approved)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("##### 1. Feature Engineering & Scaling")
        create_domain = st.checkbox("💡 Engineer Domain Ratios (`rooms_per_household`, `bedrooms_per_room`, `population_per_household`)", value=True)
        scaling_method = st.selectbox("Select Feature Scaler", ["StandardScaler", "MinMaxScaler", "RobustScaler", "None (Raw)"])
        
    with col2:
        st.markdown("##### 2. Data Partitioning Strategy")
        test_ratio = st.slider("Untouched Test Ratio", 0.1, 0.3, 0.2, 0.05)
        val_ratio = st.slider("Validation Set Ratio", 0.1, 0.3, 0.2, 0.05)

    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    run_proc = st.button("🚀 Execute Preprocessing & Generate Partitions", type="primary", use_container_width=True)
    
    if run_proc or st.session_state.get("train_df") is not None:
        if run_proc:
            with st.spinner("Executing transformations, encodings, scaling, and leakage-safe splits..."):
                proc_results = preprocess_and_split(
                    df,
                    target_col,
                    selected_features,
                    test_size=test_ratio,
                    val_size=val_ratio,
                    scaling_method=scaling_method,
                    create_domain_features=create_domain
                )
                
                st.session_state["train_df"] = proc_results["train"]
                st.session_state["val_df"] = proc_results["val"]
                st.session_state["test_df"] = proc_results["test"]
                st.session_state["train_ols"] = proc_results["train_ols"]
                st.session_state["val_ols"] = proc_results["val_ols"]
                st.session_state["test_ols"] = proc_results["test_ols"]
                st.session_state["feature_names"] = proc_results["feature_names"]
                st.session_state["scaler"] = proc_results["scaler"]
                
                # Save splits to project directory
                proc_results["train"].to_csv(SPLITS_DATA_DIR / "train.csv", index=False)
                proc_results["val"].to_csv(SPLITS_DATA_DIR / "validation.csv", index=False)
                proc_results["test"].to_csv(SPLITS_DATA_DIR / "test.csv", index=False)
                proc_results["train_ols"].to_csv(SPLITS_DATA_DIR / "train_ols.csv", index=False)
                
                set_approval_gate("preprocessing", True)
                st.success("✅ Preprocessing complete! Datasets split cleanly.")
                st.toast("Preprocessing Gate Approved & Saved!", icon="✅")
                
        train_df = st.session_state.get("train_df")
        val_df = st.session_state.get("val_df")
        test_df = st.session_state.get("test_df")
        
        if train_df is not None:
            st.markdown("---")
            st.markdown("##### 📊 Partition Size & Feature Summary")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Training Set (Train)", f"{len(train_df):,}")
            m2.metric("Validation Set (Val)", f"{len(val_df):,}")
            m3.metric("Test Set (Untouched)", f"{len(test_df):,}")
            m4.metric("Engineered Features", len(st.session_state.get("feature_names", [])))
            
            with st.expander("🔍 Preview Preprocessed Training Matrix", expanded=False):
                st.dataframe(train_df.head(10), use_container_width=True)
