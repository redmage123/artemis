#!/usr/bin/env python3
"""
Resource Limit Validation Module

WHY: Validates resource limits are within acceptable bounds before pipeline execution

RESPONSIBILITY: Validate configured resource limits (parallel developers, budgets)

PATTERNS: Guard clauses for early returns, pure validation logic
"""

import os
from typing import List
from ..models import ValidationResult
from ..constants import (
    MIN_PARALLEL_DEVELOPERS,
    MAX_PARALLEL_DEVELOPERS,
    DEFAULT_MAX_PARALLEL_DEVELOPERS
)


class ResourceLimitValidator:
    """
    Validates resource limits are reasonable

    WHY: Single Responsibility - handles only resource limit validation

    PATTERNS: Guard clauses for early returns
    """

    def validate_resource_limits(self) -> List[ValidationResult]:
        """
        Check resource limits are reasonable

        WHY: Validates configured resource limits before pipeline runs
        PERFORMANCE: O(1) environment variable checks

        Returns:
            List of ValidationResult for resource limit checks
        """
        results = []

        # Check max parallel developers
        max_devs = int(os.getenv("ARTEMIS_MAX_PARALLEL_DEVELOPERS", DEFAULT_MAX_PARALLEL_DEVELOPERS))
        if MIN_PARALLEL_DEVELOPERS <= max_devs <= MAX_PARALLEL_DEVELOPERS:
            results.append(ValidationResult(
                check_name="Parallel Developers",
                passed=True,
                message=f"Max parallel developers: {max_devs}",
                severity="info"
            ))
        else:
            results.append(ValidationResult(
                check_name="Parallel Developers",
                passed=False,
                message=f"Invalid max parallel developers: {max_devs}",
                severity="warning",
                fix_suggestion=f"Set ARTEMIS_MAX_PARALLEL_DEVELOPERS between {MIN_PARALLEL_DEVELOPERS} and {MAX_PARALLEL_DEVELOPERS}"
            ))

        # Check budgets if set
        daily_budget = os.getenv("ARTEMIS_DAILY_BUDGET")

        # Guard clause: No budget set
        if not daily_budget:
            return results

        # Validate budget value
        try:
            budget = float(daily_budget)
        except ValueError:
            results.append(ValidationResult(
                check_name="Daily Budget",
                passed=False,
                message=f"Invalid daily budget: {daily_budget}",
                severity="warning",
                fix_suggestion="Set ARTEMIS_DAILY_BUDGET to a number (e.g., 10.00)"
            ))
            return results

        # Guard clause: Budget must be positive
        if budget <= 0:
            results.append(ValidationResult(
                check_name="Daily Budget",
                passed=False,
                message="Daily budget must be positive",
                severity="warning"
            ))
            return results

        # Success case: Valid budget
        results.append(ValidationResult(
            check_name="Daily Budget",
            passed=True,
            message=f"Daily budget: ${budget:.2f}",
            severity="info"
        ))

        return results
