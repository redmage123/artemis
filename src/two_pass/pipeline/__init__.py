"""
Module: two_pass/pipeline/__init__.py

WHY: Clean public API for two_pass.pipeline package.
RESPONSIBILITY: Export main classes and maintain clean namespace.
PATTERNS: Facade Pattern, Information Hiding.

This module handles:
- Export TwoPassPipeline as main entry point
- Export supporting classes for advanced usage
- Hide internal implementation details
- Provide backward compatibility
"""

from two_pass.pipeline.orchestrator import TwoPassPipeline
from two_pass.pipeline.executor import TwoPassExecutor
from two_pass.pipeline.retry import RetryStrategy, RetryConfig
from two_pass.pipeline.ai_integration import AIIntegrationMixin, AIConfig

# Main public interface
__all__ = [
    'TwoPassPipeline',        # Main facade - use this for most cases
    'TwoPassExecutor',        # Advanced: Direct executor access
    'RetryStrategy',          # Advanced: Custom retry configuration
    'RetryConfig',            # Advanced: Retry policy configuration
    'AIIntegrationMixin',     # Advanced: AI integration capabilities
    'AIConfig',               # Advanced: AI configuration
]

# Version information
__version__ = '2.0.0'  # Modularized version

# Package metadata
__author__ = 'Artemis Development Pipeline'
__description__ = 'Modular two-pass pipeline with AI integration and rollback'
