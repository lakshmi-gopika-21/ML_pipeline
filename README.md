# Customer Churn Prediction Pipeline

An end-to-end Streamlit application for exploring customer data, training churn classifiers, and evaluating customers' churn risk to support retention planning.

## Features

- **IBM Telco Customer Churn dataset** with 7,043 customer records and the binary `Churn` target.
- Data ingestion from the included dataset, CSV/Excel/Parquet uploads, direct CSV URLs, or Kaggle.
- Data quality review and configurable target/feature selection.
- Preprocessing with missing-value imputation, categorical encoding, feature scaling, and stratified train/validation/test splits.
- Churn-specific feature engineering, including customer value to date and average monthly charge.
- Classification model comparison with Logistic Regression, Random Forest, Gradient Boosting, and Extra Trees.
- Accuracy, precision, recall, F1, and ROC-AUC reporting.
- Model freeze and evaluation on an untouched test split.
- Executive reports, project workspaces, and an optional Groq-powered assistant.

## Requirements

- Python 3.10 or later
- pip
- A Groq API key only if you want to use the AI assistant

## Quick start

From the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`).

On systems where the `py` launcher is unavailable, use `python` in its place.

## Using the churn workflow

1. Sign in to the application. For a local demo, the default analyst account is `analyst` / `analyst123`; you can also create an account from the registration tab.
2. Load **IBM Telco Customer Churn** from Data Ingestion, or upload a dataset that has a binary churn target.
3. In Validation, select `Churn` as the target and choose input features. Avoid identifiers such as customer IDs as predictors.
4. Run preprocessing to create stratified training, validation, and test splits.
5. Benchmark the classification models and select one using validation metrics. For retention use cases, consider recall alongside ROC-AUC and precision.
6. Freeze the selected model to evaluate it on the untouched test set.
7. Review the model comparison and generate a report.

The default dataset is stored at `data/raw/telco_churn.csv`; if it is missing, the application downloads it from the dataset URL configured in `config.py`.

## Optional Groq assistant

The assistant uses Groq Compound by default (`groq/compound`) and also offers `groq/compound-mini`. Provide a key through the in-app key field or the `GROQ_API_KEY` environment variable. For example, in PowerShell:

```powershell
$env:GROQ_API_KEY = "your-groq-api-key"
streamlit run app.py
```

Do not commit API keys or other credentials to the repository.

## Repository layout

```text
app.py                 Streamlit application entry point
config.py              Paths, Groq models, and pipeline stages
core/                  Ingestion, validation, EDA, preprocessing, and modeling
ai_assistant/          Optional Groq assistant
data/raw/              Included and project input datasets
models/                Saved model artifacts
projects/              Project configuration and registry
requirements.txt       Python dependencies
```

## Notes

- This project is an analytics/demo pipeline. Its churn estimates should be validated against your own customer population before being used to make business decisions.
- The `statsmodels`-based econometrics stage is not used for churn classification; use the classification metrics in the predictive stage instead.
- Uploaded data and generated artifacts may be written under `data/`, `models/`, `projects/`, and `results/`.
