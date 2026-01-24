"""
Anomaly Detection Module
Identifies suspicious transaction patterns beyond AI classification.
Implements forensic heuristics: round numbers, frequency analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

# =============================================================================
# ROUND NUMBER DETECTION
# =============================================================================

def detect_round_numbers(df: pd.DataFrame, threshold: float = 100.0) -> pd.DataFrame:
    """
    Flags transactions with "round" amounts (e.g., $10,000.00 vs $10,234.56).
    
    Rationale: Round numbers are statistically more likely to be gifts than 
    legitimate expenses. A $500.00 Zelle transfer is suspicious; a $487.23 
    utility bill is not.
    
    Args:
        df: DataFrame with 'amount' column
        threshold: Minimum amount to check (default: $100)
    
    Returns:
        DataFrame with 'Is_Round_Number' and 'Round_Anomaly_Score' columns
    
    Example:
        $10,000.00 → Is_Round=True, Score=High
        $10,234.56 → Is_Round=False, Score=None
    """
    if df.empty or 'amount' not in df.columns:
        df['Is_Round_Number'] = False
        df['Round_Anomaly_Score'] = 0
        return df
    
    # Convert amount to absolute value for analysis
    amounts = df['amount'].abs()
    
    # Check if amount is a "round" number
    # Level 1: Exact hundreds ($500.00, $1000.00)
    is_exact_hundred = (amounts % 100 == 0) & (amounts >= threshold)
    
    # Level 2: Exact thousands ($5000.00, $10000.00)
    is_exact_thousand = (amounts % 1000 == 0) & (amounts >= threshold)
    
    # Level 3: Suspicious patterns (e.g., $9500.00 - structuring)
    is_just_below_ten_k = (amounts > 9000) & (amounts < 10000) & (amounts % 100 == 0)
    
    # Assign anomaly score
    df['Is_Round_Number'] = is_exact_hundred | is_exact_thousand | is_just_below_ten_k
    df['Round_Anomaly_Score'] = 0
    
    # Scoring logic
    df.loc[is_exact_hundred, 'Round_Anomaly_Score'] = 25  # Moderate
    df.loc[is_exact_thousand, 'Round_Anomaly_Score'] = 50  # High
    df.loc[is_just_below_ten_k, 'Round_Anomaly_Score'] = 75  # Critical (structuring)
    
    return df


# =============================================================================
# FREQUENCY PATTERN ANALYSIS
# =============================================================================

def detect_frequency_patterns(df: pd.DataFrame, min_occurrences: int = 3) -> pd.DataFrame:
    """
    Identifies recurring payments to the same recipient/description.
    
    Rationale: Multiple payments to "John Doe" over time may indicate a 
    pattern of gifting that, when aggregated, exceeds penalty thresholds.
    
    Args:
        df: DataFrame with 'Description' column
        min_occurrences: Minimum number of times a pattern must occur (default: 3)
    
    Returns:
        DataFrame with 'Frequency_Pattern_Group' and 'Pattern_Total' columns
    
    Example:
        3 x "Check to John Doe" = High risk (aggregate $15,000)
    """
    if df.empty or 'Description' not in df.columns:
        df['Frequency_Pattern_Group'] = None
        df['Pattern_Total'] = 0
        df['Pattern_Count'] = 0
        return df
    
    # Normalize descriptions for grouping
    df['_normalized_desc'] = df['Description'].str.lower().str.strip()
    
    # Group by normalized description
    pattern_groups = df.groupby('_normalized_desc').agg({
        'amount': ['sum', 'count']
    }).reset_index()
    
    pattern_groups.columns = ['_normalized_desc', 'total_amount', 'occurrence_count']
    
    # Filter for patterns that occur >= min_occurrences
    significant_patterns = pattern_groups[pattern_groups['occurrence_count'] >= min_occurrences]
    
    # Merge back to original dataframe
    df = df.merge(
        significant_patterns[['_normalized_desc', 'total_amount', 'occurrence_count']],
        on='_normalized_desc',
        how='left'
    )
    
    # Tag transactions that are part of a pattern
    df['Frequency_Pattern_Group'] = df['_normalized_desc'].where(df['occurrence_count'] >= min_occurrences, None)
    df['Pattern_Total'] = df['total_amount'].fillna(0)
    df['Pattern_Count'] = df['occurrence_count'].fillna(0)
    
    # Clean up temporary columns
    df = df.drop(columns=['_normalized_desc', 'total_amount', 'occurrence_count'], errors='ignore')
    
    return df


# =============================================================================
# VELOCITY ANALYSIS (Bonus)
# =============================================================================

def detect_velocity_anomalies(df: pd.DataFrame, window_days: int = 30, velocity_threshold: float = 10000.0) -> pd.DataFrame:
    """
    Flags periods with unusually high transaction velocity.
    
    Rationale: A cluster of withdrawals within a short timeframe may indicate 
    "last-minute" asset divestment before Medicaid application.
    
    Args:
        df: DataFrame with 'Date' and 'amount' columns
        window_days: Rolling window size (default: 30 days)
        velocity_threshold: Total amount in window to trigger flag
    
    Returns:
        DataFrame with 'Velocity_Anomaly' flag
    """
    if df.empty or 'Date' not in df.columns:
        df['Velocity_Anomaly'] = False
        return df
    
    # Ensure Date is datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.sort_values('Date')
    
    # Calculate rolling sum over window
    df['Rolling_Amount'] = df.set_index('Date')['amount'].abs().rolling(f'{window_days}D', min_periods=1).sum().values
    
    # Flag if rolling sum exceeds threshold
    df['Velocity_Anomaly'] = df['Rolling_Amount'] > velocity_threshold
    
    return df


# =============================================================================
# MASTER ANOMALY DETECTION PIPELINE
# =============================================================================

def run_anomaly_detection(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs all anomaly detection modules on transaction data.
    
    Args:
        df: DataFrame with bank transaction data
    
    Returns:
        DataFrame with anomaly flags and scores
    
    Columns Added:
        - Is_Round_Number (bool)
        - Round_Anomaly_Score (int: 0-75)
        - Frequency_Pattern_Group (str or None)
        - Pattern_Total (float)
        - Pattern_Count (int)
        - Velocity_Anomaly (bool)
        - Overall_Anomaly_Score (int: 0-100)
    """
    if df.empty:
        return df
    
    # Run detection modules
    df = detect_round_numbers(df)
    df = detect_frequency_patterns(df)
    df = detect_velocity_anomalies(df)
    
    # Calculate overall anomaly score
    df['Overall_Anomaly_Score'] = 0
    
    # Add round number score
    df['Overall_Anomaly_Score'] += df['Round_Anomaly_Score']
    
    # Add frequency pattern score (if total > $5000)
    pattern_score = df['Pattern_Total'].apply(lambda x: min(25, int(x / 1000) * 5) if x > 5000 else 0)
    df['Overall_Anomaly_Score'] += pattern_score
    
    # Add velocity score
    df.loc[df['Velocity_Anomaly'], 'Overall_Anomaly_Score'] += 15
    
    # Cap at 100
    df['Overall_Anomaly_Score'] = df['Overall_Anomaly_Score'].clip(upper=100)
    
    # Elevate risk level for high anomaly scores
    high_anomaly_mask = (df['Overall_Anomaly_Score'] >= 50) & (df.get('Risk_Level', 'Low') != 'High')
    df.loc[high_anomaly_mask, 'Risk_Level'] = 'Medium'  # Bump to Medium
    
    return df


