import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = BASE_DIR / "projects"
REGISTRY_FILE = PROJECTS_DIR / "projects.json"
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SPLITS_DATA_DIR = DATA_DIR / "splits"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

# Ensure essential directories exist
for d in [PROJECTS_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, SPLITS_DATA_DIR, MODELS_DIR, RESULTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Default Groq Settings
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
AVAILABLE_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

# Primary Benchmark Dataset Settings
CHURN_DEFAULT_PATH = RAW_DATA_DIR / "telco_churn.csv"
CHURN_DATASET_URL = (
    "https://raw.githubusercontent.com/ahmedshahriar/"
    "Telco-Customer-Churn-Prediction-Streamlit-App/main/dataset/"
    "Telco-Customer-Churn-dataset.csv"
)

# Pipeline Stages
PIPELINE_STAGES = [
    ("auth", "🔐 Authentication & Workspace"),
    ("projects", "📁 Project Environment"),
    ("ingestion", "📥 1. Data Ingestion"),
    ("validation", "🛡️ 2. Validation & Human Gate"),
    ("eda", "📊 3. Exploratory Data Analysis"),
    ("preprocessing", "🛠️ 4. Feature Engineering Gate"),
    ("predictive", "🤖 5. Predictive ML Path"),
    ("inferential", "🔬 6. Churn Risk Diagnostics"),
    ("explainability", "🔍 7. SHAP & Interpretability"),
    ("comparison", "⚖️ 8. Cross-Window Comparison"),
    ("reports", "📄 9. Reports & Slide Deck"),
    ("ai_chat", "💬 Groq AI Assistant")
]

# Theme Colors
DARK_THEME = {
    "bg": "#0B0F19",
    "card_bg": "rgba(23, 31, 51, 0.7)",
    "border": "rgba(255, 255, 255, 0.1)",
    "text": "#E2E8F0",
    "text_muted": "#94A3B8",
    "accent_primary": "#6366F1",
    "accent_secondary": "#06B6D4",
    "accent_success": "#10B981",
    "accent_warning": "#F59E0B",
    "accent_danger": "#EF4444",
    "shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
}

LIGHT_THEME = {
    "bg": "#F8FAFC",
    "card_bg": "#FFFFFF",
    "border": "rgba(0, 0, 0, 0.08)",
    "text": "#1E293B",
    "text_muted": "#64748B",
    "accent_primary": "#4F46E5",
    "accent_secondary": "#0891B2",
    "accent_success": "#059669",
    "accent_warning": "#D97706",
    "accent_danger": "#DC2626",
    "shadow": "0 4px 16px 0 rgba(0, 0, 0, 0.06)"
}
