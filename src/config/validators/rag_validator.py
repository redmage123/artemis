#!/usr/bin/env python3
"""
RAG Database Validation Module

WHY: Validates RAG database (ChromaDB) availability for retrieval-augmented generation

RESPONSIBILITY: Validate ChromaDB access for RAG features

PATTERNS: Guard clauses for early returns, pure validation logic
"""

import os
from pathlib import Path
from ..models import ValidationResult
from ..constants import DEFAULT_RAG_DB_PATH
from ..path_utils import resolve_relative_path, get_script_directory


class RAGDatabaseValidator:
    """
    Validates RAG database (ChromaDB) access

    WHY: Single Responsibility - handles only RAG database validation

    PATTERNS: Guard clauses for early returns
    """

    def validate_rag_database(self) -> ValidationResult:
        """
        Check RAG database (ChromaDB) access

        WHY: Validates ChromaDB availability for RAG features
        PERFORMANCE: O(1) import and directory check

        Returns:
            ValidationResult for RAG database check
        """
        # Get RAG DB path from env or use default relative to script directory
        rag_db_path = os.getenv("ARTEMIS_RAG_DB_PATH", DEFAULT_RAG_DB_PATH)
        script_dir = get_script_directory()
        rag_db_path = resolve_relative_path(rag_db_path, script_dir)

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
