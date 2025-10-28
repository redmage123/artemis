#!/usr/bin/env python3
"""
WHY: Provide unified API for Jupyter notebook operations
RESPONSIBILITY: Export public interfaces from jupyter package
PATTERNS:
- Facade pattern for simplified API
- Explicit exports for clean namespace

Jupyter Notebook Handler for Artemis

This package provides comprehensive Jupyter notebook support including:
- Reading and writing .ipynb files
- Building notebooks programmatically
- Analyzing notebook content
- Pre-built templates for common workflows

SOLID Principles Applied:
- Single Responsibility: Each module has one clear purpose
- Open/Closed: Can add new cell types/formats without modifying existing code
- Liskov Substitution: All cell builders implement CellBuilderInterface
- Interface Segregation: Minimal, focused interfaces
- Dependency Inversion: Depends on abstractions, not concretions

Design Patterns:
- Builder Pattern: Fluent API for notebook construction
- Factory Pattern: CellFactory creates different cell types
- Strategy Pattern: Different output strategies (markdown, code, raw)
- Template Method: Base notebook structure with customizable cells

Performance Optimizations:
- O(1) cell type lookup using dict dispatch
- Single-pass notebook parsing
- Lazy cell rendering (only render when needed)
- Pre-compiled regex for code pattern matching
"""

# Core models
from .models import (
    NotebookCell,
    CellType,
    NotebookMetadata,
    VALID_CELL_TYPES,
    IMPORT_PATTERN,
    FUNCTION_PATTERN,
    CLASS_PATTERN,
    MATPLOTLIB_PATTERN
)

# Builders and factories
from .builders import (
    CellBuilderInterface,
    CodeCellBuilder,
    MarkdownCellBuilder,
    CellFactory
)

# I/O operations
from .parser import JupyterNotebookReader
from .writer import JupyterNotebookWriter

# High-level builders
from .notebook_builder import NotebookBuilder

# Templates
from .templates import (
    create_data_analysis_notebook,
    create_ml_notebook,
    create_exploratory_notebook
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

__version__ = '1.0.0'
