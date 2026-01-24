import pandas as pd
from io import BytesIO
import logging
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.datamodel.base_models import InputFormat, DocumentStream

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoclingProcessor:
    """
    Handles PDF ingestion using IBM Docling.
    Uses export_to_markdown() for semantic analysis preparation.
    Zero-Persistence: Processes via in-memory DocumentStream.
    """
    def __init__(self):
        # Configure Pipeline Options for Forensic Accuracy (Strategy 2)
        self.pipeline_options = PdfPipelineOptions(do_table_structure=True)
        self.pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        self.pipeline_options.images_scale = 2.0 # 2x Resolution for better whitespace detection
        self.pipeline_options.table_structure_options.do_cell_matching = False # Prevent aggressive merging
        
        # Initialize Converter
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=self.pipeline_options)
            }
        )

    def process_pdf(self, file_stream: BytesIO, filename: str = "upload.pdf"):
        """
        Converts a PDF file stream into Markdown text AND extracted DataFrames.
        Returns: (markdown_text: str, tables: list[pd.DataFrame])
        """
        if not isinstance(file_stream, BytesIO):
            raise ValueError("Input must be a BytesIO stream.")

        try:
            # 1. Reset pointer (CRITICAL)
            file_stream.seek(0)
            
            # 2. Wrap buffer for Docling v2
            source = DocumentStream(name=filename, stream=file_stream)
            
            # 3. Convert (Using pre-configured forensic converter)
            logger.info(f"Docling: Converting {filename}...")
            doc = self.converter.convert(source)
            
            # 4. Export to Markdown (for text search/context)
            md_text = doc.document.export_to_markdown()
            
            # 5. Native Table Export with Forensic Enrichment
            tables = []
            for table in doc.document.tables:
                try:
                    df = table.export_to_dataframe()
                    if not df.empty:
                        # APPLY FORENSIC PIPELINE (Unfold -> Clean)
                        unfolded_dfs = self.unfold_table(df)
                        for sub_df in unfolded_dfs:
                            clean_df = self.clean_table(sub_df)
                            if not clean_df.empty:
                                tables.append(clean_df)
                except Exception as table_err:
                    logger.warning(f"Failed to export specific table: {table_err}")

            logger.info(f"Docling: Success ({len(md_text)} chars, {len(tables)} clean tables).")
            return md_text, tables

        except Exception as e:
            logger.error(f"Docling Processing Failed: {str(e)}", exc_info=True)
            raise e

    def unfold_table(self, df: pd.DataFrame) -> list[pd.DataFrame]:
        """
        Detects side-by-side tables (repeating headers) and splits them.
        Example: [Date | Amt || Date.1 | Amt.1] -> Stacked.
        """
        cols_lower = [str(c).lower() for c in df.columns]
        
        # Check for duplicate markers (.1, .2)
        if any('amount.1' in c for c in cols_lower) or any('date.1' in c for c in cols_lower):
            logger.info(f"Unfolding Side-by-Side Table: {df.shape}")
            from collections import defaultdict
            groups = defaultdict(list)
            
            for c in df.columns:
                parts = str(c).rsplit('.', 1)
                # Group by suffix (e.g. '1' for Date.1)
                if len(parts) == 2 and parts[1].isdigit():
                    suffix = parts[1]
                    groups[suffix].append(c)
                else:
                    groups['0'].append(c) # Base group
            
            sub_dfs = []
            for suffix, cols in groups.items():
                sub_df = df[cols].copy()
                # Rename back to base (Remove .1 regex-safe)
                sub_df.columns = [
                    c.rsplit('.', 1)[0] if '.' in c and c.rsplit('.', 1)[1].isdigit() else c 
                    for c in sub_df.columns
                ]
                sub_dfs.append(sub_df)
            return sub_dfs
        
        return [df]

    def clean_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes table format: String conversion, trimming, and Nuclear Deduplication.
        """
        # 1. String conversion
        df = df.astype(str).replace('nan', '').apply(lambda x: x.str.strip())
        
        # 2. Nuclear Deduplication (Resolves Index Ambiguity)
        if not df.columns.is_unique:
             cols = df.columns.tolist()
             counts = {}
             new_cols = []
             for col in cols:
                 col_str = str(col).strip()
                 cur_count = counts.get(col_str, 0)
                 if cur_count == 0: new_cols.append(col_str)
                 else: new_cols.append(f"{col_str}.{cur_count}")
                 counts[col_str] = cur_count + 1
             df.columns = new_cols
        
        # 3. Drop empty
        df = df.dropna(axis=1, how='all').dropna(axis=0, how='all')
        return df
