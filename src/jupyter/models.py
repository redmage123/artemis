#!/usr/bin/env python3
"""
WHY: Define Jupyter notebook data models and cell types
RESPONSIBILITY: Provide immutable representations of notebook components
PATTERNS:
- Dataclass pattern for structured data
- Strategy pattern for cell type handling
- Template pattern for cell formatting

This module contains the core data structures used throughout the Jupyter
notebook handler. All cell types and notebook metadata are represented here.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class CellType(Enum):
    """Jupyter notebook cell types"""
    CODE = "code"
    MARKDOWN = "markdown"
    RAW = "raw"


# Performance: Pre-compiled regex patterns for code analysis
IMPORT_PATTERN = re.compile(r'^\s*(?:from|import)\s+', re.MULTILINE)
FUNCTION_PATTERN = re.compile(r'^\s*def\s+(\w+)\s*\(', re.MULTILINE)
CLASS_PATTERN = re.compile(r'^\s*class\s+(\w+)\s*[:(]', re.MULTILINE)
MATPLOTLIB_PATTERN = re.compile(
    r'(?:import|from)\s+matplotlib|plt\.(?:plot|show|figure)',
    re.MULTILINE
)

# Performance: O(1) cell type validation
VALID_CELL_TYPES = {ct.value for ct in CellType}


@dataclass
class NotebookCell:
    """
    WHY: Represent a single Jupyter notebook cell with type-safe structure
    RESPONSIBILITY: Store cell data and provide analysis capabilities

    Immutable representation of notebook content that can be easily
    serialized to/from Jupyter's JSON format.
    """
    cell_type: str
    source: List[str]  # Lines of code/text
    metadata: Dict[str, Any] = field(default_factory=dict)
    outputs: List[Dict] = field(default_factory=list)  # For code cells
    execution_count: Optional[int] = None  # For code cells

    def to_dict(self) -> Dict[str, Any]:
        """
        WHY: Convert cell to Jupyter notebook JSON format
        RESPONSIBILITY: Serialize cell for .ipynb file writing

        Returns:
            Dict matching Jupyter notebook cell schema
        """
        cell_dict = {
            "cell_type": self.cell_type,
            "metadata": self.metadata,
            "source": self.source
        }

        # Guard clause: Only add code-specific fields for code cells
        if self.cell_type != "code":
            return cell_dict

        cell_dict["execution_count"] = self.execution_count
        cell_dict["outputs"] = self.outputs
        return cell_dict

    def get_source_text(self) -> str:
        """
        WHY: Get cell source as single string for analysis
        RESPONSIBILITY: Join source lines into readable text

        Returns:
            Complete cell source as string
        """
        return ''.join(self.source)

    def analyze_code(self) -> Dict[str, Any]:
        """
        WHY: Analyze code cell content for insights
        RESPONSIBILITY: Extract code structure information
        PERFORMANCE: Single-pass analysis with pre-compiled regex - O(n)

        Returns:
            Dict with imports, functions, classes, plotting info
        """
        # Guard clause: Only analyze code cells
        if self.cell_type != "code":
            return {}

        source_text = self.get_source_text()

        # Single-pass analysis using pre-compiled patterns
        imports = IMPORT_PATTERN.findall(source_text)
        functions = FUNCTION_PATTERN.findall(source_text)
        classes = CLASS_PATTERN.findall(source_text)
        has_plotting = bool(MATPLOTLIB_PATTERN.search(source_text))

        return {
            "has_imports": bool(imports),
            "import_count": len(imports),
            "functions": functions,
            "classes": classes,
            "has_plotting": has_plotting,
            "line_count": len(self.source)
        }


@dataclass
class NotebookMetadata:
    """
    WHY: Store notebook-level metadata with defaults
    RESPONSIBILITY: Manage kernel and language configuration
    """
    kernelspec: Dict[str, str] = field(default_factory=lambda: {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    })
    language_info: Dict[str, Any] = field(default_factory=lambda: {
        "name": "python",
        "version": "3.8.0",
        "mimetype": "text/x-python",
        "codemirror_mode": {
            "name": "ipython",
            "version": 3
        }
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dict for JSON serialization"""
        return {
            "kernelspec": self.kernelspec,
            "language_info": self.language_info
        }
