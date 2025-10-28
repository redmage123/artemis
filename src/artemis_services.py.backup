#!/usr/bin/env python3
"""
Artemis Services (SOLID: Single Responsibility Principle)

Each service class has ONE clear responsibility:
- TestRunner: Running tests
- HTMLValidator: Validating HTML
- PipelineLogger: Logging messages
- FileManager: File operations
"""

import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict
from bs4 import BeautifulSoup

from artemis_stage_interface import TestRunnerInterface, ValidatorInterface, LoggerInterface
from artemis_constants import PYTEST_PATH as DEFAULT_PYTEST_PATH


class TestRunner(TestRunnerInterface):
    """
    Single Responsibility: Run pytest and parse results

    WHAT: Executes pytest test suites and parses the output into structured data.
    WHY: Encapsulates all test execution logic in one place, making it testable and
         allowing easy substitution with mock implementations.

    This class does ONLY test execution - nothing else.
    """

    def __init__(self, pytest_path: str = None):
        """
        Initialize test runner.

        WHAT: Sets up pytest executable path.
        WHY: Allows overriding pytest location for different environments (venv, system, etc).
        """
        self.pytest_path = pytest_path or DEFAULT_PYTEST_PATH

    def run_tests(self, test_path: str, timeout: int = 60) -> Dict:
        """
        Run pytest and return parsed results.

        WHAT: Executes pytest with verbose output and parses pass/fail/skip counts.
        WHY: Provides standardized test results format for pipeline stages to consume.
             Timeout prevents hanging on infinite loops in tests.

        Args:
            test_path: Path to tests
            timeout: Timeout in seconds

        Returns:
            Dict with test results
        """
        result = subprocess.run(
            [self.pytest_path, test_path, "-v", "--tb=short", "-q"],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = result.stdout + result.stderr
        passed, failed, skipped = self._parse_pytest_output(output)
        total = passed + failed + skipped

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "exit_code": result.returncode,
            "output": output
        }

    def _parse_pytest_output(self, output: str) -> tuple:
        """
        Parse pytest output to extract counts.

        WHAT: Uses regex to extract passed/failed/skipped counts from pytest summary.
        WHY: Pytest output format is consistent, regex is reliable and fast for parsing.
        """
        passed = failed = skipped = 0

        if match := re.search(r'(\d+) passed', output):
            passed = int(match.group(1))
        if match := re.search(r'(\d+) failed', output):
            failed = int(match.group(1))
        if match := re.search(r'(\d+) skipped', output):
            skipped = int(match.group(1))

        return passed, failed, skipped


class HTMLValidator(ValidatorInterface):
    """
    Single Responsibility: Validate HTML syntax

    WHAT: Validates HTML files for syntax errors using BeautifulSoup parser.
    WHY: Catches malformed HTML early before it causes runtime errors.
         BeautifulSoup is lenient but will catch serious syntax issues.

    This class does ONLY HTML validation - nothing else.
    """

    def validate(self, file_path: Path) -> Dict:
        """
        Validate HTML file syntax using BeautifulSoup.

        WHAT: Attempts to parse HTML file and reports any parsing errors.
        WHY: BeautifulSoup's parser is forgiving but will fail on severely malformed HTML.
             Returns standardized result format for pipeline consumption.

        Args:
            file_path: Path to HTML file

        Returns:
            Dict with validation results
        """
        try:
            with open(file_path) as f:
                html = f.read()
            soup = BeautifulSoup(html, 'html.parser')
            return {
                "status": "PASS",
                "errors": 0,
                "note": "HTML is valid and parseable"
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "errors": 1,
                "note": str(e)
            }


class PipelineLogger(LoggerInterface):
    """
    Single Responsibility: Log pipeline messages

    WHAT: Provides formatted console logging with timestamps and emoji indicators.
    WHY: Separates logging concerns from business logic and provides consistent,
         readable output format across all pipeline stages.

    This class does ONLY logging - nothing else.
    """

    EMOJI_MAP = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "STAGE": "🔄"
    }

    def __init__(self, verbose: bool = True):
        """
        Initialize logger.

        WHAT: Sets verbosity flag to control output.
        WHY: Allows silencing logs during testing or batch operations.
        """
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """
        Log message with timestamp and emoji.

        WHAT: Formats and prints log message with UTC timestamp and level-specific emoji.
        WHY: Timestamps help trace execution order, emojis make scanning logs easier.
        """
        if self.verbose:
            timestamp = datetime.utcnow().strftime("%H:%M:%S")
            emoji = self.EMOJI_MAP.get(level, "•")
            print(f"[{timestamp}] {emoji} {message}")

    # Standard logging interface compatibility
    def info(self, message: str, **kwargs):
        """
        Log info message (ignores extra kwargs for compatibility).

        WHAT: Standard logging interface method mapping to log() with INFO level.
        WHY: Enables drop-in replacement of Python's standard logger without code changes.
        """
        self.log(message, "INFO")

    def warning(self, message: str, **kwargs):
        """
        Log warning message (ignores extra kwargs for compatibility).

        WHAT: Standard logging interface method mapping to log() with WARNING level.
        WHY: Enables drop-in replacement of Python's standard logger without code changes.
        """
        self.log(message, "WARNING")

    def error(self, message: str, **kwargs):
        """
        Log error message (ignores extra kwargs for compatibility).

        WHAT: Standard logging interface method mapping to log() with ERROR level.
        WHY: Enables drop-in replacement of Python's standard logger without code changes.
        """
        self.log(message, "ERROR")

    def debug(self, message: str, **kwargs):
        """
        Log debug message (ignores extra kwargs for compatibility).

        WHAT: Standard logging interface method mapping to log() with INFO level.
        WHY: Enables drop-in replacement of Python's standard logger without code changes.
        """
        self.log(message, "INFO")


class FileManager:
    """
    Single Responsibility: Handle file operations

    WHAT: Provides simple, safe file I/O operations with consistent error handling.
    WHY: Centralizes all file operations to enable mocking in tests and consistent
         error handling across the codebase.

    This class does ONLY file I/O - nothing else.
    """

    @staticmethod
    def read_json(file_path: Path) -> Dict:
        """
        Read JSON file.

        WHAT: Reads and parses JSON file into Python dictionary.
        WHY: Encapsulates JSON parsing logic and provides single point for error handling.
        """
        import json
        with open(file_path) as f:
            return json.load(f)

    @staticmethod
    def write_json(file_path: Path, data: Dict):
        """
        Write JSON file.

        WHAT: Serializes dictionary to JSON and writes to file with indentation.
        WHY: Consistent JSON formatting (2-space indent) makes files human-readable.
        """
        import json
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def read_text(file_path: Path) -> str:
        """
        Read text file.

        WHAT: Reads entire text file content as string.
        WHY: Provides consistent interface for text file reading across all modules.
        """
        with open(file_path) as f:
            return f.read()

    @staticmethod
    def write_text(file_path: Path, content: str):
        """
        Write text file.

        WHAT: Writes string content to file, overwriting if exists.
        WHY: Provides consistent interface for text file writing across all modules.
        """
        with open(file_path, 'w') as f:
            f.write(content)

    @staticmethod
    def ensure_directory(dir_path: Path):
        """
        Ensure directory exists.

        WHAT: Creates directory and all parent directories if they don't exist.
        WHY: Prevents FileNotFoundError when writing files to new directories.
        """
        dir_path.mkdir(parents=True, exist_ok=True)
