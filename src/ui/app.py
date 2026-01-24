"""
LexMetric - Medicaid Audit Defense Platform
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import io
import logging
import warnings
import sys
import importlib

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === IMPORTS ===
from src.ingestion.excel_processor import process_excel_forensic
from src.ingestion.docling_processor import DoclingProcessor
from src.audit_engine.audit_logic import apply_hybrid_logic, LedgerNormalizer
from src.intelligence.classifier import TransactionClassifier
from src.ui.cockpit import render_cockpit
from src.ui.styles import inject_production_css
from src.ui.dashboard import render_dashboard, save_case

# === PAGE CONFIGURATION ===
st.set_page_config(
    page_title="LexMetric - Medicaid Audit Defense",
    layout="wide",
    page_icon="⚖️"
)

# === INJECT PREMIUM CSS ===
inject_production_css()

# === FORCE RELOAD (Cache Buster) ===
if 'src.audit_engine.audit_logic' in sys.modules:
    importlib.reload(sys.modules['src.audit_engine.audit_logic'])

# === HIDE STREAMLIT DEFAULT BUTTONS ===
st.markdown("""
<style>
[data-testid="stElementToolbar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR UI
# =============================================================================

# Premium Sidebar Styling
st.sidebar.markdown("""
<style>
    /* Sidebar Premium Background */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(253, 252, 251, 1) 0%, rgba(245, 243, 240, 1) 100%);
        border-right: 2px solid rgba(197, 160, 89, 0.2);
    }
    
    /* Sidebar Title */
    [data-testid="stSidebar"] h1 {
        font-family: 'Playfair Display', serif;
        color: #1a365d;
        font-weight: 900;
        font-size: 24px;
        margin-bottom: 8px;
    }
    
    /* Input Focus State - Gold */
    [data-testid="stSidebar"] input:focus {
        border-color: #C5A059 !important;
        box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.1) !important;
    }
    
    /* Select Box Focus */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        border-color: #C5A059 !important;
    }
    
    /* File Uploader Premium Card */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed rgba(197, 160, 89, 0.3);
        border-radius: 8px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Header
st.sidebar.markdown("# 📁 Case Entry")

# Client Name Input
client_name = st.sidebar.text_input(
    "👤 CLIENT NAME (REQUIRED)",
    value="",
    key="client_name_input"
)

# Jurisdiction Selector
st.sidebar.markdown("### 📍 JURISDICTION (STATE RULES)")
jurisdiction = st.sidebar.selectbox(
    "Select State",
    options=["New York", "Pennsylvania", "California", "Florida", "Texas", "Ohio", "New Jersey"],
    key="jurisdiction_select",
    label_visibility="collapsed"
)

# Medicaid Rules Display
MEDICAID_RULES = {
    "New York": {"divisor": "$15,150", "gift_cap": "$2000"},
    "Pennsylvania": {"divisor": "$482.50", "gift_cap": "$500"},
    "California": {"divisor": "$11,576", "gift_cap": "$2000"},
    "Florida": {"divisor": "$10,809", "gift_cap": "$2000"},
    "Texas": {"divisor": "$242.60 (daily)", "gift_cap": "$1000"},
    "Ohio": {"divisor": "$7,453", "gift_cap": "$1500"},
    "New Jersey": {"divisor": "$14,785", "gift_cap": "$2000"}
}

rules = MEDICAID_RULES.get(jurisdiction, MEDICAID_RULES["Pennsylvania"])

st.sidebar.markdown(f"""
<div style="
    background: white;
    border-left: 3px solid #C5A059;
    padding: 16px;
    margin: 16px 0;
    border-radius: 4px;
">
<div style="font-family: 'Playfair Display', serif; font-weight: 700; color: #1a365d; margin-bottom: 8px;">
        {jurisdiction} Rules
</div>
<div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; line-height: 1.6;">
        <strong>Divisor:</strong> {rules['divisor']}<br>
        <strong>Gift Cap:</strong> {rules['gift_cap']}
</div>
</div>
""", unsafe_allow_html=True)

# File Uploader
st.sidebar.markdown("---")
uploaded_files = st.sidebar.file_uploader(
    "Upload Evidence (Bank Statements)",
    type=['pdf', 'xlsx', 'csv'],
    accept_multiple_files=True,
    key="file_upload"
)

# Reset Button
if st.sidebar.button("⚠️ Reset & Clear Cache", key="reset_btn"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# =============================================================================
# VIEW NAVIGATION
# =============================================================================

view_mode = st.radio(
    'View',
    ['Dashboard', 'New Case'],
    horizontal=True,
    label_visibility='hidden'
)

if view_mode == 'Dashboard':
    render_dashboard()
    st.stop()  # Don't process file uploads in Dashboard view

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

@st.cache_resource
def get_docling_processor():
    """Cache Docling processor to avoid reloading heavy models"""
    return DoclingProcessor()

def nuclear_deduplication(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows and reset index"""
    if df.empty:
        return df
    df = df.drop_duplicates(ignore_index=True)
    df = df.reset_index(drop=True)
    return df

def build_context_description(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches 'Description' column with context from other columns
    """
    if df.empty or 'Description' not in df.columns:
        return df
    
    def build_context(row):
        original = str(row.get('Description', ''))
        extras = []
        
        # Add relevant context
        for col in ['Payee', 'Type', 'Category', 'Notes']:
            if col in row and pd.notna(row[col]):
                val = str(row[col]).strip()
                if val and val.lower() not in original.lower():
                    extras.append(f"{col}: {val}")
        
        if extras:
            return f"{original} | {' | '.join(extras)}"
        return original
    
    df['Description'] = df.apply(build_context, axis=1)
    return df

# =============================================================================
# FILE UPLOAD WORKFLOW
# =============================================================================

if not uploaded_files:
    # Premium Welcome Screen
    st.markdown("""
<div style="max-width:800px;margin:80px auto;text-align:center;padding:0 24px;">
<h1 style="font-family:'Playfair Display',serif;font-size:56px;font-weight:900;color:#1a365d;margin-bottom:16px;">⚖️ LexMetric</h1>
<p style="font-family:'Inter',sans-serif;font-size:20px;color:#64748B;margin-bottom:12px;">Forensic AI-Powered Medicaid Audit Defense</p>
<p style="font-family:'Inter',sans-serif;font-size:16px;color:#C5A059;font-weight:600;">Transform financial records into actionable legal defense</p>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:48px auto;max-width:500px;">
<div style="background:linear-gradient(135deg,rgba(26,54,93,0.04),rgba(26,54,93,0.08));padding:20px;border-radius:8px;border-left:3px solid #1a365d;text-align:left;">
<div style="font-size:24px;margin-bottom:8px;">📄</div>
<div style="font-family:'Inter',sans-serif;font-size:13px;font-weight:600;color:#1a365d;">PDF Analysis</div>
<div style="font-size:11px;color:#64748B;">Docling OCR</div>
</div>
<div style="background:linear-gradient(135deg,rgba(197,160,89,0.04),rgba(197,160,89,0.08));padding:20px;border-radius:8px;border-left:3px solid #C5A059;text-align:left;">
<div style="font-size:24px;margin-bottom:8px;">📊</div>
<div style="font-family:'Inter',sans-serif;font-size:13px;font-weight:600;color:#1a365d;">Excel/CSV</div>
<div style="font-size:11px;color:#64748B;">Smart mapping</div>
</div>
<div style="background:linear-gradient(135deg,rgba(26,54,93,0.04),rgba(26,54,93,0.08));padding:20px;border-radius:8px;border-left:3px solid #1a365d;text-align:left;">
<div style="font-size:24px;margin-bottom:8px;">🤖</div>
<div style="font-family:'Inter',sans-serif;font-size:13px;font-weight:600;color:#1a365d;">AI Detection</div>
<div style="font-size:11px;color:#64748B;">Gemini forensics</div>
</div>
<div style="background:linear-gradient(135deg,rgba(197,160,89,0.04),rgba(197,160,89,0.08));padding:20px;border-radius:8px;border-left:3px solid #C5A059;text-align:left;">
<div style="font-size:24px;margin-bottom:8px;">📝</div>
<div style="font-family:'Inter',sans-serif;font-size:13px;font-weight:600;color:#1a365d;">Defense Reports</div>
<div style="font-size:11px;color:#64748B;">Trial-ready DOCX</div>
</div>
</div>

<div style="background:linear-gradient(135deg,rgba(26,54,93,0.03),rgba(197,160,89,0.05));border:2px solid rgba(197,160,89,0.2);border-radius:12px;padding:32px;margin-top:48px;">
<div style="font-family:'Inter',sans-serif;font-size:15px;color:#1e293b;font-weight:600;margin-bottom:8px;">👈 Ready to Begin?</div>
<div style="font-size:13px;color:#64748B;">Upload files via the sidebar to start your analysis</div>
</div>
</div>
""", unsafe_allow_html=True)
    st.stop()

# =============================================================================
# FILE PROCESSING LOGIC
# =============================================================================

# Store audit context
st.session_state['client_name'] = client_name
st.session_state['active_filenames'] = [f.name for f in uploaded_files]

# Map jurisdiction to state code
state_map = {
    "New York": "NY",
    "Pennsylvania": "PA",
    "California": "CA",
    "Florida": "FL",
    "Texas": "TX",
    "Ohio": "OH",
    "New Jersey": "NJ"
}

st.session_state['audit_context'] = {
    'state_rules': state_map.get(jurisdiction, 'PA'),
    'client_name': client_name,
    'jurisdiction': jurisdiction
}

all_data = []

# Process each uploaded file
for f in uploaded_files:
    try:
        if f.name.lower().endswith('.pdf'):
            # PDF ROUTE
            with st.spinner(f"⚡ AI Analyzing PDF Evidence: {f.name}..."):
                f_bytes = f.getvalue()
                doc_processor = get_docling_processor()
                # process_pdf returns (markdown_text, tables)
                markdown_text, tables = doc_processor.process_pdf(io.BytesIO(f_bytes), f.name)
                
                if tables:
                    result_df = pd.concat(tables, ignore_index=True)
                else:
                    result_df = pd.DataFrame()
                
                if not result_df.empty:
                    all_data.append(result_df)
                    logger.info(f"PDF processed: {len(result_df)} transactions")
                else:
                    st.warning(f"⚠️ No data extracted from {f.name}")
        
        elif f.name.lower().endswith(('.xlsx', '.csv')):
            # EXCEL/CSV ROUTE
            with st.spinner(f"📊 Processing Excel/CSV: {f.name}..."):
                excel_df = process_excel_forensic(f)
                
                if not excel_df.empty:
                    all_data.append(excel_df)
                    logger.info(f"Excel/CSV processed: {len(excel_df)} transactions")
                else:
                    st.warning(f"⚠️ No data extracted from {f.name}")
    
    except Exception as e:
        st.error(f"❌ Error processing {f.name}: {str(e)}")
        logger.error(f"File processing error: {e}")

# Combine and process data
if all_data:
    combined = pd.concat(all_data, ignore_index=True)
    combined = nuclear_deduplication(combined)
    combined = build_context_description(combined)
    
    # Run AI Analysis
    with st.spinner("🤖 AI Risk Analysis in Progress..."):
        classifier = TransactionClassifier()
        analyzed = classifier.process_ledger_batches(combined, batch_size=20)
    
    # Render Cockpit
    render_cockpit(analyzed)
else:
    st.error("⚠️ No valid data found in uploaded files. Please upload PDF, Excel, or CSV bank statements.")
