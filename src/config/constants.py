#!/usr/bin/env python3
"""
Configuration Validation Constants

WHY: Centralizes configuration constants and defaults

RESPONSIBILITY: Define all configuration constants and default values

PATTERNS: Module-level constants for easy access
"""

from typing import Dict, Any, Optional, Callable

# Valid LLM providers
VALID_LLM_PROVIDERS = ["openai", "anthropic", "mock"]

# Valid messenger types
VALID_MESSENGER_TYPES = ["file", "rabbitmq", "mock"]

# Valid persistence types
VALID_PERSISTENCE_TYPES = ["sqlite", "postgres"]

# Resource limits
MIN_PARALLEL_DEVELOPERS = 1
MAX_PARALLEL_DEVELOPERS = 5

# Default environment variable names
DEFAULT_LLM_PROVIDER = "openai"
DEFAULT_MESSENGER_TYPE = "file"
DEFAULT_PERSISTENCE_TYPE = "sqlite"
DEFAULT_MAX_PARALLEL_DEVELOPERS = "2"

# Default paths (relative to script directory)
DEFAULT_TEMP_DIR = "../../.artemis_data/temp"
DEFAULT_ADR_DIR = "../../.artemis_data/adrs"
DEFAULT_DEVELOPER_DIR = "../../.artemis_data/developer_output"
DEFAULT_PERSISTENCE_DB = "../../.artemis_data/artemis_persistence.db"
DEFAULT_RAG_DB_PATH = "db"
DEFAULT_MESSAGE_DIR = "/tmp/agent_messages"
DEFAULT_RABBITMQ_URL = "amqp://localhost"

# Provider configurations
# WHY: Strategy pattern via dictionary mapping instead of if/elif chain
# Makes it easy to add new providers without modifying code structure
PROVIDER_CONFIGS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "env_var": "OPENAI_API_KEY",
        "name": "OpenAI API Key",
        "validator": lambda key: key.startswith("sk-"),
        "error_msg": "API key has invalid format",
        "fix_suggestion": "export OPENAI_API_KEY=sk-...",
        "validation_msg": "OpenAI keys should start with 'sk-'"
    },
    "anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "name": "Anthropic API Key",
        "validator": None,
        "fix_suggestion": "export ANTHROPIC_API_KEY=..."
    },
    "mock": {
        "env_var": None,
        "name": "Mock LLM",
        "is_mock": True
    }
}
