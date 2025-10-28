#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER for code_examples_database module.

WHY:
This wrapper maintains backward compatibility while the actual implementation
has been refactored into a modular package structure.

RESPONSIBILITY:
- Re-export all database example constants from the code_examples package
- Maintain exact same API for existing code
- Provide deprecation path for future migrations

PATTERNS:
- Simple re-export pattern using __all__
- Imports from modularized code_examples package
- Zero business logic (all logic in package modules)

MIGRATION:
Old import: from code_examples_database import POSTGRESQL_EXAMPLES
New import: from code_examples.postgresql_examples import POSTGRESQL_EXAMPLES
Or: from code_examples import POSTGRESQL_EXAMPLES

This wrapper allows gradual migration without breaking existing code.
"""

from code_examples import (
    POSTGRESQL_EXAMPLES,
    MONGODB_EXAMPLES,
    CASSANDRA_EXAMPLES,
    MYSQL_EXAMPLES,
    REDIS_EXAMPLES,
    DYNAMODB_EXAMPLES,
    ALL_DATABASE_EXAMPLES,
)

__all__ = [
    "POSTGRESQL_EXAMPLES",
    "MONGODB_EXAMPLES",
    "CASSANDRA_EXAMPLES",
    "MYSQL_EXAMPLES",
    "REDIS_EXAMPLES",
    "DYNAMODB_EXAMPLES",
    "ALL_DATABASE_EXAMPLES",
]
