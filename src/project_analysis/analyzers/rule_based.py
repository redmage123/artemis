#!/usr/bin/env python3
"""
WHY: Rule-based dimension analyzers for project analysis
RESPONSIBILITY: Implement fast, deterministic analysis across key dimensions
PATTERNS: Single Responsibility (one analyzer per dimension), Strategy Pattern

This module provides rule-based analyzers that quickly identify common issues
using pattern matching and heuristics. These complement LLM-powered analysis
with deterministic, explainable results.
"""

from typing import Dict

from project_analysis.interfaces import DimensionAnalyzer
from project_analysis.models import AnalysisResult, Issue, Severity


class ScopeAnalyzer(DimensionAnalyzer):
    """
    WHY: Validate requirement clarity before implementation
    RESPONSIBILITY: Check scope definition and acceptance criteria
    PATTERNS: Guard clauses, early returns

    Single Responsibility: Analyze scope & requirements only.
    Validates that requirements are well-defined with clear descriptions and
    acceptance criteria. This prevents implementation based on vague requirements.
    """

    def analyze(self, card: Dict, context: Dict) -> AnalysisResult:
        """
        Analyze task scope and requirements clarity.

        Guard clauses prevent deep nesting and improve readability.

        Args:
            card: Kanban card containing task information
            context: Pipeline context (unused by this analyzer)

        Returns:
            AnalysisResult with scope-related issues and recommendations
        """
        issues = []
        recommendations = []

        # Check if description is clear
        description = card.get('description', '')
        if not description or len(description) < 20:
            issues.append(Issue(
                category="Scope & Requirements",
                severity=Severity.HIGH,
                description="Task description is too vague or missing",
                impact="Implementation may not meet actual requirements",
                suggestion="Add detailed description explaining what needs to be done and why",
                reasoning="Clear requirements prevent rework and misunderstandings",
                user_approval_needed=True
            ))

        # Check for acceptance criteria
        acceptance_criteria = card.get('acceptance_criteria', [])
        if not acceptance_criteria:
            issues.append(Issue(
                category="Scope & Requirements",
                severity=Severity.HIGH,
                description="No acceptance criteria defined",
                impact="No clear definition of 'done'",
                suggestion="Add measurable acceptance criteria (Given-When-Then format)",
                reasoning="Acceptance criteria define success and enable proper testing",
                user_approval_needed=True
            ))

        recommendations.append("Define clear success metrics")

        return AnalysisResult(
            dimension="Scope & Requirements",
            issues=issues,
            recommendations=recommendations
        )

    def get_dimension_name(self) -> str:
        """Get the name of this analysis dimension."""
        return "scope"


class SecurityAnalyzer(DimensionAnalyzer):
    """
    WHY: Identify security risks before implementation
    RESPONSIBILITY: Detect security-sensitive operations and recommend safeguards
    PATTERNS: Keyword detection, dispatch table for security concerns

    Single Responsibility: Analyze security concerns only.
    Detects security-sensitive operations (authentication, data storage, APIs)
    and recommends appropriate security measures. This prevents shipping
    insecure implementations.
    """

    def analyze(self, card: Dict, context: Dict) -> AnalysisResult:
        """
        Analyze security concerns in task requirements.

        Uses keyword detection to identify security-sensitive features.

        Args:
            card: Kanban card containing task information
            context: Pipeline context (unused by this analyzer)

        Returns:
            AnalysisResult with security issues and recommendations
        """
        issues = []
        recommendations = []

        title = card.get('title', '').lower()
        description = card.get('description', '').lower()
        combined = f"{title} {description}"

        # Check for authentication/authorization
        if any(kw in combined for kw in ['auth', 'login', 'user', 'password', 'token']):
            issues.append(Issue(
                category="Security",
                severity=Severity.CRITICAL,
                description="Task involves authentication/authorization - security review needed",
                impact="Potential security vulnerabilities (auth bypass, token leaks)",
                suggestion="Add security requirements: token encryption, session management, OWASP compliance",
                reasoning="Authentication bugs are critical security vulnerabilities",
                user_approval_needed=True
            ))

        # Check for data storage
        if any(kw in combined for kw in ['store', 'save', 'database', 'data']):
            issues.append(Issue(
                category="Security",
                severity=Severity.HIGH,
                description="Task involves data storage - encryption and validation needed",
                impact="Data exposure, SQL injection, insecure storage",
                suggestion="Add requirements: input validation, parameterized queries, encryption at rest",
                reasoning="Data storage requires protection against common attacks",
                user_approval_needed=True
            ))

        # Check for API endpoints
        if any(kw in combined for kw in ['api', 'endpoint', 'rest', 'graphql']):
            recommendations.append("Add rate limiting and authentication to API endpoints")
            recommendations.append("Implement input validation and sanitization")

        return AnalysisResult(
            dimension="Security",
            issues=issues,
            recommendations=recommendations
        )

    def get_dimension_name(self) -> str:
        """Get the name of this analysis dimension."""
        return "security"


