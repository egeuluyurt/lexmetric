"""
Professional Medicaid Audit Defense Report Generator
Produces enterprise-grade DOCX reports with charts and legal styling
"""

import io
import logging
from datetime import datetime
from typing import Optional
import pandas as pd

# Core dependencies
try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# Chart generation
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

logger = logging.getLogger(__name__)

# ============================================================================
# LEXMETRIC BRANDING
# ============================================================================
BRAND_COLORS = {
    'navy': RGBColor(26, 54, 93),      # #1a365d
    'gray': RGBColor(113, 128, 150),   # #718096
    'red': RGBColor(220, 38, 38),      # High risk
    'yellow': RGBColor(217, 119, 6),   # Medium risk
    'green': RGBColor(22, 163, 74),    # Low risk
    'white': RGBColor(255, 255, 255)
}

# ============================================================================
# CHART GENERATION
# ============================================================================

def generate_risk_pie_chart(penalty_df: pd.DataFrame) -> Optional[io.BytesIO]:
    """Generate risk distribution pie chart"""
    if not HAS_MATPLOTLIB or penalty_df.empty:
        return None
    
    try:
        # Group by risk level
        risk_counts = penalty_df.groupby('Risk_Level').agg({
            'amount': 'sum'
        }).reset_index()
        
        if risk_counts.empty:
            return None
        
        # Create figure
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='white')
        
        colors_map = {'High': '#dc2626', 'Medium': '#d97706', 'Low': '#16a34a'}
        colors = [colors_map.get(level, '#718096') for level in risk_counts['Risk_Level']]
        
        wedges, texts, autotexts = ax.pie(
            risk_counts['amount'],
            labels=risk_counts['Risk_Level'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        # Style
        for text in texts:
            text.set_fontsize(11)
            text.set_weight('bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        ax.set_title('Flagged Transfers by Risk Level', fontsize=13, weight='bold', pad=20)
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        logger.error(f"Chart generation failed: {e}")
        return None


def generate_timeline_chart(full_df: pd.DataFrame) -> Optional[io.BytesIO]:
    """Generate monthly spending timeline"""
    if not HAS_MATPLOTLIB or full_df.empty:
        return None
    
    try:
        # Ensure date column
        df = full_df.copy()
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        
        if df.empty:
            return None
        
        # Monthly aggregation
        df['YearMonth'] = df['Date'].dt.to_period('M')
        monthly = df.groupby('YearMonth')['amount'].sum().reset_index()
        monthly['YearMonth'] = monthly['YearMonth'].dt.to_timestamp()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')
        
        ax.plot(monthly['YearMonth'], monthly['amount'], 
                color='#1a365d', linewidth=2.5, marker='o', markersize=5)
        
        ax.fill_between(monthly['YearMonth'], monthly['amount'], 
                        alpha=0.2, color='#1a365d')
        
        # Styling
        ax.set_title('60-Month Transaction Volume', fontsize=13, weight='bold', pad=15)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Total Amount ($)', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        logger.error(f"Timeline chart failed: {e}")
        return None


# ============================================================================
# DOCX UTILITIES
# ============================================================================

def add_header_footer(doc: Document, client_name: str):
    """Add professional header and footer to all pages"""
    try:
        # Header
        section = doc.sections[0]
        header = section.header
        header_para = header.paragraphs[0]
        header_para.text = "LexMetric Medicaid Audit Defense | CONFIDENTIAL - ATTORNEY WORK PRODUCT"
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = header_para.runs[0]
        run.font.size = Pt(9)
        run.font.color.rgb = BRAND_COLORS['gray']
        run.font.name = 'Georgia'
        
        # Add bottom border to header
        pPr = header_para._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '718096')
        pBdr.append(bottom)
        pPr.append(pBdr)
        
        # Footer
        footer = section.footer
        footer_para = footer.paragraphs[0]
        footer_para.text = f"Client: {client_name} | Page "
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = footer_para.runs[0]
        run.font.size = Pt(9)
        run.font.color.rgb = BRAND_COLORS['gray']
        run.font.name = 'Georgia'
        
    except Exception as e:
        logger.warning(f"Header/footer setup failed: {e}")


def set_cell_background(cell, color_rgb: RGBColor):
    """Set table cell background color"""
    try:
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:fill'), f'{color_rgb.r:02x}{color_rgb.g:02x}{color_rgb.b:02x}')
        cell._element.get_or_add_tcPr().append(shading_elm)
    except:
        pass


# ============================================================================
# MAIN REPORT GENERATOR
# ============================================================================

def generate_defense_memo(
    full_df: pd.DataFrame,
    client_name: str = "Unknown Client",
    case_number: str = "N/A",
    attorney_name: str = "Reviewing Counsel",
    state: str = "PA"
) -> Optional[io.BytesIO]:
    """
    Generate professional DOCX report for Medicaid audit defense
    
    Args:
        full_df: Complete transaction DataFrame with AI analysis
        client_name: Client's full name
        case_number: Internal case identifier
        attorney_name: Lead attorney name
        state: State jurisdiction (PA, NY, FL, etc.)
    
    Returns:
        BytesIO buffer containing DOCX file, or None if failed
    """
    if not HAS_DOCX:
        logger.error("python-docx not installed")
        return None
    
    try:
        doc = Document()
        
        # Setup header/footer
        add_header_footer(doc, client_name)
        
        # ====================================================================
        # COVER PAGE
        # ====================================================================
        title = doc.add_heading('MEDICAID AUDIT DEFENSE REPORT', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in title.runs:
            run.font.color.rgb = BRAND_COLORS['navy']
            run.font.name = 'Georgia'
        
        doc.add_paragraph()  # Spacing
        
        # Case info table
        info_table = doc.add_table(rows=5, cols=2)
        info_table.style = 'Light Grid Accent 1'
        
        info_data = [
            ('Client Name:', client_name),
            ('Case Number:', case_number),
            ('Jurisdiction:', state),
            ('Reviewing Attorney:', attorney_name),
            ('Report Date:', datetime.now().strftime('%B %d, %Y'))
        ]
        
        for i, (label, value) in enumerate(info_data):
            row = info_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            
            # Bold labels
            row.cells[0].paragraphs[0].runs[0].font.bold = True
            row.cells[0].paragraphs[0].runs[0].font.color.rgb = BRAND_COLORS['navy']
        
        # Confidentiality notice
        doc.add_paragraph()
        notice = doc.add_paragraph()
        notice_run = notice.add_run(
            '⚠️ CONFIDENTIAL - ATTORNEY-CLIENT PRIVILEGE\n'
            'This document contains privileged legal analysis prepared for litigation. '
            'Unauthorized disclosure is prohibited.'
        )
        notice_run.font.size = Pt(9)
        notice_run.font.italic = True
        notice_run.font.color.rgb = BRAND_COLORS['gray']
        notice.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_page_break()
        
        # ====================================================================
        # DATA PREPARATION
        # ====================================================================
        full_df = full_df.copy()
        full_df['Audit_Flag'] = full_df['Audit_Flag'].fillna(False).astype(bool)
        
        penalty_df = full_df[full_df['Audit_Flag'] == True].copy()
        exempt_df = full_df[full_df['Audit_Flag'] == False].copy()
        
        total_penalty = penalty_df['amount'].sum()
        total_exempt = exempt_df['amount'].sum()
        total_transactions = len(full_df)
        flagged_count = len(penalty_df)
        
        # ====================================================================
        # EXECUTIVE SUMMARY
        # ====================================================================
        doc.add_heading('I. EXECUTIVE SUMMARY', level=1)
        
        # Key metrics
        metrics_table = doc.add_table(rows=4, cols=2)
        metrics_table.style = 'Medium Shading 1 Accent 1'
        
        metrics_data = [
            ('Total Flagged Transfers:', f'${total_penalty:,.2f}'),
            ('Justified Exemptions:', f'${total_exempt:,.2f}'),
            ('Total Transactions Reviewed:', f'{total_transactions:,}'),
            ('Flagged Transaction Count:', f'{flagged_count:,}')
        ]
        
        for i, (label, value) in enumerate(metrics_data):
            row = metrics_table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value
            row.cells[1].paragraphs[0].runs[0].font.bold = True
            row.cells[1].paragraphs[0].runs[0].font.size = Pt(12)
        
        doc.add_paragraph()
        
        # Net exposure calculation
        net_para = doc.add_paragraph()
        net_para.add_run('Estimated Divestment Penalty Liability: ').bold = True
        net_run = net_para.add_run(f'${total_penalty:,.2f}')
        net_run.bold = True
        net_run.font.size = Pt(14)
        net_run.font.color.rgb = BRAND_COLORS['red'] if total_penalty > 1000 else BRAND_COLORS['green']
        
        doc.add_paragraph()
        
        # ====================================================================
        # CHARTS
        # ====================================================================
        if HAS_MATPLOTLIB and not penalty_df.empty:
            doc.add_heading('II. VISUAL FORENSIC ANALYSIS', level=1)
            
            # Risk pie chart
            pie_buffer = generate_risk_pie_chart(penalty_df)
            if pie_buffer:
                doc.add_picture(pie_buffer, width=Inches(5.5))
                last_paragraph = doc.paragraphs[-1]
                last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph()
            
            # Timeline chart
            timeline_buffer = generate_timeline_chart(full_df)
            if timeline_buffer:
                doc.add_picture(timeline_buffer, width=Inches(6.5))
                last_paragraph = doc.paragraphs[-1]
                last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_page_break()
        
        # ====================================================================
        # METHODOLOGY
        # ====================================================================
        doc.add_heading('III. METHODOLOGY & AI ANALYSIS', level=1)
        
        method_para = doc.add_paragraph(
            'This report utilized Google Gemini 2.5 Flash AI model for forensic transaction analysis. '
            f'All transactions were evaluated against {state} Medicaid divestment rules, including:\n'
        )
        
        doc.add_paragraph('60-month look-back period compliance', style='List Bullet')
        doc.add_paragraph('Structured payment detection (e.g., amounts just under $10,000)', style='List Bullet')
        doc.add_paragraph('High-risk transfer identification (gambling, cash withdrawals, P2P)', style='List Bullet')
        doc.add_paragraph('State-specific penalty divisor application', style='List Bullet')
        
        doc.add_paragraph(
            '\n⚖️ All AI determinations were reviewed and validated by licensed counsel. '
            'Attorney overrides and annotations are marked throughout this report.'
        ).runs[0].font.italic = True
        
        doc.add_page_break()
        
        # ====================================================================
        # TRANSACTION TABLES
        # ====================================================================
        
        def add_transaction_table(df: pd.DataFrame, title: str, schedule_letter: str):
            """Add formatted transaction table"""
            if df.empty:
                doc.add_heading(f'{schedule_letter}. {title}', level=1)
                doc.add_paragraph(f'No {title.lower()} identified.')
                return
            
            doc.add_heading(f'{schedule_letter}. {title}', level=1)
            doc.add_paragraph(f'Total: ${df["amount"].sum():,.2f} ({len(df)} transactions)\n')
            
            # Create table
            table = doc.add_table(rows=1, cols=5)
            table.style = 'Light Grid Accent 1'
            table.autofit = False
            
            # Set column widths
            table.columns[0].width = Inches(1.0)   # Date
            table.columns[1].width = Inches(2.5)   # Description
            table.columns[2].width = Inches(0.8)   # Risk
            table.columns[3].width = Inches(1.0)   # Amount
            table.columns[4].width = Inches(1.2)   # AI Reason
            
            # Header row
            header_cells = table.rows[0].cells
            headers = ['Date', 'Description', 'Risk', 'Amount', 'AI Analysis']
            
            for i, header_text in enumerate(headers):
                header_cells[i].text = header_text
                header_cells[i].paragraphs[0].runs[0].font.bold = True
                header_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                set_cell_background(header_cells[i], BRAND_COLORS['navy'])
            
            # Data rows
            for _, row_data in df.iterrows():
                row_cells = table.add_row().cells
                
                # Date
                date_val = row_data.get('Date')
                if pd.notna(date_val):
                    if isinstance(date_val, pd.Timestamp):
                        row_cells[0].text = date_val.strftime('%Y-%m-%d')
                    else:
                        row_cells[0].text = str(date_val)[:10]
                else:
                    row_cells[0].text = 'N/A'
                
                # Description
                desc = str(row_data.get('Description', 'Unidentified'))[:60]
                row_cells[1].text = desc if desc != 'nan' else 'Unidentified'
                
                # Risk Level with color
                risk = str(row_data.get('Risk_Level', 'Low'))
                row_cells[2].text = risk
                
                risk_color = BRAND_COLORS.get(
                    {'High': 'red', 'Medium': 'yellow', 'Low': 'green'}.get(risk, 'gray'),
                    BRAND_COLORS['gray']
                )
                row_cells[2].paragraphs[0].runs[0].font.bold = True
                row_cells[2].paragraphs[0].runs[0].font.color.rgb = risk_color
                
                # Amount
                amount = row_data.get('amount', 0)
                row_cells[3].text = f'${amount:,.2f}'
                row_cells[3].paragraphs[0].runs[0].font.bold = True
                
                # AI Reasoning (truncated)
                ai_reason = str(row_data.get('Forensic_Reasoning', ''))[:100]
                row_cells[4].text = ai_reason if ai_reason != 'nan' else '—'
                row_cells[4].paragraphs[0].runs[0].font.size = Pt(8)
                
                # Attorney Notes (if present)
                attorney_note = str(row_data.get('Attorney_Notes', ''))
                if attorney_note and attorney_note != 'nan':
                    note_row = table.add_row()
                    merged_cell = note_row.cells[0].merge(note_row.cells[4])
                    
                    note_para = merged_cell.paragraphs[0]
                    note_run = note_para.add_run(f'⚖️ COUNSEL NOTE: {attorney_note}')
                    note_run.font.bold = True
                    note_run.font.italic = True
                    note_run.font.color.rgb = BRAND_COLORS['navy']
                    
                    set_cell_background(merged_cell, RGBColor(240, 248, 255))  # Light blue
            
            doc.add_paragraph()  # Spacing
        
        # Add both schedules
        add_transaction_table(penalty_df, 'Flagged Transfers (Penalty Base)', 'Schedule A')
        doc.add_page_break()
        add_transaction_table(exempt_df, 'Justified Exemptions', 'Schedule B')
        
        # ====================================================================
        # ATTORNEY WORKSPACE
        # ====================================================================
        doc.add_page_break()
        doc.add_heading('IV. ATTORNEY OPINION & RECOMMENDATIONS', level=1)
        
        doc.add_paragraph(
            'The following section is reserved for counsel\'s legal analysis and strategic recommendations:'
        )
        
        # Editable placeholder boxes
        doc.add_paragraph('\n☐ Legal Opinion on Divestment Penalty Applicability:')
        doc.add_paragraph('_' * 100)
        doc.add_paragraph('_' * 100)
        doc.add_paragraph('_' * 100)
        
        doc.add_paragraph('\n☐ Recommended Client Response Strategy:')
        doc.add_paragraph('_' * 100)
        doc.add_paragraph('_' * 100)
        
        doc.add_paragraph('\n☐ Exemption Arguments to Assert:')
        doc.add_paragraph('_' * 100)
        doc.add_paragraph('_' * 100)
        
        # ====================================================================
        # CERTIFICATION
        # ====================================================================
        doc.add_page_break()
        doc.add_heading('V. ATTORNEY CERTIFICATION', level=1)
        
        cert_para = doc.add_paragraph(
            f'I, {attorney_name}, hereby certify that I have reviewed the AI-generated analysis '
            'contained in this report and verified its accuracy to the best of my professional ability. '
            'This document represents my legal work product prepared in anticipation of litigation.\n\n'
        )
        
        doc.add_paragraph('\n\n')
        sig_table = doc.add_table(rows=3, cols=2)
        sig_table.rows[0].cells[0].text = 'Attorney Signature:'
        sig_table.rows[0].cells[1].text = '_' * 40
        sig_table.rows[1].cells[0].text = 'Print Name:'
        sig_table.rows[1].cells[1].text = attorney_name
        sig_table.rows[2].cells[0].text = 'Date:'
        sig_table.rows[2].cells[1].text = '_' * 40
        
        # ====================================================================
        # FINALIZE
        # ====================================================================
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        logger.info(f"Report generated: {total_transactions} transactions, ${total_penalty:,.2f} flagged")
        return buffer
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        return None
