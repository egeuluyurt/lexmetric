import pytest
import pandas as pd
from io import BytesIO
from src.ingestion.pdf_processor import PDFProcessor
from src.audit_engine.audit_logic import AuditEngine

def test_pdf_processor_contract():
    """Verify PDFProcessor accepts BytesIO and returns DataFrame."""
    processor = PDFProcessor()
    dummy_pdf = BytesIO(b"%PDF-1.4 dummy content")
    
    df = processor.process_pdf(dummy_pdf)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.columns.empty

def test_audit_engine_contract():
    """Verify AuditEngine accepts DataFrame and returns processed DataFrame."""
    engine = AuditEngine()
    dummy_data = pd.DataFrame({
        "Date": ["2026-01-01"], 
        "Description": ["Test Txn"], 
        "Amount": [100.0]
    })
    
    result = engine.analyze_ledger(dummy_data)
    
    assert isinstance(result, pd.DataFrame)
    assert "Risk_Flag" in result.columns
