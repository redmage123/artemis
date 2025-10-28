#!/usr/bin/env python3
"""
WHY: Jupyter Notebook parsing and content extraction.
RESPONSIBILITY: Extract and format code cells, markdown cells, and outputs from .ipynb files.
PATTERNS: Strategy pattern for output types, Guard clauses to avoid deep nesting.
"""

from typing import Dict, List, Optional, Callable, Any
from artemis_exceptions import DocumentReadError, wrap_exception
from jupyter_notebook_handler import JupyterNotebookReader


class JupyterParser:
    """
    WHY: Parse Jupyter notebooks into readable text format.
    RESPONSIBILITY: Extract cells, outputs, and metadata from notebook JSON structure.
    """

    def __init__(self, verbose: bool = False):
        """
        WHY: Initialize notebook parser.
        RESPONSIBILITY: Create JupyterNotebookReader instance.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.reader = JupyterNotebookReader()

    def is_available(self) -> bool:
        """
        WHY: Check if Jupyter parsing is available.
        RESPONSIBILITY: Return availability status.

        Returns:
            True (Jupyter parsing is always available)
        """
        return True

    def parse(self, file_path: str) -> str:
        """
        WHY: Parse Jupyter notebook file.
        RESPONSIBILITY: Extract and format all cells and metadata.

        Args:
            file_path: Path to .ipynb file

        Returns:
            Formatted text with cells and summary

        Raises:
            DocumentReadError: If parsing fails
        """
        try:
            notebook = self.reader.read_notebook(file_path)

            text_content: List[str] = []
            text_content.append("=" * 80)
            text_content.append("JUPYTER NOTEBOOK")
            text_content.append("=" * 80)
            text_content.append("")

            # Add kernel info if available
            metadata = notebook.get('metadata', {})
            kernelspec_info = self._format_kernelspec_info(metadata)
            if kernelspec_info:
                text_content.append(kernelspec_info)

            # Process all cells
            self._process_cells(notebook, text_content)

            # Add summary
            self._add_summary(notebook, text_content)

            return "\n".join(text_content)

        except Exception as e:
            raise wrap_exception(
                e,
                DocumentReadError,
                f"Error reading Jupyter notebook: {file_path}",
                context={"file_path": file_path}
            )

    def _format_kernelspec_info(self, metadata: Dict[str, Any]) -> str:
        """
        WHY: Extract kernel information from metadata.
        RESPONSIBILITY: Format kernelspec as readable string.

        Args:
            metadata: Notebook metadata dictionary

        Returns:
            Formatted kernel info or empty string
        """
        kernelspec = metadata.get('kernelspec', {})
        if not kernelspec:
            return ""

        kernel_name = kernelspec.get('display_name', kernelspec.get('name', 'Unknown'))
        return f"Kernel: {kernel_name}\n"

    def _convert_source_to_text(self, source: Any) -> str:
        """
        WHY: Normalize cell source to string.
        RESPONSIBILITY: Handle both list and string source formats.

        Args:
            source: Cell source (list or string)

        Returns:
            Source as text string
        """
        if isinstance(source, list):
            return ''.join(source)
        return str(source)

    def _process_cells(self, notebook: Dict[str, Any], text_content: List[str]) -> None:
        """
        WHY: Process all cells in the notebook.
        RESPONSIBILITY: Route cells to appropriate formatters based on type.

        Args:
            notebook: Notebook dictionary
            text_content: List to append formatted cells to
        """
        # Dispatch table for cell type handlers
        cell_formatters: Dict[str, Callable] = {
            'markdown': self._format_markdown_cell,
            'code': self._format_code_cell,
            'raw': self._format_raw_cell
        }

        cells = notebook.get('cells', [])
        for i, cell_data in enumerate(cells, 1):
            cell_type = cell_data.get('cell_type', 'unknown')
            source = cell_data.get('source', [])

            # Convert source to text
            source_text = self._convert_source_to_text(source)
            if not source_text.strip():
                continue

            # Get formatter for this cell type
            formatter = cell_formatters.get(cell_type)
            if not formatter:
                continue

            # Format cell (code cells need outputs)
            if cell_type == 'code':
                outputs = cell_data.get('outputs', [])
                formatter(i, source_text, outputs, text_content)
            else:
                formatter(i, source_text, text_content)

    def _format_markdown_cell(self, i: int, source_text: str, text_content: List[str]) -> None:
        """
        WHY: Format markdown cell for output.
        RESPONSIBILITY: Add markdown cell with header and separator.

        Args:
            i: Cell index
            source_text: Cell source text
            text_content: List to append to
        """
        text_content.append(f"[MARKDOWN CELL {i}]")
        text_content.append("-" * 40)
        text_content.append(source_text)
        text_content.append("")

    def _format_code_cell(self, i: int, source_text: str, outputs: List[Dict],
                          text_content: List[str]) -> None:
        """
        WHY: Format code cell with outputs.
        RESPONSIBILITY: Add code cell with header, source, and outputs.

        Args:
            i: Cell index
            source_text: Cell source text
            outputs: List of output dictionaries
            text_content: List to append to
        """
        text_content.append(f"[CODE CELL {i}]")
        text_content.append("-" * 40)
        text_content.append(source_text)

        self._process_cell_outputs(outputs, text_content)
        text_content.append("")

    def _format_raw_cell(self, i: int, source_text: str, text_content: List[str]) -> None:
        """
        WHY: Format raw cell for output.
        RESPONSIBILITY: Add raw cell with header and separator.

        Args:
            i: Cell index
            source_text: Cell source text
            text_content: List to append to
        """
        text_content.append(f"[RAW CELL {i}]")
        text_content.append("-" * 40)
        text_content.append(source_text)
        text_content.append("")

    def _process_cell_outputs(self, outputs: List[Dict], text_content: List[str]) -> None:
        """
        WHY: Process and format cell outputs.
        RESPONSIBILITY: Route outputs to appropriate handlers based on type.

        Args:
            outputs: List of output dictionaries
            text_content: List to append formatted outputs to
        """
        if not outputs:
            return

        text_content.append("")
        text_content.append("[OUTPUT]")

        # Dispatch table for output type handlers
        output_handlers: Dict[str, Callable] = {
            'stream': self._process_stream_output,
            'execute_result': self._process_data_output,
            'display_data': self._process_data_output,
            'error': self._process_error_output
        }

        for output in outputs:
            output_type = output.get('output_type', '')
            handler = output_handlers.get(output_type)

            if not handler:
                continue

            result = handler(output)
            if result:
                text_content.append(result)

    def _process_stream_output(self, output: Dict[str, Any]) -> str:
        """
        WHY: Process stream output type.
        RESPONSIBILITY: Extract and format stream text.

        Args:
            output: Output dictionary with stream data

        Returns:
            Formatted stream text
        """
        stream_text = output.get('text', [])
        if isinstance(stream_text, list):
            return ''.join(stream_text)
        return stream_text

    def _process_data_output(self, output: Dict[str, Any]) -> Optional[str]:
        """
        WHY: Process execute_result or display_data output.
        RESPONSIBILITY: Extract plain text from data output.

        Args:
            output: Output dictionary with data

        Returns:
            Formatted plain text or None if not available
        """
        data = output.get('data', {})
        if 'text/plain' not in data:
            return None

        plain_text = data['text/plain']
        if isinstance(plain_text, list):
            return ''.join(plain_text)
        return plain_text

    def _process_error_output(self, output: Dict[str, Any]) -> str:
        """
        WHY: Process error output type.
        RESPONSIBILITY: Format error name and value.

        Args:
            output: Output dictionary with error data

        Returns:
            Formatted error message
        """
        error_name = output.get('ename', 'Error')
        error_value = output.get('evalue', '')
        return f"{error_name}: {error_value}"

    def _add_summary(self, notebook: Dict[str, Any], text_content: List[str]) -> None:
        """
        WHY: Add notebook summary section.
        RESPONSIBILITY: Extract and format notebook statistics.

        Args:
            notebook: Notebook dictionary
            text_content: List to append summary to
        """
        summary = self.reader.get_notebook_summary(notebook)

        text_content.append("=" * 80)
        text_content.append("NOTEBOOK SUMMARY")
        text_content.append("=" * 80)
        text_content.append(f"Total Cells: {summary.get('total_cells', 0)}")
        text_content.append(f"Code Cells: {summary.get('code_cells', 0)}")
        text_content.append(f"Markdown Cells: {summary.get('markdown_cells', 0)}")
        text_content.append(f"Total Code Lines: {summary.get('total_code_lines', 0)}")

        # Add optional items
        functions = summary.get('functions_defined', [])
        if functions:
            text_content.append(f"Functions Defined: {', '.join(functions)}")

        classes = summary.get('classes_defined', [])
        if classes:
            text_content.append(f"Classes Defined: {', '.join(classes)}")

        text_content.append("=" * 80)
