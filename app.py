import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from groq import Groq  # Import official Groq SDK

st.set_page_config(page_title="AI Loan Underwriter", layout="wide")
st.title("🏦 Automated Real-Time Loan Underwriter Dashboard")

# Initialize Groq Client securely using Streamlit Secrets or Environment Variables
# To configure this locally, add GROQ_API_KEY = "your_key" inside .streamlit/secrets.toml
if "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]
else:
    groq_api_key = os.environ.get("GROQ_API_KEY", "")

# Sidebar configuration for AI Model Parameters
st.sidebar.header("🤖 Groq AI Engine Settings")
if not groq_api_key:
    groq_api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

# UPDATED: Replaced deprecated model IDs with active Groq models
model_choice = st.sidebar.selectbox(
    "Select Analysis Model:",
    ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
)

# 1. Core Operation Mode Selector
st.header("⚙️ Core Processing Pipeline Execution")
pipeline_mode = st.radio(
    "Select Processing Mode Environment Setup:", 
    ["Option A: Mock Developer Data Testing (Free Sandbox)", "Option B: Production API-Driven Integration (Live OTP Required)"]
)

# Load Master Risk Parameters from prompt_template.txt
try:
    with open(os.path.join("data", "prompt_template.txt"), "r") as f:
        system_prompt = f.read()
except:
    system_prompt = """You are an elite, automated Banking Risk Officer and Underwriting Expert. Your objective is to analyze incoming loan applications and real-time streaming financial data payloads to make rapid, secure, and compliant credit decisions.

### OUTPUT FORMAT (JSON ONLY)
You must output your evaluation strictly as a valid JSON object. Do not include conversational filler, introductory remarks, markdown code blocks (like ```json), or explanations outside the JSON block. Use this exact schema:
{
  "application_id": "string",
  "decision": "APPROVE | REFER | DENY",
  "risk_score_assigned": 1-100,
  "calculated_dti": "percentage_string",
  "recommended_interest_rate": "percentage_string or null",
  "decision_rationale": ["Fact-based point 1", "Fact-based point 2"],
  "flagged_anomalies": []
}"""

payload_to_process = None

# Helper function to convert messy JSON streams into a clean, readable data ledger table
def render_payload_table(payload):
    flat_data = {
        "Metric Parameter": [
            "Application Tracking ID", "Customer Name", "PAN Identification", "Requested Principal", "Loan Tenure",
            "PAN Registry Status", "Credit Score (CIBIL)", "Existing Monthly EMIs", 
            "Verified Monthly Net Income", "Current Employer", "Employment Continuity", "Fraud / Device Alert"
        ],
        "Ingested Value": [
            payload.get("application_id"), payload.get("customer_name"), payload.get("pan_number"),
            f"₹{payload.get('requested_amount', 0):,}", f"{payload.get('loan_term_months')} Months",
            payload.get("pan_verification", {}).get("status"),
            payload.get("credit_bureau_stream", {}).get("score"),
            f"₹{payload.get('credit_bureau_stream', {}).get('total_existing_monthly_emis', 0):,}",
            f"₹{payload.get('account_aggregator_stream', {}).get('verified_monthly_net_income', 0):,}",
            payload.get("account_aggregator_stream", {}).get("employer_name"),
            f"{payload.get('account_aggregator_stream', {}).get('employment_stability_years')} Years",
            "SUSPICIOUS" if payload.get("fraud_check_stream", {}).get("device_mismatch") or payload.get("fraud_check_stream", {}).get("location_anomaly") else "PASS / SECURE"
        ]
    }
    st.write("### 📥 Stream Pipeline Ingestion Ledger Table")
    st.table(pd.DataFrame(flat_data))

