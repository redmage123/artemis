#!/usr/bin/env python3
"""
Configuration Agent Package

WHY: Modular configuration management system for Artemis pipeline.
Separates concerns: loading, validation, generation, and coordination.

RESPONSIBILITY: Export public API for configuration management

ARCHITECTURE:
- models.py: Data models and schema definitions
- loader.py: Configuration loading from environment/files
- validator.py: Configuration validation logic
- generator.py: Report and export generation
- agent_core.py: Main agent coordination

PATTERNS:
- Facade pattern: agent_core provides simple API
- Single Responsibility: Each module has one purpose
- Composition: Agent composes loader, validator, generator
"""

# Import main agent class
from agents.config.agent_core import (
    ConfigurationAgent,
    get_config,
    reset_config
)

# Import models for type hints and direct use
from agents.config.models import (
    ConfigValidationResult,
    ConfigSchema,
    BOOL_STRING_MAP,
    PROVIDER_KEY_MAP
)

# Import loader for advanced usage
from agents.config.loader import ConfigLoader

# Import validator for advanced usage
from agents.config.validator import ConfigValidator

# Import generator for custom reporting
from agents.config.generator import ConfigGenerator


# Public API
__all__ = [
    # Main agent
    'ConfigurationAgent',
    'get_config',
    'reset_config',

    # Models
    'ConfigValidationResult',
    'ConfigSchema',
    'BOOL_STRING_MAP',
    'PROVIDER_KEY_MAP',

    # Components (for advanced usage)
    'ConfigLoader',
    'ConfigValidator',
    'ConfigGenerator',
]


# Package metadata
__version__ = '1.0.0'
__author__ = 'Artemis Team'
__description__ = 'Modular configuration management for Artemis pipeline'
