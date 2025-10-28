#!/usr/bin/env python3
"""
Resource Validators - Resource limits and optional services validation

WHY: Validates resource limits and optional services before pipeline runs to
     ensure reasonable configuration and prevent resource exhaustion.

RESPONSIBILITY: Validate resource limits (budgets, parallel workers) and
                optional services (RAG database, Redis).

PATTERNS: Guard clauses for early returns, pure functions for validation.
"""

import os
from pathlib import Path
from typing import List, Optional
from config.validation.models import ValidationResult


class ResourceLimitValidator:
    """
    Validates resource limits are reasonable.

    WHY: Ensures configured resource limits prevent system overload.
    RESPONSIBILITY: Validate resource limit configuration only.
    PATTERNS: Guard clauses for early returns, pure validation functions.
    """

    # Constants for validation
    MIN_PARALLEL_DEVELOPERS = 1
    MAX_PARALLEL_DEVELOPERS = 5

    @staticmethod
    def _validate_parallel_developers() -> ValidationResult:
        """
        Validate max parallel developers setting.

        WHY: Pure function to validate developer parallelism limit.
        PERFORMANCE: O(1) environment variable check.

        Returns:
            ValidationResult for parallel developers setting
        """
        max_devs = int(os.getenv("ARTEMIS_MAX_PARALLEL_DEVELOPERS", "2"))

        if ResourceLimitValidator.MIN_PARALLEL_DEVELOPERS <= max_devs <= ResourceLimitValidator.MAX_PARALLEL_DEVELOPERS:
            return ValidationResult(
                check_name="Parallel Developers",
                passed=True,
                message=f"Max parallel developers: {max_devs}",
                severity="info"
            )

        return ValidationResult(
            check_name="Parallel Developers",
            passed=False,
            message=f"Invalid max parallel developers: {max_devs}",
            severity="warning",
            fix_suggestion=f"Set ARTEMIS_MAX_PARALLEL_DEVELOPERS between {ResourceLimitValidator.MIN_PARALLEL_DEVELOPERS} and {ResourceLimitValidator.MAX_PARALLEL_DEVELOPERS}"
        )

    @staticmethod
    def _validate_daily_budget() -> Optional[ValidationResult]:
        """
        Validate daily budget setting if configured.

        WHY: Pure function to validate budget configuration.
        PERFORMANCE: O(1) environment variable check.

        Returns:
            ValidationResult if budget is configured, None otherwise
        """
        daily_budget = os.getenv("ARTEMIS_DAILY_BUDGET")

        # Guard clause: No budget set
        if not daily_budget:
            return None

        # Validate budget value
        try:
            budget = float(daily_budget)
        except ValueError:
            return ValidationResult(
                check_name="Daily Budget",
                passed=False,
                message=f"Invalid daily budget: {daily_budget}",
                severity="warning",
                fix_suggestion="Set ARTEMIS_DAILY_BUDGET to a number (e.g., 10.00)"
            )

        # Guard clause: Budget must be positive
        if budget <= 0:
            return ValidationResult(
                check_name="Daily Budget",
                passed=False,
                message="Daily budget must be positive",
                severity="warning"
            )

        # Success case: Valid budget
        return ValidationResult(
            check_name="Daily Budget",
            passed=True,
            message=f"Daily budget: ${budget:.2f}",
            severity="info"
        )

    @staticmethod
    def validate() -> List[ValidationResult]:
        """
        Validate all resource limits.

        WHY: Ensures resource limits are reasonable before pipeline runs.
        PERFORMANCE: O(1) environment variable checks.

        Returns:
            List of ValidationResults for resource limits
        """
        results = []

        # Validate parallel developers
        results.append(ResourceLimitValidator._validate_parallel_developers())

        # Validate daily budget if configured
        budget_result = ResourceLimitValidator._validate_daily_budget()
        if budget_result:
            results.append(budget_result)

        return results


class RAGDatabaseValidator:
    """
    Validates RAG database (ChromaDB) access.

    WHY: RAG database is optional but important for code examples.
    RESPONSIBILITY: Validate RAG database access only.
    """

    @staticmethod
    def _get_absolute_rag_path(rag_db_path: str) -> str:
        """
        Convert relative RAG database path to absolute.

        WHY: Pure function to ensure consistent path handling.
        PERFORMANCE: O(1) path conversion.

        Args:
            rag_db_path: RAG database path to convert

        Returns:
            Absolute RAG database path
        """
        if os.path.isabs(rag_db_path):
            return rag_db_path

        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, rag_db_path)

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate RAG database (ChromaDB) access.

        WHY: Ensures ChromaDB is available for RAG features if configured.
        PERFORMANCE: O(1) import and directory check.

        Returns:
            ValidationResult for RAG database access
        """
        rag_db_path = os.getenv("ARTEMIS_RAG_DB_PATH", "db")
        rag_db_path = RAGDatabaseValidator._get_absolute_rag_path(rag_db_path)

        try:
            # Try to import chromadb
            import chromadb

            # Try to create/access database
            Path(rag_db_path).mkdir(parents=True, exist_ok=True)

            return ValidationResult(
                check_name="RAG Database (ChromaDB)",
                passed=True,
                message=f"ChromaDB accessible at {rag_db_path}"
            )
        except ImportError:
            return ValidationResult(
                check_name="RAG Database (ChromaDB)",
                passed=False,
                message="chromadb library not installed",
                severity="warning",
                fix_suggestion="pip install chromadb (optional but recommended)"
            )
        except Exception as e:
            return ValidationResult(
                check_name="RAG Database (ChromaDB)",
                passed=False,
                message=f"Cannot access RAG database: {e}",
                severity="warning",
                fix_suggestion=f"Check permissions on {rag_db_path}"
            )


class RedisValidator:
    """
    Validates Redis service availability.

    WHY: Redis is optional for caching and may improve performance.
    RESPONSIBILITY: Validate Redis connectivity only.
    """

    @staticmethod
    def validate(redis_url: str) -> ValidationResult:
        """
        Validate Redis service availability.

        WHY: Ensures Redis is available if configured.
        PERFORMANCE: Uses socket_connect_timeout to avoid long waits (O(1) with timeout).

        Args:
            redis_url: Redis connection URL

        Returns:
            ValidationResult for Redis access
        """
        try:
            import redis
            client = redis.from_url(redis_url, socket_connect_timeout=2)
            client.ping()
            return ValidationResult(
                check_name="Redis (Optional)",
                passed=True,
                message=f"Connected to Redis at {redis_url}",
                severity="info"
            )
        except ImportError:
            return ValidationResult(
                check_name="Redis (Optional)",
                passed=False,
                message="redis library not installed",
                severity="warning",
                fix_suggestion="pip install redis (optional)"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Redis (Optional)",
                passed=False,
                message=f"Cannot connect to Redis: {e}",
                severity="warning",
                fix_suggestion="Ensure Redis is running or unset REDIS_URL"
            )


class OptionalServiceValidator:
    """
    Validates optional services.

    WHY: Optional services enhance functionality but aren't required.
    RESPONSIBILITY: Orchestrate optional service validation.
    """

    @staticmethod
    def validate() -> List[ValidationResult]:
        """
        Validate all optional services.

        WHY: Checks optional services if configured.
        PERFORMANCE: O(1) environment variable check, O(n) for Redis if present.

        Returns:
            List of ValidationResults for optional services
        """
        results = []

        # Check Redis if configured
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            results.append(RedisValidator.validate(redis_url))

        return results