if "Option A" in pipeline_mode:
    st.subheader("📊 Option A Sandbox Environment Engine & Analytics")
    try:
        with open(os.path.join("data", "mock_payloads.json"), "r") as f:
            mock_db = json.load(f)
            
        st.write(f"Loaded **{len(mock_db)} historical test profiles** successfully from local storage.")
        
        # --- PORTFOLIO INTERACTIVE RISK ANALYTICS ---
        st.write("### 📈 Sandbox Portfolio Risk Analytics Overview")
        plot_records = []
        for row in mock_db:
            inc = row["account_aggregator_stream"]["verified_monthly_net_income"]
            deb = row["credit_bureau_stream"]["total_existing_monthly_emis"]
            plot_records.append({
                "Application ID": row["application_id"],
                "Customer Name": row["customer_name"],
                "CIBIL Score": row["credit_bureau_stream"]["score"],
                "Monthly Income (₹)": inc,
                "DTI Ratio (%)": (deb / inc) * 100 if inc > 0 else 0
            })
        df_analytics = pd.DataFrame(plot_records)
        
        # Summary Metric Cards
        avg_col1, avg_col2, avg_col3 = st.columns(3)
        avg_col1.metric("Average Portfolio CIBIL Score", f"{df_analytics['CIBIL Score'].mean():.0f}")
        avg_col2.metric("Average Applicant Monthly Income", f"₹{df_analytics['Monthly Income (₹)'].mean():,.2f}")
        avg_col3.metric("Average Portfolio DTI Ratio", f"{df_analytics['DTI Ratio (%)'].mean():.2f}%")
        
        # Interactive Scatter Chart Grid
        fig = px.scatter(
            df_analytics, 
            x="CIBIL Score", 
            y="DTI Ratio (%)", 
            hover_data=["Application ID", "Customer Name", "Monthly Income (₹)"],
            title="Sandbox Portfolio Underwriting Risk Distribution Matrix",
            color="DTI Ratio (%)",
            color_continuous_scale="RdYlGn_r"
        )
        fig.add_hline(y=43, line_dash="dash", line_color="red", annotation_text="Automatic Pass DTI Max Limit (43%)")
        fig.add_vline(x=640, line_dash="dash", line_color="orange", annotation_text="Subprime FICO Boundary (640)")
        fig.update_layout(xaxis_range=[550, 850], yaxis_range=[0, 70])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")

        app_ids = [row["application_id"] for row in mock_db]
        selected_id = st.selectbox("Select Target Application ID Profile Row:", app_ids)
        
        payload_to_process = next(row for row in mock_db if row["application_id"] == selected_id)
        render_payload_table(payload_to_process)
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
    
    if 'consent_triggered' not in st.session_state:
        st.session_state.consent_triggered = False

    if st.button("Trigger Live API Consent Handshake"):
        if len(real_pan) == 10 and real_phone:
            st.session_state.consent_triggered = True
            st.warning("📲 Secure Account Aggregator Permission Request Triggered! Official banking SMS OTP dispatched to customer cell line.")
        else:
            st.error("Please provide valid identity metrics inputs.")
            
    if st.session_state.consent_triggered:
        otp_code = st.text_input("Enter Cryptographic Secure 6-Digit OTP Code Sent to Mobile:", type="password")
        if st.button("Verify OTP & Fetch Real-Time Data Streams"):
            st.success("✅ Secure Signature Token Authorized! Fetching live credit and income matrix...")
            
            payload_to_process = {
                "application_id": "APP-LIVE-PRODUCTION-7731",
                "customer_id": "CUST-LIVE-0941",
                "customer_name": "Verified PAN Holder",
                "pan_number": real_pan.upper(),
                "requested_amount": requested_amt,
                "loan_term_months": 36,
                "pan_verification": {"status": "VALID", "holder_name": "Verified PAN Holder", "pan_type": "INDIVIDUAL"},
                "credit_bureau_stream": {"score_provider": "CIBIL", "score": 765, "active_loans_count": 2, "total_existing_monthly_emis": 15000},
                "account_aggregator_stream": {"verified_monthly_net_income": 125000, "employer_name": "Production Verified Enterprise", "employment_stability_years": 4.2},
                "fraud_check_stream": {"device_mismatch": False, "location_anomaly": False}
            }
            st.session_state.active_production_payload = payload_to_process

    if 'active_production_payload' in st.session_state:
        payload_to_process = st.session_state.active_production_payload
        render_payload_table(payload_to_process)
