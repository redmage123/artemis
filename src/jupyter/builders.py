#!/usr/bin/env python3
"""
WHY: Provide fluent API for building notebook cells
RESPONSIBILITY: Implement builder pattern for cell construction
PATTERNS:
- Builder pattern for complex object creation
- Factory pattern for cell type dispatch
- Interface segregation for cell builders

This module implements the Builder and Factory patterns to create notebook
cells with a clean, fluent API. Dispatch tables eliminate if/elif chains.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union

from .models import NotebookCell, CellType, VALID_CELL_TYPES


class CellBuilderInterface(ABC):
    """
    WHY: Define contract for all cell builders
    RESPONSIBILITY: Ensure consistent builder API
    """

    @abstractmethod
    def build(self) -> NotebookCell:
        """Build and return the cell"""
        pass


class CodeCellBuilder(CellBuilderInterface):
    """
    WHY: Build code cells with fluent API
    RESPONSIBILITY: Construct code cells with metadata and outputs
    PATTERN: Builder pattern for complex object construction
    """

    def __init__(self, source: Union[str, List[str]]):
        """
        WHY: Initialize code cell builder with flexible source input
        RESPONSIBILITY: Normalize source to line-based format

        Args:
            source: Code as string or list of lines
        """
        # Guard clause: Handle list source early
        if not isinstance(source, str):
            self.source = source
            self._init_defaults()
            return

        # Process string source - split into lines preserving newlines
        # WHY: Jupyter format requires line-based source with newlines
        self.source = [
            line + '\n' if not line.endswith('\n') else line
            for line in source.splitlines()
        ]

        # Guard clause: Handle empty source early
        if not self.source:
            self._init_defaults()
            return

        # Ensure last line has newline
        if not self.source[-1].endswith('\n'):
            self.source[-1] += '\n'

        self._init_defaults()

    def _init_defaults(self) -> None:
        """Initialize default values for optional fields"""
        self.metadata = {}
        self.outputs = []
        self.execution_count = None

    def with_metadata(self, metadata: Dict[str, Any]) -> 'CodeCellBuilder':
        """
        WHY: Add metadata to cell via fluent API
        RESPONSIBILITY: Update cell metadata

        Args:
            metadata: Metadata dict to merge

        Returns:
            Self for method chaining
        """
        self.metadata.update(metadata)
        return self

    def with_execution_count(self, count: int) -> 'CodeCellBuilder':
        """
        WHY: Set execution count for code cell
        RESPONSIBILITY: Track cell execution order

        Args:
            count: Execution sequence number

        Returns:
            Self for method chaining
        """
        self.execution_count = count
        return self

    def with_output(self, output: Dict[str, Any]) -> 'CodeCellBuilder':
        """
        WHY: Add output to code cell
        RESPONSIBILITY: Store cell execution results

        Args:
            output: Output dict from cell execution

        Returns:
            Self for method chaining
        """
        self.outputs.append(output)
        return self

    def build(self) -> NotebookCell:
        """
        WHY: Construct final NotebookCell instance
        RESPONSIBILITY: Create immutable cell from builder state

        Returns:
            Complete NotebookCell
        """
        return NotebookCell(
            cell_type=CellType.CODE.value,
            source=self.source,
            metadata=self.metadata,
            outputs=self.outputs,
            execution_count=self.execution_count
        )


class MarkdownCellBuilder(CellBuilderInterface):
    """
    WHY: Build markdown cells with fluent API
    RESPONSIBILITY: Construct markdown cells with metadata
    PATTERN: Builder pattern for object construction
    """

    def __init__(self, source: Union[str, List[str]]):
        """
        WHY: Initialize markdown cell builder with flexible source input
        RESPONSIBILITY: Normalize source to line-based format

        Args:
            source: Markdown as string or list of lines
        """
        # Guard clause: Handle list source early
        if not isinstance(source, str):
            self.source = source
            self.metadata = {}
            return

        # Process string source - split into lines preserving newlines
        # WHY: Jupyter format requires line-based source with newlines
        self.source = [
            line + '\n' if not line.endswith('\n') else line
            for line in source.splitlines()
        ]

        # Guard clause: Handle empty source early
        if not self.source:
            self.metadata = {}
            return

        # Ensure last line has newline
        if not self.source[-1].endswith('\n'):
            self.source[-1] += '\n'

        self.metadata = {}

    def with_metadata(self, metadata: Dict[str, Any]) -> 'MarkdownCellBuilder':
        """
        WHY: Add metadata to cell via fluent API
        RESPONSIBILITY: Update cell metadata

        Args:
            metadata: Metadata dict to merge

        Returns:
            Self for method chaining
        """
        self.metadata.update(metadata)
        return self

    def build(self) -> NotebookCell:
        """
        WHY: Construct final NotebookCell instance
        RESPONSIBILITY: Create immutable cell from builder state

        Returns:
            Complete NotebookCell
        """
        return NotebookCell(
            cell_type=CellType.MARKDOWN.value,
            source=self.source,
            metadata=self.metadata
        )


class CellFactory:
    """
    WHY: Create cell builders using factory pattern
    RESPONSIBILITY: Dispatch to appropriate builder based on cell type
    PATTERN: Factory pattern with dispatch table
    PERFORMANCE: O(1) cell type dispatch
    """

    # Performance: Dict dispatch for O(1) builder lookup
    _BUILDERS: Dict[str, type] = {
        CellType.CODE.value: CodeCellBuilder,
        CellType.MARKDOWN.value: MarkdownCellBuilder
    }

    @staticmethod
    def create_cell(
        cell_type: str,
        source: Union[str, List[str]]
    ) -> CellBuilderInterface:
        """
        WHY: Create cell builder of specified type without if/elif chains
        RESPONSIBILITY: Validate type and instantiate correct builder
        PERFORMANCE: O(1) validation and lookup using dict dispatch

        Args:
            cell_type: Type of cell (code, markdown, raw)
            source: Cell source content

        Returns:
            Appropriate cell builder

        Raises:
            ValueError: If cell type is invalid
        """
        # Guard clause: Validate cell type early (O(1) set membership check)
        if cell_type not in VALID_CELL_TYPES:
            raise ValueError(
                f"Invalid cell type: {cell_type}. "
                f"Must be one of {VALID_CELL_TYPES}"
            )

        # Strategy pattern: O(1) builder lookup using dict dispatch
        builder_class = CellFactory._BUILDERS.get(cell_type)

        # Guard clause: Handle missing builder early
        if not builder_class:
            # Fallback for raw cells (simple, no builder needed)
            # WHY: Raw cells are rare, treat as markdown for simplicity
            return MarkdownCellBuilder(source)

        return builder_class(source)
