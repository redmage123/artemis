"""
Module: agents/developer/file_manager.py

WHY: Centralize all file I/O operations for the developer agent.
RESPONSIBILITY: Read and write implementation files, test files, and examples.
PATTERNS: Guard Clauses (early returns), Single Responsibility.

This module handles:
- Writing implementation files to disk
- Writing test files to disk
- Reading developer prompts from files
- Loading example HTML slides for reference
- Creating directory structures

EXTRACTED FROM: standalone_developer_agent.py (lines 1204-2620)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from artemis_stage_interface import LoggerInterface
from artemis_exceptions import FileReadError, create_wrapped_exception


class FileManager:
    """
    Manages file I/O operations for developer agent

    WHY: Centralize file operations with consistent error handling
    PATTERNS: Guard Clauses, Single Responsibility
    """

    def __init__(self, logger: Optional[LoggerInterface] = None):
        """
        Initialize file manager

        Args:
            logger: Optional logger for file operation logging
        """
        self.logger = logger

    def write_implementation_files(
        self,
        implementation: Dict,
        output_dir: Path
    ) -> List[str]:
        """
        Write implementation and test files to disk

        Args:
            implementation: Dict with 'implementation_files' and 'test_files' keys
            output_dir: Directory to write files to

        Returns:
            List of file paths written
        """
        files_written = []

        # Write implementation files
        impl_files = implementation.get("implementation_files", [])
        files_written.extend(self._write_files(impl_files, output_dir, "Wrote"))

        # Write test files
        test_files = implementation.get("test_files", [])
        files_written.extend(self._write_files(test_files, output_dir, "Wrote"))

        return files_written

    def write_test_files(self, test_files: List[Dict], output_dir: Path) -> List[str]:
        """
        Write test files to disk

        Args:
            test_files: List of dicts with 'path' and 'content' keys
            output_dir: Directory to write tests to

        Returns:
            List of file paths written
        """
        return self._write_files(test_files, output_dir, "Wrote test")

    def write_implementation_only(self, impl_files: List[Dict], output_dir: Path) -> List[str]:
        """
        Write implementation files to disk (not tests)

        Handles absolute paths from LLM by extracting just the filename.

        Args:
            impl_files: List of dicts with 'path' and 'content' keys
            output_dir: Directory to write files to

        Returns:
            List of file paths written
        """
        files_written = []

        for file_info in impl_files:
            # Extract just the filename (handle absolute paths from LLM)
            raw_path = file_info["path"]
            filename = Path(raw_path).name if raw_path.startswith('/') else raw_path

            file_path = output_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w') as f:
                f.write(file_info["content"])

            files_written.append(str(file_path))

            if self.logger:
                self.logger.log(f"  ✅ Wrote: {file_path}", "INFO")

        return files_written

    def _write_files(
        self,
        file_list: List[Dict],
        output_dir: Path,
        log_prefix: str
    ) -> List[str]:
        """
        Internal helper to write files to disk

        Args:
            file_list: List of dicts with 'path' and 'content' keys
            output_dir: Directory to write to
            log_prefix: Prefix for log messages

        Returns:
            List of file paths written
        """
        files_written = []

        for file_info in file_list:
            file_path = output_dir / file_info["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w') as f:
                f.write(file_info["content"])

            files_written.append(str(file_path))

            if self.logger:
                self.logger.log(f"  ✅ {log_prefix}: {file_path}", "INFO")

        return files_written

    def read_developer_prompt(self, prompt_file: str) -> str:
        """
        Read developer prompt from file

        Args:
            prompt_file: Path to prompt file

        Returns:
            Prompt content or default prompt
        """
        try:
            with open(prompt_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            if self.logger:
                self.logger.log(f"⚠️  Prompt file not found: {prompt_file}, using default", "WARNING")
            return self._get_default_developer_prompt()

    def load_example_slides(self, adr_content: str) -> Optional[str]:
        """
        Load example HTML slide presentations to use as reference.

        WHY: Provides high-quality reference examples to guide LLM code generation.
        PATTERNS: Early return pattern (guard clauses), functional composition.
        PERFORMANCE: Reads only first 500 lines to limit memory usage.

        Args:
            adr_content: ADR content to parse for example file path

        Returns:
            Formatted example slides content or None

        Raises:
            FileReadError: If file reading fails (wrapped, non-blocking)
        """
        try:
            # Extract example file path from ADR
            example_file_path = self._extract_example_path(adr_content)

            # Guard: no example path found
            if not example_file_path:
                if self.logger:
                    self.logger.log("No example file specified in ADR", "INFO")
                return None

            example_file = Path(example_file_path)

            # Guard: example file doesn't exist
            if not example_file.exists():
                if self.logger:
                    self.logger.log(f"⚠️  Example file not found: {example_file}", "WARNING")
                return None

            # Read first 500 lines of example (enough to show structure/styling)
            with open(example_file, 'r') as f:
                lines = f.readlines()[:500]
                example_content = ''.join(lines)

            example_text = self._format_example_slides(example_file, example_content)

            if self.logger:
                self.logger.log(f"✅ Loaded example slides from: {example_file}", "INFO")

            return example_text

        except Exception as e:
            if self.logger:
                self.logger.log(f"⚠️  Error loading example slides: {e}", "WARNING")

            # Don't raise, just log and return None - example slides are optional
            # But wrap the exception for proper context tracking
            wrapped_exception = create_wrapped_exception(
                e,
                FileReadError,
                f"Failed to load example slides from ADR",
                {"adr_length": len(adr_content)}
            )

            if self.logger:
                self.logger.log(f"Details: {wrapped_exception}", "DEBUG")

            return None

    def _extract_example_path(self, adr_content: str) -> Optional[str]:
        """
        Extract example file path from ADR content

        Args:
            adr_content: ADR content to parse

        Returns:
            Example file path or None
        """
        example_patterns = [
            r'Example:\s*([/\w.-]+\.html)',
            r'Reference:\s*([/\w.-]+\.html)',
            r'Template:\s*([/\w.-]+\.html)',
            r'example file:\s*([/\w.-]+\.html)',
            r'reference file:\s*([/\w.-]+\.html)',
        ]

        # Find first matching pattern (early termination on match)
        matches = (re.search(pattern, adr_content, re.IGNORECASE) for pattern in example_patterns)
        return next((m.group(1) for m in matches if m), None)

    def _format_example_slides(self, example_file: Path, example_content: str) -> str:
        """
        Format example slides content with instructions

        Args:
            example_file: Path to example file
            example_content: Example file content

        Returns:
            Formatted example text
        """
        return f"""
# REFERENCE EXAMPLE: High-Quality HTML Slide Presentation

Below is a COMPLETE example of a professional HTML slide presentation that meets our quality standards.
Study this example carefully - your implementation should match this level of quality and completeness.

Example source: {example_file}

Key features to replicate:
- Complete HTML structure with embedded CSS and JavaScript
- Glassmorphism styling (backdrop-filter, transparency)
- Smooth slide transitions with animations
- Navigation controls (Previous/Next buttons)
- Keyboard navigation support (arrow keys, space)
- Auto-advance functionality (8 seconds per slide)
- Slide counter (e.g., "1/7")
- Responsive design
- Professional gradient backgrounds
- Multiple complete slides (not just 1!)

```html
{example_content}
... (truncated for brevity, but your implementation should be COMPLETE)
```

**CRITICAL**: Your implementation must be COMPLETE like this example, not a partial prototype!
"""

    def _get_default_developer_prompt(self) -> str:
        """
        Get default developer prompt

        Returns:
            Default prompt string
        """
        return """You are an expert software developer. Generate high-quality, production-ready code."""


__all__ = [
    "FileManager"
]