class PerformanceAnalyzer(DimensionAnalyzer):
    """
    WHY: Prevent performance issues through proactive requirements
    RESPONSIBILITY: Identify performance-critical features and define targets
    PATTERNS: Keyword detection, early warning system

    Single Responsibility: Analyze scalability & performance only.
    Detects performance-critical features (dashboards, search, analytics)
    and ensures performance targets are defined. This prevents slow UX
    and scalability issues in production.
    """

    def analyze(self, card: Dict, context: Dict) -> AnalysisResult:
        """
        Analyze scalability and performance requirements.

        Identifies performance-critical features and suggests targets.

        Args:
            card: Kanban card containing task information
            context: Pipeline context (unused by this analyzer)

        Returns:
            AnalysisResult with performance issues and recommendations
        """
        issues = []
        recommendations = []

        description = card.get('description', '').lower()

        # Check for performance requirements
        if any(kw in description for kw in ['dashboard', 'report', 'analytics', 'search']):
            issues.append(Issue(
                category="Scalability & Performance",
                severity=Severity.MEDIUM,
                description="No performance requirements defined",
                impact="Slow user experience under load",
                suggestion="Add performance target: <200ms response time, <2s page load",
                reasoning="Performance expectations prevent slowdowns in production",
                user_approval_needed=False
            ))

        # Check for caching needs
        if any(kw in description for kw in ['report', 'analytics', 'dashboard']):
            recommendations.append("Consider caching strategy for expensive queries")

        # Check for pagination
        if any(kw in description for kw in ['list', 'search', 'display']):
            recommendations.append("Implement pagination for large result sets")

        return AnalysisResult(
            dimension="Scalability & Performance",
            issues=issues,
            recommendations=recommendations
        )

    def get_dimension_name(self) -> str:
        """Get the name of this analysis dimension."""
        return "performance"


class TestingAnalyzer(DimensionAnalyzer):
    """
    WHY: Ensure comprehensive testing strategy
    RESPONSIBILITY: Promote TDD and validate test coverage requirements
    PATTERNS: Best practices enforcement, proactive recommendations

    Single Responsibility: Analyze testing strategy only.
    Ensures tasks include testing requirements and promotes TDD practices.
    This prevents untested code from reaching production.
    """

    def analyze(self, card: Dict, context: Dict) -> AnalysisResult:
        """
        Analyze testing strategy and coverage requirements.

        Promotes Test-Driven Development and comprehensive test coverage.

        Args:
            card: Kanban card containing task information
            context: Pipeline context (unused by this analyzer)

        Returns:
            AnalysisResult with testing issues and recommendations
        """
        issues = []
        recommendations = []

        # Always recommend TDD
        recommendations.append("Use TDD: Write tests BEFORE implementation (Red-Green-Refactor)")
        recommendations.append("Target 85%+ test coverage (unit + integration + acceptance)")

        # Check for testing strategy
        description = card.get('description', '')
        if 'test' not in description.lower():
            issues.append(Issue(
                category="Testing Strategy",
                severity=Severity.HIGH,
                description="No testing approach mentioned in requirements",
                impact="Untested code leads to bugs in production",
                suggestion="Add testing requirements: unit tests (85%), integration tests, E2E tests",
                reasoning="TDD and comprehensive tests ensure quality and prevent regressions",
                user_approval_needed=True
            ))

        return AnalysisResult(
            dimension="Testing Strategy",
            issues=issues,
            recommendations=recommendations
        )

    def get_dimension_name(self) -> str:
        """Get the name of this analysis dimension."""
        return "testing"


class ErrorHandlingAnalyzer(DimensionAnalyzer):
    """
    WHY: Ensure robust error handling and edge case coverage
    RESPONSIBILITY: Validate failure scenarios and recovery strategies
    PATTERNS: Defensive programming promotion, edge case awareness

    Single Responsibility: Analyze error handling & edge cases only.
    Ensures tasks consider failure scenarios, input validation, and
    proper error handling. This prevents crashes and improper error states.
    """

    def analyze(self, card: Dict, context: Dict) -> AnalysisResult:
        """
        Analyze error handling and edge case coverage.

        Promotes defensive programming and graceful error handling.

        Args:
            card: Kanban card containing task information
            context: Pipeline context (unused by this analyzer)

        Returns:
            AnalysisResult with error handling issues and recommendations
        """
        issues = []
        recommendations = []

        description = card.get('description', '').lower()

        # Check for error handling requirements
        if 'error' not in description and 'fail' not in description:
            issues.append(Issue(
                category="Error Handling",
                severity=Severity.MEDIUM,
                description="No error handling strategy defined",
                impact="Poor user experience when things go wrong",
                suggestion="Add error handling: try-catch blocks, user-friendly messages, logging",
                reasoning="Graceful error handling improves user experience and debuggability",
                user_approval_needed=False
            ))

        recommendations.append("Define failure scenarios and recovery strategies")
        recommendations.append("Add logging for debugging and monitoring")

        return AnalysisResult(
            dimension="Error Handling & Edge Cases",
            issues=issues,
            recommendations=recommendations
        )

    def get_dimension_name(self) -> str:
        """Get the name of this analysis dimension."""
        return "error_handling"
