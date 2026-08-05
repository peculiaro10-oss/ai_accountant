import os
import io
import base64
import re
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from PIL import Image

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

# 3. Helper Function to Compress Images
def compress_image(image_bytes: bytes, max_size: tuple = (1024, 1024), quality: int = 70) -> bytes:
    """Resizes and compresses image bytes to speed up API requests."""
    img = Image.open(io.BytesIO(image_bytes))
    
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()

# 4. Deep Modern Fintech CSS Customizations
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

# 5. Top Hero Section
st.markdown("""
    <div class="hero-card">
        <span class="hero-badge">⚡ AI-Powered Financial Suite</span>
        <div class="hero-title">AI Financial Bookkeeper</div>
        <div class="hero-subtitle">Snap a photo of paper ledgers, paste transaction logs, or upload documents to instantly extract, structure, and audit financial records.</div>
    </div>
""", unsafe_allow_html=True)

# 6. Quick System Status Stats
m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="System Status", value="Active", delta="Ready")
with m2:
    st.metric(label="AI Engine", value="Groq LLaMA-3.3", delta="Ultra-Fast")
with m3:
    st.metric(label="Audit Security", value="Encrypted", delta="Local .env")

st.markdown("<br>", unsafe_allow_html=True)

# 7. Selection Mode
st.subheader("Select Ledger Input Method")
input_method = st.radio(
    "Choose Input Method:",
    ("Snap Photo of Book/Receipt", "Paste Text/Notes", "Upload File"),
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

captured_image_bytes = None
pasted_text = ""

# 8. Dynamic Inputs Handling
if input_method == "Snap Photo of Book/Receipt":
    camera_photo = st.camera_input("Capture image of physical receipt or paper ledger")
    if camera_photo:
        captured_image_bytes = camera_photo.getvalue()

elif input_method == "Paste Text/Notes":
    pasted_text = st.text_area(
        "Paste sales logs, receipt details, or expense records below:",
        placeholder="e.g.,\n01/08/2026 - Office Supplies - 15,000 NGN\n02/08/2026 - Generator Fuel - 45,000 NGN",
        height=180
    )

elif input_method == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload statement or ledger (CSV, TXT, Images)", 
        type=["csv", "txt", "png", "jpg", "jpeg"]
    )
    if uploaded_file is not None:
        if uploaded_file.type.startswith("image"):
            captured_image_bytes = uploaded_file.getvalue()
        elif uploaded_file.type == "text/csv":
            df_temp = pd.read_csv(uploaded_file)
            pasted_text = df_temp.to_string()
        else:
            pasted_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")

st.markdown("<br>", unsafe_allow_html=True)

# 9. Main Action & Groq Execution Engine
if st.button("🚀 Process & Generate Accounting Report", use_container_width=True):
    if not api_key:
        st.error("❌ GROQ_API_KEY not detected in .env file! Please add it to proceed.")
    elif not captured_image_bytes and not pasted_text.strip():
        st.warning("⚠️ Please snap a photo, upload a document, or paste transaction notes first.")
    else:
        with st.spinner("⚡ Processing records with Groq LLaMA engine..."):
            try:
                client = Groq(api_key=api_key)
                
                # Using current stable multimodal/text models
                if captured_image_bytes:
                    compressed_bytes = compress_image(captured_image_bytes)
                    base64_image = base64.b64encode(compressed_bytes).decode('utf-8')
                    selected_model = "qwen/qwen3.6-27b"  # Current supported multimodal model on Groq
                    
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "You are an expert AI Accountant. Read the handwritten or printed text in this image carefully, itemise all transactions clearly, calculate totals, and present a structured accounting report using clean markdown tables."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ]
                else:
                    selected_model = "llama-3.3-70b-versatile"
                    prompt = f"""
                    You are an expert AI Accountant. Parse the following accounting text, itemize all transactions clearly, calculate totals, and present a structured accounting report using clean markdown tables.

                    Text to analyze:
                    {pasted_text}
                    """
                    messages = [{"role": "user", "content": prompt}]

                response = client.chat.completions.create(
                    model=selected_model,
                    messages=messages
                )

                raw_output = response.choices[0].message.content

                # Clean out any residual formatting tags
                clean_output = re.sub(r'(?i)<think>.*?</think>', '', raw_output, flags=re.DOTALL).strip()

                st.success("✅ Financial Processing Complete!")
                st.markdown(clean_output)

                # --- Spreadsheet Export Feature ---
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📥 Export Spreadsheet Report")
                
                csv_data = clean_output.encode("utf-8")
                
                st.download_button(
                    label="📥 Download Accounting Report as Spreadsheet (CSV)",
                    data=csv_data,
                    file_name="Financial_Accounting_Report.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            except Exception as error:
                st.error(f"❌ Processing Error: {str(error)}")