import os
import pytest

# Forbidden extensions that often contain PII or financial data
FORBIDDEN_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.pdf', '.json'}
# Allowed directories for sensitive files (if any, e.g., specifically marked test data)
ALLOWED_DIRECTORIES = {'tests/data', 'tests/fixtures', '.agent'}

def is_allowed_path(path):
    """Check if the path is in an allowed directory."""
    for allowed in ALLOWED_DIRECTORIES:
        if allowed in path:
            return True
    return False

def test_zero_persistence_policy():
    """
    Enforce Zero-Persistence Policy:
    Scan the codebase to ensure no financial data files (CSV, Excel, PDF) 
    are stored on the local disk, violating the in-memory only rule.
    """
    project_root = os.getcwd()
    violating_files = []

    for root, dirs, files in os.walk(project_root):
        # Skip hidden directories like .git, .gemini
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        rel_root = os.path.relpath(root, project_root)
        
        # Skip allowed directories
        if is_allowed_path(rel_root):
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in FORBIDDEN_EXTENSIONS:
                # specific exceptions can be added here (e.g., package.json is okay)
                if file == 'package.json' or file == 'tsconfig.json':
                    continue
                violating_files.append(os.path.join(rel_root, file))

    assert not violating_files, f"Zero-Persistence Violation! Found data files on disk: {violating_files}"
