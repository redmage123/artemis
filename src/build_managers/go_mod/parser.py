"""
Go Modules - go.mod Parser

WHY: Dedicated module for parsing go.mod files
RESPONSIBILITY: Extract module metadata from go.mod and go.sum files
PATTERNS: Parser pattern, regex-based extraction, guard clauses
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from artemis_exceptions import wrap_exception
from build_system_exceptions import ProjectConfigurationError
from .models import GoModuleInfo


class GoModParser:
    """
    WHY: Centralize all go.mod parsing logic
    RESPONSIBILITY: Parse and extract information from go.mod files
    PATTERNS: Single Responsibility, guard clauses
    """

    @staticmethod
    @wrap_exception(ProjectConfigurationError, "Failed to parse go.mod")
    def parse_go_mod(go_mod_path: Path, go_sum_path: Path) -> GoModuleInfo:
        """
        WHY: Extract structured data from go.mod file
        RESPONSIBILITY: Parse module path, version, dependencies, directives
        PATTERNS: Guard clause, regex parsing, factory method

        Args:
            go_mod_path: Path to go.mod file
            go_sum_path: Path to go.sum file

        Returns:
            GoModuleInfo with parsed data

        Raises:
            ProjectConfigurationError: If parsing fails
        """
        if not go_mod_path.exists():
            raise ProjectConfigurationError(
                "go.mod not found",
                {"path": str(go_mod_path)}
            )

        content = go_mod_path.read_text()

        module_path = GoModParser._extract_module_path(content)
        go_version = GoModParser._extract_go_version(content)
        dependencies = GoModParser._extract_dependencies(content)
        replace_directives = GoModParser._extract_replace_directives(content)
        exclude_directives = GoModParser._extract_exclude_directives(content)

        return GoModuleInfo(
            module_path=module_path,
            go_version=go_version,
            dependencies=dependencies,
            replace_directives=replace_directives,
            exclude_directives=exclude_directives,
            has_sum_file=go_sum_path.exists()
        )

    @staticmethod
    def _extract_module_path(content: str) -> str:
        """
        WHY: Extract module path from go.mod
        RESPONSIBILITY: Parse 'module' directive
        PATTERNS: Regex extraction with default fallback
        """
        module_match = re.search(r'module\s+(\S+)', content)
        return module_match.group(1) if module_match else ""

    @staticmethod
    def _extract_go_version(content: str) -> str:
        """
        WHY: Extract Go version from go.mod
        RESPONSIBILITY: Parse 'go' version directive
        PATTERNS: Regex extraction with sensible default
        """
        go_version_match = re.search(r'go\s+([\d.]+)', content)
        return go_version_match.group(1) if go_version_match else "1.21"

    @staticmethod
    def _extract_dependencies(content: str) -> Dict[str, str]:
        """
        WHY: Extract dependencies from require block
        RESPONSIBILITY: Parse dependency specifications
        PATTERNS: Regex extraction, dictionary comprehension
        """
        dependencies = {}

        # Parse require block
        require_block = re.search(r'require\s*\((.*?)\)', content, re.DOTALL)
        if not require_block:
            return dependencies

        for line in require_block.group(1).split('\n'):
            dep_match = re.match(r'\s*(\S+)\s+v([\d.]+(?:-[\w.]+)?)', line)
            if dep_match:
                dependencies[dep_match.group(1)] = f"v{dep_match.group(2)}"

        return dependencies

    @staticmethod
    def _extract_replace_directives(content: str) -> Dict[str, str]:
        """
        WHY: Extract module replacement directives
        RESPONSIBILITY: Parse 'replace' directives for local development
        PATTERNS: Regex extraction, dictionary mapping
        """
        replace_directives = {}

        for replace_match in re.finditer(r'replace\s+(\S+)\s+=>\s+(\S+)', content):
            replace_directives[replace_match.group(1)] = replace_match.group(2)

        return replace_directives

    @staticmethod
    def _extract_exclude_directives(content: str) -> List[str]:
        """
        WHY: Extract excluded module versions
        RESPONSIBILITY: Parse 'exclude' directives
        PATTERNS: Regex extraction, list comprehension
        """
        exclude_directives = []

        for exclude_match in re.finditer(r'exclude\s+(\S+)', content):
            exclude_directives.append(exclude_match.group(1))

        return exclude_directives
