import pdfplumber
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extract_with_pdfplumber(file_path: str, page_index: int = 0) -> pd.DataFrame:
    """
    Deterministic fallback parser using pdfplumber's 'vertical_strategy="text"'.
    Used when probabilistic models fail to resolve merged columns.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            if page_index >= len(pdf.pages):
                return pd.DataFrame()
                
            page = pdf.pages[page_index]
            
            # CRITICAL CONFIG FOR FINANCIAL TABLES
            # tight x_tolerance forces separation of "Date" and "Description"
            settings = {
                "vertical_strategy": "text", 
                "horizontal_strategy": "text",
                "x_tolerance": 1,  # Lower tolerance = more columns
                "min_words_vertical": 2,
                "keep_blank_chars": True
            }
            
            tables = page.extract_tables(settings)
            
            if not tables:
                return pd.DataFrame()
                
            # Heuristic: The largest table is likely the statement
            main_table = max(tables, key=len)
            
            # Create DataFrame
            if len(main_table) < 2:
                 return pd.DataFrame()

            df = pd.DataFrame(main_table[1:], columns=main_table[0])
            return df

    except Exception as e:
        logger.error(f"Fallback Parsing Failed: {e}")
        return pd.DataFrame()
