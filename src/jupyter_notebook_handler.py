#!/usr/bin/env python3
"""
WHY: Maintain backward compatibility with existing code
RESPONSIBILITY: Re-export all public APIs from jupyter package
PATTERNS:
- Facade pattern for unified interface
- Proxy pattern for transparent redirection

DEPRECATION NOTICE:
This module is a backward compatibility wrapper. All functionality has been
moved to the jupyter/ package for better modularity and maintainability.

New code should import directly from the jupyter package:
    from jupyter import NotebookBuilder, JupyterNotebookReader

This wrapper will be maintained for backward compatibility but may be
deprecated in future versions.

Original file: 775 lines
Refactored: Modular jupyter/ package with 6 focused modules
"""

# Re-export all public APIs from jupyter package for backward compatibility
from jupyter import (
    # Models
    NotebookCell,
    CellType,
    NotebookMetadata,
    VALID_CELL_TYPES,
    IMPORT_PATTERN,
    FUNCTION_PATTERN,
    CLASS_PATTERN,
    MATPLOTLIB_PATTERN,

    # Builders
    CellBuilderInterface,
    CodeCellBuilder,
    MarkdownCellBuilder,
    CellFactory,
    NotebookBuilder,

    # I/O
    JupyterNotebookReader,
    JupyterNotebookWriter,

    # Templates
    create_data_analysis_notebook,
    create_ml_notebook,
    create_exploratory_notebook,
)

__all__ = [
    # Models
    'NotebookCell',
    'CellType',
    'NotebookMetadata',
    'VALID_CELL_TYPES',
    'IMPORT_PATTERN',
    'FUNCTION_PATTERN',
    'CLASS_PATTERN',
    'MATPLOTLIB_PATTERN',

    # Builders
    'CellBuilderInterface',
    'CodeCellBuilder',
    'MarkdownCellBuilder',
    'CellFactory',
    'NotebookBuilder',

    # I/O
    'JupyterNotebookReader',
    'JupyterNotebookWriter',

    # Templates
    'create_data_analysis_notebook',
    'create_ml_notebook',
    'create_exploratory_notebook',
]
