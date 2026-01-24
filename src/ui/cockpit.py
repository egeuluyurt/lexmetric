import streamlit as st
import pandas as pd
from src.reporting.generator import generate_defense_memo

def render_cockpit(df): 
    # --- 1. DATA SANITIZATION (Safety First) --- 
    # Ensure Amount is numeric 
    if 'amount' not in df.columns: 
        df['amount'] = 0.0 
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

    # Ensure Risk Level exists
    if 'Risk_Level' not in df.columns: 
        df['Risk_Level'] = 'Low'
    df['Risk_Level'] = df['Risk_Level'].astype(str).fillna('Low')

    # --- 2. LOGIC CORE ---
    # A. Status Emojis
    # A. Status Emojis (User Req: Lows should be Yellow too)
    def get_status(risk):
        r = str(risk).lower()
        if 'high' in r: return '🔴'
        # Medium AND Low are now Yellow as requested ("Lowlar falan da sarı işaretlensin")
        return '🟡'
        
    df['Status'] = df['Risk_Level'].apply(get_status)

    # B. Auto-Check (High Risk = Checked)
    df['Audit_Flag'] = df['Risk_Level'].str.contains('High', case=False, na=False)

    # C. Strict Sorting (High > Medium > Low)
    # Map Risk Level to Score for Sorting
    # High=3, Medium=2, Low=1
    def get_sort_score(risk):
        r = str(risk).lower()
        if 'high' in r: return 3
        if 'medium' in r: return 2
        return 1
        
    df['Sort_Score'] = df['Risk_Level'].apply(get_sort_score)
    
    # Sort: Flag (Checked) > Risk Score (High->Low) > Amount (Desc)
    df = df.sort_values(by=['Audit_Flag', 'Sort_Score', 'amount'], ascending=[False, False, False])

    # D. Reset Index (Crucial for UI stability)
    df = df.reset_index(drop=True)

    # --- 3. PREMIUM CLIENT HEADER (Gradient) ---
    c_name = st.session_state.get('client_name', 'Unknown Client')
    
    # Premium Gradient Header (matching case-workspace_premium.html)
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a365d, #1e293b);
        padding: 32px 0;
        margin: -2rem -2rem 2rem -2rem;
        color: white;
        position: relative;
        overflow: hidden;
        border-radius: 0 0 4px 4px;
    ">
        <div style="
            position: absolute;
            top: 0; right: 0;
            width: 40%; height: 100%;
            background: radial-gradient(circle at top right, rgba(197, 160, 89, 0.15) 0%, transparent 60%);
        "></div>
        <div style="max-width: 1400px; margin: 0 auto; padding: 0 24px; position: relative; z-index: 1;">
            <h1 style="
                font-family: 'Playfair Display', serif;
                font-size: 32px;
                font-weight: 900;
                margin-bottom: 8px;
                color: white;
            ">⚖️ {c_name} — Case Analysis</h1>
            <div style="
                font-size: 13px;
                color: rgba(255, 255, 255, 0.7);
                display: flex;
                gap: 16px;
                align-items: center;
            ">
                <span>Status: <span style="color: #34D399; font-weight: 600;">✓ Analysis Complete</span></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a container for metrics that we will fill AFTER the editor runs
    metrics_container = st.container()

    # --- 4. PREMIUM TRANSACTION TABLE ---
    st.markdown("""
    <h2 style="
        font-family: 'Playfair Display', serif;
        font-size: 22px;
        font-weight: 700;
        color: #1a365d;
        margin-top: 40px;
        margin-bottom: 20px;
    ">🔍 Transaction Analysis</h2>
    """, unsafe_allow_html=True)
    
    edited_df = st.data_editor( 
        df, 
        column_config={ 
            "Status": st.column_config.TextColumn("🚦", width="small", help="Red=High Risk"), 
            "Audit_Flag": st.column_config.CheckboxColumn("Include?", width="small", default=False), 
            "Risk_Level": st.column_config.SelectboxColumn(
                "Risk Level", 
                options=["High", "Medium", "Low"],
                width="medium",
                required=True,
                help="Adjust risk level manually if needed"
            ), 
            "Date": st.column_config.DatetimeColumn("Date", format="D MMM YYYY"), 
            "Description": st.column_config.TextColumn("Description", width="large"), 
            "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
            "Forensic_Reasoning": st.column_config.TextColumn("AI Reasoning", width="medium", help="System Logic"),
            "Attorney_Notes": st.column_config.TextColumn("⚖️ Attorney Notes", width="large", required=False),
        }, 
        # FORCE COLUMN ORDER 
        column_order=("Status", "Audit_Flag", "Risk_Level", "Date", "Description", "amount", "Forensic_Reasoning", "Attorney_Notes"), 
        use_container_width=True, 
        hide_index=True, 
        num_rows="fixed", 
        height=600, 
        # Lock everything EXCEPT Checkbox, Risk Level, and NOTES
        disabled=["Status", "Date", "Description", "amount", "Forensic_Reasoning"] 
    )

    # --- DYNAMIC METRICS CALCULATION (Based on User Edits) ---
    # Filter ONLY checked items from the EDITED dataframe
    flagged_items = edited_df[edited_df['Audit_Flag'] == True]
    
    # Retrieve Context for Math
    ctx = st.session_state.get('audit_context', {})
    state_code = ctx.get('state_rules', 'PA')
    
    # Simple lookup since we don't import MEDICAID_RULES here to avoid circular circular imports if not careful, 
    # but ideally we should. Or simpler: Pass it in args.
    # Let's rely on the Divisor we stored? No, we stored 'state_rules' code only.
    # We need to re-fetch the divisor.
    from src.config.jurisdictions import MEDICAID_RULES
    rule = MEDICAID_RULES.get(state_code, MEDICAID_RULES['PA'])
    divisor = rule['divisor']
    
    total_risk = flagged_items['amount'].sum()
    if state_code == 'TX':
        penalty_val = total_risk / divisor
        penalty_label = f"{penalty_val:.1f} Days"
    else:
        penalty_val = (total_risk / divisor) # Months usually, but wait. Divisor is Monthly? No, usually Monthly Divisor.
        # NY Divisor is 15150 (Monthly).
        # So Risk / Divisor = Months.
        penalty_label = f"{penalty_val:.1f} Months"

    # Update the container at the top
    with metrics_container:
        c1, c2, c3 = st.columns(3) 
        c1.metric("🚨 High Risks", f"{len(flagged_items)}", delta="Selected Items") 
        c2.metric("💰 Risk Exposure", f"${total_risk:,.2f}", delta="Audit Value") 
        c3.metric(f"🗓️ Penalty ({state_code})", penalty_label, delta=f"Divisor: ${divisor:,.0f}")

    # --- 5. STRICT EXPORT SECTION (The 'Sağlama') ---
    st.markdown("---") 
    st.markdown("### 📝 Final Report Verification")

    # filter ONLY checked items? NO. 
    # For the Advanced Trial Report, we need EVERYTHING to show "Schedule B: Exemptions".
    # The generator will split them based on 'Audit_Flag'.
    final_export = edited_df.copy()

    count = len(final_export) 
    total = final_export[final_export['Audit_Flag']==True]['amount'].sum()
    
    st.markdown("---")
    st.subheader("📄 Report Generation")
    
    # Report metadata form
    with st.expander("📋 Report Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            case_number = st.text_input(
                "Case Number",
                value=st.session_state.get('case_number', 'CASE-2026-001'),
                help="Internal case identifier"
            )
            
            attorney_name = st.text_input(
                "Reviewing Attorney",
                value=st.session_state.get('attorney_name', 'Reviewing Counsel'),
                help="Lead attorney name for certification"
            )
        
        with col2:
            state = st.selectbox(
                "Jurisdiction",
                options=['PA', 'NY', 'FL', 'TX', 'NJ', 'CA'],
                index=0,
                help="State Medicaid rules applied"
            )
            
            st.info(f"📊 **{count}** transactions | **${total:,.2f}** flagged")
    
    # Save to session state
    st.session_state['case_number'] = case_number
    st.session_state['attorney_name'] = attorney_name
    st.session_state['jurisdiction'] = state

    # Export button
    if count > 0: 
        try: 
            doc_buffer = generate_defense_memo(
                full_df=final_export,
                client_name=c_name,
                case_number=case_number,
                attorney_name=attorney_name,
                state=state
            )
            
            if doc_buffer: 
                st.download_button( 
                    label=f"⬇️ DOWNLOAD PROFESSIONAL REPORT ({count} Items)", 
                    data=doc_buffer, 
                    file_name=f"LexMetric_Defense_Report_{c_name.replace(' ', '_')}_{case_number}.docx", 
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                    type="primary", 
                    use_container_width=True,
                    help="Editable DOCX with charts, tables, and attorney workspace"
                )
                
                st.success("✅ Report includes: Executive Summary, Visual Charts, Transaction Tables, and Attorney Certification")
            else:
                st.error("❌ Report generation failed. Ensure python-docx is installed.")
        except Exception as e: 
            st.error(f"❌ Report Error: {e}") 
    else: 
        st.button("🚫 Select Transactions First", disabled=True, use_container_width=True)

