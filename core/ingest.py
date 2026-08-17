from pathlib import Path
import pandas as pd
import streamlit as st
import kagglehub
from config import RAW_DATA_DIR, CALIFORNIA_HOUSING_DEFAULT_PATH, FALLBACK_RAW_DATA_PATH
from utils.theme import render_section_header


def load_preset_california_housing() -> pd.DataFrame:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if CALIFORNIA_HOUSING_DEFAULT_PATH.exists():
        df = pd.read_csv(CALIFORNIA_HOUSING_DEFAULT_PATH)
        return df
    elif FALLBACK_RAW_DATA_PATH.exists():
        df = pd.read_csv(FALLBACK_RAW_DATA_PATH)
        df.to_csv(CALIFORNIA_HOUSING_DEFAULT_PATH, index=False)
        return df
    else:
        # Download from kagglehub as fallback
        dataset_dir = Path(kagglehub.dataset_download("harrywang/housing"))
        source_file = dataset_dir / "housing.csv"
        df = pd.read_csv(source_file)
        df.to_csv(CALIFORNIA_HOUSING_DEFAULT_PATH, index=False)
        return df


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
            "🏡 Primary Benchmark: California Housing Dataset",
            "📁 Upload Local File (CSV / Excel / Parquet)",
            "🌐 Web API / Direct URL CSV",
            "🤗 Kaggle Dataset Hub"
        ],
        index=0
    )
    
    df = None
    source_name = "California Housing"
    
    if "California Housing" in source_type:
        st.info("💡 **Benchmark Dataset**: California Housing Median Prices (`housing.csv`) containing 20,640 records across 10 features.")
        try:
            df = load_preset_california_housing()
            source_name = "California Housing (Preset)"
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
        url = st.text_input("CSV Direct Endpoint URL", value="https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv")
        if st.button("Fetch Endpoint Data", type="primary"):
            try:
                df = load_from_url(url)
                source_name = f"URL ({url})"
                st.toast("Dataset successfully fetched!", icon="🌐")
            except Exception as e:
                st.error(f"Failed to fetch dataset from URL: {e}")
                
    elif "Kaggle Dataset Hub" in source_type:
        kaggle_handle = st.text_input("Kaggle Dataset Handle (owner/dataset)", value="harrywang/housing")
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
        active_project_id = st.session_state.get("active_project_id", "PRJ-CA-HOUSING-01")
        save_path = RAW_DATA_DIR / f"{active_project_id}_raw.csv"
        df.to_csv(save_path, index=False)
        
    return df
