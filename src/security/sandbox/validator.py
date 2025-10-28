#!/usr/bin/env python3
"""
WHY: Security validation for code before sandbox execution.

RESPONSIBILITY:
    - Scan code for dangerous patterns and security risks
    - Identify potentially harmful operations
    - Provide risk assessment before execution
    - Block execution of high-risk code

PATTERNS:
    - Static pattern matching for security scanning
    - Dispatch table for severity classification
    - Guard clauses for early returns
    - Immutable configuration with class constants
"""

from typing import Dict, List, Callable, Any
from .models import SecurityScanResult


class SecurityValidator:
    """
    Validates code security before sandbox execution.

    Scans for dangerous patterns including system calls, file operations,
    network access, and code injection vectors.
    """

    # Dangerous patterns organized by category
    DANGEROUS_PATTERNS: Dict[str, List[str]] = {
        "system_calls": [
            "os.system",
            "subprocess.call",
            "subprocess.run",
            "subprocess.Popen",
        ],
        "code_execution": [
            "eval(",
            "exec(",
            "__import__",
            "compile(",
        ],
        "file_access": [
            "open(",
            "file(",
            "pathlib.Path.open",
        ],
        "network_access": [
            "socket.",
            "urllib",
            "requests",
            "http.",
            "httplib",
        ],
    }

    # Severity classification dispatch table
    SEVERITY_DISPATCH: Dict[str, Callable[[str], str]] = {}

    @classmethod
    def _init_severity_dispatch(cls) -> None:
        """Initialize severity dispatch table."""
        # Guard: Only initialize once
        if cls.SEVERITY_DISPATCH:
            return

        cls.SEVERITY_DISPATCH.update({
            "eval(": lambda _: "high",
            "exec(": lambda _: "high",
            "os.system": lambda _: "high",
            "__import__": lambda _: "high",
            "compile(": lambda _: "high",
            "subprocess.call": lambda _: "medium",
            "subprocess.run": lambda _: "medium",
            "subprocess.Popen": lambda _: "medium",
            "open(": lambda _: "medium",
            "socket.": lambda _: "medium",
            "urllib": lambda _: "medium",
            "requests": lambda _: "medium",
        })

    @classmethod
    def _get_severity(cls, pattern: str) -> str:
        """
        Get severity level for a pattern.

        Args:
            pattern: Pattern to classify

        Returns:
            Severity level: "high", "medium", or "low"
        """
        # Guard: Initialize dispatch table if needed
        if not cls.SEVERITY_DISPATCH:
            cls._init_severity_dispatch()

        # Use dispatch table or default to medium
        severity_func = cls.SEVERITY_DISPATCH.get(pattern, lambda _: "medium")
        return severity_func(pattern)

    @classmethod
    def scan_code(cls, code: str) -> SecurityScanResult:
        """
        Scan code for security issues.

        Args:
            code: Python code to scan

        Returns:
            SecurityScanResult with scan details
        """
        # Guard: Empty code is safe
        if not code or not code.strip():
            return SecurityScanResult(safe=True, issues=[], risk_level="low")

        issues = cls._detect_patterns(code)
        risk_level = cls._calculate_risk_level(issues)
        safe = len(issues) == 0

        return SecurityScanResult(
            safe=safe,
            issues=issues,
            risk_level=risk_level
        )

    @classmethod
    def _detect_patterns(cls, code: str) -> List[Dict[str, Any]]:
        """
        Detect dangerous patterns in code.

        Args:
            code: Python code to scan

        Returns:
            List of detected issues
        """
        issues = []

        # Scan all pattern categories
        for category, patterns in cls.DANGEROUS_PATTERNS.items():
            for pattern in patterns:
                # Guard: Skip if pattern not in code
                if pattern not in code:
                    continue

                severity = cls._get_severity(pattern)
                issues.append({
                    "pattern": pattern,
                    "category": category,
                    "severity": severity,
                    "message": f"Potentially dangerous code: {pattern}",
                })

        return issues

    @classmethod
    def _calculate_risk_level(cls, issues: List[Dict[str, Any]]) -> str:
        """
        Calculate overall risk level from issues.

        Args:
            issues: List of detected issues

        Returns:
            Risk level: "high", "medium", or "low"
        """
        # Guard: No issues means low risk
        if not issues:
            return "low"

        # Check for high severity issues
        has_high = any(issue["severity"] == "high" for issue in issues)
        if has_high:
            return "high"

        # Has medium or low severity issues
        return "medium"

    @classmethod
    def validate_safe(cls, code: str, allow_risky: bool = False) -> tuple[bool, str]:
        """
        Validate if code is safe to execute.

        Args:
            code: Python code to validate
            allow_risky: Allow medium-risk code

        Returns:
            Tuple of (is_safe, reason)
        """
        # Guard: Empty code is safe
        if not code or not code.strip():
            return True, "Empty code"

        scan_result = cls.scan_code(code)

        # Guard: Safe code passes
        if scan_result.safe:
            return True, "No security issues detected"

        # Guard: High risk always blocked
        if scan_result.risk_level == "high":
            return False, f"High-risk code detected: {len(scan_result.issues)} issues"

        # Medium risk depends on allow_risky flag
        if scan_result.risk_level == "medium":
            if allow_risky:
                return True, "Medium-risk code allowed"
            return False, f"Medium-risk code detected: {len(scan_result.issues)} issues"

        # Low risk (shouldn't reach here, but defensive)
        return True, "Low-risk code"
