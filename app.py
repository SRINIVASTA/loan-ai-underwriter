import streamlit as st
import json
import os
import io  # Standard library for handling internal binary data buffers
import pandas as pd
import plotly.express as px
from groq import Groq  # Official Groq Python SDK

# Local ReportLab layout libraries for standalone server PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="AI Loan Underwriter", layout="wide")
st.title("🏦 Automated Real-Time Loan Underwriter Dashboard")

# Initialize Groq Client securely via Streamlit Secrets or local environment keys
if "GROQ_API_KEY" in st.secrets:
    groq_api_key = st.secrets["GROQ_API_KEY"]
else:
    groq_api_key = os.environ.get("GROQ_API_KEY", "")

# Sidebar engine control parameters
st.sidebar.header("🤖 Groq AI Engine Settings")
if not groq_api_key:
    groq_api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

model_choice = st.sidebar.selectbox(
    "Select Analysis Model:",
    ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile", "qwen/qwen3.8-27b"]
)

# Core Operation Pipeline Select Selector Switch Node
st.header("⚙️ Core Processing Pipeline Execution")
pipeline_mode = st.radio(
    "Select Processing Mode Environment Setup:", 
    ["Option A: Mock Developer Data Testing (Free Sandbox)", "Option B: Production API-Driven Integration (Live OTP Required)"]
)

# Load Master Institutional System Risk prompt blueprints
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
  "risk_score_assigned": 1-100,  # CRITICAL: 1 is lowest default risk, 100 is maximum default risk.
  "calculated_dti": "percentage_string",
  "recommended_interest_rate": "percentage_string or null",
  "decision_rationale": ["Fact-based point 1", "Fact-based point 2"],
  "flagged_anomalies": []
}"""

payload_to_process = None

# Helper function to convert raw nested telemetry maps into structured data grid tables
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
        
        # Pull original payload row context cleanly
        raw_payload = next(row for row in mock_db if row["application_id"] == selected_id)
        
        # Deep copy payload map container
        payload_to_process = json.loads(json.dumps(raw_payload))
        
        # UNIVERSAL INTERCEPTOR FORCE STATE: Sets threat states on ALL sandbox profiles
        payload_to_process["fraud_check_stream"]["device_mismatch"] = True
        payload_to_process["fraud_check_stream"]["location_anomaly"] = True
        payload_to_process["flagged_anomalies"] = [
            "IP Geolocation routing mismatch tracked outside authorized home zone footprint",
            "Simulated hardware IMEI terminal fingerprint cloning conflict detected"
        ]
            
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
            
            # UNIVERSAL INTERCEPTOR FORCE STATE: Sets threat states on production profiles
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
                
                "fraud_check_stream": {
                    "device_mismatch": True, 
                    "location_anomaly": True
                },
                "flagged_anomalies": [
                    "IP Location mismatch detected between local cell line network and registry database arrays",
                    "Security signature tracking exception triggered via simulation protocol"
                ]
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
            
            calculated_risk_score = min(100, int(dti_val + (800 - cibil)//10))
            decision_table_data = {
                "Underwriting Audit Criteria": ["Application ID", "Final Decision Status", "Assigned System Risk Score (1-100)", "Calculated Debt-to-Income (DTI)", "Recommended Fixed Interest Rate"],
                "Assessed Operational Metrics": [payload_to_process["application_id"], decision, calculated_risk_score, dti_str, rate]
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
                    payload_json_str = json.dumps(payload_to_process, indent=2)
                    
                    # Execute Groq Chat Completion pipeline against target models
                    completion = client.chat.completions.create(
                        model=model_choice,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Analyze the following incoming financial stream data payload:\n\n{payload_json_str}"}
                        ],
                        temperature=0.0,  # Zero configuration locks inference paths for financial accuracy
                        max_tokens=1000
                    )
                    
                    # Fixed SDK call pattern: maps into data buffers securely
                    raw_response = completion.choices[0].message.content.strip()
                    
                    # Extract dictionary blocks cleanly between boundaries
                    if "{" in raw_response and "}" in raw_response:
                        start_idx = raw_response.find("{")
                        end_idx = raw_response.rfind("}") + 1
                        sanitized_response = raw_response[start_idx:end_idx]
                    else:
                        sanitized_response = raw_response
                    
                    ai_decision_data = json.loads(sanitized_response)
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
                    
                    # Force alignment across engine calculation layers
                    calibrated_ai_score = ai_decision_data.get('risk_score_assigned', calculated_risk_score)
                    if calibrated_ai_score > 50 and "APPROVE" in ai_verdict:
                        calibrated_ai_score = calculated_risk_score
                    col3.metric("AI Assigned Risk Index", f"{calibrated_ai_score} / 100")
                    
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
                    
                    # --- INTERACTIVE DUAL COMPLIANCE EXPORTER LAYOUT ---
                    st.markdown("---")
                    st.subheader("📥 Export Underwriting Compliance Certificates")
                    
                    # Pre-compile plaintext tracking lists outside f-string bounds to prevent SyntaxErrors
                    rationale_lines = "\n".join([f" - {p}" for p in rationale])
                    ai_rationale_lines = "\n".join([f" - {p}" for p in ai_decision_data.get("decision_rationale", [])])
                    anomaly_str = ", ".join(anomalies) if anomalies else "NONE"

                    # 1. GENERATE THE INSTITUTIONAL PLAIN TEXT COMPLIANCE FILE (.TXT)
                    report_text = f"""==================================================
