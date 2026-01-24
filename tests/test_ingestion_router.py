import pytest
import pandas as pd
from io import BytesIO
from src.ingestion.processor import FormatRouter

# --- Mocks ---
def create_dummy_pdf_content():
    return b"%PDF-1.5...."

def create_dummy_excel_content():
    # In a real test, we might use a small fixture, 
    # but FormatRouter.process_excel requires a real excel structure 
    # or we can mock pd.read_excel. 
    # For integration testing without files, we rely on the PDF simulation which is robust.
    return b"PK....." 

# --- Tests ---

def test_router_pdf_simulation():
    """Verify PDF Routing and Simulation Data Return."""
    dummy_pdf = BytesIO(create_dummy_pdf_content())
    # Name must end in .pdf
    df = FormatRouter.process_file(dummy_pdf, "statement.pdf")
    
    # Check Schema
    expected_cols = ["Date", "Description", "Withdrawal", "Deposit", "Balance", "Source_File"]
    assert list(df.columns) == expected_cols
    assert not df.empty
    assert "statement.pdf" in df["Source_File"].values

def test_router_unsupported_format():
    """Verify router rejects unknown extensions."""
    dummy = BytesIO(b"data")
    with pytest.raises(Exception) as excinfo:
        FormatRouter.process_file(dummy, "statement.txt")
    assert "Unsupported file format" in str(excinfo.value)

def test_schema_normalization_empty():
    """Verify schema is enforced even on empty frames."""
    df = pd.DataFrame()
    norm_df = FormatRouter._normalize_schema(df)
    expected_cols = ["Date", "Description", "Withdrawal", "Deposit", "Balance", "Source_File"]
    assert list(norm_df.columns) == expected_cols

def test_schema_normalization_casting():
    """Verify data types are cast correctly."""
    raw_data = {
        "Date": ["2026-01-01"],
        "Description": ["Test"],
        "Withdrawal": ["-100.50"], # String, negative
        "Deposit": [50],
        "Balance": ["1000"]
    }
    df = pd.DataFrame(raw_data)
    norm_df = FormatRouter._normalize_schema(df)
    
    # Withdrawal should be absolute float
    assert norm_df["Withdrawal"].iloc[0] == 100.50 
    assert isinstance(norm_df["Balance"].iloc[0], float)

def test_failure_protocol_artifact_creation():
    """
    Verify that after 2 failures, an error artifact is created.
    Uses the internal _handle_failure method directly or triggers via process_file.
    """
    filename = "bad_file.pdf"
    
    # Reset counts
    FormatRouter._failure_counts = {}
    
    # 1st Fail
    FormatRouter._handle_failure(filename, "Error 1")
    assert FormatRouter._failure_counts[filename] == 1
    
    # 2nd Fail
    FormatRouter._handle_failure(filename, "Error 2")
    assert FormatRouter._failure_counts[filename] == 2
    
    # Check if artifact was "written" (We check file existence)
    import os
    expected_path = "parsing_error_report.md"
    assert os.path.exists(expected_path)
    
    # Cleanup
    if os.path.exists(expected_path):
        os.remove(expected_path)
