"""
LexMetric Premium CSS Layer
Bespoke Luxury Legal Tech Design System v2.0
Inject this at the top of app.py to apply the complete design system.
"""

import streamlit as st

def inject_production_css():
    """
    Applies LexMetric Premium Design System to Streamlit application.
    Call this function once at the top of app.py.
    """
    
    st.markdown("""
    <style>
        /* ==========================================
           GOOGLE FONTS - LOAD FIRST
           ========================================== */
        
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        /* ==========================================
           CSS VARIABLES (Bespoke Luxury Tokens)
           ========================================== */
        
        :root {
            /* Brand Colors */
            --legal-blue: #1a365d !important;
            --accent-gold: #C5A059 !important;
            --bg-ivory: #FDFCFB !important;
            --border-light: rgba(26, 54, 93, 0.08) !important;
            
            /* Text Colors */
            --slate-900: #1E293B !important;
            --text-muted: #64748B !important;
            
            /* Semantic */
            --success-green: #059669 !important;
            --success-bg: #ECFDF5 !important;
            --warning-amber: #D97706 !important;
            --warning-bg: #FFFBEB !important;
            --danger-red: #DC2626 !important;
            --danger-bg: #FEF2F2 !important;
            
            /* Spacing */
            --space-1: 4px !important;
            --space-2: 8px !important;
            --space-3: 12px !important;
            --space-4: 16px !important;
            --space-6: 24px !important;
            --space-8: 32px !important;
            
            /* Typography */
            --font-serif: 'Playfair Display', Georgia, serif !important;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            --font-mono: 'JetBrains Mono', 'Courier New', monospace !important;
        }
        
        /* ==========================================
           STREAMLIT RESETS & GLOBAL OVERRIDES
           ========================================== */
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        header {visibility: hidden !important;}
        .stDeployButton {display: none !important;}
        
        /* CRITICAL: Premium Background with Cream Paper Texture */
        .stApp {
            background-color: #FDFCFB !important;
            background-image: url('https://www.transparenttextures.com/patterns/cream-paper.png') !important;
            background-blend-mode: multiply !important;
        }
        
        /* Force body background too */
        body {
            background-color: #FDFCFB !important;
        }
        
        /* Main container */
        .main .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1400px !important;
            background: transparent !important;
        }
        
        /* ==========================================
           SIDEBAR - BESPOKE LUXURY DESIGN
           ========================================== */
        
        /* Sidebar Background - Cream Gradient */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #FDFCFB 0%, #F5F3F0 100%) !important;
            border-right: 2px solid rgba(197, 160, 89, 0.3) !important;
        }
        
        /* Remove default Streamlit sidebar bg */
        [data-testid="stSidebar"] > div:first-child {
            background-color: transparent !important;
        }
        
        /* Sidebar Title Styling */
        [data-testid="stSidebar"] h1 {
            font-family: var(--font-serif) !important;
            color: var(--legal-blue) !important;
            font-weight: 900 !important;
            font-size: 24px !important;
            margin-bottom: 12px !important;
        }
        
        /* Sidebar Section Headers */
        [data-testid="stSidebar"] h3 {
            font-family: var(--font-sans) !important;
            color: var(--legal-blue) !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            margin-top: 24px !important;
            margin-bottom: 12px !important;
        }
        
        [data-testid="stSidebar"] h4 {
            font-family: var(--font-sans) !important;
            color: var(--text-muted) !important;
            font-weight: 600 !important;
            font-size: 12px !important;
            margin-top: 16px !important;
            margin-bottom: 8px !important;
        }
        
        /* Sidebar Labels */
        [data-testid="stSidebar"] label {
            font-family: var(--font-sans) !important;
            color: var(--text-muted) !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }
        
        /* Input Fields in Sidebar - Gold Focus */
        [data-testid="stSidebar"] input {
            background: white !important;
            border: 1.5px solid rgba(26, 54, 93, 0.15) !important;
            border-radius: 4px !important;
            padding: 10px 12px !important;
            font-family: var(--font-sans) !important;
            font-size: 14px !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stSidebar"] input:focus {
            border-color: var(--accent-gold) !important;
            box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.15) !important;
            outline: none !important;
        }
        
        /* Select Boxes - Gold Focus */
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: white !important;
            border: 1.5px solid rgba(26, 54, 93, 0.15) !important;
            border-radius: 4px !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
            border-color: var(--accent-gold) !important;
            box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.15) !important;
        }
        
        /* File Uploader - Gold Dashed Border */
        [data-testid="stSidebar"] [data-testid="stFileUploader"] {
            background: white !important;
            border: 2px dashed rgba(197, 160, 89, 0.5) !important;
            border-radius: 8px !important;
            padding: 20px !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
            border-color: var(--accent-gold) !important;
            background: rgba(197, 160, 89, 0.03) !important;
        }
        
        /* Sidebar Buttons */
        [data-testid="stSidebar"] button {
            background: var(--legal-blue) !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 10px 20px !important;
            font-family: var(--font-sans) !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stSidebar"] button:hover {
            background: #0f1f3d !important;
            box-shadow: 0 4px 12px rgba(26, 54, 93, 0.25) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Sidebar Markdown Content */
        [data-testid="stSidebar"] .stMarkdown {
            font-family: var(--font-sans) !important;
        }
        
        /* Horizontal Rule in Sidebar - Gold */
        [data-testid="stSidebar"] hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(to right, transparent, rgba(197, 160, 89, 0.3), transparent) !important;
            margin: 24px 0 !important;
        }

        
        /* ==========================================
           TYPOGRAPHY
           ========================================== */
        
        /* Headers - Playfair Display */
        .main h1 {
            font-family: var(--font-serif) !important;
            font-size: 36px !important;
            font-weight: 700 !important;
            color: var(--legal-blue) !important;
            letter-spacing: -1px !important;
            line-height: 1.2 !important;
            margin-bottom: var(--space-6) !important;
        }
        
        .main h2 {
            font-family: var(--font-serif) !important;
            font-size: 28px !important;
            font-weight: 700 !important;
            color: var(--legal-blue) !important;
            letter-spacing: -0.5px !important;
            margin-bottom: var(--space-4) !important;
        }
        
        .main h3 {
            font-family: var(--font-serif) !important;
            font-size: 22px !important;
            font-weight: 700 !important;
            color: var(--legal-blue) !important;
        }
        
        /* Body text - Inter */
        .main p, .main li, .main span {
            font-family: var(--font-sans) !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
            color: var(--slate-900) !important;
        }
        
        /* Code - JetBrains Mono */
        code {
            background: rgba(26, 54, 93, 0.05) !important;
            color: var(--legal-blue) !important;
            padding: 2px 8px !important;
            border-radius: 2px !important;
            font-family: var(--font-mono) !important;
            font-size: 13px !important;
        }
        
        /* ==========================================
           BUTTONS
           ========================================== */
        
        .stButton>button {
            background: var(--legal-blue) !important;
            color: white !important;
            border: none !important;
            border-radius: 2px !important;
            font-family: var(--font-sans) !important;
            font-weight: 600 !important;
            font-size: 12px !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
            padding: 14px 28px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
        }
        
        .stButton>button:hover {
            background: var(--accent-gold) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(197, 160, 89, 0.25) !important;
        }
        
        .stButton>button:active {
            transform: translateY(0) !important;
        }
        
        /* Download Button */
        .stDownloadButton>button {
            background: var(--success-green) !important;
            color: white !important;
            border-radius: 2px !important;
            font-weight: 600 !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
        }
        
        .stDownloadButton>button:hover {
            background: #047857 !important;
            box-shadow: 0 8px 20px rgba(5, 150, 105, 0.25) !important;
        }
        
        /* ==========================================
           TEXT INPUTS & FORMS
           ========================================== */
        
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stNumberInput>div>div>input {
            background: var(--bg-ivory) !important;
            border: 1px solid var(--border-light) !important;
            border-radius: 2px !important;
            padding: 14px 16px !important;
            font-size: 14px !important;
            font-family: var(--font-sans) !important;
            color: var(--slate-900) !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus,
        .stNumberInput>div>div>input:focus {
            border-color: var(--accent-gold) !important;
            box-shadow: 0 0 0 3px rgba(197, 160, 89, 0.1) !important;
            background: white !important;
            outline: none !important;
        }
        
        /* Input Labels */
        .stTextInput>label,
        .stTextArea>label,
        .stNumberInput>label,
        .stSelectbox>label {
            font-family: var(--font-sans) !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
            color: var(--text-muted) !important;
            margin-bottom: var(--space-2) !important;
        }
        
        /* ==========================================
           SELECT BOXES & DROPDOWNS
           ========================================== */
        
        .stSelectbox>div>div {
            background: white !important;
            border: 1px solid var(--border-light) !important;
            border-radius: 2px !important;
        }
        
        .stSelectbox>div>div:hover {
            border-color: var(--accent-gold) !important;
        }
        
        /* ==========================================
           DATA EDITOR / TABLE STYLING
           ========================================== */
        
        .stDataFrame {
            border: 1px solid var(--border-light) !important;
            border-radius: 4px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 8px rgba(26, 54, 93, 0.03) !important;
        }
        
        .stDataFrame thead tr th {
            background: var(--bg-ivory) !important;
            color: var(--text-muted) !important;
            font-family: var(--font-sans) !important;
            font-weight: 600 !important;
            font-size: 10px !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            padding: 14px 16px !important;
            border-bottom: 2px solid var(--border-light) !important;
        }
        
        .stDataFrame tbody tr td {
            font-family: var(--font-sans) !important;
            font-size: 14px !important;
            padding: 14px 16px !important;
            border-bottom: 1px solid var(--border-light) !important;
            color: var(--slate-900) !important;
        }
        
        .stDataFrame tbody tr:hover {
            background: rgba(197, 160, 89, 0.03) !important;
        }
        
        /* Amount columns */
        .stDataFrame tbody tr td:has(span:contains("$")),
        .stDataFrame tbody tr td:has(span:contains("-")) {
            font-family: var(--font-mono) !important;
            text-align: right !important;
            font-weight: 500 !important;
        }
        
        /* ==========================================
           METRICS & CARDS
           ========================================== */
        
        [data-testid="stMetricValue"] {
            font-family: var(--font-mono) !important;
            font-size: 36px !important;
            font-weight: 700 !important;
            color: var(--legal-blue) !important;
            letter-spacing: -1px !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-family: var(--font-sans) !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            color: var(--text-muted) !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 13px !important;
            font-weight: 500 !important;
        }
        
        div[data-testid="metric-container"] {
            background: white !important;
            border: 1px solid var(--border-light) !important;
            border-radius: 4px !important;
            padding: var(--space-6) !important;
            box-shadow: 0 2px 8px rgba(26, 54, 93, 0.03) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
        }
        
        div[data-testid="metric-container"]::before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 3px !important;
            background: var(--legal-blue) !important;
            opacity: 0.1 !important;
        }
        
        div[data-testid="metric-container"]:hover {
            box-shadow: 0 8px 20px rgba(26, 54, 93, 0.06) !important;
            transform: translateY(-2px) !important;
        }
        
        /* ==========================================
           SIDEBAR
           ========================================== */
        
        [data-testid="stSidebar"] {
            background: white !important;
            border-right: 1px solid var(--border-light) !important;
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            font-family: var(--font-sans) !important;
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            font-family: var(--font-serif) !important;
            color: var(--legal-blue) !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox>div>div {
            background: var(--bg-ivory) !important;
        }
        
        /* ==========================================
           ALERTS & NOTIFICATIONS
           ========================================== */
        
        .stSuccess {
            background: var(--success-bg) !important;
            color: #047857 !important;
            border-left: 4px solid var(--success-green) !important;
            border-radius: 2px !important;
            padding: var(--space-4) !important;
        }
        
        .stWarning {
            background: var(--warning-bg) !important;
            color: #B45309 !important;
            border-left: 4px solid var(--warning-amber) !important;
            border-radius: 2px !important;
            padding: var(--space-4) !important;
        }
        
        .stError {
            background: var(--danger-bg) !important;
            color: #B91C1C !important;
            border-left: 4px solid var(--danger-red) !important;
            border-radius: 2px !important;
            padding: var(--space-4) !important;
        }
        
        .stInfo {
            background: rgba(26, 54, 93, 0.05) !important;
            color: var(--legal-blue) !important;
            border-left: 4px solid var(--legal-blue) !important;
            border-radius: 2px !important;
            padding: var(--space-4) !important;
        }
        
        /* ==========================================
           SPINNERS & LOADING STATES
           ========================================== */
        
        .stSpinner>div {
            border-top-color: var(--accent-gold) !important;
        }
        
        /* ==========================================
           EXPANDER / ACCORDIONS
           ========================================== */
        
        .streamlit-expanderHeader {
            background: var(--bg-ivory) !important;
            border-radius: 2px !important;
            padding: var(--space-4) !important;
            font-family: var(--font-sans) !important;
            font-weight: 600 !important;
            color: var(--legal-blue) !important;
        }
        
        .streamlit-expanderHeader:hover {
            background: white !important;
            border-color: var(--accent-gold) !important;
        }
        
        /* ==========================================
           FILE UPLOADER
           ========================================== */
        
        [data-testid="stFileUploader"] {
            background: white !important;
            border: 2px dashed var(--border-light) !important;
            border-radius: 4px !important;
            padding: var(--space-8) !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: var(--accent-gold) !important;
            background: var(--bg-ivory) !important;
        }
        
        [data-testid="stFileUploader"] button {
            background: var(--legal-blue) !important;
            color: white !important;
            border-radius: 2px !important;
        }
        
        /* ==========================================
           TABS
           ========================================== */
        
        .stTabs [data-baseweb="tab-list"] {
            gap: var(--space-6) !important;
            border-bottom: 1px solid var(--border-light) !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-family: var(--font-sans) !important;
            font-weight: 500 !important;
            font-size: 13px !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            color: var(--text-muted) !important;
            padding: var(--space-4) var(--space-6) !important;
            border-radius: 0 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: transparent !important;
            color: var(--legal-blue) !important;
            border-bottom: 2px solid var(--accent-gold) !important;
            font-weight: 600 !important;
        }
        
        /* ==========================================
           PROGRESS BARS
           ========================================== */
        
        .stProgress>div>div>div {
            background: linear-gradient(90deg, var(--legal-blue), var(--accent-gold)) !important;
        }
        
        /* ==========================================
           CUSTOM BADGE CLASSES
           ========================================== */
        
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 2px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .badge-high {
            background: var(--danger-bg);
            color: var(--danger-red);
            border: 1px solid rgba(220, 38, 38, 0.2);
        }
        
        .badge-medium {
            background: var(--warning-bg);
            color: var(--warning-amber);
            border: 1px solid rgba(217, 119, 6, 0.2);
        }
        
        .badge-low {
            background: var(--success-bg);
            color: var(--success-green);
            border: 1px solid rgba(5, 150, 105, 0.2);
        }
        
        /* Card component */
        .card {
            background: white;
            border: 1px solid var(--border-light);
            border-radius: 4px;
            padding: var(--space-6);
            box-shadow: 0 2px 8px rgba(26, 54, 93, 0.03);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            box-shadow: 0 8px 20px rgba(26, 54, 93, 0.06);
            transform: translateY(-2px);
        }
        
        /* ==========================================
           RESPONSIVE DESIGN
           ========================================== */
        
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            [data-testid="stMetricValue"] {
                font-size: 28px !important;
            }
            
            .main h1 {
                font-size: 28px !important;
            }
            
            .main h2 {
                font-size: 22px !important;
            }
        }
        
        /* ==========================================
           ACCESSIBILITY
           ========================================== */
        
        button:focus,
        a:focus,
        input:focus,
        select:focus,
        textarea:focus {
            outline: 3px solid var(--accent-gold) !important;
            outline-offset: 2px !important;
        }
        
        ::selection {
            background: var(--accent-gold);
            color: white;
        }
        
    </style>
    """, unsafe_allow_html=True)


# Optional: Custom HTML components
def render_badge(text, variant="low"):
    """
    Render a styled badge.
    variant: 'high', 'medium', or 'low'
    """
    return f'<span class="badge badge-{variant}">{text}</span>'


def render_card(title, content, footer_buttons=None):
    """
    Render a card component.
    """
    card_html = f"""
    <div class="card">
        <h3 style="font-family: 'Playfair Display', serif; color: #1a365d; margin-bottom: 16px;">{title}</h3>
        <div>{content}</div>
        {f'<div style="margin-top: 16px;">{footer_buttons}</div>' if footer_buttons else ''}
    </div>
    """
    return card_html
