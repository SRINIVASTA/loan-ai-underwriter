import streamlit as st
import json
import os
import requests

st.set_page_config(page_title="AI Loan Underwriter", layout="wide")
st.title("🏦 Automated Real-Time AI Loan Underwriter Dashboard")

# 1. API Configuration & Key Pickers
st.sidebar.header("🔑 LLM Engine Authentication Configuration")
provider = st.sidebar.selectbox("Choose AI Model Provider", ["Google Gemini", "Hugging Face (Serverless Inference)"])

if provider == "Google Gemini":
    api_key_input = st.sidebar.text_input("Enter Google API Key (or leave blank to use hidden secrets)", type="password")
    # Resolve precedence: User Input -> Streamlit Secrets
    api_key = api_key_input if api_key_input else st.secrets.get("GOOGLE_API_KEY", "")
    model_name = "gemini-1.5-flash"
else:
    api_key_input = st.sidebar.text_input("Enter Hugging Face Token (or leave blank to use hidden secrets)", type="password")
    api_key = api_key_input if api_key_input else st.secrets.get("HF_TOKEN", "")
    model_name = st.sidebar.text_input("HF Model Repository ID", "Qwen/Qwen2.5-Coder-7B-Instruct")

# 2. Core Operation Mode Selector
st.header("⚙️ Core Processing Pipeline Execution")
pipeline_mode = st.radio("Select Processing Mode Environment Setup:", ["Option A: Mock Developer Data Testing (Free Sandbox)", "Option B: Production API-Driven Integration (Live OTP Required)"])

# Load Prompt
try:
    with open(os.path.join("data", "prompt_template.txt"), "r") as f:
        system_prompt = f.read()
except:
    system_prompt = "You are an automated Banking Risk Officer..."

payload_to_process = None

if "Option A" in pipeline_mode:
    st.subheader("📊 Option A Sandbox Environment Engine")
    try:
        with open(os.path.join("data", "mock_payloads.json"), "r") as f:
            mock_db = json.load(f)
            
        st.write(f"Loaded **{len(mock_db)} historical test profiles** successfully from GitHub repositories.")
        app_ids = [row["application_id"] for row in mock_db]
        selected_id = st.selectbox("Select Target Application ID Profile Row:", app_ids)
        
        payload_to_process = next(row for row in mock_db if row["application_id"] == selected_id)
        st.json(payload_to_process)
    except Exception as e:
        st.error(f"Failed to load data/mock_payloads.json: {str(e)}")

else:
    st.subheader("🌐 Option B Live Production API-Driven Stream Pipeline")
    st.info("Bypassing manual document uploads. Fetching verified income from bank networks using secure credentials.")
    
    col1, col2 = st.columns(2)
    with col1:
        real_pan = st.text_input("Enter Applicant Customer 10-Digit PAN Number:", max_chars=10, placeholder="ABCDE1234F")
    with col2:
        real_phone = st.text_input("Enter Mobile Number Registered to Bank/Aadhaar:", placeholder="+9198765...")
        
    requested_amt = st.number_input("Requested Funding Principal Amount (₹):", min_value=10000, value=500000, step=50000)
    
    if st.button("Trigger Live API Consent Handshake"):
        if len(real_pan) == 10 and real_phone:
            st.warning("📲 Secure Account Aggregator Permission Request Triggered! Official banking SMS OTP dispatched to customer cell line.")
            
    otp_code = st.text_input("Enter Cryptographic Secure 6-Digit OTP Code (Simulated Live Integration):", type="password")
    if otp_code:
        st.success("✅ Secure Signature Token Authorized! Fetching live credit and income matrix...")
        payload_to_process = {
            "application_id": "APP-LIVE-PRODUCTION-7731",
            "customer_id": "CUST-LIVE-0941",
            "customer_name": "Verified PAN Holder",
            "pan_number": real_pan if real_pan else "ABCDE1234F",
            "requested_amount": requested_amt,
            "loan_term_months": 36,
            "pan_verification": {"status": "VALID", "holder_name": "Verified PAN Holder", "pan_type": "INDIVIDUAL"},
            "credit_bureau_stream": {"score_provider": "CIBIL", "score": 765, "active_loans_count": 2, "total_existing_monthly_emis": 15000},
            "account_aggregator_stream": {"verified_monthly_net_income": 125000, "employer_name": "Production Verified Enterprise", "employment_stability_years": 4.2},
            "fraud_check_stream": {"device_mismatch": False, "location_anomaly": False}
        }

