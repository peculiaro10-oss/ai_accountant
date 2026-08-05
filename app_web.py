import streamlit as st
import pandas as pd
from groq import Groq
from pydantic import BaseModel, Field
from typing import List, Optional
import base64

# Page Configuration
st.set_page_config(page_title="AI Accountant Assistant", page_icon="📊", layout="wide")

st.title("📊 AI Financial Bookkeeper")
st.write("Snap a photo of your paper ledger, paste notes, or upload a file to automatically extract and audit your bookkeeping records.")

# Sidebar for Setup
st.sidebar.header("Settings")
groq_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

# Pydantic Schemas
class Transaction(BaseModel):
    date: Optional[str] = Field(None, description="Date of transaction")
    description: str = Field(..., description="Description of the item or service")
    category: str = Field(..., description="Category like Revenue, Rent, Fuel, Supplies")
    amount: float = Field(..., description="Numerical cost or amount")

class FinancialStatement(BaseModel):
    business_name: str = Field("Unknown Business", description="Name of business")
    period: str = Field("Unknown Period", description="Time period")
    currency: str = Field("NGN", description="Currency symbol/code")
    reported_grand_total: float = Field(0.0, description="Grand total")
    transactions: List[Transaction] = Field(default_factory=list)

# Main Form Interface - Added Photo / Camera options
input_method = st.radio(
    "Choose Input Method:", 
    ["Snap Photo of Book/Receipt", "Paste Text/Notes", "Upload File"]
)

document_text = ""
uploaded_image_bytes = None

if input_method == "Snap Photo of Book/Receipt":
    st.info("📷 Use your phone or laptop camera to capture a clear picture of your ledger book or paper receipt.")
    camera_photo = st.camera_input("Take a photo")
    if camera_photo:
        uploaded_image_bytes = camera_photo.getvalue()

elif input_method == "Paste Text/Notes":
    document_text = st.text_area(
        "Paste sales logs, receipt details, or expense records here:", 
        height=200, 
        placeholder="e.g., 01/08/2026 - Office Supplies - 15,000 NGN\n02/08/2026 - Generator Fuel - 45,000 NGN"
    )

else:
    uploaded_file = st.file_uploader("Upload a text ledger (.txt) or image (.png, .jpg)", type=["txt", "jpg", "jpeg", "png"])
    if uploaded_file is not None:
        if uploaded_file.type.startswith("image"):
            uploaded_image_bytes = uploaded_file.getvalue()
        else:
            document_text = uploaded_file.getvalue().decode("utf-8")

# Process Button
if st.button("🚀 Process & Generate Accounting Report", type="primary"):
    if not groq_key:
        st.error("Please enter a valid Groq API Key in the sidebar to proceed.")
    elif not document_text.strip() and not uploaded_image_bytes:
        st.warning("Please provide text, snap a photo, or upload a file first.")
    else:
        with st.spinner("AI Accountant is analyzing transactions..."):
            try:
                client = Groq(api_key=groq_key)
                
                # Check if we are processing an Image or Text
                if uploaded_image_bytes:
                    # Convert image to base64 for Vision model
                    base64_image = base64.b64encode(uploaded_image_bytes).decode('utf-8')
                    model_name = "llama-3.2-11b-vision-preview" # Vision model for reading handwriting/images
                    
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """You are an expert AI Accountant. Read the handwritten or printed text in this photo carefully. 
Extract all transactions and financial records, then return ONLY valid JSON matching this exact structure:
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
                    # Standard text processing
                    model_name = "llama-3.3-70b-versatile"
                    prompt = f"""
                    You are an expert AI Accountant. Parse the following accounting text and return ONLY valid JSON matching this exact structure:
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
                    {document_text}
                    """
                    messages = [{"role": "user", "content": prompt}]

                # Call Groq API
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    response_format={"type": "json_object"}
                )

                json_output = response.choices[0].message.content
                statement = FinancialStatement.model_validate_json(json_output)

                st.success("Analysis Complete!")

                # Display High-Level Summary
                col1, col2, col3 = st.columns(3)
                col1.metric("Business Name", statement.business_name)
                col2.metric("Reporting Period", statement.period)
                col3.metric("Calculated Total", f"{statement.currency} {statement.reported_grand_total:,.2f}")

                # Display Transaction Table
                if statement.transactions:
                    st.subheader("📋 Parsed General Ledger Transactions")
                    tx_list = [t.model_dump() for t in statement.transactions]
                    df = pd.DataFrame(tx_list)
                    st.dataframe(df, use_container_width=True)

                    # Export Button for Excel
                    excel_file = "accounting_report.xlsx"
                    df.to_excel(excel_file, index=False)
                    with open(excel_file, "rb") as f:
                        st.download_button(
                            label="📥 Download Excel Spreadsheet",
                            data=f,
                            file_name=f"{statement.business_name}_Ledger.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            except Exception as e:
                st.error(f"An error occurred during processing: {str(e)}")