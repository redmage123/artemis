#!/usr/bin/env python3
"""
Database Validation Module

WHY: Validates database connectivity before pipeline execution to fail fast

RESPONSIBILITY: Validate database access for persistence layer

PATTERNS: Strategy pattern via dispatch table for different database types
"""

import os
from pathlib import Path
from typing import Callable, Dict
from ..models import ValidationResult
from ..constants import DEFAULT_PERSISTENCE_TYPE, DEFAULT_PERSISTENCE_DB
from ..path_utils import resolve_relative_path, get_script_directory


class DatabaseValidator:
    """
    Validates database/persistence access

    WHY: Single Responsibility - handles only database validation

    PATTERNS: Strategy pattern via dispatch table
    """

    def validate_database(self) -> ValidationResult:
        """
        Check database/persistence access

        WHY: Validates database connectivity before pipeline runs
        PATTERNS: Strategy pattern via dictionary mapping

        Returns:
            ValidationResult for database check
        """
        persistence_type = os.getenv("ARTEMIS_PERSISTENCE_TYPE", DEFAULT_PERSISTENCE_TYPE)

        # Strategy pattern: Dictionary mapping instead of if/elif
        # WHY: Makes it easy to add new persistence types without modifying code
        database_checks: Dict[str, Callable[[], ValidationResult]] = {
            "sqlite": self._check_sqlite,
            "postgres": self._check_postgres
        }

        check_func = database_checks.get(persistence_type)
        if not check_func:
            return ValidationResult(
                check_name="Database",
                passed=False,
                message=f"Unknown persistence type: {persistence_type}",
                fix_suggestion="Set ARTEMIS_PERSISTENCE_TYPE to 'sqlite' or 'postgres'"
            )

        return check_func()

    def _check_sqlite(self) -> ValidationResult:
        """
        Check SQLite database access

        WHY: Extracted to avoid nested if statements and improve readability
        PERFORMANCE: O(1) database connection check

        Returns:
            ValidationResult for SQLite check
        """
        db_path = os.getenv("ARTEMIS_PERSISTENCE_DB", DEFAULT_PERSISTENCE_DB)

        # Convert relative path to absolute early
        script_dir = get_script_directory()
        db_path = resolve_relative_path(db_path, script_dir)

        db_file = Path(db_path)

        try:
            # Try to create/access database
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()

            return ValidationResult(
                check_name="SQLite Database",
                passed=True,
                message=f"Database accessible at {db_path}"
            )
        except Exception as e:
            return ValidationResult(
                check_name="SQLite Database",
                passed=False,
                message=f"Cannot access database: {e}",
                fix_suggestion=f"Check permissions on {db_path}"
            )

    def _check_postgres(self) -> ValidationResult:
        """
        Check PostgreSQL database access

        WHY: Extracted to separate method for clarity
        PERFORMANCE: O(1) - currently just logs warning

        Returns:
            ValidationResult for PostgreSQL check
        """
        return ValidationResult(
            check_name="PostgreSQL Database",
            passed=False,
            message="PostgreSQL persistence not yet implemented",
            severity="warning",
            fix_suggestion="Use ARTEMIS_PERSISTENCE_TYPE=sqlite for now"
        )
