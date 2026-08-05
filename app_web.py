import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Load hidden API key from .env
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Page Configuration
st.set_page_config(
    page_title="AI Financial Bookkeeper", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (CSS for a cleaner look)
st.markdown("""
    <style>
    /* Main container background tweaks */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    /* Card headers */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .header-title {
        color: #38bdf8;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Top Header Card
st.markdown("""
    <div class="header-card">
        <div class="header-title">⚡ AI Financial Bookkeeper</div>
        <div class="header-subtitle">Snap a photo of your paper ledger, paste transaction notes, or upload a file to automatically audit your records.</div>
    </div>
""", unsafe_allow_html=True)

# Quick Stat Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Status", value="System Ready", delta="Online")
with col2:
    st.metric(label="Engine", value="Groq LLaMA 3", delta="Active")
with col3:
    st.metric(label="Audit Mode", value="Auto-Extract", delta="Instant")

st.markdown("---")

# Input Selection
input_method = st.radio(
    "Choose Input Method:",
    ("Snap Photo of Book/Receipt", "Paste Text/Notes", "Upload File"),
    horizontal=True
)

st.write("")

# Dynamic Input Sections
if input_method == "Snap Photo of Book/Receipt":
    st.camera_input("Take a photo of your paper ledger or physical receipt")

elif input_method == "Paste Text/Notes":
    st.text_area(
        "Paste sales logs, receipt details, or expense records here:",
        placeholder="e.g., 01/08/2026 - Office Supplies - 15,000 NGN\n02/08/2026 - Generator Fuel - 45,000 NGN",
        height=180
    )

elif input_method == "Upload File":
    st.file_uploader(
        "Upload financial documents", 
        type=["csv", "xlsx", "png", "jpg", "jpeg"]
    )

st.markdown("<br>", unsafe_allow_html=True)

# Custom Action Button
if st.button("🚀 Process & Generate Accounting Report", type="primary", use_container_width=True):
    st.info("Processing financial data...")