#!/usr/bin/env python3
"""
Quality Analyzer - Technical Debt and Anti-Pattern Detection

WHY: Identify quality issues, technical debt, and anti-patterns in architecture
RESPONSIBILITY: Check for hardcoded config, missing error handling, security gaps, testing gaps
PATTERNS: Single Responsibility, Guard Clauses, Configuration-Driven Detection

This module detects:
- Hardcoded configuration
- Missing error handling
- No logging/monitoring
- Missing tests
- Security vulnerabilities
"""

import json
from typing import Dict, List, Any, Optional


class QualityAnalyzer:
    """
    Analyzes architecture for technical debt and anti-patterns

    WHY: Early detection of quality issues prevents technical debt accumulation
    RESPONSIBILITY: Scan architecture for common anti-patterns and missing best practices
    """

    def __init__(self, logger: Any, tech_debt_penalty: float = 0.5):
        """
        Initialize Quality Analyzer

        Args:
            logger: Logger interface for diagnostics
            tech_debt_penalty: Score deduction for technical debt items
        """
        if not logger:
            raise ValueError("Logger is required for quality analysis")

        self.logger = logger
        self.tech_debt_penalty = tech_debt_penalty

        # Define quality checks using dispatch table pattern
        self.quality_checks = {
            'hardcoded_config': self._check_hardcoded_config,
            'error_handling': self._check_error_handling,
            'logging_monitoring': self._check_logging_monitoring,
            'testing_strategy': self._check_testing_strategy,
            'security_practices': self._check_security_practices,
            'database_migrations': self._check_database_migrations
        }

    def check_quality_issues(
        self,
        architecture: Optional[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check for technical debt, anti-patterns, and code smells

        WHY: Comprehensive quality assessment using multiple checks

        Args:
            architecture: Architecture design dictionary (may be None)
            context: Pipeline context with additional information

        Returns:
            Dictionary with score, critical issues, and warnings
        """
        if not architecture:
            return self._create_neutral_review()

        arch_str = self._serialize_architecture(architecture)
        issues, warnings, score = self._run_quality_checks(arch_str, architecture)

        return {
            "score": score,
            "critical_issues": issues,
            "warnings": warnings,
            "total_issues": len(issues) + len(warnings)
        }

    def _create_neutral_review(self) -> Dict[str, Any]:
        """Create neutral review when architecture is missing"""
        return {
            "score": 7,
            "critical_issues": [],
            "warnings": ["No architecture to analyze"],
            "total_issues": 1
        }

    def _serialize_architecture(self, architecture: Dict[str, Any]) -> str:
        """
        Serialize architecture to string for pattern matching

        WHY: Single serialization for all checks
        """
        return json.dumps(architecture).lower()

    def _run_quality_checks(
        self,
        arch_str: str,
        architecture: Dict[str, Any]
    ) -> tuple[List[str], List[str], int]:
        """
        Run all quality checks using dispatch table

        WHY: Extensible check system without elif chains

        Returns:
            Tuple of (issues, warnings, score)
        """
        issues = []
        warnings = []
        score = 10

        for check_name, check_func in self.quality_checks.items():
            check_result = check_func(arch_str, architecture)

            if check_result['is_critical']:
                issues.append(check_result['message'])
                score -= check_result['penalty']
            elif check_result['is_warning']:
                warnings.append(check_result['message'])
                score -= check_result['penalty']

        return issues, warnings, max(0, score)

    def _check_hardcoded_config(
        self,
        arch_str: str,
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for hardcoded configuration values"""
        if 'hardcoded' in arch_str or 'localhost' in arch_str:
            return {
                'is_critical': True,
                'is_warning': False,
                'message': "Hardcoded configuration detected",
                'penalty': 2
            }

        return {'is_critical': False, 'is_warning': False, 'message': '', 'penalty': 0}

    def _check_error_handling(
        self,
        arch_str: str,
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for error handling strategy"""
        if 'error' not in arch_str and 'exception' not in arch_str:
            return {
                'is_critical': False,
                'is_warning': True,
                'message': "No explicit error handling mentioned",
                'penalty': 1
            }

        return {'is_critical': False, 'is_warning': False, 'message': '', 'penalty': 0}

    def _check_logging_monitoring(
        self,
        arch_str: str,
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for logging and monitoring strategy"""
        if 'log' not in arch_str and 'monitor' not in arch_str:
            return {
                'is_critical': False,
                'is_warning': True,
                'message': "No logging/monitoring strategy mentioned",
                'penalty': 1
            }

        return {'is_critical': False, 'is_warning': False, 'message': '', 'penalty': 0}

    def _check_testing_strategy(
        self,
        arch_str: str,
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for testing strategy"""
        if 'test' not in arch_str:
            return {
                'is_critical': False,
                'is_warning': True,
                'message': "No testing strategy mentioned",
                'penalty': 2
            }

        return {'is_critical': False, 'is_warning': False, 'message': '', 'penalty': 0}

    def _check_security_practices(
        self,
        arch_str: str,
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for security practices"""
        if 'auth' not in arch_str and 'security' not in arch_str:
            return {
                'is_critical': False,
                'is_warning': True,
                'message': "No authentication/security mentioned",
                'penalty': 1
            }

        return {'is_critical': False, 'is_warning': False, 'message': '', 'penalty': 0}

    def _check_database_migrations(
        self,
        arch_str: str,
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for database migration strategy"""
        has_database = 'database' in arch_str or 'db' in arch_str
        has_migrations = 'migration' in arch_str

        if has_database and not has_migrations:
            return {
                'is_critical': False,
                'is_warning': True,
                'message': "No database migration strategy",
                'penalty': self.tech_debt_penalty
            }

        return {'is_critical': False, 'is_warning': False, 'message': '', 'penalty': 0}
