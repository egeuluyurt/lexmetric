import pytest
import pandas as pd
from datetime import datetime
from src.audit_engine.audit_logic import AuditEngine
from src.audit_engine.config import REGULATORY_DATA_2026

def test_calculate_lookback_window():
    """Verify exact 60-month calculation."""
    app_date = datetime(2026, 6, 1)
    start, end = AuditEngine.calculate_lookback_window(app_date)
    
    # 2026 - 5 years = 2021
    assert start == datetime(2021, 6, 1)
    assert end == datetime(2026, 6, 1)

def test_filter_ledger_boundary():
    """Verify transactions outside the window are excluded."""
    app_date = datetime(2026, 6, 1)
    start, end = AuditEngine.calculate_lookback_window(app_date)
    
    data = {
        "Date": [
            datetime(2021, 5, 31), # 1 day before start (Should be Excluded)
            datetime(2021, 6, 1),  # On start day (Should be Included)
            datetime(2026, 6, 1),  # On end day (Included)
            datetime(2026, 6, 2)   # 1 day after end (Excluded)
        ],
        "Amount": [100, 200, 300, 400]
    }
    df = pd.DataFrame(data)
    
    filtered = AuditEngine.filter_ledger(df, start, end)
    
    assert len(filtered) == 2
    assert 200 in filtered["Amount"].values
    assert 300 in filtered["Amount"].values
    assert 100 not in filtered["Amount"].values

def test_calculate_penalty_math():
    """
    Verify deterministic math.
    FL Divisor = 375.00
    Amount = 3750.00
    Expected = 10 days
    """
    days, months = AuditEngine.calculate_penalty(3750.00, "FL")
    assert days == 10.0
    
    # Test NY (515.00)
    # 10300 / 515 = 20
    days_ny, _ = AuditEngine.calculate_penalty(10300.00, "NY")
    assert days_ny == 20.0

def test_calculate_penalty_invalid_state():
    """Verify error on unknown state."""
    with pytest.raises(ValueError) as exc:
        AuditEngine.calculate_penalty(5000, "XX")
    assert "not supported" in str(exc.value)

def test_regulatory_data_integrity():
    """Verify config contains required keys."""
    for state in ["PA", "FL", "NY", "CA"]:
        assert state in REGULATORY_DATA_2026
        assert "daily_penalty_divisor" in REGULATORY_DATA_2026[state]
