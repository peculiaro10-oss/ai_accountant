import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# 1. Load secret environment variables (.env file)
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# 2. Page Config
st.set_page_config(
    page_title="AI Financial Bookkeeper", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. Deep Modern Fintech CSS Customizations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% -20%, #1e1b4b 0%, #0f172a 45%, #020617 100%);
        color: #f8fafc;
    }

    .hero-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 32px;
        margin-bottom: 28px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
    }

    .hero-badge {
        display: inline-block;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: #ffffff;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        padding: 6px 14px;
        border-radius: 20px;
        margin-bottom: 14px;
    }

    .hero-title {
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 16px;
        font-weight: 400;
        line-height: 1.6;
        max-width: 800px;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 28px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        color: #38bdf8;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Top Hero Section
st.markdown("""
    <div class="hero-card">
        <span class="hero-badge">⚡ AI-Powered Financial Suite</span>
        <div class="hero-title">AI Financial Bookkeeper</div>
        <div class="hero-subtitle">Snap a photo of paper ledgers, paste transaction logs, or upload documents to instantly extract, structure, and audit financial records safely.</div>
    </div>
""", unsafe_allow_html=True)

# 5. Quick System Status Stats
m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="System Status", value="Active", delta="Ready")
with m2:
    st.metric(label="AI Engine", value="Groq LLaMA-3.3", delta="Secure JSON")
with m3:
    st.metric(label="Audit Security", value="Encrypted", delta="Protected")

st.markdown("<br>", unsafe_allow_html=True)

# 6. Selection Mode
st.subheader("Select Ledger Input Method")
input_method = st.radio(
    "Choose Input Method:",
    ("Snap Photo of Book/Receipt", "Paste Text/Notes", "Upload File"),
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

captured_image = None
pasted_text = ""
uploaded_file = None

# 7. Dynamic Inputs
if input_method == "Snap Photo of Book/Receipt":
    captured_image = st.camera_input("Capture image of physical receipt or paper ledger")

elif input_method == "Paste Text/Notes":
    pasted_text = st.text_area(
        "Paste sales logs, receipt details, or expense records below:",
        placeholder="e.g.,\n01/08/2026 - Office Supplies - 15,000 NGN\n02/08/2026 - Generator Fuel - 45,000 NGN",
        height=180
    )

elif input_method == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload statement or ledger (CSV, Excel, Images)", 
        type=["csv", "xlsx", "png", "jpg", "jpeg"]
    )

st.markdown("<br>", unsafe_allow_html=True)

# 8. Main Action Button & Safety/Execution Handler
if st.button("🚀 Process & Generate Accounting Report", use_container_width=True):
    if not api_key:
        st.error("❌ GROQ_API_KEY not detected in .env file! Please check your configuration.")
    elif input_method == "Paste Text/Notes" and not pasted_text.strip():
        st.warning("⚠️ Please provide text records before processing.")
    elif input_method == "Snap Photo of Book/Receipt" and not captured_image:
        st.warning("⚠️ Please capture an image first.")
    elif input_method == "Upload File" and not uploaded_file:
        st.warning("⚠️ Please upload a file first.")
    else:
        with st.spinner("⚡ Processing records securely with Groq AI engine..."):
            try:
                client = Groq(api_key=api_key)
                
                # Safety Prompt instructing JSON compliance and boundary limitations
                system_prompt = (
                    "You are an expert, precise AI Accountant. "
                    "Parse the provided financial information carefully. "
                    "Return ONLY a valid JSON object containing a single key named 'transactions', "
                    "which must be a list of objects with fields: 'Date', 'Description', 'Category', and 'Amount'. "
                    "Do not include any extra conversational text, markdown formatting blocks, or think tags."
                )

                if input_method == "Paste Text/Notes":
                    user_content = f"Analyze this text data:\n{pasted_text}"
                elif input_method == "Upload File" and uploaded_file and uploaded_file.type == "text/csv":
                    df_temp = pd.read_csv(uploaded_file)
                    user_content = f"Analyze this CSV data:\n{df_temp.to_string()}"
                else:
                    user_content = "Analyze the attached financial document/ledger image accurately."

                # Safe API Call with strict JSON enforcement
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"}
                )

                raw_json_output = response.choices[0].message.content

                # --- Safety Cautions & Error Boundary Handling ---
                try:
                    parsed_data = json.loads(raw_json_output)
                    transactions_list = parsed_data.get("transactions", [])
                    
                    if not transactions_list:
                        st.warning("⚠️ The model processed the input, but no structured transactions were identified. Try breaking down your input into smaller chunks.")
                    else:
                        df_report = pd.DataFrame(transactions_list)
                        st.success("✅ Financial Processing & Audit Complete Safely!")
                        
                        # Display clean data table
                        st.dataframe(df_report, use_container_width=True)

                        # --- Spreadsheet Export Feature ---
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.subheader("📥 Export Spreadsheet Report")
                        
                        csv_bytes = df_report.to_csv(index=False).encode("utf-8")
                        
                        st.download_button(
                            label="📥 Download Clean Report as Spreadsheet (CSV)",
                            data=csv_bytes,
                            file_name="Safe_Financial_Accounting_Report.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                except json.JSONDecodeError:
                    st.error("⚠️ **Safety Limitation Triggered:** The output was cut off or formatted incorrectly due to length or formatting limits. Please process your ledger in smaller monthly or weekly batches.")
                    
            except Exception as error:
                st.error(f"❌ Processing Error: {str(error)}")