# =============================================================================
# REPORTING UTILITIES
# =============================================================================

def get_anomaly_summary(df: pd.DataFrame) -> Dict[str, any]:
    """
    Generates a summary report of detected anomalies.
    
    Returns:
        Dictionary with anomaly statistics
    """
    if df.empty:
        return {'total_anomalies': 0}
    
    summary = {
        'total_transactions': len(df),
        'round_number_count': int(df['Is_Round_Number'].sum()) if 'Is_Round_Number' in df.columns else 0,
        'frequency_patterns': len(df[df['Frequency_Pattern_Group'].notna()]) if 'Frequency_Pattern_Group' in df.columns else 0,
        'velocity_anomalies': int(df['Velocity_Anomaly'].sum()) if 'Velocity_Anomaly' in df.columns else 0,
        'high_anomaly_score': len(df[df.get('Overall_Anomaly_Score', 0) >= 50]),
        'total_anomalies': len(df[(df.get('Is_Round_Number', False)) | 
                                   (df.get('Frequency_Pattern_Group').notna()) | 
                                   (df.get('Velocity_Anomaly', False))])
    }
    
    # Top frequency patterns
    if 'Frequency_Pattern_Group' in df.columns:
        agg_dict = {'Pattern_Total': 'first'}
        if 'Pattern_Count' in df.columns:
            agg_dict['Pattern_Count'] = 'first'
            
        top_patterns = df[df['Frequency_Pattern_Group'].notna()].groupby('Frequency_Pattern_Group').agg(agg_dict).sort_values('Pattern_Total', ascending=False).head(5)
        
        summary['top_patterns'] = top_patterns.to_dict('index')
    
    return summary
