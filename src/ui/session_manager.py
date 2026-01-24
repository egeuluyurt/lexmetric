import streamlit as st
import pandas as pd
from typing import Optional, Dict

class SessionManager:
    """
    Manages the Streamlit Session State to ensure Zero-Persistence.
    All data is kept in memory.
    """

    @staticmethod
    def initialize_session():
        """
        Initializes the session state with default values if they don't exist.
        """
        if 'ledger_df' not in st.session_state:
            st.session_state['ledger_df'] = None
        
        if 'audit_context' not in st.session_state:
            st.session_state['audit_context'] = {
                'state_rules': 'PA', # Default: Commonwealth of Pennsylvania
                'lookback_date': '2021-01-01' # Default placeholder
            }
            
        if 'processing_status' not in st.session_state:
            st.session_state['processing_status'] = 'idle'
            
    @staticmethod
    def get_ledger() -> Optional[pd.DataFrame]:
        """Safe accessor for the ledger."""
        return st.session_state.get('ledger_df')

    @staticmethod
    def set_ledger(df: pd.DataFrame):
        """Safe setter for the ledger."""
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Ledger must be a Pandas DataFrame")
        st.session_state['ledger_df'] = df
        st.session_state['processing_status'] = 'loaded'
        
    @staticmethod
    def clear_session():
        """Clears sensitive data from memory."""
        st.session_state['ledger_df'] = None
        st.session_state['processing_status'] = 'idle'
