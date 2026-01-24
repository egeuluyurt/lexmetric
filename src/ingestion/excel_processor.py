import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_excel_forensic(file_obj): 
    # 1. HUNTER-SEEKER LOGIC FOR HEADERS (Keyword Based - Reverting to Step 433 methodology)
    # This logic scans rows for "date" and "description" keywords to find the true header.
    try: 
        # Try Excel engine first 
        preview = pd.read_excel(file_obj, header=None, nrows=30) 
    except: 
        # Fallback to CSV engine 
        file_obj.seek(0) 
        preview = pd.read_csv(file_obj, header=None, nrows=30)

    # Scan for a row that looks like a header (Must contain 'Date' AND 'Description' or similar)
    header_idx = -1
    for i, row in preview.iterrows():
        row_str = row.astype(str).str.lower().tolist()
        joined_row = " ".join(row_str)
        # Keywords that MUST exist in the header row
        if "date" in joined_row and ("description" in joined_row or "details" in joined_row or "memo" in joined_row or "payee" in joined_row or "explanation" in joined_row):
            header_idx = i
            break
            
    if header_idx == -1: 
        # Fallback: Assume row 0 if detection fails (but warn internally) 
        logger.warning("Header detection failed. Defaulting to row 0.")
        header_idx = 0

    # 2. RELOAD WITH PROPER HEADER
    file_obj.seek(0)
    try:
        df = pd.read_excel(file_obj, header=header_idx)
    except:
        file_obj.seek(0)
        df = pd.read_csv(file_obj, header=header_idx)
        
    # 3. NORMALIZE COLUMNS (Strip spaces, lowercase)
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    # Map diverse bank columns to our standard
    col_map = { 
        'posting date': 'Date', 
        'effective date': 'Date', 
        'date': 'Date', 
        'description': 'Description', 
        'details': 'Description', 
        'transaction description': 'Description', 
        'memo': 'Description', 
        'explanation': 'Description',
        'amount': 'amount', 
        'debit': 'amount', 
        'payment amount': 'amount', 
        'amt': 'amount',
        'withdrawal': 'amount' 
    }

    # Smart Rename
    new_cols = {} 
    for c in df.columns: 
        for k, v in col_map.items(): 
            if k == c or k in c: # Exact or partial match 
                new_cols[c] = v 
                break 
    
    df.rename(columns=new_cols, inplace=True)

    # 4. AGGRESSIVE DATA CLEANING
    # A. Drop Garbage Rows (Where Date is NaN)
    if 'Date' in df.columns: 
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce') 
        df = df.dropna(subset=['Date']) # Drop rows where Date parsing failed

    # B. Force Amount to Float (Handle '$', ',', '()')
    if 'amount' in df.columns:
        def clean_money(x):
            s = str(x).replace('$', '').replace(',', '').strip()
            if '(' in s and ')' in s: 
                s = '-' + s.replace('(', '').replace(')', '')
            try: 
                return float(s)
            except: 
                return 0.0
            
        df['amount'] = df['amount'].apply(clean_money)
    else:
         # Create dummy amount if missing so system doesn't crash
         df['amount'] = 0.0
        
    # C. Fill Text NaNs
    if 'Description' in df.columns:
        df['Description'] = df['Description'].fillna("Unknown")
    else:
        # Critical Fail-safe: If no description, create one
        df['Description'] = "Transaction Details"
        
    return df
