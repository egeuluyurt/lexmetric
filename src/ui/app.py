import streamlit as st
import pandas as pd
import io
import logging
from src.ingestion.excel_processor import process_excel_forensic
from src.ingestion.docling_processor import DoclingProcessor
from src.audit_engine.audit_logic import apply_hybrid_logic
from src.ui.cockpit import render_cockpit
from src.ui.styles import inject_production_css
from src.ui.dashboard import render_dashboard, save_case

# Configure logging
import warnings
import logging
# Suppress noisy Google/Pandas warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="LexMetric - Medicaid Audit Defense", layout="wide", page_icon="⚖️")

# ✨ INJECT PREMIUM DESIGN SYSTEM (Bespoke Luxury Legal Tech v2.0)
inject_production_css()  # Hot reload trigger

import sys
import importlib
# FORCE RELOAD to fix Stale Cache issue
if 'src.audit_engine.audit_logic' in sys.modules:
    importlib.reload(sys.modules['src.audit_engine.audit_logic'])

from src.audit_engine.audit_logic import LedgerNormalizer
from src.intelligence.classifier import TransactionClassifier

# --- CRITICAL CSS: HIDE THE NATIVE CSV BUTTON ---
st.markdown("""
<style>
/* Hide the Streamlit default download button on dataframes */
[data-testid="stElementToolbar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)


# Premium Sidebar Styling
st.sidebar.markdown("""
<style>
    /* Sidebar Premium Background */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FDFCFB 0%, #F8F7F5 100%) !important;
        border-right: 2px solid rgba(197, 160, 89, 0.2) !important;
    }
    
    /* Sidebar Title Styling */
    [data-testid="stSidebar"] h1 {
        font-family: 'Playfair Display', serif !important;
        color: #1a365d !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        padding-bottom: 16px !important;
        border-bottom: 1px solid rgba(197, 160, 89, 0.3) !important;
    }
    
    /* Input Labels */
    [data-testid="stSidebar"] label {
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Text Inputs - Gold Focus */
    [data-testid="stSidebar"] input {
        border: 1px solid rgba(26, 54, 93, 0.15) !important;
        border-radius: 6px !important;
        padding: 10px 12px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] input:focus {
        border-color: #C5A059 !important;
        box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.1) !important;
    }
    
    /* Selectbox - Premium */
    [data-testid="stSidebar"] select {
        border: 1px solid rgba(26, 54, 93, 0.15) !important;
        border-radius: 6px !important;
        padding: 10px !important;
        background: white !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* File Uploader Card */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: white !important;
        border: 2px dashed rgba(197, 160, 89, 0.4) !important;
        border-radius: 8px !important;
        padding: 20px !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
        border-color: #C5A059 !important;
        background: rgba(197, 160, 89, 0.02) !important;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🗂️ Case Entry") 
client_name = st.sidebar.text_input("👤 Client Name (Required)", placeholder="Enter Name...", key="client_input").strip()

if not client_name: 
    st.warning("Please enter a Client Name to unlock.") 
    st.stop()

st.session_state['client_name'] = client_name 

# --- JURISDICTION SETTINGS ---
MEDICAID_RULES = {
    "New York": {"penalty_divisor": 15150, "gift_cap": 2000, "lookback_months": 60},
    "California": {"penalty_divisor": 11576, "gift_cap": 500, "lookback_months": 30},
    "Florida": {"penalty_divisor": 10809, "gift_cap": 1200, "lookback_months": 60},
    "Texas": {"penalty_divisor": 242.60, "gift_cap": 200, "lookback_months": 60}, # Day rate
    "Pennsylvania": {"penalty_divisor": 482.50, "gift_cap": 500, "lookback_months": 60},
    "Ohio": {"penalty_divisor": 7453, "gift_cap": 0, "lookback_months": 60},
    "New Jersey": {"penalty_divisor": 14785, "gift_cap": 500, "lookback_months": 60},
}

selected_state = st.sidebar.selectbox("🏛️ Jurisdiction (State Rules)", options=list(MEDICAID_RULES.keys()), key="jurisdiction_select")
current_rules = MEDICAID_RULES[selected_state]

# Premium Info Card
st.sidebar.markdown(f"""
<div style="
    background: linear-gradient(135deg, rgba(26, 54, 93, 0.05), rgba(197, 160, 89, 0.05));
    border-left: 3px solid #C5A059;
    border-radius: 6px;
    padding: 16px;
    margin: 16px 0;
">
    <div style="font-family: 'Playfair Display', serif; font-size: 16px; font-weight: 700; color: #1a365d; margin-bottom: 12px;">
        {selected_state} Rules
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #64748B; line-height: 1.8;">
        <div><strong>Divisor:</strong> ${current_rules['penalty_divisor']:,}</div>
        <div><strong>Gift Cap:</strong> ${current_rules['gift_cap']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---") 
uploaded_files = st.sidebar.file_uploader("Upload Evidence (Bank Statements)", type=['pdf', 'xlsx', 'csv'], accept_multiple_files=True, key="file_upload")

if st.sidebar.button("⚠️ Reset & Clear Cache", key="reset_btn"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()



    # Dashboard: Show case history

# Main content area - conditionally render Dashboard or File Upload
view_mode = st.radio('View', ['Dashboard', 'New Case'], horizontal=True, label_visibility='hidden')

if view_mode == 'Dashboard':
    render_dashboard()
elif view_mode == 'New Case':
    # File upload workflow - everything below this is indented inside this block
    # NOTE: The code after line ~330 (helper functions, if uploaded_files, etc.) 
    # needs to be indented by 4 spaces to be inside this elif block



# Cache Docling to avoid reloading heavy models
@st.cache_resource
def get_docling_v3(): # Cache-Buster V3
    return DoclingProcessor()

# --- HELPER: Nuclear Deduplication (Architectural Standard) ---
def nuclear_deduplication(df: pd.DataFrame) -> pd.DataFrame:
    """
    Destroys and rebuilds the DataFrame Index to guarantee uniqueness.
    Resolves 'ValueError: The truth value of a Series is ambiguous'.
    """
    if df.columns.is_unique:
        return df

    cols = df.columns.tolist()
    counts = {}
    new_cols = []
    
    # Simple, robust counter loop
    for col in cols:
        col_str = str(col).strip()
        cur_count = counts.get(col_str, 0)
        
        if cur_count == 0:
            new_cols.append(col_str)
        else:
            new_cols.append(f"{col_str}.{cur_count}")
        
        counts[col_str] = cur_count + 1
        
    df.columns = new_cols
    logger.info(f"Nuclear Deduplication Applied: {df.columns.tolist()}")
    logger.info(f"Nuclear Deduplication Applied: {df.columns.tolist()}")
    return df

# --- HELPER: Nuclear Accessor ---
def get_series_safe(dframe, col_name):
    """Guarantees a Series return even if duplicate columns exist."""
    if col_name not in dframe.columns:
        return pd.Series(dtype='object')
        
    data = dframe[col_name]
    if isinstance(data, pd.DataFrame):
        logger.warning(f"Ambiguity Found: '{col_name}' has {data.shape[1]} duplicates. Using first.")
        return data.iloc[:, 0] # Take first instance
    return data

# --- HELPER: Safe Rename (Prevents Collision Crash) ---
def safe_rename(dframe, old, new):
    if old == new: return # No op
    # If target exists, drop it to prevent duplicates
    if new in dframe.columns:
        logger.info(f"SafeRename: Dropping existing '{new}' to make way for '{old}'")
        # Handle case where target itself is duplicated
        dframe.drop(columns=[new], inplace=True)
    dframe.rename(columns={old: new}, inplace=True)

# --- HELPER: Flexible Date Parser (Forensic) ---
def parse_flexible_date(date_series):
    """
    Handles 'MM/DD', 'YYYY.MM.DD', 'OCT 25' etc.
    """
    # 1. Try standard coercion
    parsed = pd.to_datetime(date_series, errors='coerce')
    
    # 2. If failure rate is high, try appending year (assuming MM/DD)
    if parsed.isna().mean() > 0.4:
        # HARDCODED FIX: Do not use system year (2026). Use 2025 or 2024.
        # Ideally we'd scan the PDF for a year, but for now 2024 is safer context.
        safe_year = 2024 
        
        mask = date_series.astype(str).str.len() < 6
        retry_series = date_series.copy()
        retry_series[mask] = retry_series[mask].astype(str) + f"/{safe_year}"
        parsed_retry = pd.to_datetime(retry_series, errors='coerce')
        
        if parsed_retry.isna().mean() < parsed.isna().mean():
            return parsed_retry

    return parsed



# --- ARCHITECTURAL CORE: Immutable Ingestion Cache ---
@st.cache_data(show_spinner=False)
def ingest_pdf_data_safe(file_bytes: bytes, file_name: str):
    """
    Safe Ingestion Layer.
    Uses @st.cache_data to serialize results (Pickle), guaranteeing 
    that no mutable reference is shared across sessions.
    """
    import io
    # Re-hydrate the bytes into a stream
    stream = io.BytesIO(file_bytes)
    
    # Get Processor (Resource Cache)
    processor = get_docling_v3()
    
    try:
        # 1. Raw Extraction
        _, tables = processor.process_pdf(stream, file_name)
        
        # 2. Immediate Sanitization (The Firewall)
        clean_tables = []
        for df in tables:
            # Force String Headers
            df.columns = df.columns.astype(str).str.strip()
            # Nuclear Option
            df = nuclear_deduplication(df)
            # Drop Empty
            df = df.dropna(axis=1, how='all').dropna(axis=0, how='all')
            if not df.empty:
                clean_tables.append(df)
                
        return clean_tables
        
    except Exception as e:
        logger.error(f"Ingestion Error: {e}")
        return []

def enrich_excel_for_ai(df):
    """
    Excel Enrichment Engine.
    Combines all available columns into a rich Description for AI analysis.
    """
    if df.empty:
        return df
    
    # If Description already exists, enhance it with extra columns
    extra_cols = []
    for col in df.columns:
        col_lower = col.lower()
        # Collect useful metadata columns
        if col_lower not in ['date', 'amount', 'description'] and col not in ['Date', 'amount', 'Description']:
            extra_cols.append(col)
    
    if extra_cols and 'Description' in df.columns:
        # Create enriched description: "Original Desc | Check: 1234 | Payee: Walmart"
        def build_context(row):
            original = str(row.get('Description', 'Unknown'))
            extras = []
            for col in extra_cols:
                val = row.get(col)
                if pd.notna(val) and str(val).strip() and str(val).lower() != 'nan':
                    extras.append(f"{col}: {val}")
            
            if extras:
                return f"{original} | {' | '.join(extras)}"
            return original
        
        df['Description'] = df.apply(build_context, axis=1)
    
        return df

        if uploaded_files: 
            st.session_state['active_filenames'] = [f.name for f in uploaded_files] 
    
            all_data = []
    
            # (Removed old doc_processor initialization here, moved to inside safe function)

            for f in uploaded_files:
                try:
                    if f.name.lower().endswith('.pdf'):
                        # --- PDF ROUTE (Robust Native Export) ---
                        with st.spinner(f"⚡ AI Analyzing PDF Evidence: {f.name}..."):
                    
                            # Read bytes for cacheable key
                            f_bytes = f.getvalue()
                    
                            # CALL THE SAFE CACHE
                            tables = ingest_pdf_data_safe(f_bytes, f.name)
                    
                            if not tables:
                                 st.warning(f"No structured tables valid for analysis found in {f.name}.")
                                 # Fallback logic logic moved inside loop below if needed
                                 pass 


                            # --- 5. FORENSIC PIPELINE (Refactored) ---
                            # Logic migrated to src/audit_engine/audit_logic.py
                    
                            df_clean = LedgerNormalizer.process_candidates(tables)
                    
                            if not df_clean.empty:
                                all_data.append(df_clean)
                            else:
                                st.warning(f"Analysis produced no valid ledger rows for {f.name}")

                    else:
                         # --- EXCEL/CSV ROUTE (Enhanced with AI) ---
                         with st.spinner(f"📊 AI Analyzing Excel: {f.name}..."):
                             df = process_excel_forensic(f)
                     
                             if not df.empty:
                                 # CRITICAL: Send Excel to AI BEFORE merging
                                 # Create enriched descriptions from ALL Excel columns
                                 df = enrich_excel_for_ai(df)
                         
                                 # Initialize AI for Excel-specific context
                                 classifier_excel = TransactionClassifier()
                                 df = classifier_excel.process_ledger_batches(df)
                         
                             all_data.append(df)
                  
                except Exception as e:
                     import traceback
                     error_details = traceback.format_exc()
                     st.error(f"Error processing {f.name}: {e}\n\nDetails:\n{error_details}")
                     logger.error(f"Full traceback for {f.name}: {error_details}")
             
            if all_data:
                combined = pd.concat(all_data, ignore_index=True)
        
                # --- GLOBAL DEDUPLICATION (Crucial for Multi-Page/Multi-File) ---
                initial_len = len(combined)
                if 'Date' in combined.columns and 'amount' in combined.columns:
                     # 1. Exact Dedupe (Safe)
                     combined.drop_duplicates(subset=['Date', 'amount', 'Description'], keep='first', inplace=True)
             
                     # 2. Check Number Dedupe (Strict)
                     # If "Check 1234" appears twice, it is a duplicate, even if date varies by a day.
                     # We filter for checks first.
                     mask_check = combined['Description'].astype(str).str.contains(r'Check\s+#?\d+', case=False, na=False)
                     if mask_check.any():
                         # Create a temporary key based on Amount + Description(CheckNum)
                         combined.loc[mask_check, 'dedupe_key'] = (
                             combined.loc[mask_check, 'amount'].astype(str) + "_" + 
                             combined.loc[mask_check, 'Description'].astype(str).str.extract(r'(Check\s*#?\d+)')[0]
                         )
                 
                         # DETECTIVE MODE SORTING
                         # Sort by Description Length (Descending) so "Check 123 - WalMart" stays, "Check 123" is dropped.
                         combined['desc_len_temp'] = combined['Description'].astype(str).str.len()
                         combined.sort_values(by=['desc_len_temp'], ascending=False, inplace=True)
                 
                         # Separate Checks and Others to prevent dropping non-checks (NaN keys)
                         checks_df = combined[combined['dedupe_key'].notna()]
                         others_df = combined[combined['dedupe_key'].isna()]
                 
                         # Dedupe ONLY the checks
                         checks_df = checks_df.drop_duplicates(subset=['dedupe_key'], keep='first')
                 
                         # Merge back
                         combined = pd.concat([checks_df, others_df], ignore_index=True)
                         combined.drop(columns=['dedupe_key', 'desc_len_temp'], inplace=True, errors='ignore')

                # Sort Chronologically
                if 'Date' in combined.columns:
                    combined.sort_values(by='Date', inplace=True)

                # Logic 
        
                # Map Full Name to Code
                STATE_MAP = {
                    "New York": "NY", "Pennsylvania": "PA", "Florida": "FL",
                    "California": "CA", "Texas": "TX", "Ohio": "OH", "New Jersey": "NJ"
                }
                state_code = STATE_MAP.get(selected_state, 'PA')
        
                # Initialize Gemini
                # Initialize Gemini
                classifier = TransactionClassifier()
                st.session_state['audit_context'] = {'state_rules': state_code}
        
                # Check if we need AI analysis (PDFs need it, Excel already done)
                # We can detect this by checking if Risk_Level column exists
                needs_ai = 'Risk_Level' not in combined.columns or combined['Risk_Level'].isna().sum() > len(combined) * 0.5
        
                if needs_ai:
                    # --- CACHED AI EXECUTION TO PREVENT LOOP ---
                    @st.cache_data(show_spinner=False, ttl=3600)
                    def run_cached_ai(df_input, rules_code):
                         """
                         Wraps the expensive AI call. 
                         Streamlit will HASH df_input and rules_code. 
                         If they haven't changed, it returns the stored result instantly.
                         """
                         # Re-instantiate inside to avoid pickling issues if needed, 
                         # but classifier is stateless mostly.
                         clf = TransactionClassifier()
                         return clf.process_ledger_batches(df_input)

                    with st.spinner("🤖 Forensic AI is analyzing risk patterns with State Logic..."):
                         # We pass state_code JUST to force cache invalidation if user changes state
                         analyzed = run_cached_ai(combined, state_code)
                else:
                    # Excel was already analyzed, just use the data
                    analyzed = combined
             
                render_cockpit(analyzed) 
        else: 
            # Premium Welcome Screen (Redesigned - Clean & Elegant)
            st.markdown("""
            <div style="
                max-width: 800px;
                margin: 80px auto;
                text-align: center;
                padding: 0 24px;
            ">
                <!-- Hero Section -->
                <div style="margin-bottom: 48px;">
                    <h1 style="
                        font-family: 'Playfair Display', serif;
                        font-size: 56px;
                        font-weight: 900;
                        color: #1a365d;
                        margin-bottom: 16px;
                        line-height: 1.1;
                        letter-spacing: -1px;
                    ">⚖️ LexMetric</h1>
            
                    <p style="
                        font-family: 'Inter', sans-serif;
                        font-size: 20px;
                        color: #64748B;
                        margin-bottom: 12px;
                        font-weight: 400;
                    ">Forensic AI-Powered Medicaid Audit Defense</p>
            
                    <p style="
                        font-family: 'Inter', sans-serif;
                        font-size: 16px;
                        color: #C5A059;
                        font-weight: 600;
                        letter-spacing: 0.5px;
                    ">Transform financial records into actionable legal defense</p>
                </div>
        
                <!-- Compact Feature Badges (2x2 Grid) -->
                <div style="
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                    margin: 48px 0;
                    max-width: 500px;
                    margin-left: auto;
                    margin-right: auto;
                ">
                    <div style="
                        background: linear-gradient(135deg, rgba(26, 54, 93, 0.04), rgba(26, 54, 93, 0.08));
                        padding: 20px;
                        border-radius: 8px;
                        border-left: 3px solid #1a365d;
                        text-align: left;
                    ">
                        <div style="font-size: 24px; margin-bottom: 8px;">📄</div>
                        <div style="
                            font-family: 'Inter', sans-serif;
                            font-size: 13px;
                            font-weight: 600;
                            color: #1a365d;
                            margin-bottom: 4px;
                        ">PDF Analysis</div>
                        <div style="font-size: 11px; color: #64748B;">Docling OCR</div>
                    </div>
            
                    <div style="
                        background: linear-gradient(135deg, rgba(197, 160, 89, 0.04), rgba(197, 160, 89, 0.08));
                        padding: 20px;
                        border-radius: 8px;
                        border-left: 3px solid #C5A059;
                        text-align: left;
                    ">
                        <div style="font-size: 24px; margin-bottom: 8px;">📊</div>
                        <div style="
                            font-family: 'Inter', sans-serif;
                            font-size: 13px;
                            font-weight: 600;
                            color: #1a365d;
                            margin-bottom: 4px;
                        ">Excel/CSV</div>
                        <div style="font-size: 11px; color: #64748B;">Smart mapping</div>
                    </div>
            
                    <div style="
                        background: linear-gradient(135deg, rgba(26, 54, 93, 0.04), rgba(26, 54, 93, 0.08));
                        padding: 20px;
                        border-radius: 8px;
                        border-left: 3px solid #1a365d;
                        text-align: left;
                    ">
                        <div style="font-size: 24px; margin-bottom: 8px;">🤖</div>
                        <div style="
                            font-family: 'Inter', sans-serif;
                            font-size: 13px;
                            font-weight: 600;
                            color: #1a365d;
                            margin-bottom: 4px;
                        ">AI Detection</div>
                        <div style="font-size: 11px; color: #64748B;">Gemini forensics</div>
                    </div>
            
                    <div style="
                        background: linear-gradient(135deg, rgba(197, 160, 89, 0.04), rgba(197, 160, 89, 0.08));
                        padding: 20px;
                        border-radius: 8px;
                        border-left: 3px solid #C5A059;
                        text-align: left;
                    ">
                        <div style="font-size: 24px; margin-bottom: 8px;">📝</div>
                        <div style="
                            font-family: 'Inter', sans-serif;
                            font-size: 13px;
                            font-weight: 600;
                            color: #1a365d;
                            margin-bottom: 4px;
                        ">Defense Reports</div>
                        <div style="font-size: 11px; color: #64748B;">Trial-ready DOCX</div>
                    </div>
                </div>
        
                <!-- Call to Action -->
                <div style="
                    background: linear-gradient(135deg, rgba(26, 54, 93, 0.03), rgba(197, 160, 89, 0.05));
                    border: 2px solid rgba(197, 160, 89, 0.2);
                    border-radius: 12px;
                    padding: 32px;
                    margin-top: 48px;
                ">
                    <div style="
                        font-family: 'Inter', sans-serif;
                        font-size: 15px;
                        color: #1e293b;
                        margin-bottom: 8px;
                        font-weight: 600;
                    ">👈 Ready to Begin?</div>
                    <div style="
                        font-size: 13px;
                        color: #64748B;
                    ">Upload files via the sidebar to start your analysis</div>
                </div>
            </div>
        """, unsafe_allow_html=True)