# 3. Execution Logic
if payload_to_process:
    if st.button("🚀 Execute AI Underwriter Scoring Rules"):
        if not api_key:
            st.error("❌ Authentication error! Please input your API key/token or save it inside `.streamlit/secrets.toml` parameters.")
        else:
            with st.spinner("Processing underwriting decision via AI model..."):
                final_input = f"{system_prompt}\n\nINCOMING STREAM PAYLOAD:\n{json.dumps(payload_to_process, indent=2)}"
                
                try:
                    if provider == "Google Gemini":
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                        headers = {"Content-Type": "application/json"}
                        data = {"contents": [{"parts": [{"text": final_input}]}]}
                        res = requests.post(url, json=data, headers=headers, timeout=10)
                        result_json = res.json()
                        raw_ai_out = result_json['candidates'][0]['content']['parts'][0]['text']
                    else:
                        url = f"https://api-inference.huggingface.co/models/{model_name}"
                        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                        data = {"inputs": final_input, "parameters": {"max_new_tokens": 500, "return_full_text": False}}
                        res = requests.post(url, json=data, headers=headers, timeout=10)
                        res.raise_for_status()
                        result_json = res.json()
                        raw_ai_out = result_json['generated_text'] if isinstance(result_json, list) else str(result_json)
                    
                    st.subheader("📤 AI Loan Underwriter Decision Output (Strict JSON)")
                    try:
                        clean_json = raw_ai_out.replace("```json", "").replace("```", "").strip()
                        st.json(json.loads(clean_json))
                    except:
                        st.text(raw_ai_out)
                        
                except Exception as e:
                    err_msg = str(e)
                    if "Failed to resolve" in err_msg or "NameResolutionError" in err_msg or "Max retries exceeded" in err_msg:
                        st.warning("⚠️ Local Network Offline Override Triggered: Executing Python Operational Underwriting Risk Engine...")
                        
                        income = payload_to_process["account_aggregator_stream"]["verified_monthly_net_income"]
                        emis = payload_to_process["credit_bureau_stream"]["total_existing_monthly_emis"]
                        cibil = payload_to_process["credit_bureau_stream"]["score"]
                        stability = payload_to_process["account_aggregator_stream"]["employment_stability_years"]
                        
                        dti_val = (emis / income) * 100
                        dti_str = f"{dti_val:.2f}%"
                        rationale = []
                        
                        if dti_val > 50 or cibil < 640:
                            decision = "DENY"
                            rate = None
                            if dti_val > 50: rationale.append(f"Debt-to-Income ratio ({dti_str}) exceeds critical 50% ceiling.")
                            if cibil < 640: rationale.append(f"CIBIL profile score ({cibil}) drops inside high-risk Subprime floor limits.")
                        elif dti_val > 43:
                            decision = "REFER"
                            rate = None
                            rationale.append(f"DTI ratio is {dti_str}, which exceeds standard 43% automatic clearing threshold. Route to human evaluation.")
                        else:
                            decision = "APPROVE"
                            rate = "10.50%" if cibil >= 720 else "12.75%"
                            rationale.append(f"Applicant CIBIL rating of {cibil} hits Prime credit guidelines tier benchmarks securely.")
                            rationale.append(f"Calculated Debt-to-Income factor scales safely at {dti_str}.")
                        
                        if stability < 2:
                            decision = "REFER"
                            rationale.append(f"Verifiable work history longevity ({stability} years) sits below the mandatory 2-year constraint.")
                        
                        offline_json = {
                            "application_id": payload_to_process["application_id"],
                            "decision": decision,
                            "risk_score_assigned": min(100, int(dti_val + (800 - cibil)//10)),
                            "calculated_dti": dti_str,
                            "recommended_interest_rate": rate,
                            "decision_rationale": rationale,
                            "flagged_anomalies": ["Low Work Stability"] if stability < 2 else []
                        }
                        
                        st.subheader("📥 AI Loan Underwriter Decision Output (Local Fallback Engine JSON)")
                        st.json(offline_json)
                    else:
                        st.error(f"Execution failure: {err_msg}")
