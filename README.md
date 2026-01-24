# ⚖️ LexMetric - Premium Medicaid Audit Defense Platform

AI-powered forensic analysis platform for Medicaid audit defense attorneys. Transform complex financial records into actionable legal defense with premium Bespoke Luxury design.

## 🚀 Features

### Core Capabilities
- **AI-Powered Risk Detection**: Gemini-based forensic analysis of transactions
- **Multi-Format Ingestion**: PDF (Docling OCR), Excel (.xlsx), CSV
- **Smart Data Processing**: Auto-detection of debits/credits, date normalization, column mapping
- **Interactive Case Workspace**: Transaction table with risk levels, attorney notes, audit flags
- **Professional Reports**: Trial-ready DOCX with charts, tables, and attorney certification
- **Dashboard**: Case history grid with search and metadata

### Premium UI/UX
- **Bespoke Luxury Design System**:
  - Playfair Display (serif headings)
  - Inter (body text)
  - JetBrains Mono (financial data)
  - Cream paper texture background
  - Gold accent colors (#C5A059)
  - Legal blue primary (#1a365d)

### Technical Stack
- **Backend**: Python 3.x
- **Frontend**: Streamlit
- **AI**: Google Gemini 1.5 Pro/Flash
- **PDF Processing**: Docling, pdfplumber
- **Data**: pandas, numpy
- **Reports**: python-docx, docx-mailmerge

## 📦 Installation

### Prerequisites
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup
Create `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "your-gemini-api-key"
```

Get your API key: https://aistudio.google.com/app/apikey

## 🎯 Usage

### Start Application
```bash
streamlit run src/ui/app.py --server.port=8501
```

Open browser: `http://localhost:8501`

### Workflow
1. **Select View Mode**: Dashboard (history) or New Case (upload)
2. **Enter Client Info**: Name and jurisdiction (state)
3. **Upload Files**: PDF bank statements or Excel/CSV ledgers
4. **Review Analysis**: AI-flagged high-risk transactions
5. **Annotate**: Add attorney notes, adjust risk levels
6. **Export Report**: Download professional DOCX for trial

## 📁 Project Structure

```
lexmetric/
├── src/
│   ├── ui/                  # Streamlit interface
│   │   ├── app.py          # Main application
│   │   ├── dashboard.py    # Case history
│   │   ├── cockpit.py      # Transaction workspace
│   │   └── styles.py       # Premium CSS
│   ├── ingestion/          # Data processing
│   │   ├── docling_processor.py
│   │   └── excel_processor.py
│   ├── intelligence/       # AI analysis
│   │   ├── classifier.py
│   │   └── prompts.py
│   ├── audit_engine/       # Risk logic
│   │   └── audit_logic.py
│   ├── reporting/          # DOCX generation
│   │   └── generator.py
│   └── config/             # Medicaid rules
│       └── jurisdictions.py
├── mockups/                # Premium HTML prototypes
│   ├── public/            # Landing, login
│   └── app/               # Dashboard, workspace, settings
├── tests/                  # Unit tests
└── requirements.txt
```

## 🧪 Testing

```bash
pytest tests/
```

## 🎨 Design System

### Colors
- **Legal Blue**: `#1a365d` (primary)
- **Accent Gold**: `#C5A059` (highlights)
- **Ivory Background**: `#FDFCFB`
- **Slate Text**: `#1E293B`

### Typography
- **Headings**: Playfair Display (700/900)
- **Body**: Inter (400/500/600)
- **Financial**: JetBrains Mono (500/600)

## 📊 Medicaid Rules Supported

- New York (Monthly divisor: $15,150)
- Pennsylvania (Monthly divisor: $482.50)
- California (Monthly divisor: $11,576)
- Florida (Monthly divisor: $10,809)
- Texas (Daily divisor: $242.60)
- Ohio (Monthly divisor: $7,453)
- New Jersey (Monthly divisor: $14,785)

## 🔒 Security

- No data stored externally (local processing only)
- Case history saved to `~/.lexmetric/cases.json`
- Secrets managed via Streamlit secrets.toml
- No client data in version control (.gitignore configured)

## 📝 License

Proprietary - All rights reserved

## 👤 Author

Ege Uluyurt (@egeuluyurt)

## 🙏 Acknowledgments

- Google Gemini API for AI analysis
- Docling for PDF OCR
- Streamlit for rapid UI development
