import os
import streamlit as st
from config import DEFAULT_GROQ_MODEL, AVAILABLE_GROQ_MODELS
from utils.theme import render_section_header

try:
    from ai_assistant.api_key_config import GROQ_API_KEY as FILE_GROQ_API_KEY
except ImportError:
    FILE_GROQ_API_KEY = ""

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def build_pipeline_context_prompt() -> str:
    ctx = []
    ctx.append("Current Pipeline Context State:")
    
    project_meta = st.session_state.get("active_project_meta", {})
    if project_meta:
        ctx.append(f"- Active Project: {project_meta.get('name')} (ID: {project_meta.get('id')})")
        
    raw_df = st.session_state.get("raw_df")
    if raw_df is not None:
        ctx.append(f"- Dataset Shape: {raw_df.shape[0]} records, {raw_df.shape[1]} features")
        ctx.append(f"- Target Variable: {st.session_state.get('target_col', 'median_house_value')}")
        
    vif_accepted = st.session_state.get("vif_accepted_cols", [])
    if vif_accepted:
        ctx.append(f"- VIF-Accepted Features ({len(vif_accepted)}): {vif_accepted}")
        
    reset_res = st.session_state.get("reset_result", {})
    if reset_res:
        ctx.append(f"- Ramsey RESET Test: F={reset_res.get('f_statistic', 0):.4f}, p={reset_res.get('p_value', 0):.4e}, Passed={reset_res.get('passed')}")
        
    pred_test_m = st.session_state.get("predictive_test_metrics", {})
    if pred_test_m:
        ctx.append(f"- Frozen Predictive Model: {st.session_state.get('frozen_predictive_name')} (Test RMSE=${pred_test_m.get('rmse', 0):,.2f}, R2={pred_test_m.get('r2', 0):.4f})")
        
    inf_test_m = st.session_state.get("inferential_test_metrics", {})
    if inf_test_m:
        ctx.append(f"- Selected Inferential Model Test Metrics: RMSE=${inf_test_m.get('rmse', 0):,.2f}, R2={inf_test_m.get('r2', 0):.4f}")
        
    return "\n".join(ctx)


def estimate_tokens(text: str) -> int:
    return len(text) // 4 + 1


def query_groq_api(api_key: str, model_name: str, messages: list, max_prompt_tokens: int = 4000) -> str:
    if not GROQ_AVAILABLE:
        return "The `groq` Python package is not installed. Run `pip install groq`."
        
    try:
        system_msg = messages[0] if messages and messages[0]["role"] == "system" else None
        chat_msgs = [m for m in messages if m["role"] != "system"]
        
        budget = max_prompt_tokens
        if system_msg:
            budget -= estimate_tokens(system_msg["content"])
            
        pruned_chat = []
        for msg in reversed(chat_msgs):
            msg_tokens = estimate_tokens(msg["content"])
            if budget - msg_tokens > 0:
                pruned_chat.insert(0, msg)
                budget -= msg_tokens
            else:
                break
                
        final_messages = ([system_msg] if system_msg else []) + pruned_chat
        
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=final_messages,
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq API Error: {str(e)}"


def get_heuristic_fallback_response(user_query: str) -> str:
    q = user_query.lower()
    
    if "vif" in q or "multicollinearity" in q:
        return ("**Variance Inflation Factor (VIF)** quantifies severity of correlation among predictors:\n\n"
                "- **VIF = 1**: Uncorrelated\n- **1 < VIF < 5**: Moderate correlation (Acceptable)\n- **VIF > 5 or 10**: Severe multicollinearity!\n\n"
                "In our pipeline, we iteratively prune the maximum VIF feature until all remaining variables fall below the chosen threshold.")
        
    elif "reset" in q or "ramsey" in q:
        return ("**Ramsey RESET Test** checks functional specification errors in linear regression:\n\n"
                "- **Null Hypothesis ($H_0$)**: Linear relationship is correctly specified.\n"
                "- **If $p > 0.05$**: Linear OLS specification is acceptable.\n"
                "- **If $p \\le 0.05$**: Non-linear patterns present! Fit a **Semiparametric GAM** or Non-linear regression model.")
        
    elif "shap" in q or "explain" in q:
        return ("**SHAP Values** compute Shapley game theory attributions:\n\n"
                "- **Beeswarm Plot**: Shows feature value magnitudes vs impact on prediction.\n"
                "- **Partial Dependence**: Shows marginal impact curves holding all other variables constant.")
        
    else:
        return f"I analyzed your query: '{user_query}'. For California house price prediction, key drivers include location, median income, and engineered density ratios. The dual-track predictive and econometrics path ensures full accuracy and decision transparency."


def render_ai_chat_ui():
    render_section_header("💬 Groq AI Assistant — Data Science Co-Pilot", "Context-aware AI assistant powered by Groq (llama-3.3-70b-versatile)", icon="💬")
    
    api_key_input = st.sidebar.text_input("🔑 Groq API Key", type="password", help="Set in ai_assistant/api_key_config.py or enter here")
    groq_api_key = api_key_input or FILE_GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "")

    selected_groq_model = st.sidebar.selectbox("Groq LLM Model Engine", options=AVAILABLE_GROQ_MODELS, index=0)
    
    col_status1, col_status2 = st.columns([7, 3])
    with col_status1:
        if groq_api_key:
            st.markdown(f'<span class="badge-pill badge-success">⚡ Connected to Groq ({selected_groq_model})</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-pill badge-warning">💡 Offline Mode — Heuristic Advisor Active</span>', unsafe_allow_html=True)
            
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    
    # Suggested Prompt Chips
    st.markdown("##### 💡 Suggested Questions")
    chip_col1, chip_col2, chip_col3 = st.columns(3)
    
    prompt_clicked = None
    if chip_col1.button("🔍 Explain VIF & Multicollinearity", key="chip_vif", use_container_width=True):
        prompt_clicked = "Explain VIF elimination and how it helps our linear model."
    if chip_col2.button("📐 Interpret Ramsey RESET Test", key="chip_reset", use_container_width=True):
        prompt_clicked = "How do I interpret the Ramsey RESET test p-value result?"
    if chip_col3.button("🐝 How do SHAP plots work?", key="chip_shap", use_container_width=True):
        prompt_clicked = "Explain SHAP summary beeswarm plots and partial dependence."

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "assistant", "content": "Hello! I am your AI Data Science Co-Pilot. Ask me any question about VIF pruning, Ramsey RESET tests, OLS vs GAM trade-offs, SHAP plots, or model evaluation!"}
        ]
        
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    user_input = st.chat_input("Ask a question about your dataset, statistical tests, or models...")
    actual_query = prompt_clicked or user_input
    
    if actual_query:
        st.session_state["chat_history"].append({"role": "user", "content": actual_query})
        with st.chat_message("user"):
            st.markdown(actual_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing context & generating advice..."):
                if groq_api_key:
                    context_str = build_pipeline_context_prompt()
                    system_prompt = (
                        "You are an expert Data Science and Econometrics AI assistant embedded inside an end-to-end ML platform. "
                        "Help the user understand pipeline steps, VIF elimination, Ramsey RESET specification tests, OLS vs GAM models, "
                        "and SHAP interpretability. Answer clearly in concise markdown.\n\n" + context_str
                    )
                    messages = [
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state["chat_history"] if m["role"] != "system"]
                    ]
                    response_text = query_groq_api(groq_api_key, selected_groq_model, messages)
                else:
                    response_text = get_heuristic_fallback_response(actual_query)
                    
                st.markdown(response_text)
                st.session_state["chat_history"].append({"role": "assistant", "content": response_text})
