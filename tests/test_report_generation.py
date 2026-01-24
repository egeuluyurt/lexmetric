import pandas as pd
from src.reporting.generator import generate_defense_memo
import os

def test_report_generation():
    # Create dummy data
    data = {
        'Date': [pd.Timestamp('2024-01-01'), pd.Timestamp('2024-01-02')],
        'Description': ['Test Transaction 1', 'Test Transaction 2'],
        'Risk_Level': ['High', 'Low'],
        'amount': [1000.50, 50.00]
    }
    df = pd.DataFrame(data)
    
    # Generate report
    print("Generating report...")
    buffer = generate_defense_memo(df, client_name="Test Client")
    
    if buffer:
        print("Report generated successfully (buffer created).")
        # Optional: Save to file to manually check if needed, but for now just confirming buffer creation
        with open("test_report_output.docx", "wb") as f:
            f.write(buffer.getvalue())
        print("Saved to test_report_output.docx")
    else:
        print("Failed to generate report (buffer is None).")

if __name__ == "__main__":
    test_report_generation()
