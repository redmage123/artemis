#!/usr/bin/env python3
"""
Local Filesystem Research Strategy

WHY: Implements research strategy for local filesystem, enabling discovery of code
examples from project files. Useful for finding existing patterns and examples within
the current codebase without making external API calls.

RESPONSIBILITY: Handles all local filesystem research operations:
- Search local directories for matching files
- Filter files by extension based on technology
- Calculate relevance scores based on query matches
- Convert file contents to ResearchExample objects

PATTERNS:
- Strategy Pattern: Concrete implementation of ResearchStrategy
- Guard Clause Pattern: Early returns for validation (max 1 level nesting)
- Dispatch Table Pattern: Technology to extension mapping via dictionary
- LRU Cache: Cache extension mapping for performance
"""

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from research.base_strategy import ResearchStrategy
from research.models import ResearchExample


class LocalExamplesResearchStrategy(ResearchStrategy):
    """
    Research strategy for local filesystem.

    Searches local directories for code examples matching the query and technologies.
    Uses file extensions to filter by language and content matching for relevance.
    """

    def __init__(self, search_paths: Optional[List[str]] = None, timeout_seconds: int = 30):
        """
        Initialize with search paths.

        Args:
            search_paths: Directories to search (default: current, src, examples)
            timeout_seconds: Timeout (not used for local search, but included for consistency)
        """
        super().__init__(timeout_seconds)
        self.search_paths = search_paths or [".", "src", "examples"]

    def get_source_name(self) -> str:
        """
        Get the name of this research source.

        Returns:
            Human-readable name "Local"
        """
        return "Local"

    def search(self, query: str, technologies: List[str], max_results: int = 5) -> List[ResearchExample]:
        """
        Search local filesystem for code examples.

        Args:
            query: Search query to match against filenames and paths
            technologies: List of technologies to determine file extensions
            max_results: Maximum results to return

        Returns:
            List of ResearchExample objects sorted by relevance score
        """
        # Guard clause: validate query
        if not query:
            return []

        # Get file extensions for technologies
        extensions = self._get_extensions_for_technologies(tuple(technologies))

        # Collect files from all search paths
        files = self._collect_files_from_paths(extensions)

        # Filter by query and create examples
        examples = self._create_matching_examples(files, query)

        # Sort by relevance and limit
        examples.sort(key=lambda x: x.relevance_score, reverse=True)
        return examples[:max_results]

    def _collect_files_from_paths(self, extensions: List[str]) -> List[Path]:
        """
        Collect files from all search paths.

        Args:
            extensions: File extensions to search for

        Returns:
            List of file Path objects
        """
        # Filter to valid paths (guard clause via list comprehension)
        valid_paths = [Path(path) for path in self.search_paths if Path(path).exists()]

        # Guard clause: return empty if no valid paths
        if not valid_paths:
            return []

        # Search each path (list comprehension - no nested loops)
        all_files = [
            self._find_files_in_path(path, extensions)
            for path in valid_paths
        ]

        # Flatten results (list comprehension)
        return [f for file_list in all_files for f in file_list]

    def _create_matching_examples(self, files: List[Path], query: str) -> List[ResearchExample]:
        """
        Create examples from files that match query.

        Args:
            files: List of file Path objects
            query: Search query string

        Returns:
            List of ResearchExample objects
        """
        # Filter matching files (list comprehension)
        matching_files = [f for f in files if self._file_matches_query(f, query)]

        # Convert to examples (list comprehension)
        return [self._create_example_from_file(f, query) for f in matching_files]

    @lru_cache(maxsize=128)
    def _get_extensions_for_technologies(self, technologies_tuple: tuple) -> List[str]:
        """
        Get file extensions for technologies.

        Uses LRU cache for performance on repeated calls.
        Uses dispatch table instead of if/elif chain.

        Args:
            technologies_tuple: Technologies as tuple (required for caching)

        Returns:
            List of file extensions (e.g., [".py", ".js"])
        """
        # Guard clause: default extensions if no technologies
        if not technologies_tuple:
            return [".py", ".js", ".java"]

        # Dispatch table: technology -> extensions mapping
        extension_map = {
            "python": [".py", ".ipynb"],
            "javascript": [".js", ".jsx", ".ts", ".tsx"],
            "java": [".java"],
            "rust": [".rs"],
            "go": [".go"],
            "ruby": [".rb"],
            "php": [".php"],
            "c++": [".cpp", ".hpp", ".cc", ".h"],
            "c": [".c", ".h"],
        }

        # Collect extensions for all technologies
        all_extensions = []
        for tech in technologies_tuple:
            tech_lower = tech.lower()
            # Use dispatch table, fallback to custom extension
            tech_extensions = extension_map.get(tech_lower, [f".{tech}"])
            all_extensions.extend(tech_extensions)

        # Return collected extensions or defaults
        return all_extensions if all_extensions else [".py", ".js", ".java"]

    def _find_files_in_path(self, path: Path, extensions: List[str]) -> List[Path]:
        """
        Find files with given extensions in path.

        Args:
            path: Directory Path object to search
            extensions: File extensions to find

        Returns:
            List of matching file Path objects (limited to 20 for performance)
        """
        # Guard clause: skip non-directories
        if not path.is_dir():
            return []

        # Use list comprehension with combined conditions (no nested loops)
        matching_files = [
            f for f in path.rglob("*")
            if f.is_file() and f.suffix in extensions
        ]

        # Limit results for performance
        return matching_files[:20]

    def _file_matches_query(self, file_path: Path, query: str) -> bool:
        """
        Check if file matches query.

        Args:
            file_path: File Path object
            query: Search query string

        Returns:
            True if filename or parent directory contains query (case-insensitive)
        """
        query_lower = query.lower()
        filename_match = query_lower in file_path.name.lower()
        path_match = query_lower in str(file_path.parent).lower()

        return filename_match or path_match

    def _create_example_from_file(self, file_path: Path, query: str) -> ResearchExample:
        """
        Create ResearchExample from file.

        Args:
            file_path: File Path object
            query: Search query for relevance calculation

        Returns:
            ResearchExample object with file content and metadata
        """
        try:
            # Read file content (limited to 5000 chars)
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:5000]

            # Calculate relevance score
            relevance = self._calculate_relevance(content, query)

            return ResearchExample(
                title=file_path.name,
                content=content,
                source="Local",
                url=str(file_path),
                language=file_path.suffix[1:] if file_path.suffix else "unknown",
                tags=[file_path.parent.name],
                relevance_score=relevance
            )

        except Exception:
            # Return empty example on error (don't fail entire search)
            return ResearchExample(
                title=file_path.name,
                content="",
                source="Local",
                url=str(file_path),
                language=file_path.suffix[1:] if file_path.suffix else "unknown",
                tags=[],
                relevance_score=0.0
            )

    def _calculate_relevance(self, content: str, query: str) -> float:
        """
        Calculate relevance score based on query matches.

        Args:
            content: File content string
            query: Search query string

        Returns:
            Relevance score between 0.0 and 1.0
        """
        # Guard clause: return 0 for empty content or query
        if not content or not query:
            return 0.0

        content_lower = content.lower()
        query_words = query.lower().split()

        # Guard clause: return 0 if no query words
        if not query_words:
            return 0.0

        # Count matches (list comprehension to sum)
        matches = sum(1 for word in query_words if word in content_lower)

        # Normalize to 0-1 range
        return matches / len(query_words)
