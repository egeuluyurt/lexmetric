import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.intelligence.classifier import TransactionClassifier

def test_anonymization_regex():
    """Verify PII redaction (Regex)."""
    text = "Transfer to John Doe 1234567890"
    clean = TransactionClassifier._anonymize(text)
    assert "[ACCT]" in clean
    assert "1234567890" not in clean
    
    # Verify SSN-like
    text2 = "ID: 123-45-6789"
    clean2 = TransactionClassifier._anonymize(text2)
    assert "[PII]" in clean2

@patch("src.intelligence.classifier.genai.GenerativeModel")
@patch("src.intelligence.classifier.st")
def test_batch_processing_structure(mock_st, mock_model_cls):
    """
    Verify batching logic chunks the dataframe correctly.
    We mock the actual Gemini call.
    """
    # Setup Mocks
    # Configure secrets on the mocked st object
    mock_st.secrets = {"GOOGLE_API_KEY": "fake_key"}
    mock_instance = MagicMock()
    mock_model_cls.return_value = mock_instance
    
    # Mock Response
    mock_response = MagicMock()
    mock_response.text = '[{"id": 0, "Category": "Test", "Risk_Level": 5}]'
    mock_instance.generate_content.return_value = mock_response
    
    # Create Classifier
    classifier = TransactionClassifier()
    
    # Create DataFrame (25 rows, batch size 20 -> 2 batches)
    df = pd.DataFrame({"Date": ["2026-01-01"]*25, "Description": ["Txn"]*25, "Withdrawal": [100]*25})
    
    # Patch the progress bar to avoid UI error in test
    with patch("src.intelligence.classifier.st.progress") as mock_progress:
        result_df = classifier.process_ledger_batches(df, batch_size=20)
        
    # Assertions
    assert not result_df.empty
    assert "Category" in result_df.columns
    # Check if mock was called twice (25 items / 20 = 2 batches)
    assert mock_instance.generate_content.call_count == 2

def test_classifier_initialization_no_key():
    """Verify graceful handling of missing key."""
    with patch("src.intelligence.classifier.st.secrets", {}): # Empty secrets
        classifier = TransactionClassifier()
        assert classifier.model is None
