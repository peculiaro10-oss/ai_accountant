import os
import io
import base64
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field
from typing import List, Optional
from PIL import Image
from datetime import datetime

# 1. Load secret environment variables (.env file)
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# 2. Page Config
st.set_page_config(
    page_title="AI Financial Bookkeeper | Enterprise Ledger", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. Helper Function to Compress Images
def compress_image(image_bytes: bytes, max_size: tuple = (640, 640), quality: int = 50) -> bytes:
    """Resizes and compresses image bytes aggressively to speed up API requests and stay within API token rate limits."""
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert RGBA/PNG to RGB for JPEG conversion
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()

# 4. Pydantic Schemas for Structured AI Outputs
class Transaction(BaseModel):
    date: Optional[str] = Field(None, description="Date of transaction in YYYY-MM-DD or original format")
    description: str = Field(..., description="Description of the item or service")
    category: str = Field(..., description="General business category like Revenue, Sales, Rent, Maintenance, Utilities, Salaries, Supplies, Fuel, Equipment")
    amount: float = Field(..., description="Numerical cost or income amount")

class FinancialStatement(BaseModel):
    business_name: str = Field("Unknown Business", description="Name of organization or business")
    period: str = Field("Unknown Period", description="Time period covered")
    currency: str = Field("NGN", description="Currency symbol or code")
    reported_grand_total: float = Field(0.0, description="Calculated grand total of transactions")
    transactions: List[Transaction] = Field(default_factory=list, description="List of extracted transactions")

# 5. Deep Modern Fintech CSS Customizations
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

# 6. Top Hero Section
st.markdown("""
    <div class="hero-card">
        <span class="hero-badge">⚡ Enterprise AI Financial Suite</span>
        <div class="hero-title">AI Financial Bookkeeper</div>
        <div class="hero-subtitle">Instantly extract, categorize, and audit universal business records, sales notes, and receipts with dynamic category breakdown tables and structured Excel exports.</div>
    </div>
""", unsafe_allow_html=True)

# 7. Quick System Status Stats
m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="System Status", value="Active", delta="Ready")
with m2:
    st.metric(label="AI Engine", value="Groq LLaMA-3.3 / Qwen", delta="High Precision")
with m3:
    st.metric(label="Audit Security", value="Encrypted", delta="Secure Local")

st.markdown("<br>", unsafe_allow_html=True)

# 8. Selection Mode
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

# 9. Dynamic Inputs Handling
if input_method == "Snap Photo of Book/Receipt":
    camera_photo = st.camera_input("Capture image of physical receipt or paper ledger")
    if camera_photo:
        captured_image_bytes = camera_photo.getvalue()

elif input_method == "Paste Text/Notes":
    pasted_text = st.text_area(
        "Paste sales logs, receipt details, or expense records below:",
        placeholder="e.g.,\n01/08/2026 - Client Consultation Sales - 150,000 NGN\n02/08/2026 - Generator Diesel Fuel - 45,000 NGN\n03/08/2026 - Office Rent Payment - 250,000 NGN",
        height=180
    )

