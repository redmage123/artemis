#!/usr/bin/env python3
"""
Fix RAGStorageHelper Imports Placement

This utility script ensures that RAGStorageHelper imports are properly placed
in pipeline stage files. It removes any existing imports and re-adds them in
the correct location after the last import statement.

Purpose:
    Corrects import statement placement to maintain consistent code style and
    ensure proper module initialization order across all pipeline stages.

Why This Exists:
    During refactoring, imports may end up in incorrect positions. This script
    automatically corrects their placement to follow Python best practices
    (all imports at the top, properly grouped).

Usage:
    python fix_imports.py

Affected Files:
    - stages/development_stage.py
    - stages/integration_stage.py
    - stages/testing_stage.py
    - requirements_stage.py
    - sprint_planning_stage.py
    - code_review_stage.py
    - uiux_stage.py
    - project_review_stage.py
"""

from pathlib import Path

# List of files to process
files = [
    'stages/development_stage.py',
    'stages/integration_stage.py',
    'stages/testing_stage.py',
    'requirements_stage.py',
    'sprint_planning_stage.py',
    'code_review_stage.py',
    'uiux_stage.py',
    'project_review_stage.py'
]

# Process each file
for filepath in files:
    """
    Process each file to fix import placement.

    Steps:
    1. Check if file exists (skip if missing)
    2. Read all lines from file
    3. Remove any existing RAGStorageHelper imports
    4. Find the last import statement
    5. Insert RAGStorageHelper import after last import
    6. Write corrected content back to file
    """
    path = Path(filepath)
    if not path.exists():
        continue

    # Read file contents
    with open(path, 'r') as f:
        lines = f.readlines()

    # Remove any existing RAGStorageHelper imports to avoid duplicates
    lines = [line for line in lines if 'from rag_storage_helper import' not in line]

    # Find last import line (where we should insert the new import)
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')) and 'rag_storage_helper' not in line:
            last_import_idx = i

    # Insert import after last import, maintaining proper formatting
    lines.insert(last_import_idx + 1, 'from rag_storage_helper import RAGStorageHelper\n')

    # Write corrected content back to file
    with open(path, 'w') as f:
        f.writelines(lines)

    print(f"Fixed {filepath}")

print("Done!")
