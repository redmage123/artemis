#!/usr/bin/env python3
"""
Configuration Validators - Backward Compatibility Wrapper

WHY: Maintains 100% backward compatibility while delegating to modular package

RESPONSIBILITY: Re-export all validator classes from modular validators package

PATTERNS: Facade pattern, backward compatibility wrapper, clean delegation

REFACTORED: This file has been refactored into a modular package structure.
Original 619-line monolithic file is now split into focused modules:
- validators/llm_validator.py - LLM provider and API key validation
- validators/path_validator.py - File system path validation
- validators/database_validator.py - Database connectivity validation
- validators/messenger_validator.py - Messenger backend validation
- validators/rag_validator.py - RAG database validation
- validators/resource_validator.py - Resource limit validation
- validators/optional_service_validator.py - Optional service validation
- validators/facade.py - Orchestration facade

All imports from this module continue to work without modification.
"""

# Re-export all validator classes for backward compatibility
# WHY: Existing code can still import from config.validators without changes
from .validators import (
    LLMProviderValidator,
    PathValidator,
    DatabaseValidator,
    MessengerValidator,
    RAGDatabaseValidator,
    ResourceLimitValidator,
    OptionalServiceValidator,
    ValidatorFacade
)

# Maintain public API
__all__ = [
    "LLMProviderValidator",
    "PathValidator",
    "DatabaseValidator",
    "MessengerValidator",
    "RAGDatabaseValidator",
    "ResourceLimitValidator",
    "OptionalServiceValidator",
    "ValidatorFacade",
]
