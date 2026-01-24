import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

def render_dashboard():
    """
    Dashboard screen showing case history grid.
    Cases are loaded from ~/.lexmetric/cases.json
    """
    
    # Ensure data directory exists
    data_dir = Path.home() / ".lexmetric"
    data_dir.mkdir(exist_ok=True)
    cases_file = data_dir / "cases.json"
    
    # Load cases
    if cases_file.exists():
        with open(cases_file, 'r') as f:
            cases = json.load(f)
    else:
        cases = []
    
    # Dashboard Header
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px;">
        <h1 style="
            font-family: 'Playfair Display', serif;
            font-size: 36px;
            font-weight: 700;
            color: #1a365d;
            margin: 0;
        ">Active Cases</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Search Bar
    search_term = st.text_input(
        "🔍 Search",
        placeholder="Search by client name or jurisdiction...",
        key="dashboard_search",
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)
    
    # Filter cases
    if search_term:
        filtered_cases = [
            c for c in cases 
            if search_term.lower() in c.get('client_name', '').lower() 
            or search_term.lower() in c.get('state', '').lower()
        ]
    else:
        filtered_cases = cases
    
    # Empty State
    if not filtered_cases:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 80px 24px;
            background: white;
            border: 2px dashed rgba(26, 54, 93, 0.12);
            border-radius: 8px;
        ">
            <div style="font-size: 48px; opacity: 0.4; margin-bottom: 16px;">📂</div>
            <h3 style="
                font-family: 'Playfair Display', serif;
                font-size: 24px;
                color: #1a365d;
                margin-bottom: 8px;
            ">No cases found</h3>
            <p style="color: #64748B; margin-bottom: 24px;">
                Try adjusting your search or create a new case.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Case Grid (3 columns)
    cols = st.columns(3)
    
    for idx, case in enumerate(filtered_cases):
        col_idx = idx % 3
        with cols[col_idx]:
            # Case Card
            status = case.get('status', 'Draft')
            client = case.get('client_name', 'Unknown')
            state = case.get('state', 'N/A')
            risk_total = case.get('risk_total', 0.0)
            high_risks = case.get('high_risks', 0)
            penalty = case.get('penalty', '0.0 Months')
            timestamp = case.get('timestamp', '')
            
            # Status badge color
            if status == 'Analyzed':
                badge_bg = 'rgba(26, 54, 93, 0.1)'
                badge_color = '#1a365d'
            elif status == 'Exported':
                badge_bg = 'rgba(5, 150, 105, 0.1)'
                badge_color = '#059669'
            else:
                badge_bg = 'rgba(100, 116, 139, 0.1)'
                badge_color = '#64748B'
            
            # Penalty color
            penalty_color = '#DC2626' if risk_total > 0 else '#64748B'
            
            st.markdown(f"""
            <div style="
                background: white;
                border: 1px solid rgba(26, 54, 93, 0.08);
                border-radius: 4px;
                padding: 24px;
                margin-bottom: 20px;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
            " class="case-card">
                <!-- Card Header -->
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
                    <div>
                        <div style="
                            font-family: 'Playfair Display', serif;
                            font-size: 18px;
                            font-weight: 700;
                            color: #1a365d;
                            margin-bottom: 6px;
                        ">{client}</div>
                        <div style="font-size: 12px; color: #64748B;">
                            📍 {state} • {timestamp}
                        </div>
                    </div>
                    <span style="
                        padding: 4px 12px;
                        border-radius: 2px;
                        font-size: 10px;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        background: {badge_bg};
                        color: {badge_color};
                    ">{status}</span>
                </div>
                
                <!-- Penalty Amount -->
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 28px;
                    font-weight: 700;
                    color: {penalty_color};
                    margin-bottom: 12px;
                ">${risk_total:,.2f}</div>
                
                <!-- Case Info -->
                <div style="
                    display: flex;
                    gap: 16px;
                    margin-bottom: 16px;
                    font-size: 13px;
                    color: #64748B;
                ">
                    <div>🚨 {high_risks} high risks</div>
                    <div>📅 {penalty}</div>
                </div>
                
                <!-- Divider -->
                <div style="border-top: 1px solid rgba(26, 54, 93, 0.08); margin: 16px 0;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("Open", key=f"open_{idx}", use_container_width=True):
                    st.info(f"Loading case: {client}")
            with col_b:
                if st.button("Export", key=f"export_{idx}", use_container_width=True):
                    st.info(f"Exporting case: {client}")
            with col_c:
                if st.button("Delete", key=f"delete_{idx}", use_container_width=True):
                    # Remove from cases list
                    cases.pop(filtered_cases.index(case))
                    with open(cases_file, 'w') as f:
                        json.dump(cases, f, indent=2)
                    st.rerun()

def save_case(client_name, state, risk_total=0.0, high_risks=0, penalty="0.0 Months", status="Draft"):
    """
    Save case to ~/.lexmetric/cases.json
    """
    data_dir = Path.home() / ".lexmetric"
    data_dir.mkdir(exist_ok=True)
    cases_file = data_dir / "cases.json"
    
    # Load existing cases
    if cases_file.exists():
        with open(cases_file, 'r') as f:
            cases = json.load(f)
    else:
        cases = []
    
    # Add new case
    new_case = {
        'client_name': client_name,
        'state': state,
        'risk_total': risk_total,
        'high_risks': high_risks,
        'penalty': penalty,
        'status': status,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    cases.append(new_case)
    
    # Save
    with open(cases_file, 'w') as f:
        json.dump(cases, f, indent=2)