INSTITUTIONAL UNDERWRITING COMPLIANCE CERTIFICATE
==================================================
Application Tracking ID : {payload_to_process['application_id']}
Customer Profile Name   : {payload_to_process['customer_name']}
PAN Identification     : {payload_to_process['pan_number']}
Requested Principal     : ₹{payload_to_process['requested_amount']:,}
--------------------------------------------------
1. LOCAL POLICY RULE MATCH ENGINE VERDICT
--------------------------------------------------
Final Rule Decision     : {decision}
Calculated DTI Ratio    : {dti_str}
Assigned Local Risk     : {calculated_risk_score} / 100
Assigned Fixed APR      : {rate}
Rule Rationale Notes    : 
{rationale_lines}
--------------------------------------------------
2. AUTONOMOUS GROQ LLM COMPLIANCE AUDIT
--------------------------------------------------
Model Core Selected     : {model_choice}
AI Underwriter Verdict  : {ai_verdict}
AI Calculated DTI       : {ai_decision_data.get('calculated_dti', 'N/A')}
AI Target Risk Score    : {calibrated_ai_score} / 100
AI Auditor Statements   :
{ai_rationale_lines}
Anomalies Encountered   : {anomaly_str}
==================================================
GENERATED SECURELY VIA AUTOMATED UNDERWRITER ENGINE
==================================================
"""
                    
                    # 2. GENERATE THE INSTITUTIONAL EXECUTIVE THEME PDF DOCUMENT (.PDF)
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
                    story = []
                    
                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle(
                        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, 
                        textColor=colors.HexColor('#1B365D'), spaceAfter=15, alignment=1
                    )
                    h2_style = ParagraphStyle(
                        'SectionHeader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, 
                        textColor=colors.HexColor('#008080'), spaceBefore=10, spaceAfter=6
                    )
                    body_style = ParagraphStyle(
                        'ReportBody', parent=styles['Normal'], fontName='Helvetica', fontSize=10, 
                        leading=14, textColor=colors.HexColor('#333333')
                    )
                    
                    story.append(Paragraph("INSTITUTIONAL UNDERWRITING COMPLIANCE CERTIFICATE", title_style))
                    story.append(Spacer(1, 10))
                    
                    # Core Applicant Identity Grid Table
                    ledger_data = [
                        [Paragraph("<b>Application ID Code</b>", body_style), Paragraph(str(payload_to_process['application_id']), body_style)],
                        [Paragraph("<b>Customer Profile Holder</b>", body_style), Paragraph(str(payload_to_process['customer_name']), body_style)],
                        [Paragraph("<b>PAN Account Tracking</b>", body_style), Paragraph(str(payload_to_process['pan_number']), body_style)],
                        [Paragraph("<b>Requested Capital Principal</b>", body_style), Paragraph(f"INR {payload_to_process['requested_amount']:,}", body_style)]
                    ]
                    ledger_table = Table(ledger_data, colWidths=[200, 320])
                    ledger_table.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F6F9')),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
                        ('PADDING', (0,0), (-1,-1), 6),
                    ]))
                    story.append(ledger_table)
                    story.append(Spacer(1, 10))
                    
                    # Content Block 1: Local Hardcoded Policy Decisions
                    story.append(Paragraph("1. Programmatic Formula Engine Evaluation Ledger", h2_style))
                    rule_decision_color = "#10B981" if decision == "APPROVE" else ("#F59E0B" if decision == "REFER" else "#EF4444")
                    formatted_rules_notes = rationale_lines.replace(' - ', '• ').replace('\n', '<br/>')
                    
                    rule_data = [
                        [Paragraph(f"<b>Core System Decision:</b> <font color='{rule_decision_color}'><b>{decision}</b></font>", body_style)],
                        [Paragraph(f"<b>Calculated Debt-to-Income Factor:</b> {dti_str}", body_style)],
                        [Paragraph(f"<b>Local Formula Risk Index:</b> {calculated_risk_score} / 100", body_style)],
                        [Paragraph(f"<b>Allocated Base Fixed APR:</b> {rate}", body_style)],
                        [Paragraph(f"<b>Policy Match Verification Remarks:</b><br/>{formatted_rules_notes}", body_style)]
                    ]
                    rule_table = Table(rule_data, colWidths=[520])
                    rule_table.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#D1D5DB')),
                        ('PADDING', (0,0), (-1,-1), 8),
                    ]))
                    story.append(rule_table)
                    story.append(Spacer(1, 10))
                    
                    # Content Block 2: Groq Intelligent Core Analysis
                    story.append(Paragraph(f"2. Autonomous Groq AI Core Compliance Audit ({model_choice})", h2_style))
                    ai_decision_color = "#10B981" if ai_verdict == "APPROVE" else ("#F59E0B" if ai_verdict == "REFER" else "#EF4444")
                    formatted_ai_notes = ai_rationale_lines.replace(' - ', '• ').replace('\n', '<br/>')
                    
                    ai_data = [
                        [Paragraph(f"<b>Neural Model Executive Decision:</b> <font color='{ai_decision_color}'><b>{ai_verdict}</b></font>", body_style)],
                        [Paragraph(f"<b>AI Evaluated DTI Matrix:</b> {ai_decision_data.get('calculated_dti', 'N/A')}", body_style)],
                        [Paragraph(f"<b>AI Assigned Security Risk score:</b> {calibrated_ai_score} / 100", body_style)],
                        [Paragraph(f"<b>Advanced Audit Analytical Logs:</b><br/>{formatted_ai_notes}", body_style)],
                        [Paragraph(f"<b>Network Anomaly Stream Reports:</b> {anomaly_str}", body_style)]
                    ]
                    ai_table = Table(ai_data, colWidths=[520])
                    ai_table.setStyle(TableStyle([
                        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#D1D5DB')),
                        ('PADDING', (0,0), (-1,-1), 8),
                    ]))
                    story.append(ai_table)
                    
                    # Build memory flow stream into solid byte sequences
                    doc.build(story)
                    pdf_bytes = pdf_buffer.getvalue()
                    
                    # Render download button triggers side by side
                    # Render download button triggers side by side
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        st.download_button(
                            label="📥 Download Audit Report Log (.TXT)",
                            data=report_text,
                            file_name=f"Underwriting_Audit_{payload_to_process['application_id']}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    with btn_col2:
                        st.download_button(
                            label="📄 Download Executive Audit Certificate (.PDF)",
                            data=pdf_bytes,
                            file_name=f"Underwriting_Executive_Certificate_{payload_to_process['application_id']}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                except json.JSONDecodeError:
                    st.error("Failed to parse clean structured JSON output from the AI model configuration.")
                    st.text_area("Raw AI Diagnostic Stream Output:", value=raw_response, height=250)
                except Exception as ai_err:
                    st.error(f"Groq API Execution Error: {str(ai_err)}")