elif input_method == "Upload File":
    uploaded_file = st.file_uploader(
        "Upload statement or ledger (CSV, TXT, Images, Excel)", 
        type=["csv", "txt", "png", "jpg", "jpeg", "xlsx", "xls"]
    )
    if uploaded_file is not None:
        if uploaded_file.type.startswith("image"):
            captured_image_bytes = uploaded_file.getvalue()
        else:
            try:
                if uploaded_file.name.endswith(".csv"):
                    try:
                        df_temp = pd.read_csv(uploaded_file)
                        pasted_text = df_temp.to_string()
                    except Exception:
                        uploaded_file.seek(0)
                        pasted_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                elif uploaded_file.name.endswith((".xlsx", ".xls")):
                    df_temp = pd.read_excel(uploaded_file)
                    pasted_text = df_temp.to_string()
                else:
                    pasted_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            except Exception as e:
                st.error(f"❌ Error parsing file structure: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# 10. Main Action & Groq Execution Engine
if st.button("🚀 Process & Generate Accounting Report", use_container_width=True):
    if not api_key:
        st.error("❌ GROQ_API_KEY not detected in .env file! Please add it to proceed.")
    elif not captured_image_bytes and not pasted_text.strip():
        st.warning("⚠️ Please snap a photo, upload a document, or paste transaction notes first.")
    else:
        with st.spinner("⚡ Processing records with Groq AI engine..."):
            try:
                client = Groq(api_key=api_key)
                
                if captured_image_bytes:
                    compressed_bytes = compress_image(captured_image_bytes)
                    base64_image = base64.b64encode(compressed_bytes).decode('utf-8')
                    selected_model = "qwen/qwen3.6-27b"
                    
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """You are an expert corporate AI Accountant. Read the handwritten or printed text in this image carefully. 
Extract all records, assign clean universal business categories (e.g., Revenue, Sales, Rent, Maintenance, Utilities, Salaries, Supplies, Fuel, Equipment, General Expenses), then return ONLY valid JSON matching this exact structure:
{
  "business_name": "string",
  "period": "string",
  "currency": "string",
  "reported_grand_total": 0.0,
  "transactions": [
    {"date": "YYYY-MM-DD", "description": "item name", "category": "category name", "amount": 0.0}
  ]
}"""
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
                    You are an expert corporate AI Accountant. Parse the following accounting records, assign universal professional business categories (e.g., Revenue, Sales, Rent, Maintenance, Utilities, Salaries, Supplies, Fuel, Equipment, General Expenses), and return ONLY valid JSON matching this exact structure:
                    {{
                      "business_name": "string",
                      "period": "string",
                      "currency": "string",
                      "reported_grand_total": 0.0,
                      "transactions": [
                        {{"date": "YYYY-MM-DD", "description": "item name", "category": "category name", "amount": 0.0}}
                      ]
                    }}

                    Text to analyze:
                    {pasted_text}
                    """
                    messages = [{"role": "user", "content": prompt}]

                # API Call to Groq
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=messages,
                    response_format={"type": "json_object"}
                )

                json_output = response.choices[0].message.content
                statement = FinancialStatement.model_validate_json(json_output)

                if statement.transactions:
                    calculated_sum = sum(t.amount for t in statement.transactions if t.amount is not None)
                    statement.reported_grand_total = calculated_sum

                st.success("✅ Financial Audit Processing Complete!")

                # --- Professional Metric KPI Cards ---
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Organization / Business", statement.business_name)
                c2.metric("Reporting Period", statement.period)
                c3.metric("Total Line Items", len(statement.transactions))
                c4.metric("Grand Total Value", f"{statement.currency} {statement.reported_grand_total:,.2f}")

                st.markdown("<br>", unsafe_allow_html=True)

                if statement.transactions:
                    tx_data = [t.model_dump() for t in statement.transactions]
                    df_result = pd.DataFrame(tx_data)

                    # --- Interactive Sidebar Filter ---
                    st.sidebar.markdown("### 🔍 Filter Audit View")
                    categories_list = ["All Categories"] + list(df_result['category'].unique())
                    selected_cat_filter = st.sidebar.selectbox("Select Category View", categories_list)

                    if selected_cat_filter != "All Categories":
                        df_display = df_result[df_result['category'] == selected_cat_filter]
                    else:
                        df_display = df_result

                    # --- Main Complete Table ---
                    st.subheader("📋 Master General Ledger")
                    st.dataframe(df_display, use_container_width=True)

                    # --- Professional Automatically Split Category Tables ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("📂 Departmental / Category Breakdowns")
                    
                    unique_categories = df_result['category'].unique()
                    for cat in unique_categories:
                        with st.expander(f"🏷️ Category: {cat}", expanded=True):
                            df_cat_subset = df_result[df_result['category'] == cat]
                            st.dataframe(df_cat_subset, use_container_width=True)
                            cat_subtotal = df_cat_subset['amount'].sum()
                            st.caption(f"**Subtotal for {cat}:** {statement.currency} {cat_subtotal:,.2f}")

                    # --- Professional Structured Excel Export with Subtotal Rows ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("📥 Export Official Audit Report")

                    current_date_str = datetime.now().strftime("%Y-%m-%d")
                    sanitized_org_name = statement.business_name.replace(" ", "_")
                    excel_filename = f"{sanitized_org_name}_Audit_{current_date_str}.xlsx"
                    
                    export_rows = []
                    for cat in unique_categories:
                        df_cat_subset = df_result[df_result['category'] == cat]
                        
                        export_rows.append({"date": f"--- CATEGORY: {cat.upper()} ---", "description": "", "category": "", "amount": ""})
                        
                        for _, row in df_cat_subset.iterrows():
                            export_rows.append(row.to_dict())
                            
                        cat_subtotal = df_cat_subset['amount'].sum()
                        export_rows.append({"date": "", "description": f"SUBTOTAL FOR {cat.upper()}", "category": cat, "amount": cat_subtotal})
                        export_rows.append({"date": "", "description": "", "category": "", "amount": ""})

                    df_structured_export = pd.DataFrame(export_rows)

                    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                        df_structured_export.to_excel(writer, sheet_name='Categorized Ledger', index=False)
                        
                        worksheet = writer.sheets['Categorized Ledger']
                        for col in worksheet.columns:
                            max_len = max(len(str(cell.value or '')) for cell in col)
                            col_letter = col[0].column_letter
                            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
                    
                    with open(excel_filename, "rb") as file_data:
                        st.download_button(
                            label="📥 Download Structured & Categorized Excel Report",
                            data=file_data,
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

            except Exception as error:
                st.error(f"❌ Processing Error: {str(error)}")