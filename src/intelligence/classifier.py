import pandas as pd
import json
import streamlit as st
import google.generativeai as genai
import logging
import time

# Prompts importu (Varsa kullan, yoksa fallback yap)
try:
    from src.intelligence.prompts import SYSTEM_INSTRUCTION, EXTRACTION_PROMPT
except ImportError:
    SYSTEM_INSTRUCTION = "Analyze strictly."
    EXTRACTION_PROMPT = "Extract transactions."

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionClassifier:
    """
    Semantic Brain Engine - AUTO-DISCOVERY MODE.
    Model ismini tahmin etmez, Google'dan "çalışan" modeli isteyip onu kullanır.
    """
    
    def __init__(self):
        self.api_key = st.secrets.get('GOOGLE_API_KEY')
        if not self.api_key:
            st.error("🚨 Critical: GOOGLE_API_KEY not found in secrets.toml")
            return

        try:
            # 1. Bağlantıyı Kur
            genai.configure(api_key=self.api_key)
            
            # 2. AUTO-DISCOVERY: Mevcut modelleri listele
            # Ezbere isim yazmak yerine, sunucuda ne varsa onu alacağız.
            all_models = list(genai.list_models())
            
            # 'generateContent' destekleyen modelleri filtrele
            generative_models = [
                m.name for m in all_models 
                if 'generateContent' in m.supported_generation_methods
            ]
            
            logger.info(f"Available Models: {generative_models}")
            
            # 3. Model Seçimi (Öncelik: Flash > Pro > Herhangi biri)
            # Senin ortamında adı ne geçiyorsa onu yakalayacak.
            target_model_name = None
            
            # Flash ara (gemini-1.5-flash, gemini-flash-latest vs.)
            for m in generative_models:
                if 'flash' in m.lower():
                    target_model_name = m
                    break
            
            # Flash yoksa Pro ara
            if not target_model_name:
                for m in generative_models:
                    if 'pro' in m.lower() and 'vision' not in m.lower():
                        target_model_name = m
                        break
            
            # Hiçbiri yoksa ilkini al
            if not target_model_name and generative_models:
                target_model_name = generative_models[0]
                
            if not target_model_name:
                raise ValueError("No generative models available for this API Key.")

            logger.info(f"🚀 SELECTED MODEL: {target_model_name}")
            self.model = genai.GenerativeModel(target_model_name)
            
        except Exception as e:
            logger.error(f"Gemini Init Error: {e}")
            st.error(f"AI Connection Failed: {e}")

    def extract_from_markdown(self, markdown_text: str) -> pd.DataFrame:
        if not markdown_text:
            return pd.DataFrame()

        prompt = f"""
        {EXTRACTION_PROMPT}
        
        DOCUMENT CONTENT (MARKDOWN):
        {markdown_text[:30000]}
        """
        
        try:
            # Prototip Mantığı
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            if not response.text:
                return pd.DataFrame()

            data = json.loads(response.text)
            
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict) and 'transactions' in data:
                 return pd.DataFrame(data['transactions'])
            else:
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"Extraction Failed: {str(e)}")
            return pd.DataFrame()

    def process_ledger_batches(self, df: pd.DataFrame, batch_size: int = 20) -> pd.DataFrame:
        if df.empty:
            return df
            
        # 0. Context Retrieval
        from src.audit_engine.audit_logic import AuditEngine
        audit_context = st.session_state.get('audit_context', {})
        state_code = audit_context.get('state_rules', 'PA')

        # 1. LAYER 1: SNIPER (Run Regex Rules)
        df = AuditEngine.run_sniper_logic(df)
        
        # 2. LAYER 2: AI (Smart Filtering)
        # Identify rows that still need analysis (Risk_Level is None or NaN)
        # Assuming Sniper fills Risk_Level for matches.
        
        results = []
        import math
        
        # Filter for AI candidates (Token Saver)
        # We need to map back to original indices, so we prefer iterating or filtering.
        # Let's iterate and skip.
        
        # Prepare list of indices that need AI
        ai_indices = []
        for idx, row in df.iterrows():
            r = row.get('Risk_Level')
            # Check if Risk_Level is set (High/Low). If None or empty, needs AI.
            if pd.isna(r) or str(r).strip() == '' or str(r) == 'None':
                 ai_indices.append(idx)
        
        num_items = len(ai_indices)
        num_batches = math.ceil(num_items / batch_size)
        
        progress_text = f"⚖️ Deep Audit: Analyzing {num_items} complex transactions ({len(df)-num_items} auto-cleared)..."
        progress_bar = st.progress(0, text=progress_text)

        for i in range(num_batches):
            start = i * batch_size
            end = min((i + 1) * batch_size, num_items)
            current_batch_indices = ai_indices[start:end]
            
            batch_items = []
            for idx in current_batch_indices:
                row = df.loc[idx]
                amt = 0.0
                try:
                    # FIX: Handle case-insensitive "amount" / "Amount"
                    val = row.get('amount') if 'amount' in row else row.get('Amount', 0)
                    raw = str(val).replace('$','').replace(',','')
                    amt = float(raw)
                except:
                     pass # handled

                batch_items.append({
                    "id": idx, # Keep original Index for merging
                    "date": str(row.get('Date', '')),
                    "amount": amt,
                    "description": str(row.get('Description', ''))
                })

            try:
                # 2.5 DYNAMIC PROMPT INJECTION (State-Awareness)
                # Fetch Rules
                from src.config.jurisdictions import MEDICAID_RULES
                rule = MEDICAID_RULES.get(state_code, MEDICAID_RULES['PA'])
                
                state_name_full = rule['name']
                threshold_val = rule['cash_threshold']
                
                # Dynamic Replacement
                # Base prompt says "Pennsylvania". We replace it.
                # Base prompt says "$500". We replace it.
                dynamic_system_prompt = SYSTEM_INSTRUCTION.replace("Pennsylvania", state_name_full)
                dynamic_system_prompt = dynamic_system_prompt.replace("$500", f"${threshold_val}")
                
                # Send to Gemini
                prompt = f"{dynamic_system_prompt}\nDATA: {json.dumps(batch_items)}"
                
                resp = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                
                # Extract confidence from Gemini response
                confidence_score = self._extract_confidence(resp)
                
                batch_result = json.loads(resp.text)
                
                if isinstance(batch_result, list):
                    # Add confidence to each result
                    for item in batch_result:
                        item['Confidence'] = confidence_score
                    results.extend(batch_result)
                elif isinstance(batch_result, dict) and 'results' in batch_result:
                    for item in batch_result['results']:
                        item['Confidence'] = confidence_score
                    results.extend(batch_result['results'])
                
                progress_bar.progress((i + 1) / num_batches)
                time.sleep(0.5) 
                
            except Exception as e:
                logger.error(f"Batch {i} Error: {e}")
                pass
        
        progress_bar.empty()
        
        # Merge AI Results
        df = self._merge_results(df, results)

        # 3. LAYER 3: JUDGE (De Minimis Aggregation)
        df = AuditEngine.run_judge_logic(df, state_code)
        
        return df

    def _extract_confidence(self, response) -> int:
        """
        Extract confidence score from Gemini API response.
        Returns: Confidence percentage (0-100)
        """
        try:
            # Method 1: Check if response has prompt_feedback
            if hasattr(response, 'prompt_feedback'):
                # Gemini doesn't directly provide confidence, so we infer from safety ratings
                # If content was blocked, confidence is low
                if hasattr(response.prompt_feedback, 'block_reason'):
                    return 50  # Low confidence if blocked
            
            # Method 2: Check candidates and finish_reason
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # If finish_reason is STOP (normal completion), high confidence
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = str(candidate.finish_reason)
                    if 'STOP' in finish_reason:
                        return 92  # High confidence for normal completion
                    elif 'MAX_TOKENS' in finish_reason:
                        return 75  # Medium confidence if truncated
                    else:
                        return 60  # Lower confidence for other reasons
                        
            # Default: assume reasonable confidence
            return 85
            
        except Exception as e:
            logger.warning(f"Could not extract confidence: {e}")
            return 80  # Default fallback
    
    def _merge_results(self, df, results):
        """
        AI sonuçlarını ana tablo ile birleştirir.
        """
        # ID'yi string/int karmaşasından kurtararak eşleştir
        result_map = {}
        for r in results:
            if 'id' in r:
                try:
                    result_map[int(r['id'])] = r
                except:
                    pass
        
        # Kolonları garantile (Confidence eklendi)
        for col in ['Category', 'Risk_Level', 'Forensic_Reasoning', 'Confidence']:
             if col not in df.columns: df[col] = None
        
        # Satır satır güncelle
        for idx, row in df.iterrows():
            if idx in result_map:
                r = result_map[idx]
                df.at[idx, 'Category'] = r.get('Category', 'Unidentified')
                df.at[idx, 'Risk_Level'] = r.get('Risk_Level', 'Low')
                df.at[idx, 'Forensic_Reasoning'] = r.get('Forensic_Reasoning', 'Analysis failed')
                df.at[idx, 'Confidence'] = r.get('Confidence', 80)  # Add confidence
        
        return df