"""
WHY: Provide clean public API for CLI package
RESPONSIBILITY: Export main CLI components and entry points
PATTERNS:
- Facade pattern for package interface
- Explicit exports for controlled API
"""

from cli.cli_core import ArtemisCLI, main
from cli.models import (
    CLIArguments,
    CommandResult,
    CommandType,
    PromptAction,
    SystemStatus,
    LLMConfig,
    StoragePaths
)
from cli.parser import ArgumentParser
from cli.commands import CommandDispatcher
from cli.formatters import OutputFormatter, StatusFormatter, PromptFormatter

__all__ = [
    # Main entry points
    'ArtemisCLI',
    'main',

    # Models
    'CLIArguments',
    'CommandResult',
    'CommandType',
    'PromptAction',
    'SystemStatus',
    'LLMConfig',
    'StoragePaths',

    # Components
    'ArgumentParser',
    'CommandDispatcher',
    'OutputFormatter',
    'StatusFormatter',
    'PromptFormatter',
]

__version__ = '1.0.0'
