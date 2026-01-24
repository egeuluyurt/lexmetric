# Logic Constraints & Decoupled Intelligence

## Core Principle
To eliminate "hallucinated math" and ensure legal defensibility, the system must strictly decouple semantic interpretation (Probabilistic) from calculation (Deterministic).

## The Constraints

### 1. Semantic Layer (Probabilistic)
*   **Role**: Interpretation & Classification.
*   **Engine**: Gemini 1.5 Flash.
*   **Allowed Actions**:
    *   Interpreting transaction descriptions (e.g., "Zelle to generic name" -> "Potential Gift").
    *   Extracting entities from text.
    *   Assigning risk tags (High, Medium, Low).
*   **FORBIDDEN Actions**:
    *   Summing amounts.
    *   Calculating dates.
    *   Determining penalty divisors.

### 2. Deterministic Layer (Exact)
*   **Role**: Calculation & Enforcement.
*   **Engine**: Pure Python / Pandas.
*   **Allowed Actions**:
    *   Filtering DataFrames by date range.
    *   Summing columns.
    *   Applying state-specific penalty divisors (e.g., $15,000 / $495).
    *   Managing `st.session_state`.

## Verification
*   Tests must verify that the "Total Penalty Period" is derived from a Python function, not an LLM response.
