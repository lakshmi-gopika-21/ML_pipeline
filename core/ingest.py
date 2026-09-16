from pathlib import Path
import pandas as pd
import streamlit as st
import kagglehub
from config import RAW_DATA_DIR, CHURN_DEFAULT_PATH, CHURN_DATASET_URL
from utils.theme import render_section_header


def load_preset_churn_dataset() -> pd.DataFrame:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if not CHURN_DEFAULT_PATH.exists():
        df = pd.read_csv(CHURN_DATASET_URL)
        df.to_csv(CHURN_DEFAULT_PATH, index=False)
    return pd.read_csv(CHURN_DEFAULT_PATH)


def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    filename = uploaded_file.name
    if filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(uploaded_file)
    elif filename.endswith(".parquet"):
        df = pd.read_parquet(uploaded_file)
    else:
        raise ValueError("Unsupported file format.")
    return df


def load_from_url(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    return df


def load_from_kaggle(dataset_handle: str) -> pd.DataFrame:
    dataset_dir = Path(kagglehub.dataset_download(dataset_handle))
    csv_files = list(dataset_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV file found in Kaggle dataset.")
    df = pd.read_csv(csv_files[0])
    return df


def render_ingestion_ui():
    render_section_header("📥 Stage 1: Multi-Source Data Ingestion", "Select or upload the raw dataset for the active project pipeline", icon="📥")
    
    source_type = st.radio(
        "Choose Data Source Provider",
        options=[
            "📞 Primary Benchmark: IBM Telco Customer Churn",
            "📁 Upload Local File (CSV / Excel / Parquet)",
            "🌐 Web API / Direct URL CSV",
            "🤗 Kaggle Dataset Hub"
        ],
        index=0
    )
    
    df = None
    source_name = "IBM Telco Customer Churn"
    
    if "Telco Customer Churn" in source_type:
        st.info("💡 **Real benchmark dataset**: IBM Telco Customer Churn, 7,043 customer records with account, service, demographic, and billing features.")
        try:
            df = load_preset_churn_dataset()
            source_name = "IBM Telco Customer Churn (Preset)"
        except Exception as e:
            st.error(f"Error loading California housing dataset: {e}")
            
    elif "Upload Local File" in source_type:
        uploaded_file = st.file_uploader("Upload CSV, Excel, or Parquet file", type=["csv", "xlsx", "xls", "parquet"])
        if uploaded_file is not None:
            try:
                df = load_uploaded_file(uploaded_file)
                source_name = f"Uploaded File ({uploaded_file.name})"
                st.toast(f"Loaded `{uploaded_file.name}`", icon="✅")
            except Exception as e:
                st.error(f"Failed to read file: {e}")
                
    elif "Web API" in source_type:
        url = st.text_input("CSV Direct Endpoint URL", value=CHURN_DATASET_URL)
        if st.button("Fetch Endpoint Data", type="primary"):
            try:
                df = load_from_url(url)
                source_name = f"URL ({url})"
                st.toast("Dataset successfully fetched!", icon="🌐")
            except Exception as e:
                st.error(f"Failed to fetch dataset from URL: {e}")
                
    elif "Kaggle Dataset Hub" in source_type:
        kaggle_handle = st.text_input("Kaggle Dataset Handle (owner/dataset)", value="blastchar/telco-customer-churn")
        if st.button("Download from Kaggle", type="primary"):
            try:
                df = load_from_kaggle(kaggle_handle)
                source_name = f"Kaggle ({kaggle_handle})"
                st.toast(f"Downloaded `{kaggle_handle}`", icon="🤗")
            except Exception as e:
                st.error(f"Failed to download Kaggle dataset: {e}")

    if df is not None:
        st.session_state["raw_df"] = df
        st.session_state["data_source_name"] = source_name
        
        st.markdown(f"##### 📊 Ingested Dataset Summary — `{source_name}`")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", f"{df.shape[0]:,}")
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Numeric Columns", len(df.select_dtypes(include=['number']).columns))
        col4.metric("Categorical Columns", len(df.select_dtypes(exclude=['number']).columns))
        
        st.dataframe(df.head(10), use_container_width=True)
        
        # Save raw dataset to project raw folder
        active_project_id = st.session_state.get("active_project_id", "PRJ-TELCO-CHURN-01")
        save_path = RAW_DATA_DIR / f"{active_project_id}_raw.csv"
        df.to_csv(save_path, index=False)
        
    return df
