#!/usr/bin/env python3
"""
Configuration Models and Schema Definitions

WHY: Centralizes all configuration data models, schema definitions, and constants.
Separates data structures from business logic for better maintainability.

RESPONSIBILITY: Define configuration models, validation result structures, and schema.

PATTERNS:
- Dataclass pattern for immutable data structures
- Strategy pattern using dispatch tables (BOOL_STRING_MAP, PROVIDER_KEY_MAP)
- Guard clauses for validation
"""

import tempfile
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


# Constants for boolean string conversion (Strategy pattern - avoid if/elif)
BOOL_STRING_MAP: Dict[str, bool] = {
    'true': True, 'True': True, 'TRUE': True,
    'false': False, 'False': False, 'FALSE': False
}

# Constants for LLM provider to API key mapping (Strategy pattern - avoid elif)
PROVIDER_KEY_MAP: Dict[str, str] = {
    'openai': 'OPENAI_API_KEY',
    'anthropic': 'ANTHROPIC_API_KEY'
}


@dataclass
class ConfigValidationResult:
    """
    Result of configuration validation

    WHY: Encapsulates validation results in a structured format.
    Makes validation results easy to test and consume.
    """
    is_valid: bool
    missing_keys: List[str]
    invalid_keys: List[str]
    warnings: List[str]
    config_summary: Dict[str, Any]


class ConfigSchema:
    """
    Configuration Schema Definition

    WHY: Centralizes all configuration schema definitions with defaults,
    requirements, and validation rules. Makes schema updates easier.

    RESPONSIBILITY: Define and provide access to configuration schema.
    """

    # Configuration schema with defaults and requirements
    SCHEMA: Dict[str, Dict[str, Any]] = {
        # LLM Provider Configuration
        'ARTEMIS_LLM_PROVIDER': {
            'default': 'openai',
            'required': False,
            'sensitive': False,
            'description': 'Primary LLM provider (openai/anthropic)',
            'valid_values': ['openai', 'anthropic']
        },
        'ARTEMIS_LLM_MODEL': {
            'default': None,  # Provider-specific default
            'required': False,
            'sensitive': False,
            'description': 'Specific LLM model to use'
        },

        # API Keys
        'OPENAI_API_KEY': {
            'default': None,
            'required': False,  # Required only if provider is openai
            'sensitive': True,
            'description': 'OpenAI API key'
        },
        'ANTHROPIC_API_KEY': {
            'default': None,
            'required': False,  # Required only if provider is anthropic
            'sensitive': True,
            'description': 'Anthropic API key'
        },

        # Database and Storage
        'ARTEMIS_RAG_DB_PATH': {
            'default': 'db',  # Relative to .agents/agile directory
            'required': False,
            'sensitive': False,
            'description': 'Path to RAG database (ChromaDB, relative to .agents/agile)'
        },
        'ARTEMIS_TEMP_DIR': {
            'default': tempfile.gettempdir(),
            'required': False,
            'sensitive': False,
            'description': 'Temporary directory for pipeline artifacts'
        },

        # Pipeline Configuration
        'ARTEMIS_MAX_PARALLEL_DEVELOPERS': {
            'default': '3',
            'required': False,
            'sensitive': False,
            'description': 'Maximum number of parallel developers'
        },
        'ARTEMIS_ENABLE_CODE_REVIEW': {
            'default': 'true',
            'required': False,
            'sensitive': False,
            'description': 'Enable code review stage (true/false)'
        },
        'ARTEMIS_AUTO_APPROVE_PROJECT_ANALYSIS': {
            'default': 'true',  # Default to auto-approve for non-interactive use
            'required': False,
            'sensitive': False,
            'description': 'Auto-approve project analysis suggestions (true/false)'
        },

        # Logging and Monitoring
        'ARTEMIS_VERBOSE': {
            'default': 'true',
            'required': False,
            'sensitive': False,
            'description': 'Enable verbose logging (true/false)'
        },
        'ARTEMIS_LOG_LEVEL': {
            'default': 'INFO',
            'required': False,
            'sensitive': False,
            'description': 'Log level (DEBUG/INFO/WARNING/ERROR)',
            'valid_values': ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        },

        # Security and Compliance
        'ARTEMIS_ENFORCE_GDPR': {
            'default': 'true',
            'required': False,
            'sensitive': False,
            'description': 'Enforce GDPR compliance checks'
        },
        'ARTEMIS_ENFORCE_WCAG': {
            'default': 'true',
            'required': False,
            'sensitive': False,
            'description': 'Enforce WCAG accessibility checks'
        },

        # Cost Controls
        'ARTEMIS_MAX_TOKENS_PER_REQUEST': {
            'default': '8000',
            'required': False,
            'sensitive': False,
            'description': 'Maximum tokens per LLM request'
        },
        'ARTEMIS_COST_LIMIT_USD': {
            'default': None,
            'required': False,
            'sensitive': False,
            'description': 'Maximum cost limit in USD (optional)'
        }
    }

    @classmethod
    def get_schema(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get configuration schema

        Returns:
            Configuration schema dictionary
        """
        return cls.SCHEMA

    @classmethod
    def get_key_schema(cls, key: str) -> Optional[Dict[str, Any]]:
        """
        Get schema for specific key

        Args:
            key: Configuration key

        Returns:
            Schema dictionary or None if key doesn't exist
        """
        return cls.SCHEMA.get(key)

    @classmethod
    def is_sensitive(cls, key: str) -> bool:
        """
        Check if configuration key contains sensitive data

        Args:
            key: Configuration key

        Returns:
            True if sensitive, False otherwise
        """
        schema = cls.get_key_schema(key)
        if not schema:
            return False
        return schema.get('sensitive', False)

    @classmethod
    def get_default(cls, key: str) -> Any:
        """
        Get default value for configuration key

        Args:
            key: Configuration key

        Returns:
            Default value or None
        """
        schema = cls.get_key_schema(key)
        if not schema:
            return None
        return schema.get('default')

    @classmethod
    def get_valid_values(cls, key: str) -> Optional[List[Any]]:
        """
        Get valid values for configuration key

        Args:
            key: Configuration key

        Returns:
            List of valid values or None if no constraint
        """
        schema = cls.get_key_schema(key)
        if not schema:
            return None
        return schema.get('valid_values')
