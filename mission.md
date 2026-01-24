Lexmetrix (MDIP) - Project Constitution v2.5
1. Executive Vision
Lexmetrix is a computational legal defense engine for Elder Law attorneys. The Problem: "Unbillable hours" and high error rates in manual Medicaid intake/audits. The Solution: A "Shoebox" Bank Statement Auditor automating 60-month look-back periods using IBM Docling for parsing, Pandas for forensic data manipulation, and Gemini for semantic reasoning.

2. The Hybrid Intelligence Model
To eliminate "hallucinated math" and ensure legal defensibility, the agent MUST strictly decouple:

Semantic Layer (Probabilistic): Powered by Gemini 1.5 Flash. Interprets transaction descriptions (e.g., "Zelle to Grandson" -> Potential Gift) and assigns semantic risk tags.

Deterministic Layer (Exact): Powered by Pure Python & Pandas Logic. Handles all calculations, penalty durations, and asset tracking. LLMs are strictly forbidden from performing final legal arithmetic.

3. Critical Constraints & Security
Zero-Persistence Policy: Financial data must NEVER be stored on local disk. Processing occurs exclusively in-memory (RAM) using Pandas DataFrames stored in st.session_state or io.BytesIO streams.

Regulatory Truth: Systems must adhere to January 1, 2026, asset limit rules and state-specific daily penalty rates for CA, PA, FL, and NY.

Failure Protocol (Anti-Loop): If a parsing or logic task fails twice consecutively, the Agent MUST stop, create a search_log.md artifact detailing the error, and request human intervention. Do not blindly retry via loop.

4. Technical Stack (The Armoury)
Runtime: Python 3.11+

Ingestion: IBM Docling (TableFormerMode.ACCURATE) for PDF-to-Pandas conversion.

Data Processing: Pandas (for high-speed cleaning, filtering, and forensic audit trails).

Intelligence: Gemini 3 (Architecting) & Gemini 1.5 Flash (Batch classification).

UI: Streamlit + AgGrid (Directly connected to Pandas DataFrames).

5. Agent Operational Protocols (RAPS Framework)
Plan First: Every coding task must begin with an implementation_plan.md.

Skill Modularity: Build capabilities as independent, testable "Skills" within .agent/skills/.

Definition of Done (DoD): A task is considered complete ONLY when:

The code passes all unit tests in tests/.

No PII (Personally Identifiable Information) is saved to disk.

A validation summary (Artifact) is displayed in the Streamlit UI showing calculated values vs. expected results.

6. Project Geography (Structure)
/src/ingestion: Docling PDF parsers (Strictly functional, no logic).

/src/audit_engine: Pure Python/Pandas logic for 60-month look-back rules.

/src/ui: Streamlit components and dashboard layout.

.agent/skills: Specialized agent capabilities (e.g., calculate_penalty_period).

tests/: Pytest files mirroring the src/ structure for validation.
