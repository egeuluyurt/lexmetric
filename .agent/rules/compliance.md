# Zero-Persistence Policy

## Core Principle
Financial data used within Lexmetrix (MDIP) must **NEVER** be persisted to the local filesystem (disk). All processing of sensitive user data must occur strictly in-memory (RAM).

## Rules
1.  **Forbidden I/O**: No writing of `*.csv`, `*.xlsx`, `*.pdf`, or `*.json` files containing financial transaction data or PII.
2.  **Allowed Streams**: File uploads and downloads must be handled via `io.BytesIO` streams or `st.session_state`.
3.  **Exceptions**:
    *   System configuration files (that contain no PII).
    *   `search_log.md` artifacts (containing generic error logs, no specific user financial values).
    *   Test fixtures located in `tests/data` (which must be dummy/synthetic data).

## Enforcement
*   **Static Analysis**: `tests/test_security_protocols.py` scans the filesystem for forbidden extensions in non-allowed directories.
*   **Runtime Checks**: The `SessionManager` class manages data states in memory.