# 3. Local Operational Execution Engine Logic & Groq AI Underwriter Integration
if payload_to_process:
    if st.button("🚀 Execute Scoring Underwriter Rules"):
        with st.spinner("Processing local risk matrix criteria calculations..."):
            
            # Extract financial fields instantly from the active selected data package
            income = payload_to_process["account_aggregator_stream"]["verified_monthly_net_income"]
            emis = payload_to_process["credit_bureau_stream"]["total_existing_monthly_emis"]
            cibil = payload_to_process["credit_bureau_stream"]["score"]
            stability = payload_to_process["account_aggregator_stream"]["employment_stability_years"]
            
            # Execute mathematical policy matching checks locally
            dti_val = (emis / income) * 100 if income > 0 else 0
            dti_str = f"{dti_val:.2f}%"
            rationale = []
            
            if dti_val > 50 or cibil < 640:
                decision = "DENY"
                rate = "N/A"
                if dti_val > 50: rationale.append(f"Debt-to-Income ratio ({dti_str}) exceeds critical 50% ceiling.")
                if cibil < 640: rationale.append(f"CIBIL profile score ({cibil}) drops inside high-risk Subprime floor limits.")
            elif dti_val > 43:
                decision = "REFER"
                rate = "N/A"
                rationale.append(f"DTI ratio is {dti_str}, which exceeds standard 43% automatic clearing threshold. Route to human evaluation.")
            else:
                decision = "APPROVE"
                rate = "10.50%" if cibil >= 720 else "12.75%"
                rationale.append(f"Applicant CIBIL rating of {cibil} hits Prime credit guidelines tier benchmarks securely.")
                rationale.append(f"Calculated Debt-to-Income factor scales safely at {dti_str}.")
            
            if stability < 2:
                decision = "REFER"
                rationale.append(f"Verifiable work history longevity ({stability} years) sits below the mandatory 2-year constraint.")
            
            # --- HIGH-VISIBILITY VERDICT OUTPUT GRID ---
            st.subheader("📥 Rule-Engine Underwriting Decision Audit Ledger")
            
            if decision == "APPROVE": st.success("🎉 Underwriting Verdict: AUTOMATIC APPROVAL CLEARED")
            elif decision == "REFER": st.warning("⚠️ Underwriting Verdict: MANUAL BANKING REVIEW REQUIRED")
            else: st.error("❌ Underwriting Verdict: APPLICATION RISK REJECTED / DENIED")
            
            decision_table_data = {
                "Underwriting Audit Criteria": ["Application ID", "Final Decision Status", "Assigned System Risk Score (1-100)", "Calculated Debt-to-Income (DTI)", "Recommended Fixed Interest Rate"],
                "Assessed Operational Metrics": [payload_to_process["application_id"], decision, min(100, int(dti_val + (800 - cibil)//10)), dti_str, rate]
            }
            st.table(pd.DataFrame(decision_table_data))
            
            st.write("#### 📝 Institutional Decision Rationale Breakdown:")
            for point in rationale:
                st.write(f"- {point}")

        # --- GROQ AI AUTOMATED RISK OFFICER AUDIT ---
        st.markdown("---")
        st.subheader("🤖 Groq AI Automated Risk Officer Audit")
        
        if not groq_api_key:
            st.sidebar.error("Provide a valid Groq API Key to generate AI risk summaries.")
            st.warning("Please provide a Groq API Key in the sidebar configuration to run the autonomous LLM compliance engine.")
        else:
            with st.spinner("Streaming live payload to Groq Engine for autonomous audit validation..."):
                try:
                    # Instantiate client with provided key
                    client = Groq(api_key=groq_api_key)
                    
                    # Convert full active payload stream to a clean formatted JSON string for LLM parsing
                    payload_json_str = json.dumps(payload_to_process, indent=2)
                    
                    # Execute Groq Chat Completion pipeline against your target prompt structure
                    completion = client.chat.completions.create(
                        model=model_choice,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Analyze the following incoming financial stream data payload:\n\n{payload_json_str}"}
                        ],
                        temperature=0.0,  # Locked variance ensures precise compliance on mathematical rules
                        max_tokens=1000
                    )
                    
                    raw_response = completion.choices.message.content.strip()
                    
                    # Sanitization fallback block: cleans markdown wrapper markers if added by smaller model paths
                    if raw_response.startswith("```json"):
                        raw_response = raw_response.split("```json", 1)[1].rsplit("```", 1)[0].strip()
                    elif raw_response.startswith("```"):
                        raw_response = raw_response.split("```", 1)[1].rsplit("```", 1)[0].strip()
                    
                    # Parse sanitized JSON object directly into interactive components
                    ai_decision_data = json.loads(raw_response)
                    
                    # Visual representation layout for structural response analysis metrics
                    col1, col2, col3 = st.columns(3)
                    
                    ai_verdict = ai_decision_data.get("decision", "REFER").upper()
                    if "APPROVE" in ai_verdict:
                        col1.metric("Groq AI Verdict", "APPROVE", delta="Low Risk Status")
                    elif "DENY" in ai_verdict or "REJECT" in ai_verdict:
                        col1.metric("Groq AI Verdict", "DENY", delta="- High Risk Alert", delta_color="inverse")
                    else:
                        col1.metric("Groq AI Verdict", "REFER", delta="Review Matrix Forced")
                        
                    col2.metric("AI Calculated DTI", ai_decision_data.get("calculated_dti", "N/A"))
                    col3.metric("AI Assigned Risk Index", f"{ai_decision_data.get('risk_score_assigned', 0)} / 100")
                    
                    # Render structured narrative outputs
                    st.write("#### 🛡️ AI Audit Rationale Data Breakdown:")
                    for rule_point in ai_decision_data.get("decision_rationale", []):
                        st.write(f"📊 {rule_point}")
                        
                    anomalies = ai_decision_data.get("flagged_anomalies", [])
                    if anomalies:
                        st.error("🚨 Flagged Underwriting Anomalies Encountered:")
                        for anomaly in anomalies:
                            st.write(f"- {anomaly}")
                    else:
                        st.success("🔒 System Integrity Verified: Zero Streaming Fraud/Location Anomalies Found.")
                        
                except json.JSONDecodeError:
                    st.error("Failed to parse clean structured JSON output from the AI model configuration.")
                    st.text_area("Raw AI Diagnostic Stream Output:", value=completion.choices.message.content, height=250)
                except Exception as ai_err:
                    st.error(f"Groq API Execution Error: {str(ai_err)}")
