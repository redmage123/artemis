"""
Module: agents/developer/test_runner_wrapper.py

WHY: Wrap universal TestRunner for developer agent use.
RESPONSIBILITY: Execute tests and return structured results.
PATTERNS: Adapter Pattern, Guard Clauses.

This module handles:
- Running tests using universal TestRunner
- Auto-detecting test frameworks (pytest, unittest, gtest, junit)
- Returning structured test results
- Error handling and fallback

EXTRACTED FROM: standalone_developer_agent.py (lines 2622-2685)
"""

from pathlib import Path
from typing import Dict, Optional
from artemis_stage_interface import LoggerInterface


class DeveloperTestRunner:
    """
    Wrapper around universal TestRunner for developer agent

    WHY: Isolate test execution with clean error handling
    PATTERNS: Adapter Pattern, Guard Clauses
    """

    def __init__(self, logger: Optional[LoggerInterface] = None):
        """
        Initialize test runner wrapper

        Args:
            logger: Optional logger for test execution logging
        """
        self.logger = logger

    def run_tests(self, output_dir: Path, framework: str = None) -> Dict:
        """
        Run tests using universal TestRunner (supports multiple frameworks).

        Args:
            output_dir: Directory containing tests
            framework: Test framework to use (auto-detected if None)
                      Options: pytest, unittest, gtest, junit

        Returns:
            Dict with test results
        """
        from test_runner import TestRunner

        test_path = output_dir / "tests"

        # Guard: no tests directory
        if not test_path.exists():
            if self.logger:
                self.logger.log("⚠️  No tests directory found", "WARNING")
            return self._empty_result()

        try:
            # Use universal TestRunner
            runner = TestRunner(
                framework=framework,  # Auto-detect if None
                verbose=False,
                timeout=120  # 2 minutes for all tests
            )

            result = runner.run_tests(str(test_path))

            if self.logger:
                self.logger.log(
                    f"🧪 Ran {result.total} tests using {result.framework} "
                    f"({result.passed} passed, {result.failed} failed)",
                    "INFO"
                )

            return {
                "passed": result.passed,
                "failed": result.failed,
                "skipped": result.skipped,
                "errors": result.errors,
                "total": result.total,
                "pass_rate": result.pass_rate,
                "exit_code": result.exit_code,
                "output": result.output,
                "framework": result.framework,
                "duration": result.duration
            }

        except Exception as e:
            if self.logger:
                self.logger.log(f"⚠️  Error running tests: {e}", "WARNING")

            return {
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 1,
                "total": 0,
                "exit_code": 1,
                "error": str(e),
                "framework": "unknown"
            }

    def _empty_result(self) -> Dict:
        """
        Return empty test result (when no tests exist)

        Returns:
            Empty test result dict
        """
        return {
            "passed": 0,
            "failed": 0,
            "exit_code": 0,
            "framework": "none"
        }


__all__ = [
    "DeveloperTestRunner"
]
