import os
import sys
import pandas as pd
import numpy as np

# Ensure app root in sys.path
sys.path.insert(0, os.path.dirname(__file__))

print("--- STARTING FULL ML PIPELINE INTEGRATION TEST ---")

# 1. Project Manager & Registry
import project_manager
registry = project_manager.load_registry()
print(f"[OK] Project Registry Loaded. Found {len(registry.get('recent_projects', []))} project(s).")
meta = project_manager.create_project("PRJ-TEST-01", "Integration Test Project")
print(f"[OK] Created Project PRJ-TEST-01: {meta['name']}")

# 2. Data Ingestion
from core import ingest
raw_df = ingest.load_preset_california_housing()
print(f"[OK] Data Ingestion successful. Loaded California Housing shape: {raw_df.shape}")

# 3. Data Validation
from core import validate
val_report = validate.validate_dataframe(raw_df)
print(f"[OK] Data Validation audit complete. Missing columns count: {sum(1 for v in val_report['missing_summary'].values() if v['count'] > 0)}")

# 4. Preprocessing & Feature Engineering
from core import preprocess
target_col = "median_house_value"
feature_cols = [c for c in raw_df.columns if c != target_col]
proc_res = preprocess.preprocess_and_split(raw_df, target_col, feature_cols, create_domain_features=True)
train_df = proc_res["train"]
val_df = proc_res["val"]
test_df = proc_res["test"]
train_ols = proc_res["train_ols"]
val_ols = proc_res["val_ols"]
test_ols = proc_res["test_ols"]
print(f"[OK] Preprocessing complete. Train samples: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

# 5. Predictive ML Model Basket
from core import predictive_pipeline
rf_res = predictive_pipeline.train_and_eval_predictive_model("Random Forest Regressor", train_df, val_df, target_col)
gb_res = predictive_pipeline.train_and_eval_predictive_model("Gradient Boosting Regressor", train_df, val_df, target_col)
sgd_res = predictive_pipeline.train_and_eval_predictive_model("SGD Regressor (Gradient Descent)", train_df, val_df, target_col)
print(f"[OK] Predictive Models trained.")
print(f"     Random Forest Val R2: {rf_res['val_metrics']['r2']:.4f}")
print(f"     Gradient Boosting Val R2: {gb_res['val_metrics']['r2']:.4f}")
print(f"     SGD Regressor Val R2: {sgd_res['val_metrics']['r2']:.4f}")

# 6. Inferential & Econometric Analytics Path
from core import inferential_pipeline
X_train_ols = train_ols.drop(columns=[target_col])
y_train_ols = train_ols[target_col]
vif_accepted, vif_hist = inferential_pipeline.iterative_vif_elimination(X_train_ols, list(X_train_ols.columns), threshold=5.0)
print(f"[OK] VIF Elimination complete. VIF-accepted features ({len(vif_accepted)}): {vif_accepted}")

import statsmodels.api as sm
X_train_const = sm.add_constant(X_train_ols[vif_accepted])
ols_model = sm.OLS(y_train_ols, X_train_const).fit()
reset_res = inferential_pipeline.run_ramsey_reset(ols_model)
print(f"[OK] Ramsey RESET Test complete. F-stat={reset_res['f_statistic']:.4f}, p-val={reset_res['p_value']:.4e}, Passed={reset_res['passed']}")

gam_res = inferential_pipeline.fit_gam_model(train_ols, val_ols, vif_accepted, target_col)
print(f"[OK] Non-linear / GAM Model fitted. Val R2: {gam_res['val_metrics']['r2']:.4f}")

# 7. Groq AI Assistant & Token Optimization
from ai_assistant import groq_chat
from ai_assistant.api_key_config import GROQ_API_KEY

print(f"[OK] Groq API Key loaded: {GROQ_API_KEY[:8]}... length={len(GROQ_API_KEY)}")
test_msg = [{"role": "system", "content": "You are an AI assistant."}, {"role": "user", "content": "Explain VIF in 1 sentence."}]
ai_resp = groq_chat.query_groq_api(GROQ_API_KEY, "llama-3.3-70b-versatile", test_msg)
print(f"[OK] Groq API Response: {ai_resp[:120]}...")

# 8. Reports Generation
from core import reporter
report_md = reporter.generate_markdown_report(meta)
print(f"[OK] Executive Report generated. Length: {len(report_md)} characters.")

print("--- ALL PIPELINE STAGES PASSED INTEGRATION TEST WITH 0 ERRORS! ---")
