#!/usr/bin/env python3
"""
Database Validators - Database and persistence validation

WHY: Validates database connectivity before pipeline runs to prevent runtime
     failures when trying to persist state or retrieve data.

RESPONSIBILITY: Validate database access (SQLite, PostgreSQL, etc.).

PATTERNS: Strategy pattern for database-specific validation, guard clauses.
"""

import os
from pathlib import Path
from typing import Callable, Dict
from config.validation.models import ValidationResult


class DatabaseValidator:
    """
    Validates database/persistence access.

    WHY: Ensures database connectivity before pipeline runs.
    RESPONSIBILITY: Orchestrate database-specific validators.
    PATTERNS: Strategy pattern via dictionary mapping to validators.
    """

    # Strategy pattern: Map persistence types to validator functions
    # WHY: Makes it easy to add new persistence types without modifying code
    DATABASE_VALIDATORS: Dict[str, Callable[[], ValidationResult]] = {}

    @classmethod
    def register_validator(cls, persistence_type: str, validator_func: Callable[[], ValidationResult]) -> None:
        """
        Register a database validator.

        WHY: Open/Closed principle - add new validators without modifying class.
        PERFORMANCE: O(1) dictionary insertion.

        Args:
            persistence_type: Type of persistence (sqlite, postgres, etc.)
            validator_func: Validator function to register
        """
        cls.DATABASE_VALIDATORS[persistence_type] = validator_func

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate database access based on configured type.

        WHY: Dispatches to appropriate validator based on configuration.
        PERFORMANCE: O(1) dictionary lookup.

        Returns:
            ValidationResult for database access
        """
        persistence_type = os.getenv("ARTEMIS_PERSISTENCE_TYPE", "sqlite")

        # Guard clause: Unknown persistence type
        validator_func = DatabaseValidator.DATABASE_VALIDATORS.get(persistence_type)
        if not validator_func:
            return ValidationResult(
                check_name="Database",
                passed=False,
                message=f"Unknown persistence type: {persistence_type}",
                fix_suggestion="Set ARTEMIS_PERSISTENCE_TYPE to 'sqlite' or 'postgres'"
            )

        # Delegate to specific validator
        return validator_func()


class SQLiteValidator:
    """
    Validates SQLite database access.

    WHY: SQLite is the default persistence layer, must be accessible.
    RESPONSIBILITY: Validate SQLite database access only.
    """

    @staticmethod
    def _get_absolute_db_path(db_path: str) -> str:
        """
        Convert relative database path to absolute.

        WHY: Pure function to ensure consistent path handling.
        PERFORMANCE: O(1) path conversion.

        Args:
            db_path: Database path to convert

        Returns:
            Absolute database path
        """
        if os.path.isabs(db_path):
            return db_path

        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, db_path)

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate SQLite database access.

        WHY: Ensures SQLite database is accessible before pipeline runs.
        PERFORMANCE: O(1) database connection check.

        Returns:
            ValidationResult for SQLite access
        """
        db_path = os.getenv("ARTEMIS_PERSISTENCE_DB", "../../.artemis_data/artemis_persistence.db")
        db_path = SQLiteValidator._get_absolute_db_path(db_path)
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


class PostgresValidator:
    """
    Validates PostgreSQL database access.

    WHY: PostgreSQL may be used for production deployments.
    RESPONSIBILITY: Validate PostgreSQL database access only.
    """

    @staticmethod
    def validate() -> ValidationResult:
        """
        Validate PostgreSQL database access.

        WHY: Placeholder for future PostgreSQL support.
        PERFORMANCE: O(1) - currently just logs warning.

        Returns:
            ValidationResult indicating PostgreSQL not yet implemented
        """
        return ValidationResult(
            check_name="PostgreSQL Database",
            passed=False,
            message="PostgreSQL persistence not yet implemented",
            severity="warning",
            fix_suggestion="Use ARTEMIS_PERSISTENCE_TYPE=sqlite for now"
        )


# Register validators using strategy pattern
# WHY: Decouples validator registration from DatabaseValidator class
DatabaseValidator.register_validator("sqlite", SQLiteValidator.validate)
DatabaseValidator.register_validator("postgres", PostgresValidator.validate)
