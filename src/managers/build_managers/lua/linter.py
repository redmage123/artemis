"""
Module: linter.py

WHY: Provides static analysis and linting for Lua code using luacheck
RESPONSIBILITY: Run luacheck, parse results, report code quality issues
PATTERNS: Strategy Pattern (different output parsers), Guard Clauses
"""

import subprocess
import re
from typing import Dict, Any, Tuple
from pathlib import Path


class LuaLinter:
    """
    Runs luacheck static analyzer on Lua code.

    WHY: Luacheck detects globals, unused variables, style violations
    RESPONSIBILITY: Execute linter, parse output, provide quality metrics
    """

    def __init__(self, project_path: Path, logger):
        """
        Initialize linter.

        Args:
            project_path: Root directory of Lua project
            logger: ArtemisLogger instance
        """
        self.project_path = project_path
        self.logger = logger

    def lint(self) -> Dict[str, Any]:
        """
        Run luacheck static analyzer.

        WHY: Catches errors, enforces coding standards, detects unused vars

        Returns:
            Dict with success, errors, warnings, files_checked, message
        """
        if not self._is_luacheck_available():
            self.logger.warning("⚠️  luacheck not found, skipping linting")
            return {
                "success": False,
                "errors": 0,
                "warnings": 0,
                "files_checked": 0,
                "message": "luacheck not installed"
            }

        self.logger.info("🔍 Running luacheck linter...")

        try:
            result = subprocess.run(
                ["luacheck", ".", "--formatter", "plain"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )

            # luacheck returns non-zero if issues found
            errors, warnings, files_checked = self._parse_output(result.stdout)

            success = errors == 0

            if success:
                self.logger.info(f"✅ No errors found ({warnings} warnings in {files_checked} files)")
            else:
                self.logger.warning(f"⚠️  Found {errors} errors, {warnings} warnings")

            return {
                "success": success,
                "errors": errors,
                "warnings": warnings,
                "files_checked": files_checked,
                "message": f"{errors} errors, {warnings} warnings in {files_checked} files"
            }

        except Exception as e:
            self.logger.error(f"❌ Linting failed: {e}")
            return {
                "success": False,
                "errors": 0,
                "warnings": 0,
                "files_checked": 0,
                "message": f"Linting error: {e}"
            }

    def _parse_output(self, output: str) -> Tuple[int, int, int]:
        """
        Parse luacheck output for error/warning counts.

        WHY: Extract structured metrics from text output

        Args:
            output: Luacheck stdout

        Returns:
            Tuple of (errors, warnings, files_checked)
        """
        # Try summary line: "Total: 3 warnings / 1 error in 5 files"
        match = re.search(r'Total:\s+(\d+)\s+warnings?\s+/\s+(\d+)\s+errors?\s+in\s+(\d+)\s+files?', output)

        if match:
            warnings = int(match.group(1))
            errors = int(match.group(2))
            files_checked = int(match.group(3))
            return errors, warnings, files_checked

        # Fallback: count individual issues
        errors = output.count("(E)")
        warnings = output.count("(W)")
        files_checked = len([line for line in output.split('\n') if line.strip().endswith('.lua')])

        return errors, warnings, files_checked

    def _is_luacheck_available(self) -> bool:
        """
        Check if luacheck is available.

        Returns:
            True if luacheck command exists
        """
        try:
            subprocess.run(
                ["which", "luacheck"],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
