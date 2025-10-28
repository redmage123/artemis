"""
Core package - Foundation interfaces, exceptions, and constants.

WHY: Central location for shared abstractions and contracts.
RESPONSIBILITY: Define interfaces that all other modules depend on.
PATTERNS: Dependency Inversion (interfaces before implementations).

This package has NO dependencies on other Artemis packages (bottom layer).
"""

# Import interfaces (migrated)
from .interfaces import (
    PipelineStage,
    TestRunnerInterface,
    ValidatorInterface,
    LoggerInterface,
)

# Import constants (migrated)
from .constants import *

# Import exceptions (migrated)
from .exceptions import *

__all__ = [
    # Interfaces
    "PipelineStage",
    "TestRunnerInterface",
    "ValidatorInterface",
    "LoggerInterface",
    # Constants - exported via wildcard import from .constants
]
