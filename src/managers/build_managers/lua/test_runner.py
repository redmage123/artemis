"""
Module: test_runner.py

WHY: Executes Lua tests using busted framework and parses results
RESPONSIBILITY: Run tests, parse output (JSON and text), provide test metrics
PATTERNS: Strategy Pattern (different output parsers), Guard Clauses
"""

import subprocess
import json
import re
from typing import Dict, Any, Tuple
from pathlib import Path


class LuaTestRunner:
    """
    Runs Lua tests using busted framework.

    WHY: Busted is the most popular Lua testing framework (BDD-style)
    RESPONSIBILITY: Execute tests, parse results, provide test metrics
    """

    def __init__(self, project_path: Path, logger):
        """
        Initialize test runner.

        Args:
            project_path: Root directory of Lua project
            logger: ArtemisLogger instance
        """
        self.project_path = project_path
        self.logger = logger

    def run_tests(self, timeout: int = 300) -> Dict[str, Any]:
        """
        Run tests using busted framework.

        WHY: Automated testing is critical for code quality and CI/CD

        Args:
            timeout: Test timeout in seconds (default: 5 minutes)

        Returns:
            Dict with success, total, passed, failed, duration, message
        """
        if not self._is_busted_available():
            self.logger.warning("⚠️  busted not found, skipping tests")
            return self._create_error_result("busted not installed")

        self.logger.info("🧪 Running Lua tests with busted...")

        try:
            result = subprocess.run(
                ["busted", "--output=json"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return self._parse_test_output(result.stdout, result.returncode)

        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ Tests timed out after {timeout} seconds")
            return self._create_timeout_result(timeout)

        except Exception as e:
            self.logger.error(f"❌ Test execution failed: {e}")
            return self._create_error_result(str(e))

    def _parse_test_output(self, output: str, exit_code: int) -> Dict[str, Any]:
        """
        Parse test output (JSON or text fallback).

        WHY: Busted supports JSON output for structured parsing

        Args:
            output: Stdout from busted command
            exit_code: Process exit code

        Returns:
            Dict with test results
        """
        # Try JSON parsing first
        try:
            test_results = json.loads(output)
            return self._parse_json_output(test_results)
        except json.JSONDecodeError:
            # Fallback to text parsing
            return self._parse_text_output(output)

    def _parse_json_output(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse busted JSON output.

        Args:
            test_results: Parsed JSON from busted

        Returns:
            Standardized test result dict
        """
        total = test_results.get("tests", 0)
        passed = test_results.get("successes", 0)
        failed = test_results.get("failures", 0)
        duration = test_results.get("duration", 0.0)

        success = failed == 0 and total > 0

        if success:
            self.logger.info(f"✅ All {passed} tests passed in {duration:.2f}s")
        else:
            self.logger.error(f"❌ {failed}/{total} tests failed")

        return {
            "success": success,
            "total": total,
            "passed": passed,
            "failed": failed,
            "duration": duration,
            "message": f"{passed}/{total} tests passed" if total > 0 else "No tests found"
        }

    def _parse_text_output(self, output: str) -> Dict[str, Any]:
        """
        Parse busted text output (fallback for older versions).

        WHY: Older busted versions may not support JSON output

        Args:
            output: Text output from busted

        Returns:
            Standardized test result dict
        """
        # Look for summary: "5 successes / 0 failures / 0 errors / 0 pending : 0.123 seconds"
        match = re.search(r'(\d+)\s+successes?\s+/\s+(\d+)\s+failures?', output)

        if not match:
            return self._create_error_result("Failed to parse test output")

        passed = int(match.group(1))
        failed = int(match.group(2))
        total = passed + failed

        # Extract duration
        duration_match = re.search(r'([\d.]+)\s+seconds', output)
        duration = float(duration_match.group(1)) if duration_match else 0.0

        success = failed == 0 and total > 0

        if success:
            self.logger.info(f"✅ All {passed} tests passed in {duration:.2f}s")
        else:
            self.logger.error(f"❌ {failed}/{total} tests failed")

        return {
            "success": success,
            "total": total,
            "passed": passed,
            "failed": failed,
            "duration": duration,
            "message": f"{passed}/{total} tests passed"
        }

    def _is_busted_available(self) -> bool:
        """
        Check if busted is available.

        Returns:
            True if busted command exists
        """
        try:
            subprocess.run(
                ["which", "busted"],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _create_error_result(self, message: str) -> Dict[str, Any]:
        """
        Create error result dict.

        Args:
            message: Error message

        Returns:
            Standardized error result
        """
        return {
            "success": False,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "duration": 0.0,
            "message": message
        }

    def _create_timeout_result(self, timeout: int) -> Dict[str, Any]:
        """
        Create timeout result dict.

        Args:
            timeout: Timeout duration in seconds

        Returns:
            Standardized timeout result
        """
        return {
            "success": False,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "duration": float(timeout),
            "message": "Tests timed out"
        }
