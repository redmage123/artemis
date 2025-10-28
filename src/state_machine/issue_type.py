#!/usr/bin/env python3
"""
WHY: Catalog all types of issues that can occur during pipeline execution
RESPONSIBILITY: Provide comprehensive issue taxonomy for recovery workflow routing
PATTERNS: Error categorization, recovery workflow selection
"""

from enum import Enum


class IssueType(Enum):
    """Types of issues that can occur"""
    # Infrastructure issues
    TIMEOUT = "timeout"
    HANGING_PROCESS = "hanging_process"
    MEMORY_EXHAUSTED = "memory_exhausted"
    DISK_FULL = "disk_full"
    NETWORK_ERROR = "network_error"

    # Code issues
    COMPILATION_ERROR = "compilation_error"
    TEST_FAILURE = "test_failure"
    SECURITY_VULNERABILITY = "security_vulnerability"
    LINTING_ERROR = "linting_error"

    # Dependency issues
    MISSING_DEPENDENCY = "missing_dependency"
    VERSION_CONFLICT = "version_conflict"
    IMPORT_ERROR = "import_error"

    # LLM issues
    LLM_API_ERROR = "llm_api_error"
    LLM_TIMEOUT = "llm_timeout"
    LLM_RATE_LIMIT = "llm_rate_limit"
    INVALID_LLM_RESPONSE = "invalid_llm_response"

    # Stage-specific issues
    ARCHITECTURE_INVALID = "architecture_invalid"
    CODE_REVIEW_FAILED = "code_review_failed"
    INTEGRATION_CONFLICT = "integration_conflict"
    VALIDATION_FAILED = "validation_failed"

    # Multi-agent issues
    ARBITRATION_DEADLOCK = "arbitration_deadlock"
    DEVELOPER_CONFLICT = "developer_conflict"
    MESSENGER_ERROR = "messenger_error"

    # Data issues
    INVALID_CARD = "invalid_card"
    CORRUPTED_STATE = "corrupted_state"
    RAG_ERROR = "rag_error"

    # System issues
    ZOMBIE_PROCESS = "zombie_process"
    FILE_LOCK = "file_lock"
    PERMISSION_DENIED = "permission_denied"
