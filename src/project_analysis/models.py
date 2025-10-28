#!/usr/bin/env python3
"""
WHY: Data models for project analysis system
RESPONSIBILITY: Define immutable data structures for issues, results, and enums
PATTERNS: Dataclasses for immutability, Enums for type safety

This module provides the foundational data structures used throughout the
project analysis system, ensuring type safety and consistent data representation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class Severity(Enum):
    """
    WHY: Type-safe severity classification
    RESPONSIBILITY: Define issue severity levels with clear semantics

    Issue severity levels that drive approval workflow:
    - CRITICAL: Must address before implementation (security, data loss)
    - HIGH: Strongly recommended (testing, scalability)
    - MEDIUM: Nice to have (code quality, maintainability)
    """
    CRITICAL = "CRITICAL"  # Must address before implementation
    HIGH = "HIGH"          # Strongly recommended
    MEDIUM = "MEDIUM"      # Nice to have


@dataclass
class Issue:
    """
    WHY: Structured representation of identified issues
    RESPONSIBILITY: Encapsulate issue details with all necessary context

    Represents an identified issue with complete context for decision-making.
    Includes severity, impact, and actionable suggestions.
    """
    category: str
    severity: Severity
    description: str
    impact: str
    suggestion: str
    reasoning: str
    user_approval_needed: bool


@dataclass
class AnalysisResult:
    """
    WHY: Container for dimension-specific analysis results
    RESPONSIBILITY: Group issues and recommendations by dimension

    Result from analyzing one dimension (security, performance, etc.).
    Enables dimension-by-dimension reporting and filtering.
    """
    dimension: str
    issues: List[Issue]
    recommendations: List[str]


class ApprovalOptions(Enum):
    """
    WHY: Type-safe user approval options
    RESPONSIBILITY: Define valid approval workflow states

    User approval options that control which issues are accepted:
    - APPROVE_ALL: Accept all critical and high-priority changes
    - APPROVE_CRITICAL: Accept only critical security/compliance fixes
    - CUSTOM: User selects specific issues to approve
    - REJECT: Proceed with original task as-is
    - MODIFY: User wants to suggest different changes
    """
    APPROVE_ALL = "approve_all"
    APPROVE_CRITICAL = "approve_critical"
    CUSTOM = "custom"
    REJECT = "reject"
    MODIFY = "modify"
